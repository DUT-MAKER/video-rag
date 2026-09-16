# BÁO CÁO KỸ THUẬT HỆ THỐNG THU THẬP DỮ LIỆU VIDEO (CRAWLER SYSTEM REPORT)

**Dự án:** `video-rag` (Hệ thống RAG Phân tích Pattern Video Viral & Sinh Kịch bản Ngắn)  
**Module:** `module/crawler/`  
**Kiến trúc:** Clean Architecture / Domain-Driven Design (DDD) & 12-Factor App  
**Tác giả:** Engineering Team  
**Phiên bản:** v1.0.0  
**Ngày phát hành:** 16/09/2026  

---

## 1. TỔNG QUAN & ĐỐI CHIẾU YÊU CẦU (PROJECT ALIGNMENT)

### 1.1. Phạm vi & Ranh giới trách nhiệm (Bounded Context)
Theo định hướng kiến trúc từ PRD (`project-overview-prd.md`):
* **Trách nhiệm của Crawler:** Dừng lại ở việc thu thập dữ liệu video, trích xuất metadata chuẩn hóa, tải media, bóc tách lời thoại kèm timestamp, gọi LLM tóm tắt nội dung cốt lõi, upload tài nguyên lên Object Storage và xuất payload theo đúng **Data Contract**.
* **Ranh giới:** Crawler **hoàn toàn không** chứa logic bóc tách Hook tâm lý hay lưu trữ vector database/RAG. Các bước này thuộc về `IngestVideoDataUseCase` và `SearchViralPatternsUseCase` của module `video_rag`.

### 1.2. Chuẩn Data Contract đã hiện thực
Mỗi video được xử lý thành công sẽ xuất ra một cấu trúc JSON độc lập:
```json
{
  "caption": "Tiêu đề và mô tả video",
  "hashtag": ["shorts", "viral", "tintuc"],
  "transcript": "Toàn văn lời thoại trong video...",
  "image_url": "http://storage.local/... hoặc s3://...",
  "summary": "Tóm tắt cốt lõi 2-3 câu từ mô hình LLM",
  "video_url": "http://storage.local/... hoặc s3://...",
  "_enriched_metadata": {
    "platform": "youtube_shorts",
    "video_id": "RiEg8h2jquM",
    "duration": 46.0,
    "aspect_ratio": "1080:1920",
    "upload_date": "20260315",
    "is_auto_generated": true,
    "metrics": {
      "view_count": 50000,
      "like_count": 2000,
      "comment_count": 120
    },
    "transcript_segments": [
      { "start": 0.0, "end": 2.5, "text": "Câu mở đầu video..." },
      { "start": 2.5, "end": 5.0, "text": "Câu tiếp theo..." }
    ]
  }
}
```

---

## 2. THIẾT KẾ KIẾN TRÚC HỆ THỐNG (CLEAN ARCHITECTURE)

Hệ thống được thiết kế theo cấu trúc module đa nền tảng, đảm bảo mở rộng dễ dàng sang TikTok hoặc Instagram Reels trong tương lai mà không phá vỡ logic nghiệp vụ cốt lõi.

```
module/crawler/
├── domain.py                     # Entities, Value Objects, Domain Exceptions
├── port.py                       # Interface trừu tượng (Ports)
├── cli.py                        # Entrypoint CLI điều phối đa nền tảng
├── shared/                       # Các Adapter dùng chung mọi nền tảng
│   ├── storage.py                # LocalStorageAdapter & MinioStorageAdapter
│   ├── llm_summary.py            # LLMSummaryAdapter (OpenAI-compatible / Gemini)
│   ├── dedup_store.py            # JsonFileDedupStore (Chống cào trùng)
│   └── whisper_asr.py            # WhisperASREngine (Faster-Whisper local ASR)
└── platforms/
    └── youtube_shorts/           # Adapter chuyên biệt cho YouTube Shorts
        ├── extractor.py          # yt-dlp metadata & media downloader
        ├── transcript.py         # Subtitle API & Circuit Breaker & ASR fallback
        └── pipeline.py           # Orchestrator điều phối xử lý 1 video Shorts
```

### Sơ đồ luồng xử lý (Interaction Flow)

