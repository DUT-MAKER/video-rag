# System Architecture & Technical Specifications (Clean Architecture)

Tài liệu này đặc tả kiến trúc kỹ thuật của hệ thống **RAG Viral Video** tuân thủ triệt để nguyên lý **Clean Architecture (Hexagonal / Ports & Adapters)**.

Quy tắc cốt lõi: **Core Code và Infra Code hoàn toàn độc lập và tách biệt.**

---

## 1. Nguyên Tắc Thiết Kế Clean Architecture (The Dependency Rule)

Tất cả các thành phần trong hệ thống tuân thủ nghiêm ngặt **Quy tắc Phụ thuộc (Dependency Rule)**:
* Các tầng bên trong (Core) **tuyệt đối không phụ thuộc** và **không được phép import** bất kỳ thành phần nào của tầng bên ngoài (Infra, Frameworks, Web API).
* Mọi giao tiếp từ Core ra bên ngoài đều thông qua các **Giao diện trừu tượng (Ports / Protocols)**.
* Tầng Hạ tầng (Infra) đóng vai trò là các **Adapters** hiện thực hóa (implement) các Ports đó.
* Tầng Interfaces (FastAPI) đóng vai trò điều phối HTTP request, validate DTOs và tiêm phụ thuộc (Dependency Injection).

```mermaid
flowchart TD
    subgraph OuterLayer["1. Interfaces & Frameworks Layer (Giao diện)"]
        FASTAPI["FastAPI Web API (/api/v1)"]
        CLI["CLI Commands / Admin Tool"]
        FASTAPI_DI["Dependency Injection Container"]
    end

    subgraph InfraLayer["2. Infrastructure Layer (Adapters Hạ Tầng)"]
        LLM_ADAPTER["Self-hosted LLM Adapter<br/>(OpenAI-Compatible Chat API)"]
        EMBED_ADAPTER["Self-hosted Embedding Adapter<br/>(Custom / OpenAI Embed API)"]
        CHROMA_ADAPTER["Vector Store Adapter<br/>(ChromaDB Persistent)"]
        JSON_ADAPTER["Data Reader Adapter<br/>(JSON File & MinIO Url Resolver)"]
    end

    subgraph CoreAppLayer["3. Core Layer - Use Cases & Ports (Nghiệp Vụ Ứng Dụng)"]
        USE_CASES["Use Cases (Application Services)<br/>• GenerateViralScriptUseCase<br/>• IngestVideoDataUseCase<br/>• SearchViralPatternsUseCase"]
        
        subgraph Ports["Ports (Abstract Interfaces / Protocols)"]
            P_LLM["ILLMPort"]
            P_EMBED["IEmbeddingPort"]
            P_VECTOR["IVectorStorePort"]
            P_READER["IDataReaderPort"]
        end
    end

    subgraph CoreDomainLayer["4. Core Layer - Domain Entities (Thực Thể Cốt Lõi)"]
        ENTITIES["Domain Entities & Value Objects<br/>• RawVideoRecord, ViralScript, Storyboard<br/>• Hook, Scene, VisualAction, AIPrompts<br/>• HookType, PlatformTarget, VideoDuration"]
    end

    FASTAPI --> FASTAPI_DI
    FASTAPI_DI --> USE_CASES
    CLI --> USE_CASES

    USE_CASES --> ENTITIES
    USE_CASES --> Ports

    LLM_ADAPTER -.->|Implements| P_LLM
    EMBED_ADAPTER -.->|Implements| P_EMBED
    CHROMA_ADAPTER -.->|Implements| P_VECTOR
    JSON_ADAPTER -.->|Implements| P_READER

    classDef core fill:#e1f5fe,stroke:#0288d1,stroke-width:2px;
    classDef infra fill:#fff3e0,stroke:#f57c00,stroke-width:2px;
    classDef outer fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px;

    class ENTITIES,USE_CASES,Ports,P_LLM,P_EMBED,P_VECTOR,P_READER core;
    class LLM_ADAPTER,EMBED_ADAPTER,CHROMA_ADAPTER,JSON_ADAPTER infra;
    class FASTAPI,CLI,FASTAPI_DI outer;
```

