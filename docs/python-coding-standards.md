# Python Coding Standards & Conventions (PEP 8)

Tài liệu này quy định các tiêu chuẩn lập trình Python chính thức của dự án, tuân thủ nghiêm ngặt theo [PEP 8 Style Guide for Python Code](https://peps.python.org/pep-0008/) và các yêu cầu kỹ thuật của hệ thống **English Automation**.

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
- [4. AI / PyTorch Specific Guidelines](#4-ai--pytorch-specific-guidelines)
- [5. Pre-Commit Verification & Linting Tools](#5-pre-commit-verification--linting-tools)

---

## 1. Code Layout & Formatting

### Indentation & Line Length
- **Indentation:** Use **4 spaces** per indentation level. **Never use tabs**.
- **Line Length:** Limit code lines to a maximum of **120 characters**. Limit docstrings and comments to **72 characters**.

### Blank Lines & Source Encoding
- **Source Encoding:** All Python source files MUST use **UTF-8** encoding.
- **Top-Level Definitions:** Surround top-level function and class definitions with **2 blank lines**.
- **Class Methods:** Surround method definitions inside a class with **1 blank line**.
- Use blank lines sparingly inside functions to separate logical sections.

### Top-Level Import Rules
- Place all imports at the top of the file, immediately after module docstrings and before module globals.
- Group imports in **3 distinct blocks** separated by a blank line:
  1. Standard library imports
  2. Third-party library imports
  3. Local application/library imports
- Use **absolute imports** over relative imports whenever possible.
- Avoid wildcard imports (`from module import *`).
- **Top-Level Imports Only:** All import statements MUST be placed at the top level of the file. Do **NOT** place imports inside functions, methods, or conditional blocks, and **NEVER** use `# pylint: disable=import-outside-toplevel` or inline suppression comments.

```python
"""Module docstring describing purpose of this file."""

import os
from typing import List, Optional

import numpy as np
import torch
import torch.nn as nn

from my_project.core.config import Settings
```

---

## 2. Naming Conventions

| Code Element | Format Convention | Examples |
|---|---|---|
| **Modules & Packages** | Short, lowercase, `snake_case` | `models_hub`, `data_loader`, `slide_builder` |
| **Classes** | `CapWords` (PascalCase) | `VisionTransformer`, `SlideGenerator`, `EdgeTTSAdapter` |
| **Functions & Variables** | `snake_case` | `train_epoch`, `learning_rate`, `generate_lesson` |
| **Constants** | `ALL_CAPS_WITH_UNDERSCORES` | `DEFAULT_BATCH_SIZE = 64`, `MAX_RETRY_COUNT = 3` |
| **Private Attributes** | Leading single underscore | `_private_tensor`, `_build_backbone()`, `_inject_audio()` |

---

## 3. Programming Recommendations & Annotations

### Comparisons & Conditionals
- Compare singletons like `None` using `is` or `is not`, never `==`.
  - **Correct:** `if result is None:` | **Incorrect:** `if result == None:`
- Evaluate boolean values directly:
  - **Correct:** `if is_valid:` | **Incorrect:** `if is_valid == True:`
- Check for empty sequences (lists, strings, tuples) by truthiness:
  - **Correct:** `if not sequence:` | **Incorrect:** `if len(sequence) == 0:`

### Type Hints & Annotations
All public functions and class methods MUST include full Python type annotations for all parameters and return values:

```python
def process_embeddings(
    features: torch.Tensor,
    mask: Optional[torch.Tensor] = None,
) -> torch.Tensor:
    """Processes input feature tensors."""
    ...
```

### Enum Classes for Categorical Options (`StrEnum`)
Whenever defining function parameters or configuration options that accept a finite set of categorical choices, formats, or modes (e.g., image formats, summary statistics, input modes, voice accents, CEFR levels), developers MUST define and use Python `enum.StrEnum` classes instead of raw string literals.

Function signatures MUST accept the Enum type (or `EnumClass | str`), and CLI choices MUST bind directly to `[e.value for e in EnumClass]`.

```python
from enum import StrEnum

class ImageFormat(StrEnum):
    PNG = "png"
    JPEG = "jpeg"
    TIFF = "tiff"

class AccentType(StrEnum):
    US = "en-US"
    UK = "en-GB"
    AU = "en-AU"

def convert_image(image_path: str, format_type: ImageFormat) -> str:
    """Converts image to requested format."""
    print(f"Converting to {format_type.value}")
    return format_type.value
```

### Docstrings (PEP 257)
Provide PEP 257 compliant triple-quoted docstrings for all public modules, functions, classes, and methods using Google docstring style:

```python
def train_epoch(
    model: nn.Module,
    dataloader: torch.utils.data.DataLoader,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
) -> float:
    """Runs a single training epoch over the given dataset.

    Args:
        model: PyTorch model instance to be trained.
        dataloader: DataLoader yielding input features and target labels.
        optimizer: PyTorch optimizer instance (e.g. AdamW).
        device: Target execution device (cuda or cpu).

    Returns:
        float: Average training loss for the epoch.
    """
```

### Import Safety & Fallback Rules
- **No Top-Level `try...except ImportError` Fallbacks:** Avoid wrapping top-level imports in `try...except ImportError` or `try...except ModuleNotFoundError` blocks that set imported symbols to `None` or swallow import failures silently.
- All project dependencies MUST be explicitly declared in `pyproject.toml` or `requirements.txt` and imported directly at top level.

---

## 4. AI / PyTorch Specific Guidelines

- **Device Passing:** Always allow explicit device passing (`torch.device('cuda' if torch.cuda.is_available() else 'cpu')`).
- **Inference Mode:** Use `@torch.inference_mode()` or `with torch.no_grad():` during evaluation.
- **Reproducibility:** Include seed initialization for `random`, `numpy`, and `torch`:
  ```python
  def set_seed(seed: int = 42) -> None:
      import random
      random.seed(seed)
      np.random.seed(seed)
      torch.manual_seed(seed)
      torch.cuda.manual_seed_all(seed)
  ```

---

## 5. Pre-Commit Verification & Linting Tools

Dự án áp dụng bộ công cụ kiểm tra tự động trước khi commit code:
* **Format & Linting:** `ruff format .` và `ruff check .`
* **Static Type Checking:** `mypy src --strict`
* **Test Runner:** `pytest -v tests/`
