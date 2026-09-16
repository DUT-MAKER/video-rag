# Video Crawler

The crawler discovers source video links and metadata for Facebook, TikTok, and YouTube. It does not download media or create transcripts. RAG can use `canonical_url` from `GET /api/v1/crawler/videos` as its input.

## Automatic schedule

Edit [`topics.json`](topics.json) to change the keywords. Workers read it again on every polling cycle. Times use `Asia/Ho_Chi_Minh`: `22` means 22:00 and `0` means 00:00 (the user's 24:00). The default four slots are 22:00, 00:00, 02:00, and 04:00 daily. A slot is enqueued during its first 30 minutes; if all workers are down for the entire window, that slot is skipped. The three platforms rotate through keywords at different offsets. Each platform attempts to save up to 10 **new** links per slot; fewer may be saved when search results are exhausted or already known.

`schedule_key` is unique in PostgreSQL, so restarting or scaling a worker cannot enqueue the same platform/slot twice. Video identity and canonical URL are also unique; duplicate videos are not updated or saved again. Transient errors retry up to `max_attempts` with exponential delays. Login walls, challenges, access denial, and rate limits stop the current slot. The next slot can run normally after the underlying issue is resolved.

## Run

```powershell
uv run alembic upgrade head
docker compose build crawler-worker-facebook crawler-worker-tiktok crawler-worker-youtube
docker compose up -d db crawler-worker-facebook crawler-worker-tiktok crawler-worker-youtube
docker compose logs -f crawler-worker-facebook crawler-worker-tiktok crawler-worker-youtube
```

The workers need valid Facebook and TikTok session JSON files in `video_crawler/var/secrets/sessions/`. Do not commit these files. Logs also appear in `data/crawler-work/logs/` for local workers, or the shared `crawler_work` Docker volume for containers. Failed jobs expose `error_detail`, `attempt_count`, and `rejection_reasons` through `GET /api/v1/crawler/jobs/{job_id}`.

Use `GET /api/v1/crawler/jobs` to find a scheduled job, then `GET /api/v1/crawler/videos?job_id=<job_id>&limit=100` to read its URLs from the `canonical_url` field. Both endpoints require an admin token.

For a local worker, set `CRAWLER_PLATFORM` to `facebook`, `tiktok`, or `youtube`, then run `python -m video_crawler.worker`. Start one process per platform. The API and all workers must use the same `DATABASE_URL`.

## Checks

```powershell
uv run pytest video_crawler/tests -q -m "not network"
docker compose config --services
```