---

## 2. Phân Tách Chi Tiết: Core Code vs Infra Code

### 2.1. Tầng Lõi Nghiệp Vụ: Core Layer (`src/core/`)
* **Đặc tính:** Thuần túy Python chuẩn (Standard Library + Pydantic/Dataclasses). **Hoàn toàn không import bất kỳ thư viện hạ tầng thứ 3 nào (Không `fastapi`, không `chromadb`, không `httpx`).**
* **Bao gồm:**
  1. **Domain (`src/core/domain/`):**
     * `RawVideoRecord`: Thực thể đại diện cho 1 video trong kho dữ liệu.
     * `ViralScript`: Toàn bộ kịch bản hoàn chỉnh (Hook, Narration, Storyboard, CTA, References).
     * `Hook`: Phân loại hook (Shocking Fact, Contrarian, Problem-Agitate, Curiosity Gap), lời thoại mở đầu 3-5s, mô tả visual 3s đầu và phân tích tâm lý giữ chân (retention rationale).
     * `Storyboard` & `Scene`: Cấu trúc phân cảnh chi tiết theo giây (00:00 - 00:05), lời thoại, visual cues, prompt cho AI tạo ảnh (Midjourney/Flux) và prompt tạo video (Veo 3.1/Runway/Kling).
     * `Value Objects`: `HookType`, `PlatformTarget` (TikTok, Reels, Shorts), `VideoDuration`.
  2. **Ports (`src/core/ports/`):**
     * `ILLMPort`: Giao thức gửi system prompt, user prompt, và context sang mô hình ngôn ngữ lớn để nhận về kịch bản có cấu trúc.
     * `IEmbeddingPort`: Giao thức sinh vector float list từ văn bản (transcript, caption, tóm tắt).
     * `IVectorStorePort`: Giao thức lưu trữ và truy vấn vector tương đồng (k-Nearest Neighbors).
     * `IDataReaderPort`: Giao thức nạp và parse kho video JSON.
  3. **Use Cases (`src/core/use_cases/`):**
     * `GenerateViralScriptUseCase`: Nhận chủ đề & yêu cầu -> Vectorize query -> Truy xuất Top-K video viral tương đồng từ Vector Store -> Ghép bối cảnh vào Viral Master Prompt -> Gọi LLM -> Phân tích và sinh `ViralScript`.
     * `IngestVideoDataUseCase`: Đọc file kho JSON -> Làm sạch và chunking nội dung (Hook, Body, Summary) -> Gọi Embedding Port -> Đẩy vào Vector Store kèm metadata (MinIO URL, Hashtags, Hình ảnh).
     * `SearchViralPatternsUseCase`: Tra cứu nhanh các video tương đồng và các công thức hook đã thành công trong kho.

### 2.2. Tầng Hạ Tầng: Infrastructure Layer (`src/infra/`)
* **Đặc tính:** Hiện thực hóa các Ports thông qua các công nghệ và thư viện cụ thể.
* **Bao gồm:**
  * `infra/llm/`: `SelfHostedLLMAdapter` — Kết nối API LLM self-hosted qua chuẩn OpenAI Chat Completions (`/v1/chat/completions`), hỗ trợ format JSON Mode, xử lý retry và timeout.
  * `infra/embeddings/`: `SelfHostedEmbeddingAdapter` — Kết nối API mô hình Embedding riêng của bạn (chuẩn `/v1/embeddings` hoặc custom POST endpoint).
  * `infra/vector_store/`: `ChromaVectorStoreAdapter` — Triển khai lưu trữ vector với ChromaDB chế độ persistent on-disk, quản lý collections, indexing cosine similarity.
  * `infra/data_readers/`: `JsonDataReaderAdapter` — Đọc file JSON từ kho dữ liệu, linh hoạt ánh xạ các trường tiếng Việt (`caption`, `hastag`, `trancsript`, `hình ảnh`, `nội dung tóm tắt`, `url_video`).
  * `infra/config/`: `Settings` — Quản lý biến môi trường bằng `pydantic-settings` (URL, API keys, paths).

