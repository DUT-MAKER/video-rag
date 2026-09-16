# Backend — Delivery & Presentation Layer (FastAPI + Dishka DI)

Thư mục `backend/` đóng vai trò là **Tầng Delivery & Presentation** cùng hệ thống **Dependency Injection (Dishka Container)**, kết nối các Bounded Contexts trong `module/` và tiện ích nền tảng trong `core/` thành một ứng dụng web API hoàn chỉnh.

---

## 🏛️ Cấu Trúc Thư Mục

```text
backend/
├── di/                                 # [DISHKA DEPENDENCY INJECTION]
│   ├── providers.py                    # Providers cấu hình Scope.APP & Scope.REQUEST
│   │                                   # (DatabaseSessionProvider, AuthModuleProvider,
│   │                                   #  UploadModuleProvider, VideoRagModuleProvider)
│   └── setup.py                        # Hàm khởi tạo container (make_async_container)
│
├── presentation/                       # [PRESENTATION LAYER]
│   ├── api/v1/                         # Các endpoints FastAPI
│   │   ├── auth.py                     # POST /api/v1/auth/login, POST /api/v1/auth/register
│   │   ├── me.py                       # GET /api/v1/me, PUT /api/v1/me
│   │   ├── uploads.py                  # POST /api/v1/uploads/direct, POST /api/v1/uploads/presign
│   │   ├── video_rag.py                # POST /api/v1/video-rag/generate-script, ingest, search
│   │   ├── chat.py                     # POST /api/v1/chat/message, /history, /clear
│   │   ├── health.py                   # GET /api/v1/health
│   │   └── router.py                   # Router tổng hợp gắn tiền tố /api/v1
│   ├── exception_handlers.py           # Global Exception Handlers (AppException, ValidationError)
│   └── schemas/                        # Presentation DTOs & StandardResponse[T]
│
├── static/                             # Web Chatbot Client UI (HTML, CSS, JS)
│   ├── index.html                      # Giao diện chat RAG tương tác trực tiếp
│   ├── app.js                          # Xử lý gọi API /chat và /video-rag
│   └── style.css                       # Giao diện tối ưu trải nghiệm người dùng
│
├── tests/                              # Integration tests cho tầng presentation (Auth & Uploads)
├── main.py                             # ASGI application entrypoint & Dishka lifespan setup
└── README.md                           # Tài liệu hướng dẫn này
```

---

## 🚀 Hướng Dẫn Cài Đặt & Chạy Ứng Dụng

### 1. Khởi động Cơ sở dữ liệu & Storage (Docker Compose)
Tại thư mục gốc dự án, khởi chạy PostgreSQL và MinIO:
```bash
docker compose up -d
```
* **PostgreSQL:** `100.84.187.107:5698` (hoặc cấu hình lại trong `.env`)
* **MinIO Console:** `http://localhost:9001` (user: `miniouser`, pass: `miniopassword`)
* **MinIO S3 API:** `http://localhost:9000`

### 2. Cài đặt Thư Viện Python
Dự án sử dụng môi trường ảo Python 3.11+:
```bash
# Sử dụng uv:
uv sync

# Hoặc pip:
pip install -e .
```

### 3. Đồng bộ Database Migrations (Alembic)
Áp dụng migrations mới nhất cho PostgreSQL:
```bash
alembic upgrade head
```

Tạo migration mới khi chỉnh sửa SQLAlchemy model trong `module/auth/infra/persistence/models/`:
```bash
alembic revision --autogenerate -m "Mô tả thay đổi"
```

### 4. Khởi Chạy Backend Server
Khởi chạy ứng dụng với Uvicorn:
```bash
uvicorn backend.main:app --reload --port 8000
```
Hoặc chạy trực tiếp file entrypoint:
```bash
python main.py
```

### 5. Truy Cập Giao Diện
* **Swagger API Documentation:** `http://localhost:8000/docs`
* **Interactive Chat Client UI:** `http://localhost:8000/app` hoặc `http://localhost:8000/chat`
* **Healthcheck:** `http://localhost:8000/api/v1/health`

---

## 🧪 Hướng Dẫn Chạy Kiểm Thử (Testing)

Bộ kiểm thử tự động bao gồm cả Unit tests (Core/Domain) và Integration tests (Backend API):
```bash
pytest
```
Chạy chi tiết với log:
```bash
pytest -v -s
```
Chạy riêng integration tests của Backend:
```bash
pytest backend/tests/ -v
```
