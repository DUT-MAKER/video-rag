# Project Instructions & Coding Rules

This repository enforces strict technical and architectural rules for all AI agents and contributors.
All agents operating in this workspace must automatically adhere to these guidelines on every task.

---

## 1. Language & Clean Code Standards

- **100% English Codebase:**
  - ALL code, inline comments, docstrings, exception messages, API response messages, Pydantic field descriptions, and variable names MUST be in English.
  - NEVER mix Vietnamese and English in code or docstrings ("nửa Anh nửa Việt").
- **Data Contract Compatibility:**
  - Standard JSON keys are English snake_case: `caption`, `hashtag`, `transcript`, `image_url`, `summary`, `video_url`.
  - Readers in `src/infra/data_readers/` must support standard English keys while preserving backwards-compatibility aliases for legacy Vietnamese keys (`trancsript`, `hastag`, `hình ảnh`, `nội dung tóm tắt`, `url_video`).

---

## 2. Architecture: Clean Architecture (Hexagonal / Ports & Adapters)

- **Strict Dependency Rule:**
  - `src/core/` (Domain Entities, Value Objects, Ports, Use Cases) MUST be 100% Pure Python.
  - `src/core/` MUST NEVER import any external framework or infrastructure packages (e.g., `fastapi`, `chromadb`, `httpx`, `requests`), nor any modules from `src/infra` or `src/interfaces`.
  - External capabilities are abstracted as Python Protocols in `src/core/ports/`.
  - Concrete adapters in `src/infra/` implement the ports.
  - Dependency Injection is wired exclusively in `src/interfaces/api/dependencies.py`.

---

## 3. Python PEP 8 & Typing Standards (docs/python-coding-standards.md)

- **Indentation & Formatting:**
  - 4 spaces per indentation level. NEVER use tabs.
  - Line length limit: **120 characters** maximum for code, comments, and docstrings.
  - Blank lines: Exactly **2 blank lines** before top-level classes and functions; exactly **1 blank line** before class methods.
- **Top-Level Imports Only:**
  - ALL imports MUST be at the top level of the file.
  - NEVER place `import` statements inside functions, methods, or conditional blocks (e.g. `if __name__ == "__main__":`).
  - Group imports in 3 distinct blocks separated by a blank line:
    1. Standard library imports
    2. Third-party library imports
    3. Local application imports (`from src...`)
  - Use absolute imports (`from src...`) instead of relative imports.
  - NEVER use wildcard imports (`from ... import *`).
- **Enums & Types:**
  - Always use `enum.StrEnum` (Python 3.12+) for categorical options and choices instead of `(str, Enum)`.
  - 100% type annotations required for all parameters and return types across all public functions, methods, and classes.
- **Comparisons & Conditionals:**
  - Compare singletons like `None` using `is` / `is not`, never `==`.
  - Check empty sequences with truthiness (`if not sequence:`), NEVER with `if len(sequence) == 0:`.
- **Docstrings (PEP 257):**
  - Provide Google-style triple-quoted docstrings in English for all modules, classes, and public functions.
- **Exceptions:**
  - In `except` clauses, chain re-raised exceptions using `raise ... from err`.

---

## 4. Pre-Commit Verification Commands

Before concluding any implementation or refactoring task, ALWAYS run and verify:

1. **Linter & Formatter:**
   ```bash
   .venv/bin/ruff check src tests main.py
   .venv/bin/ruff format --check src tests main.py
   ```
2. **Static Type Checker:**
   ```bash
   .venv/bin/mypy src --follow-imports=skip
   ```
3. **Automated Test Suite:**
   ```bash
   .venv/bin/pytest -v tests/
   ```
All checks must pass with 0 errors and 100% test pass rate.
