#!/usr/bin/env python3
"""End-to-End Pipeline Runner: Crawl -> Real Gemma 4 Summary -> Ingest ChromaDB (BGE-M3 1024d) -> Semantic Search."""

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from loguru import logger
from core.config import get_embedding_settings, get_vector_store_settings
from module.crawler.cli import build_pipeline, extract_id_from_url
from module.crawler.domain import PlatformType
from module.video_rag.infra.data_readers.json_reader_adapter import JsonDataReaderAdapter
from module.video_rag.infra.embeddings.self_hosted_embed import SelfHostedEmbeddingAdapter
from module.video_rag.infra.vector_store.chroma_adapter import ChromaVectorStoreAdapter
from module.video_rag.use_case.ingest_video_data import IngestVideoDataUseCase
from module.video_rag.use_case.search_viral_patterns import SearchViralPatternsUseCase
from scripts.inspect_db import inspect_db


async def run_batch_pipeline(targets: list[str], storage_type: str = "local", query: str = "tin tức sự kiện nổi bật", delay: float = 2.0):
    print(f"\n{'='*80}")
    print(f"🚀 BẮT ĐẦU CHẠY BATCH END-TO-END VIDEO RAG PIPELINE")
    print(f"🎯 Số lượng video mục tiêu : {len(targets)}")
    print(f"📦 Storage Mode            : {storage_type}")
    print(f"🔍 Test Query RAG          : '{query}'")
    print(f"{'='*80}\n")

    # -------------------------------------------------------------
    # BƯỚC 1: CRAWL DỮ LIỆU THẬT & TÓM TẮT BẰNG DUT AI GEMMA 4
    # -------------------------------------------------------------
    logger.info(">>> [BƯỚC 1/3] Khởi chạy Multi-Platform Crawler (YouTube Shorts)...")
    pipeline = build_pipeline(
        platform=PlatformType.YOUTUBE_SHORTS,
        storage_type=storage_type,
        dedup_path="data/crawled_manifest.json",
        fallback_on_ip_block=True,
    )

    crawled_records = []
    queue_dir = Path("data/ingest_queue")
    queue_dir.mkdir(parents=True, exist_ok=True)

    for idx, target in enumerate(targets):
        video_id = extract_id_from_url(target)
        logger.info(f"[{idx+1}/{len(targets)}] Đang xử lý video ID '{video_id}'...")

        # Check if already in queue or process
        json_file = queue_dir / f"{video_id}.json"
        if json_file.exists():
            logger.info(f"[{video_id}] Đã có dữ liệu trong ingest_queue. Nạp từ cache...")
            with open(json_file, "r", encoding="utf-8") as f:
                crawled_records.append(json.load(f))
        else:
            crawl_res = pipeline.process_video(video_id)
            if crawl_res:
                with open(json_file, "w", encoding="utf-8") as f:
                    json.dump(crawl_res, f, ensure_ascii=False, indent=2)
                crawled_records.append(crawl_res)
                logger.info(f"[{video_id}] Crawl & Gemma 4 summary thành công!")
            else:
                logger.warning(f"[{video_id}] Bỏ qua hoặc không thể xử lý.")

        if idx < len(targets) - 1 and delay > 0:
            time.sleep(delay)

    if not crawled_records:
        print("❌ Không có video nào được crawl thành công.")
        return

    # -------------------------------------------------------------
    # BƯỚC 2: INGEST DỮ LIỆU VÀO DATABASE (CHROMADB VỚI BGE-M3 1024D)
    # -------------------------------------------------------------
    logger.info(f">>> [BƯỚC 2/3] Nạp {len(crawled_records)} video vào Vector DB (BGE-M3 1024 dims)...")
    embed_settings = get_embedding_settings()
    vstore_settings = get_vector_store_settings()

    reader = JsonDataReaderAdapter()
    embedder = SelfHostedEmbeddingAdapter(
        api_base_url=embed_settings.api_base_url,
        api_key=embed_settings.api_key,
        model_name=embed_settings.model_name,
        dimension=embed_settings.dimension,
        fallback_mode=embed_settings.use_local_fallback,
    )
    vector_store = ChromaVectorStoreAdapter(
        persist_dir=vstore_settings.chroma_persist_dir,
        collection_name=vstore_settings.chroma_collection_name,
    )

    ingest_use_case = IngestVideoDataUseCase(
        data_reader=reader,
        embedding_port=embedder,
        vector_store_port=vector_store,
    )

    # Ingest records (pass as list of dicts)
    ingestion_res = await ingest_use_case.execute(source=crawled_records)

    logger.info(f"✅ Ingest hoàn tất:")
    print(f"  • Tổng số video đã index trong đợt: {ingestion_res.total_indexed}")
    print(f"  • Danh sách ID                    : {ingestion_res.indexed_ids}\n")

    # -------------------------------------------------------------
    # BƯỚC 3: TRUY VẤN SEMANTIC SEARCH RAG
    # -------------------------------------------------------------
    logger.info(f">>> [BƯỚC 3/3] Truy vấn thử nghiệm tìm kiếm ngữ nghĩa: '{query}'...")
    search_use_case = SearchViralPatternsUseCase(
        embedding_port=embedder,
        vector_store_port=vector_store,
    )

    search_results = await search_use_case.execute(query=query, top_k=3)

    print("\n" + "="*80)
    print(f"🔍 KẾT QUẢ TRUY VẤN TỪ DATABASE (Query: '{query}')")
    print("="*80)

    if not search_results:
        print("Không tìm thấy kết quả phù hợp.")
    else:
        for r_idx, item in enumerate(search_results):
            title = item.caption.split("\n")[0]
            print(f"Top {r_idx + 1} (Similarity Score: {item.score:.4f}):")
            print(f"  🎬 Tiêu đề: {title}")
            print(f"  🪝 Hook   : {item.hook_candidate}")
            print(f"  📝 Tóm tắt: {item.summary}")
            print(f"  🔗 URL    : {item.video_url}\n")

    # -------------------------------------------------------------
    # BƯỚC 4: XUẤT BẢNG DỮ LIỆU TỔNG HỢP (CSV & MARKDOWN)
    # -------------------------------------------------------------
    inspect_db()


def main():
    parser = argparse.ArgumentParser(description="Batch End-to-End Runner: Crawl -> Gemma 4 -> BGE-M3 1024d Ingest -> Search")
    parser.add_argument(
        "target",
        nargs="?",
        default=None,
        help="Single YouTube Shorts URL or Video ID",
    )
    parser.add_argument("--file", "-f", default="scripts/targets.txt", help="Path to text file containing list of URLs")
    parser.add_argument("--storage", choices=["local", "minio"], default="local", help="Storage mode (default: local)")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay between videos in seconds")
    parser.add_argument("--query", default="thảm họa môi trường ngao chết thanh hóa", help="Query to test retrieval")

    args = parser.parse_args()

    targets = []
    if args.target:
        targets.append(args.target)
    elif args.file and Path(args.file).exists():
        with open(args.file, "r", encoding="utf-8") as f:
            for line in f:
                c = line.strip()
                if c and not c.startswith("#"):
                    targets.append(c)

    if not targets:
        targets = ["https://www.youtube.com/shorts/RiEg8h2jquM"]

    asyncio.run(run_batch_pipeline(targets=targets, storage_type=args.storage, query=args.query, delay=args.delay))


if __name__ == "__main__":
    main()
