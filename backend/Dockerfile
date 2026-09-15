FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv (extremely fast Python package installer and resolver)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set Vietnam Timezone
ENV TZ=Asia/Ho_Chi_Minh
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Copy package config
COPY pyproject.toml ./

# Install project dependencies
RUN uv sync --no-cache

# Copy source code
COPY core ./core
COPY module ./module
COPY backend ./backend

# Expose API port
EXPOSE 8000

# Start FastAPI application
CMD ["uv", "run", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
