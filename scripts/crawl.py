#!/usr/bin/env python3
"""Shortcut runner for the Multi-Platform Video Crawler CLI."""

import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from module.crawler.cli import main

if __name__ == "__main__":
    main()
