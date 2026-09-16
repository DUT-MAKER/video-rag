# Python Coding Standards & Conventions (PEP 8)

Tài liệu này quy định các tiêu chuẩn lập trình Python chính thức của dự án, tuân thủ nghiêm ngặt theo [PEP 8 Style Guide for Python Code](https://peps.python.org/pep-0008/) và các quy chuẩn thiết kế của hệ thống **RAG Viral Video**.

---

## Table of Contents
- [1. Code Layout & Formatting](#1-code-layout--formatting)
  - [Indentation & Line Length](#indentation--line-length)
  - [Blank Lines & Source Encoding](#blank-lines--source-encoding)
  - [Top-Level Import Rules](#top-level-import-rules)
- [2. Naming Conventions](#2-naming-conventions)
- [3. Programming Recommendations & Annotations](#3-programming-recommendations--annotations)
  - [Comparisons & Conditionals](#comparisons--conditionals)
  - [Type Hints & Annotations](#type-hints--annotations)
  - [Enum Classes for Categorical Options (`StrEnum`)](#enum-classes-for-categorical-options-strenum)
  - [Docstrings (PEP 257)](#docstrings-pep-257)
  - [Import Safety & Fallback Rules](#import-safety--fallback-rules)
- [4. AI & Multimodal Specific Guidelines](#4-ai--multimodal-specific-guidelines)
- [5. Pre-Commit Verification & Linting Tools](#5-pre-commit-verification--linting-tools)

---

## 1. Code Layout & Formatting

### Indentation & Line Length
- **Indentation:** Sử dụng **4 spaces** cho mỗi mức thụt dòng. **Tuyệt đối không dùng tabs**.
- **Line Length:** Giới hạn dòng mã tối đa **120 characters**. Giới hạn docstrings và comments ở **80 characters**.

### Blank Lines & Source Encoding
- **Source Encoding:** Tất cả các tệp Python bắt buộc sử dụng mã hóa **UTF-8**.
- **Top-Level Definitions:** Cách 2 dòng trống (`2 blank lines`) trước và sau các class và function định nghĩa ở mức module.
- **Class Methods:** Cách 1 dòng trống (`1 blank line`) giữa các methods trong một class.
- Sử dụng dòng trống hợp lý bên trong hàm để phân tách các đoạn logic.

### Top-Level Import Rules
- Đặt tất cả imports ở đầu file, ngay sau module docstring và trước các biến toàn cục.
- Phân nhóm import thành **3 khối rõ ràng** cách nhau bởi một dòng trống:
  1. Standard library imports (`os`, `sys`, `typing`, `dataclasses`...)
  2. Third-party library imports (`pydantic`, `fastapi`, `sqlalchemy`, `dishka`, `httpx`...)
  3. Local application imports (`core.*`, `module.*`, `backend.*`)
- Sử dụng **absolute imports** thay vì relative imports để tăng tính minh bạch.
- Tuyệt đối tránh wildcard imports (`from module import *`).
- **Top-Level Imports Only:** Mọi lệnh import phải đặt ở mức cao nhất của file, không import bên trong function/method ngoại trừ trường hợp lazy import để tránh overhead nặng hoặc circular dependency không thể tránh khỏi.

```python
"""Module docstring describing purpose of this file."""

import os
from typing import Any, Optional

import httpx
from pydantic import BaseModel

from core.config import Settings
from module.video_rag.domain.entities.viral_script import ViralScript
```

---

## 2. Naming Conventions

| Thành Phần Code | Định Dạng Quy Ước | Ví Dụ Minh Họa |
|---|---|---|
| **Modules & Packages** | Chữ thường, ngắn gọn, `snake_case` | `video_rag`, `user_repo`, `datetime_utils` |
| **Classes** | `CapWords` (PascalCase) | `ViralScript`, `PostgresUserRepository`, `GenerateViralScriptUseCase` |
| **Functions & Variables** | `snake_case` | `generate_script`, `hash_password`, `user_id` |
| **Constants** | `ALL_CAPS_WITH_UNDERSCORES` | `DEFAULT_TOP_K = 5`, `JWT_ALGORITHM = "HS256"` |
| **Private Attributes/Methods** | Dấu gạch dưới đơn ở đầu | `_session`, `_build_prompt()`, `_client` |

---

## 3. Programming Recommendations & Annotations

### Comparisons & Conditionals
- So sánh các singleton như `None` bằng `is` hoặc `is not`, không dùng `==`.
  - **Đúng:** `if result is None:` | **Sai:** `if result == None:`
- Đánh giá giá trị boolean trực tiếp:
  - **Đúng:** `if is_active:` | **Sai:** `if is_active == True:`
- Kiểm tra danh sách/chuỗi rỗng qua truthiness:
  - **Đúng:** `if not records:` | **Sai:** `if len(records) == 0:`

### Type Hints & Annotations
Tất cả các public functions, methods, và use cases bắt buộc có đầy đủ Python type annotations cho cả tham số và giá trị trả về:

```python
async def search_patterns(
    self,
    query_vector: list[float],
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """Searches top-k similar video patterns from vector store."""
    ...
```

### Enum Classes for Categorical Options (`StrEnum`)
Khi định nghĩa các trường phân loại hữu hạn (như hook types, platform targets, video duration presets, roles), lập trình viên bắt buộc sử dụng Python `enum.StrEnum` thay vì string tự do.

```python
from enum import StrEnum

class PlatformTarget(StrEnum):
    TIKTOK = "tiktok"
    SHORTS = "youtube_shorts"
    REELS = "instagram_reels"
```

### Docstrings (PEP 257)
Tuân thủ Google Docstrings style cho các modules, classes và public methods:

```python
async def execute(
    self, topic: str, duration: int
) -> ViralScript:
    """Executes the viral script generation use case.

    Args:
        topic: The topic or niche for the video.
        duration: Desired duration in seconds.

    Returns:
        ViralScript: The fully synthesized viral script entity.
    """
```

---

## 4. AI & Multimodal Specific Guidelines

- **Asynchronous Execution:** Mọi tương tác gọi model LLM, embedding hay storage I/O đều phải sử dụng `async`/`await` qua `httpx.AsyncClient` hoặc async drivers.
- **Fail-Safe / Fallback:** Khi gọi API LLM ngoài hoặc self-hosted, luôn cấu hình `timeout` hợp lý (ví dụ: 60-120s) và cơ chế retry có giới hạn (exponential backoff).
- **Prompt Isolation:** Các template prompt phức tạp nên được cô lập và tổ chức trong các hàm helper chuyên biệt hoặc file template riêng, tránh hardcode chuỗi prompt khổng lồ trực tiếp trong Use Case logic.

---

## 5. Pre-Commit Verification & Linting Tools

Dự án áp dụng bộ công cụ kiểm tra tự động trước khi commit code:
* **Format & Linting:** `ruff format .` và `ruff check .`
* **Static Type Checking:** `mypy module core backend --strict`
* **Test Suite:** `pytest` (chạy 100% tests cho cả `tests/` và `backend/tests/`)