### 2.3. Tầng Giao Diện: Interfaces Layer (`src/interfaces/`)
* **Đặc tính:** Giao diện tiếp nhận tương tác từ bên ngoài.
* **Bao gồm:**
  * `interfaces/api/v1/routes/`: Router FastAPI tiếp nhận các HTTP requests.
  * `interfaces/schemas/`: Pydantic Request/Response DTOs cho API.
  * `interfaces/api/dependencies.py`: Container khởi tạo các Adapters và tiêm vào Use Cases (Inversion of Control).

---

## 3. Quy Trình Hoạt Động (Mermaid Sequence Diagrams)

### 3.1. Luồng Nạp Dữ Liệu Kho Video (Data Ingestion Flow)

```mermaid
sequenceDiagram
    autonumber
    actor Admin as "User / Admin"
    participant API as "FastAPI Ingestion Endpoint"
    participant UC as "IngestVideoDataUseCase (Core)"
    participant Reader as "JsonDataReaderAdapter (Infra)"
    participant Embed as "SelfHostedEmbeddingAdapter (Infra)"
    participant Chroma as "ChromaVectorStoreAdapter (Infra)"

    Admin->>API: POST /api/v1/ingest (file_path / json_data)
    API->>UC: execute(file_path)
    UC->>Reader: read_records(file_path)
    Reader-->>UC: list[RawVideoRecord]
    
    loop Từng video record
        UC->>Embed: embed_text(transcript + summary + hashtags)
        Embed-->>UC: vector (list[float])
        UC->>Chroma: upsert_vector(id, vector, metadata={minio_url, caption, hook})
    end
    
    Chroma-->>UC: IngestSummary(total_indexed, errors)
    UC-->>API: IngestResultDTO
    API-->>Admin: 200 OK (Thành công nạp kho dữ liệu)
```

### 3.2. Luồng Sinh Kịch Bản Viral (RAG Generation Flow)

```mermaid
sequenceDiagram
    autonumber
    actor Creator as "Content Creator / Client"
    participant API as "FastAPI Generation Endpoint"
    participant UC as "GenerateViralScriptUseCase (Core)"
    participant Embed as "SelfHostedEmbeddingAdapter (Infra)"
    participant Chroma as "ChromaVectorStoreAdapter (Infra)"
    participant LLM as "SelfHostedLLMAdapter (Infra)"

    Creator->>API: POST /api/v1/generate-script (Topic, Duration, Target Audience, Tone)
    API->>UC: execute(request_query)
    
    Note over UC,Embed: 1. Vectorize nhu cầu người dùng
    UC->>Embed: embed_query(topic + target_audience)
    Embed-->>UC: query_vector
    
    Note over UC,Chroma: 2. RAG Retrieval từ kho video MinIO
    UC->>Chroma: search_similar(query_vector, top_k=5)
    Chroma-->>UC: list[SimilarVideoContext] (Transcripts, Hooks, MinIO URLs)
    
    Note over UC: 3. Augment Prompt với Viral Framework & Context
    UC->>UC: build_viral_prompt(topic, retrieved_contexts)
    
    Note over UC,LLM: 4. Gọi LLM Self-hosted sinh kịch bản chi tiết
    UC->>LLM: generate_completion(prompt, schema=ViralScript)
    LLM-->>UC: raw_json_response
    
    Note over UC: 5. Parse & Validate thành Domain Entities
    UC->>UC: parse_and_validate(raw_json_response)
    UC-->>API: ViralScript Entity
    API-->>Creator: 200 OK (Hook 3s, Storyboard từng giây, AI Prompts)
```

---

## 4. Thiết Kế Chi Tiết Domain Entities & Cấu Trúc Kịch Bản

