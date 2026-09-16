FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY pyproject.toml ./
RUN uv sync --no-cache --no-install-project --extra crawler \
    && uv run playwright install --with-deps chromium

COPY core ./core
COPY module ./module
COPY backend ./backend
COPY video_crawler ./video_crawler

CMD ["uv", "run", "python", "-m", "video_crawler.worker"]
