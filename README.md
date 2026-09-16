# RAG Viral Video — Nền Tảng Tự Động Hóa Kịch Bản Video Viral Cho Sáng Tạo Nội Dung

> **Hệ thống AI Agent tự động phân tích pattern từ kho video triệu view (MinIO) và sinh kịch bản video ngắn (TikTok / Shorts / Reels) chuẩn hóa từng giây: Hook 3s giữ chân người xem, Storyboard trực quan và Prompts cho AI tạo ảnh/video.**

🏛️ **Kiến trúc:** Thiết kế theo chuẩn **Modular Clean Architecture & Domain-Driven Design (DDD)** kết hợp **Dishka IoC Container** — Phân tách tuyệt đối giữa **Cross-cutting Core** (`core/`), **Domain Modules** (`module/auth`, `module/upload`, `module/video_rag`), **Presentation API** (`backend/`), và **Web Client** (`web/`).

---

## 📌 1. Bối Cảnh & Mục Tiêu

Hiện nay, việc sáng tạo video ngắn (Shorts, Reels, TikTok) phụ thuộc lớn vào **tỷ lệ giữ chân người xem trong 3-5 giây đầu (Retention Hook)** và nhịp điệu kịch bản. Các LLM thông thường thường viết kịch bản chung chung, không có "chất viral".

**RAG Viral Video** giải quyết vấn đề này bằng cách:
1. **Kết nối kho dữ liệu video viral sẵn có:** Nạp các video đã thành công (kèm transcript, caption, hashtag, tóm tắt và link video gốc tại MinIO).
2. **Vector hóa & Truy xuất Pattern tương đồng (RAG):** Tìm kiếm các công thức hook, nhịp điệu và câu chuyện phù hợp với chủ đề người dùng yêu cầu.
3. **Sinh kịch bản hoàn chỉnh (1-Click):**
   * **Hook chiến lược (3-5s):** Phân tích tâm lý giữ chân (retention rationale).
   * **Storyboard chi tiết từng giây:** Lời thoại voiceover, mô tả visual B-roll và hiệu ứng âm thanh SFX.
   * **AI Prompts:** Sẵn sàng sao chép sang Midjourney / Flux (tạo ảnh) hoặc Veo 3.1 / Runway Gen-3 / Kling (tạo video).
4. **Hội thoại tương tác (Conversational RAG):** Trò chuyện tinh chỉnh kịch bản theo ngữ cảnh lịch sử.

---

## 🏛️ 2. Sơ Đồ Kiến Trúc Hệ Thống (Modular Clean Architecture)

```mermaid
flowchart TD
    subgraph Clients["1. Giao Diện Người Dùng (Client Layer)"]
        WEB["Next.js 15 Web App (web/)"]
        STATIC_UI["Chat UI Static Client (backend/static)"]
    end

    subgraph BackendPresentation["2. Tầng Presentation & Delivery (backend/)"]
        FASTAPI["FastAPI Web API (/api/v1)"]
        DISHKA["Dishka IoC Container (backend/di/)<br/>Scope.APP | Scope.REQUEST"]
    end

    subgraph Modules["3. Bounded Context Modules (module/)"]
        subgraph AuthModule["module/auth"]
            AUTH_UC["Use Cases: Login, Register, Profile"]
            AUTH_PORTS["Port: IUserRepository"]
            AUTH_DOMAIN["Domain: User Entity"]
        end

        subgraph UploadModule["module/upload"]
            UPLOAD_UC["Use Cases: UploadFile, PresignUpload"]
            UPLOAD_PORTS["Port: IS3Client"]
            UPLOAD_DOMAIN["Domain: Upload Entities"]
        end

        subgraph VideoRagModule["module/video_rag"]
            RAG_UC["Use Cases: Ingest, Search, Generate, Chat"]
            RAG_PORTS["Ports: ILLM, IEmbedding, IVectorStore, ISessionStore"]
            RAG_DOMAIN["Domain: RawVideoRecord, ViralScript, Hook, Storyboard"]
        end
    end

    subgraph SharedCore["4. Shared Core Layer (core/)"]
        CORE_UTILS["Config (pydantic-settings), JWT, Security (bcrypt),<br/>Datetime (now_utc), Standard Exceptions"]
    end

    subgraph InfraStorage["5. Hạ Tầng Lưu Trữ & AI Engines"]
        POSTGRES[("PostgreSQL Database<br/>(Alembic Migrations)")]
        MINIO[("MinIO S3 Storage<br/>(Video & Image Assets)")]
        PGVECTOR[("pgvector Extension<br/>(HNSW Vector Store)")]
        LLM["Self-hosted LLM, DUT AI Embedding & Rerank"]
    end

    Clients --> FASTAPI
    FASTAPI --> DISHKA
    DISHKA --> AUTH_UC
    DISHKA --> UPLOAD_UC
    DISHKA --> RAG_UC

    AUTH_UC --> AUTH_DOMAIN
    AUTH_UC --> AUTH_PORTS
    UPLOAD_UC --> UPLOAD_DOMAIN
    UPLOAD_UC --> UPLOAD_PORTS
    RAG_UC --> RAG_DOMAIN
    RAG_UC --> RAG_PORTS

    Modules -.-> SharedCore

    AUTH_PORTS -.-> POSTGRES
    UPLOAD_PORTS -.-> MINIO
    RAG_PORTS -.-> PGVECTOR
    RAG_PORTS -.-> LLM

    classDef client fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px;
    classDef pres fill:#e8eaf6,stroke:#3f51b5,stroke-width:2px;
    classDef domain fill:#e1f5fe,stroke:#0288d1,stroke-width:2px;
    classDef ports fill:#e0f2f1,stroke:#00796b,stroke-width:2px;
    classDef uc fill:#fff8e1,stroke:#fbc02d,stroke-width:2px;
    classDef core fill:#ede7f6,stroke:#512da8,stroke-width:2px;
    classDef storage fill:#fff3e0,stroke:#f57c00,stroke-width:2px;

    class WEB,STATIC_UI client;
    class FASTAPI,DISHKA pres;
    class AUTH_DOMAIN,UPLOAD_DOMAIN,RAG_DOMAIN domain;
    class AUTH_PORTS,UPLOAD_PORTS,RAG_PORTS ports;
    class AUTH_UC,UPLOAD_UC,RAG_UC uc;
    class CORE_UTILS core;
    class POSTGRES,MINIO,PGVECTOR,LLM storage;
```

