# Video Crawler

This package discovers public Facebook, TikTok, and YouTube videos. The API
creates jobs in the shared PostgreSQL database; a dedicated worker downloads
video and thumbnail artifacts, stores them in the configured S3/MinIO bucket,
and persists crawler metadata. It does not run transcription, LLM enrichment,
embedding, or RAG ingestion.

YouTube creator discovery targets the creator's Shorts feed. Direct
`/shorts/{id}`, standard watch, and `youtu.be` URLs share the same normalized
ID and database deduplication path.

## Safety

- Use only operator-authorized sessions and public content.
- Never commit `video_crawler/var/secrets` or expose storage-state values through logs/APIs.
- The worker stops on login walls, platform challenges, access denial, and rate limiting; it does not bypass them.

## Deferred operator commands

The implementation does not execute these commands. An operator may run them later after reviewing configuration:

```powershell
uv sync --python 3.12 --extra crawler --extra dev
uv run playwright install chromium
uv run alembic upgrade head
uv run python -m video_crawler.sessions login facebook
uv run python -m video_crawler.sessions login tiktok
uv run pytest tests video_crawler/tests -m "not network"
docker compose build
docker compose up -d
```

Live acceptance is opt-in with `VIDEO_CRAWLER_RUN_NETWORK=1` and is bounded to one result per platform.