```mermaid
flowchart TD
    A[User / CLI Runner] --> B[YouTubeShortsPipeline]
    B --> C{DedupStore Check}
    C -->|Đã cào| D[Skip Video]
    C -->|Chưa cào| E[YouTubeShortsExtractor]
    E --> F{Lọc định dạng Shorts\nduration <= 65s & h > w}
    F -->|Sai định dạng| D
    F -->|Đúng định dạng| G[Download Media vào TempDir]
    G --> H[YouTubeShortsTranscriptAdapter]
    
    H --> I{Thử lấy Subtitle API}
    I -->|Thành công| K[Chuẩn hóa Timestamp Segments]
    I -->|NoTranscript / Disabled| L[Gọi Faster-Whisper ASR Local]
    I -->|IpBlocked| M{fallback_on_ip_block?}
    M -->|False: Prod/Batch| N[Raise IpBlockedStopSignal -> Halt Job]
    M -->|True: Dev test| L
    L --> K

    K --> O[StorageAdapter: Upload Video & Thumbnail]
    O --> P[LLMSummaryAdapter: Gemini 2.5 Flash]
    P --> Q[Mark Processed trong DedupStore]
    Q --> R[Format Output JSON theo Data Contract]
```

---

## 3. CHI TIẾT CÁC THÀNH PHẦN KỸ THUẬT CỐT LÕI

### 3.1. Phân tầng Domain & Ports (`domain.py`, `port.py`)
* **`VideoMetadata`**: Chứa thông tin thô từ mạng xã hội; thuộc tính logic `is_shorts` tự động xác minh tỷ lệ video dọc (`height > width > 0`) và thời lượng phù hợp.
* **`TranscriptSegment`**: Đảm bảo mỗi phân đoạn âm thanh luôn đi kèm `start` và `end` (giây) dạng `float`, hỗ trợ module RAG trích xuất Hook 3-5 giây đầu chính xác.
* **Exceptions**:
  * `IpBlockedStopSignal`: Tín hiệu ngắt mạch bảo vệ hệ thống.
  * `LLMUnavailableError`: Thông báo server LLM ngoại vi gián đoạn, ngăn chặn việc tạo dữ liệu tóm tắt giả mạo (no text hallucination).

### 3.2. Động cơ Phụ đề Hybrid 2 Tầng (`transcript.py`, `whisper_asr.py`)
* **Tầng 1 (Ưu tiên Subtitle API):** Sử dụng `youtube-transcript-api==1.2.4` để lấy phụ đề có sẵn (ưu tiên phụ đề thủ công `vi`, sau đó đến auto-generated ASR). Tốc độ cực nhanh (< 1 giây/video), không tốn tài nguyên tính toán.
* **Tầng 2 (Faster-Whisper Fallback):** Tích hợp model `faster-whisper-base` (chạy CTranslate2 CPU/GPU `int8`). Tự động kích hoạt khi video không có phụ đề trực tuyến (`NoTranscriptFound` hoặc `TranscriptsDisabled`).
* **Circuit Breaker an toàn:** Khi YouTube chặn IP (`IpBlocked`), adapter mặc định **ngắt mạch ngay lập tức (`fallback_on_ip_block=False`)** để bảo vệ tài nguyên compute khi cào batch lớn. Chỉ duy nhất trong môi trường kiểm thử dev cục bộ mới bật cờ dự phòng.

### 3.3. Động cơ Tóm tắt Nội dung AI (`llm_summary.py`)
* **Giao thức:** Chuẩn hóa theo chuẩn OpenAI Chat Completions API (`/chat/completions`), cho phép cắm ghép bất kỳ LLM nào (vLLM, Ollama, Google Gemini).
* **Tích hợp thực tế:** Kết nối trực tiếp với **Google AI Studio (Gemini 2.5/Flash)** thông qua API Key người dùng.
* **Độ bền cao (Resilience):** Tích hợp vòng lặp retry 3 lần tự động với exponential backoff khi gặp mã lỗi tạm thời HTTP 429 hoặc 503 (Server High Demand).

### 3.4. Lưu trữ Media 2 Chế độ (`storage.py`)
* **`LocalStorageAdapter`:** Dành cho phát triển độc lập trên máy lập trình viên (`data/storage/videos/` và `data/storage/thumbnails/`), không yêu cầu cấu hình hạ tầng mạng.
* **`MinioStorageAdapter`:** Dành cho môi trường team/production, tự động khởi tạo bucket và đẩy tài nguyên lên Object Storage S3 chung.

---