---

## 📚 3. Tài Liệu Thiết Kế Kỹ Thuật

Tài liệu chi tiết được tổ chức trong thư mục `docs/`:

| Tài Liệu | Mô Tả Chi Tiết |
|---|---|
| [System Architecture](docs/system-architecture.md) | Kiến trúc hệ thống, quy tắc phân tầng, sơ đồ Sequence nạp dữ liệu, sinh kịch bản & xác thực. |
| [Clean Architecture Guidelines](docs/clean-architecture.md) | Quy chuẩn phân tách Core vs Infra, Dependency Injection với Dishka, tiêu chuẩn Unit/Integration test. |
| [Product Requirements (PRD)](docs/project-overview-prd.md) | Yêu cầu sản phẩm, hành trình người dùng, dữ liệu kho JSON, chức năng và phi chức năng. |
| [Python Coding Standards](docs/python-coding-standards.md) | Quy chuẩn lập trình Python, đặt tên, type hints, docstrings và công cụ kiểm thử ruff/mypy. |
| [Backend Guide](backend/README.md) | Hướng dẫn phát triển, cấu hình Dishka, chạy API và testing tầng Presentation. |

---

## 🚀 4. Cấu Trúc Dữ Liệu Kho Video (Data Contract)

Hệ thống nạp trực tiếp file JSON từ kho dữ liệu với cấu trúc chuẩn thống nhất:

```json
[
  {
    "caption": "Bí quyết tạo thói quen kỷ luật trong 21 ngày với quy tắc 2 phút",
    "hashtag": "#phattrienvanthan #kỷluat #viral #thoi_quen",
    "transcript": "90% mọi người thất bại khi xây dựng thói quen mới vì họ mắc lỗi này...",
    "image_url": "https://minio.example.com/thumbnails/video_01.jpg",
    "summary": "Video phân tích lý do bỏ cuộc sớm và giải pháp 2 phút xây dựng thói quen.",
    "video_url": "https://minio.example.com/videos/video_01.mp4"
  }
]
```

| Trường (Key) | Kiểu Dữ Liệu | Mô Tả Chi Tiết |
|---|---|---|
| `caption` | `string` | Tiêu đề hoặc mô tả bài đăng của video |
| `hashtag` | `string` / `list[string]` | Thẻ hashtag phân loại chủ đề và xu hướng |
| `transcript` | `string` | Toàn bộ lời thoại video (dùng để vector hóa & học nhịp kịch bản) |
| `image_url` | `string` | URL ảnh thumbnail hoặc keyframe của video |
| `summary` | `string` | Tóm tắt ý chính của video (ngữ cảnh vector search) |
| `video_url` | `string` | Đường dẫn file video gốc lưu trữ tại MinIO Storage |

---

## 🛠️ 5. Hướng Dẫn Cài Đặt & Khởi Chạy

### 1. Khởi động PostgreSQL & MinIO (Docker)
```bash
docker compose up -d
```

### 2. Cài đặt Dependencies & Môi Trường Ảo
```bash
# Sử dụng uv:
uv sync

# Hoặc pip:
pip install -e .
```

### 3. Đồng bộ Database Migrations (Alembic)
```bash
alembic upgrade head
```

### 4. Khởi chạy Backend API
```bash
uvicorn backend.main:app --reload --port 8000
# hoặc: python main.py
```
* **Swagger UI:** `http://localhost:8000/docs`
* **Chat Client UI:** `http://localhost:8000/app`

### 5. Khởi chạy Frontend Web App (Next.js 15)
```bash
cd web
pnpm install
pnpm dev
```
Giao diện frontend sẽ chạy tại: `http://localhost:3000`

### 6. Chạy Kiểm Thử Tự Động (Tests)
```bash
pytest
```
Chạy toàn bộ 32+ bài test tự động bao gồm Unit Tests (Domain, Ports, Use Cases) và Integration Tests (Auth, Upload, Dishka).
