# Product Requirements Document (PRD) — RAG Viral Video

> **Hệ thống AI Agent tự động phân tích pattern video viral và tạo kịch bản, storyboard, prompts cho video ngắn đa nền tảng (TikTok, Reels, YouTube Shorts) ứng dụng RAG.**

---

## 1. Bối Cảnh & Vấn Đề (The Problem)

Trong sản xuất nội dung video ngắn (Short-form Video):
1. **Thiếu tính giữ chân (Retention):** 3-5 giây đầu quyết định tới 80% tỷ lệ người xem lướt qua hay ở lại. Kịch bản thông thường do LLM tạo ra thường thiếu các công thức Hook tâm lý đã được chứng minh hiệu quả.
2. **Kịch bản chung chung, thiếu bối cảnh thực tế:** Các kịch bản do ChatGPT hay Claude tự sinh không nắm bắt được văn phong, từ khoá thịnh hành (slang, trend) và nhịp điệu (pacing) của các video đã thực sự đạt triệu view trên TikTok/Reels.
3. **Mất nhiều thời gian chuyển dịch từ Kịch bản sang Sản xuất:** Người sáng tạo nội dung không chỉ cần lời thoại (Narration), mà cần:
   * Mô tả hình ảnh / B-roll chi tiết từng giây.
   * Prompts tối ưu hóa sẵn cho AI tạo hình ảnh (Midjourney, Flux, Stable Diffusion).
   * Prompts camera movement cho AI tạo video (Veo 3.1, Runway, Kling).
   * Gợi ý hiệu ứng âm thanh (SFX) và nhịp nhạc nền.

👉 **RAG Viral Video** giải quyết bài toán này bằng cách kết nối **kho video viral đã thu thập sẵn** (chứa transcript, caption, hashtag, tóm tắt và video MinIO) với **AI Agent** để phân tích mẫu kịch bản thành công và sinh ra kịch bản hoàn chỉnh chuẩn quy trình sản xuất.

---

## 2. Mục Tiêu & Phạm Vi (Goals & Scope)

### 2.1. Mục Tiêu Cốt Lõi (Core Objectives)
* **Tận dụng kho dữ liệu có sẵn:** Ingest dữ liệu video dạng JSON vào Vector Database (ChromaDB) thông qua mô hình Embedding riêng.
* **RAG Retrieval chính xác:** Khi người dùng cung cấp một chủ đề (topic), hệ thống tự động tìm kiếm các video có cấu trúc hook, phong cách hoặc nội dung tương đồng trong kho.
* **Sinh kịch bản chi tiết (1-Click):** Sử dụng LLM self-hosted để xuất ra kịch bản phân cảnh chuẩn xác theo từng khoảng thời gian (00:00 - 00:04, 00:04 - 00:09...), bao gồm:
  1. Lời thoại voiceover.
  2. Mô tả hình ảnh và hành động nhân vật / B-roll.
  3. Image Prompts cho Midjourney / Flux.
  4. Video Prompts cho Veo 3.1 / Runway Gen-3 / Kling.
  5. Audio SFX & Background music cues.
* **Cung cấp REST API (FastAPI):** Dễ dàng tích hợp với các hệ thống frontend, bot hoặc pipeline dựng video tự động trong tương lai.

### 2.2. Ngoài Phạm Vi (Out of Scope giai đoạn này)
* Không render trực tiếp file video MP4 (việc tạo video bằng Remotion/FFmpeg được tách thành module độc lập sau này).
* Không trực tiếp gọi API trả phí từ bên ngoài mà tập trung sử dụng hạ tầng mô hình **self-hosted** của bạn.

---

## 3. Cấu Trúc Dữ Liệu Đầu Vào (Data Contract)

Dữ liệu kho video có định dạng JSON chuẩn thống nhất:

| Trường Chuẩn (Key) | Kiểu Dữ Liệu | Mục Đích Trong RAG |
|--------------------|--------------|---------------------|
| `caption` | `string` | Tiêu đề hoặc mô tả bài đăng (context & hook) |
| `hashtag` | `string` / `list[string]` | Thẻ hashtag phân loại chủ đề, xu hướng |
| `transcript` | `string` | Toàn bộ lời thoại video (vector hóa & học nhịp kịch bản) |
| `image_url` | `string` | URL ảnh thumbnail hoặc keyframe của video |
| `summary` | `string` | Tóm tắt ý chính của video (ngữ cảnh vector search) |
| `video_url` | `string` | Đường dẫn file video gốc lưu trữ tại MinIO Storage |

---

## 4. Đặc Tả Chức Năng (Functional Requirements)

```mermaid
journey
    title Trải Nghiệm Sử Dụng RAG Viral Video
    section 1. Quản Trị Kho
      Nạp file JSON kho video: 5: Admin
      Tự động bóc tách Hook & Metadata: 5: Hệ thống
      Lưu trữ Vector Embedding: 5: ChromaDB
    section 2. Khám Phá Pattern
      Tìm kiếm video tương tự theo từ khóa: 4: Creator
      Xem video mẫu trên MinIO & phân tích Hook: 5: Creator
    section 3. Sinh Kịch Bản
      Nhập chủ đề & thời lượng mong muốn: 5: Creator
      AI Agent truy xuất Pattern phù hợp: 5: Hệ thống
      Nhận Kịch bản, Storyboard & AI Prompts: 5: Creator
```

### FR-1: Quản Trị & Nạp Kho Video (`/api/v1/ingest`)
* Tiếp nhận file JSON từ hệ thống lưu trữ cục bộ hoặc payload.
* Tự động làm sạch văn bản, trích xuất 3-5 giây đầu làm ứng viên Hook.
* Sinh vector embedding thông qua Self-hosted Embedding model.
* Lưu trữ vào ChromaDB kèm metadata đầy đủ để truy vấn ngược lại link MinIO.

### FR-2: Tìm Kiếm Pattern Viral (`/api/v1/search-patterns`)
* Cho phép người dùng tìm kiếm theo ngữ nghĩa (semantic search) các video có cùng chủ đề hoặc phong cách.
* Trả về danh sách Top-K video tương đồng kèm điểm số tương đồng (similarity score), hook mẫu và link video MinIO để người dùng xem tham khảo.

### FR-3: Sinh Kịch Bản & Storyboard Tự Động (`/api/v1/generate-script`)
* **Đầu vào (Request):**
  * `topic`: Chủ đề video cần làm.
  * `target_audience`: Đối tượng người xem mục tiêu.
  * `duration_seconds`: Thời lượng video (ví dụ 30, 45, 60 giây).
  * `hook_style`: (Tùy chọn) Phong cách hook mong muốn (Shocking, Contrarian, Question, Story...).
  * `platform`: Nền tảng đích (TikTok, YouTube Shorts, Instagram Reels).
* **Đầu ra (Response):**
  * `ViralScript` hoàn chỉnh bao gồm Hook, giải thích tâm lý giữ chân (retention rationale), Storyboard từng giây kèm Visual & Audio Prompts, Call To Action, và các nguồn video tham khảo từ kho MinIO.

---

## 5. Yêu Cầu Phi Chức Năng (Non-Functional Requirements)

1. **Tuân thủ Clean Architecture:** Core code không có bất kỳ phụ thuộc nào vào FastAPI, ChromaDB hay HTTP client. Đảm bảo 100% testable độc lập.
2. **Khả năng thay thế mô hình:** LLM Adapter và Embedding Adapter tuân thủ interface chuẩn (`ILLMPort`, `IEmbeddingPort`), cho phép dễ dàng đổi endpoint self-hosted mà không ảnh hưởng bất kỳ dòng code nghiệp vụ nào.
3. **Hiệu năng:** Thời gian truy vấn RAG dưới 100ms; thời gian sinh kịch bản phụ thuộc vào throughput của self-hosted LLM nhưng API hỗ trợ timeout và xử lý bất đồng bộ (asyncio).
