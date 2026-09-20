FROM pytorch/pytorch:2.2.0-cuda12.1-cudnn8-runtime

WORKDIR /app

# Cài đặt ffmpeg & git (cần cho WhisperX / Pyannote)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Cài đặt dependencies
COPY services/stt_service/requirements.txt .
RUN pip install --no-cache-dir bentoml
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code (giữ cấu trúc package để import services.stt_service không bị lỗi)
COPY services/stt_service /app/services/stt_service

ENV PYTHONPATH=/app
ENV PORT=3000

EXPOSE 3000

CMD ["bentoml", "serve", "services.stt_service.service:WhisperXService", "--host", "0.0.0.0", "--port", "3000"]
