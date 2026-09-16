FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --locked --no-install-project --extra crawler

COPY core ./core
COPY module ./module
COPY backend ./backend
COPY video_crawler ./video_crawler
RUN uv sync --locked --extra crawler \
    && uv run --no-sync playwright install --with-deps chromium

CMD ["uv", "run", "--no-sync", "python", "-m", "video_crawler.worker"]
