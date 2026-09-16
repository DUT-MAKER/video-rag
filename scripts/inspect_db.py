#!/usr/bin/env python3
"""Inspect ChromaDB Vector Store contents and export to CSV/Markdown table."""

import csv
import json
import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import chromadb
from core.config import get_vector_store_settings


def inspect_db():
    settings = get_vector_store_settings()
    persist_dir = Path(settings.chroma_persist_dir).resolve()
    collection_name = settings.chroma_collection_name

    print(f"\n{'='*80}")
    print(f"📊 CHROMADB VECTOR DATABASE INSPECTOR")
    print(f"📁 Thư mục lưu trữ : {persist_dir}")
    print(f"📦 Tên Collection  : {collection_name}")
    print(f"{'='*80}")

    if not persist_dir.exists():
        print(f"⚠️  Thư mục ChromaDB chưa tồn tại: {persist_dir}")
        print("💡 Hãy chạy 'python scripts/run_e2e.py' để cào và nạp video đầu tiên!")
        return

    client = chromadb.PersistentClient(path=str(persist_dir))
    try:
        collection = client.get_collection(name=collection_name)
    except Exception as e:
        print(f"⚠️  Chưa tìm thấy collection '{collection_name}': {e}")
        return

    count = collection.count()
    print(f"🔥 Tổng số records/videos đã nạp trong Database: {count}\n")

    if count == 0:
        print("Trống - Chưa có video nào được ingest.")
        return

    # Fetch all records
    data = collection.get(include=["metadatas", "documents"])
    ids = data.get("ids", [])
    metadatas = data.get("metadatas", [])
    documents = data.get("documents", [])

    # Print clean list to terminal
    for i, (item_id, meta, doc) in enumerate(zip(ids, metadatas, documents)):
        caption = meta.get("caption", "N/A").split("\n")[0]
        hook = meta.get("hook_candidate", "N/A")
        summary = meta.get("summary", "N/A")
        video_url = meta.get("video_url", "N/A")
        img_url = meta.get("image_url", "N/A")

        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"🎬 VIDEO #{i+1} | ID: {item_id}")
        print(f"  📌 Tiêu đề       : {caption[:90]}")
        print(f"  🪝 Hook (3-5s)   : {hook}")
        print(f"  📝 Tóm tắt AI    : {summary}")
        print(f"  📹 File Video MP4: {video_url}")
        print(f"  🖼️ File Thumbnail: {img_url}")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    # Export to CSV with mandatory 5 core fields + helpers
    export_csv_path = Path("data/database_export.csv")
    export_csv_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Load all json files in ingest_queue for deep enrichment
    queue_dir = Path("data/ingest_queue")
    queue_data = {}
    if queue_dir.exists():
        for jf in queue_dir.glob("*.json"):
            try:
                with open(jf, "r", encoding="utf-8") as f:
                    payload = json.load(f)
                    # Key by video_id or file stem
                    vid = payload.get("_enriched_metadata", {}).get("video_id") or jf.stem
                    queue_data[vid] = payload
            except Exception:
                pass

    with open(export_csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Video_ID",
            "Caption",
            "Hashtag",
            "Transcript",
            "Image_URL",
            "Summary",
            "Hook_3_to_5s",
            "Video_URL",
        ])
        for item_id, meta, _ in zip(ids, metadatas, documents):
            v_url = meta.get("video_url", "")
            stem = Path(v_url).stem if v_url else item_id
            q_item = queue_data.get(stem, {})

            # 5 mandatory fields
            caption = q_item.get("caption") or meta.get("caption", "").replace("\n", " ")
            caption = str(caption).replace("\n", " ")
            
            hashtag_val = q_item.get("hashtag") or meta.get("hashtag", "")
            if isinstance(hashtag_val, list):
                hashtag_str = " ".join([f"#{t}" if not t.startswith("#") else t for t in hashtag_val])
            else:
                hashtag_str = str(hashtag_val)

            transcript = q_item.get("transcript") or meta.get("transcript", "")
            image_url = q_item.get("image_url") or meta.get("image_url", "")
            summary = q_item.get("summary") or meta.get("summary", "")
            
            # Optional helpers
            hook = meta.get("hook_candidate") or ""
            video_url = q_item.get("video_url") or v_url

            writer.writerow([
                stem,
                caption,
                hashtag_str,
                transcript,
                image_url,
                summary,
                hook,
                video_url,
            ])

    # Export to Markdown Table
    export_md_path = Path("data/database_table.md")
    with open(export_md_path, "w", encoding="utf-8") as f:
        f.write("# BẢNG DỮ LIỆU ĐẦY ĐỦ (5 TRƯỜNG CỐT LÕI)\n\n")
        f.write(f"**Tổng số video:** {count}  \n")
        f.write(f"**Collection:** `{collection_name}`  \n\n")
        f.write("| STT | ID Video | Caption (Tiêu Đề) | Hashtag | Transcript (Lời Thoại) | Hình Ảnh (Thumbnail) | Tóm Tắt AI |\n")
        f.write("| :---: | :---: | :--- | :--- | :--- | :--- | :--- |\n")
        for idx, (item_id, meta, _) in enumerate(zip(ids, metadatas, documents)):
            v_url = meta.get("video_url", "")
            stem = Path(v_url).stem if v_url else item_id
            q_item = queue_data.get(stem, {})

            title = (q_item.get("caption") or meta.get("caption", "")).split("\n")[0][:45]
            ht = q_item.get("hashtag") or meta.get("hashtag", "")
            if isinstance(ht, list):
                ht_str = " ".join([f"#{t}" for t in ht[:4]])
            else:
                ht_str = str(ht)[:30]
            ts = (q_item.get("transcript") or meta.get("transcript", ""))[:60] + "..."
            img = Path(q_item.get("image_url") or meta.get("image_url", "")).name
            sm = (q_item.get("summary") or meta.get("summary", "")).replace("\n", " ")[:60] + "..."
            
            f.write(f"| {idx+1} | `{stem}` | {title} | {ht_str} | {ts} | `{img}` | {sm} |\n")

    print(f"✅ Đã xuất lại bảng dữ liệu đầy đủ 5 trường bắt buộc:")
    print(f"  📄 File CSV:      {export_csv_path.resolve()}")
    print(f"  📋 File Markdown: {export_md_path.resolve()}\n")


if __name__ == "__main__":
    inspect_db()