```mermaid
classDiagram
    class RawVideoRecord {
        +string caption
        +string hashtag
        +string transcript
        +string image_url
        +string summary
        +string video_url
        +extract_hook() string
    }

    class ViralScript {
        +string title
        +string target_niche
        +int target_duration_seconds
        +Hook hook
        +list~Scene~ scenes
        +CallToAction call_to_action
        +list~ReferencedPattern~ references
    }

    class Hook {
        +HookType hook_type
        +string script
        +string visual_action
        +string retention_rationale
        +int duration_seconds
    }

    class Scene {
        +int scene_number
        +string time_range
        +string narration
        +string visual_action
        +string image_prompt
        +string video_prompt
        +string audio_sfx_cue
    }

    class CallToAction {
        +string script
        +string visual_cue
    }

    class ReferencedPattern {
        +string original_caption
        +string matched_hook
        +string minio_video_url
        +float similarity_score
    }

    ViralScript "1" *-- "1" Hook
    ViralScript "1" *-- "many" Scene
    ViralScript "1" *-- "1" CallToAction
    ViralScript "1" *-- "many" ReferencedPattern
```

---

## 5. Cấu Trúc Thư Mục Dự Án (Folder Tree)

```
rag-viral-video/
├── docs/                                 # Tài liệu kỹ thuật & kiến trúc
│   ├── system-architecture.md            # Tài liệu này
│   ├── project-overview-prd.md           # Đặc tả yêu cầu sản phẩm
│   └── clean-architecture.md             # Quy tắc Clean Architecture
├── .agents/skills/                       # 61 kỹ năng hỗ trợ phát triển
├── src/
│   ├── core/                             # TẦNG CORE (Zero external infra dependencies)
│   │   ├── domain/
│   │   │   ├── entities/
│   │   │   │   ├── video_record.py       # RawVideoRecord
│   │   │   │   ├── viral_script.py       # ViralScript, Hook, Scene, CallToAction
│   │   │   │   └── reference_pattern.py  # ReferencedPattern
│   │   │   ├── value_objects/
│   │   │   │   ├── hook_type.py          # Enum: Problem-Agitate, Contrarian, Curiosity...
│   │   │   │   └── platform_target.py    # Enum: TikTok, Reels, Shorts
│   │   │   └── exceptions.py             # Domain exceptions
│   │   ├── ports/
│   │   │   ├── llm_port.py               # ILLMPort
│   │   │   ├── embedding_port.py         # IEmbeddingPort
│   │   │   ├── vector_store_port.py      # IVectorStorePort
│   │   │   └── data_reader_port.py       # IDataReaderPort
│   │   └── use_cases/
│   │       ├── generate_viral_script.py  # GenerateViralScriptUseCase
│   │       ├── ingest_video_data.py      # IngestVideoDataUseCase
│   │       └── search_viral_patterns.py  # SearchViralPatternsUseCase
│   │
│   ├── infra/                            # TẦNG INFRA (Triển khai các Ports)
│   │   ├── config/
│   │   │   └── settings.py               # Settings (Pydantic Settings & .env)
│   │   ├── llm/
│   │   │   └── self_hosted_llm.py        # SelfHostedLLMAdapter
│   │   ├── embeddings/
│   │   │   └── self_hosted_embed.py      # SelfHostedEmbeddingAdapter
│   │   ├── vector_store/
│   │   │   └── chroma_adapter.py         # ChromaVectorStoreAdapter
│   │   └── data_readers/
│   │       └── json_reader_adapter.py    # JsonDataReaderAdapter
│   │
│   └── interfaces/                       # TẦNG GIAO DIỆN (FastAPI)
│       └── api/
│           ├── v1/
│           │   ├── routes/
│           │   │   ├── generation.py     # POST /generate-script
│           │   │   ├── ingestion.py      # POST /ingest
│           │   │   ├── search.py         # POST /search-patterns
│           │   └── router.py             # Tổng hợp router v1
│           ├── schemas/                  # DTOs cho API
│           │   ├── request_dtos.py
│           │   └── response_dtos.py
│           └── dependencies.py           # DI Container
│
├── data/
│   ├── samples/                          # Sample JSON kho video
│   └── storage/                          # Local directory cho ChromaDB persistent
├── tests/
│   ├── unit/                             # Test Core với Mock Ports
│   └── integration/                      # Test Infra với ChromaDB & Adapters
├── .env.example
├── pyproject.toml
├── main.py                               # Entry point khởi chạy FastAPI
└── README.md
```