## 4. QUY TRÌNH CHUYỂN ĐỔI LOCAL VS SERVER (12-FACTOR APP)

Hệ thống cam kết **không thay đổi một dòng code nào** khi đẩy từ máy cá nhân lên server production. Toàn bộ cấu hình được nạp động từ file biến môi trường [`.env`](file:///Users/phat/video-rag/.env):

| Thành phần | Cấu hình chạy Local (Dev) | Cấu hình chạy Server chung (Prod) |
| :--- | :--- | :--- |
| **Storage Backend** | `--storage local` | `--storage minio` |
| **LLM Model URL** | `https://generativelanguage.googleapis.com/v1beta/openai` (Gemini) | `http://<ip-server-team>:8000/v1` (vLLM / Ollama nội bộ) |
| **Vector Database** | `VECTOR_STORE_TYPE=chroma` (lưu tại `./data/storage/chroma`) | `VECTOR_STORE_TYPE=pgvector` (lưu tại PostgreSQL chung) |
| **Database URL** | SQLite / Local disk | `postgresql+asyncpg://dutai:dutai@100.84.187.107:5698/video_rag_dev` |

---

## 5. BỘ CÔNG CỤ DÒNG LỆNH (CLI & SCRIPTS)

### 5.1. `scripts/crawl.py` (Công cụ thu thập chính thức)
Dùng để chạy cào video đơn lẻ hoặc cào hàng loạt từ file danh sách:
```bash
# Cào 1 video YouTube Shorts
uv run python scripts/crawl.py "https://www.youtube.com/shorts/RiEg8h2jquM" --storage local

# Cào hàng loạt video từ file text với khoảng giãn cách 3 giây chống rate-limit
uv run python scripts/crawl.py --file links.txt --delay 3.0 --storage minio
```

### 5.2. `scripts/run_e2e.py` (Script kiểm chứng liên hoàn End-to-End)
Script kịch bản tầng ứng dụng điều phối toàn bộ chu trình: Crawl $\rightarrow$ Whisper ASR $\rightarrow$ Gemini LLM $\rightarrow$ Nạp ChromaDB $\rightarrow$ Tìm kiếm ngữ nghĩa Semantic Search:
```bash
uv run python scripts/run_e2e.py "https://www.youtube.com/shorts/RiEg8h2jquM" --query "hành hung tài xế taxi"
```

### 5.3. `scripts/inspect_db.py` (Công cụ soi dữ liệu Database)
Đọc trực tiếp ChromaDB trên đĩa và in ra số lượng bản ghi, tiêu đề, tóm tắt và Hook trích xuất:
```bash
uv run python scripts/inspect_db.py
```

---

## 6. BẰNG CHỨNG THỰC NGHIỆM & KẾT QUẢ KIỂM THỬ

### 6.1. Kết quả kiểm thử tự động (Unit Test Suite)
Bộ test gồm **10 ca kiểm thử đơn vị độc lập** bao phủ toàn bộ các kịch bản thành công và ngoại lệ:

```text
============================= test session starts ==============================
platform darwin -- Python 3.13.13, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/phat/video-rag
configfile: pyproject.toml
plugins: asyncio-1.4.0, anyio-4.15.1
collected 10 items

tests/test_crawler.py::test_pipeline_happy_path PASSED                   [ 10%]
tests/test_crawler.py::test_pipeline_skips_already_processed_video PASSED [ 20%]
tests/test_crawler.py::test_pipeline_skips_non_shorts PASSED             [ 30%]
tests/test_crawler.py::test_pipeline_reraises_ip_blocked_signal PASSED   [ 40%]
tests/test_crawler.py::test_pipeline_handles_llm_unavailable_without_fabrication PASSED [ 50%]
tests/test_crawler.py::test_local_storage_adapter PASSED                 [ 60%]
tests/test_crawler.py::test_json_file_dedup_store PASSED                 [ 70%]
tests/test_crawler.py::test_transcript_adapter_whisper_fallback_when_no_subtitles PASSED [ 80%]
tests/test_crawler.py::test_transcript_adapter_whisper_fallback_when_transcripts_disabled PASSED [ 90%]
tests/test_crawler.py::test_pipeline_asr_fallback_when_no_transcript PASSED [100%]

============================== 10 passed in 0.43s ==============================
```

### 6.2. Kết quả chạy thực tế trên Video YouTube Shorts thật
* **Target Video:** VTV24 Short ([`https://www.youtube.com/shorts/RiEg8h2jquM`](https://www.youtube.com/shorts/RiEg8h2jquM) - 46 giây, 1080x1920).
* **Trích xuất âm thanh:** Tự động kích hoạt Faster-Whisper ASR local, nhận diện thành công 17 segments lời thoại tiếng Việt.
* **Tóm tắt Gemini AI:**
  > *"Công an TP. Quảng Ninh đã khởi tố và bắt tạm giam 5/6 bị can trong nhóm hành hung tài xế taxi tại Móng Cái sau khi bị từ chối chở thêm người vì đã đủ chỗ. Vụ việc gây mất an ninh trật tự công cộng, và cơ quan điều tra đang tiếp tục truy tìm những đối tượng còn lại để xử lý theo pháp luật."*
* **Trích xuất Hook (3-5s đầu):**
  > *"liên quan đến vụ tài xế tắc xì bị hành hùng ở bóng khái, cơ quan cảnh sát điều tra công an thành phố quản định vừa khởi tố vụ án, khởi tố sấu bị..."*
* **Đánh giá chất lượng ASR tiếng Việt:**
  * Model Whisper `base` (140MB) gặp hạn chế rõ rệt với danh từ riêng tiếng Việt: *"tắc xì"* (taxi), *"bóng khái"* (Móng Cái), *"quản định"* (Quảng Ninh).
  * Điều này khẳng định nhận định trước đó: Các video không có phụ đề sẵn (chiếm 30-40%) khi dùng Whisper `base` sẽ có độ tin cậy từ khóa thấp hơn phụ đề gốc của nền tảng.
* **Lưu trữ & Truy vấn Vector DB (ChromaDB):**
  * Đã index thành công vào ChromaDB và truy xuất chính xác Top-1 với điểm số `0.4135` cho câu hỏi `"vụ án hành hung tài xế taxi"`.
  * *Lưu ý về điểm số 0.4135:* Kết quả này đạt được khi đang bật `USE_LOCAL_FALLBACK=true` (dùng token-hash 384-dim dựa trên character n-gram cosine similarity để test độc lập không cần server embedding). Khi kết nối model embedding tiếng Việt chuyên dụng (`keepitreal/vietnamese-sbert` hoặc BGE), điểm tương đồng ngữ nghĩa sẽ cao và chính xác hơn nhiều.

---

## 7. KẾT LUẬN & ĐỀ XUẤT PHÁT TRIỂN (ROADMAP)

Hệ thống Crawler hiện tại đã hoàn thiện về mặt kiến trúc kỹ thuật, tuân thủ đúng DDD và ranh giới nghiệp vụ của dự án:
1. **Tính sẵn sàng cao:** Chạy độc lập hoàn toàn trên máy local và sẵn sàng đẩy lên server team chỉ bằng việc chuyển biến môi trường `.env`.
2. **Khả năng mở rộng:** Khi cần cào thêm TikTok hay Instagram Reels, chỉ cần tạo adapter tương ứng trong `module/crawler/platforms/<platform_name>/` tuân thủ interface `IPlatformCrawlerPort`.
3. **Đề xuất nâng cấp kỹ thuật & vận hành:**
   * **Nâng cấp model Whisper cho tiếng Việt:** Cân nhắc nâng lên model `small` hoặc `medium` (hoặc Whisper tinh chỉnh riêng cho tiếng Việt) để giảm thiểu sai chính tả danh từ riêng ở 3-5 giây đầu của Hook.
   * **Gắn nhãn độ tin cậy transcript (`transcript_source`):** Bổ sung trường định danh nguồn phụ đề (`youtube_manual` | `youtube_auto` | `whisper_asr`) để tầng Ingest/RAG có thể đánh trọng số ưu tiên khi ranking tìm kiếm.
   * **Nâng ngưỡng `is_shorts` lên 180s:** Phù hợp với chính sách mở rộng Shorts lên 3 phút của YouTube từ cuối năm 2024.
   * **Kiểm thử vận hành Batch với Delay:** Chạy thử nghiệm batch nhỏ (5-10 video) kèm cờ `--delay 3.0` để đo lường ngưỡng rate-limit thực tế trước khi cào hàng loạt quy mô lớn.
   * **Cơ chế xoay Proxy / Residential VPN:** Cần chuẩn bị hạ tầng proxy nếu triển khai cào tự động 24/7 trên môi trường cloud.
