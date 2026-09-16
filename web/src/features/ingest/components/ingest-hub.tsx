"use client";

import * as React from "react";
import { CheckCircle2, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ingestKnowledge } from "@/lib/api";
import type { IngestionResponseData } from "@/lib/types";

export function IngestHub() {
  const [filePath, setFilePath] = React.useState(
    "data/samples/sample_viral_videos.json"
  );
  const [isLoading, setIsLoading] = React.useState(false);
  const [result, setResult] = React.useState<IngestionResponseData | null>(
    null
  );

  const handleIngest = async () => {
    setIsLoading(true);
    try {
      const data = await ingestKnowledge(filePath);
      setResult(data);
    } catch (err) {
      console.error("Ingestion failed:", err);
      alert(
        "Nạp dữ liệu thất bại. Hãy kiểm tra kết nối tới backend FastAPI (port 8000)."
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-5xl space-y-8 p-6 text-white">
      {/* Header */}
      <div className="space-y-1.5 border-b border-zinc-800 pb-5">
        <span className="font-mono text-[11px] font-bold uppercase tracking-widest text-zinc-400">
          Vector Ingestion & MinIO Storage
        </span>
        <h1 className="text-2xl font-bold tracking-tight text-white md:text-3xl">
          Knowledge Ingestion Hub
        </h1>
        <p className="max-w-2xl text-xs leading-relaxed text-zinc-300">
          Nạp tập dữ liệu mẫu video triệu view, trích xuất đặc trưng văn bản,
          vector hóa bằng embedding model và lưu trữ vào PostgreSQL HNSW
          pgvector.
        </p>
      </div>

      {/* Grid: Infrastructure status */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <Card className="space-y-2 border-zinc-700 bg-[#141418] p-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-zinc-300">
              Vector Database
            </span>
            <Badge variant="success">Active</Badge>
          </div>
          <p className="text-sm font-bold text-white">PostgreSQL + pgvector</p>
          <p className="font-mono text-xs text-zinc-400">
            Table: viral_video_embeddings
          </p>
        </Card>

        <Card className="space-y-2 border-zinc-700 bg-[#141418] p-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-zinc-300">
              Object Storage
            </span>
            <Badge variant="success">Online</Badge>
          </div>
          <p className="text-sm font-bold text-white">MinIO S3 Compatible</p>
          <p className="font-mono text-xs text-zinc-400">
            Bucket: viral-videos
          </p>
        </Card>

        <Card className="space-y-2 border-zinc-700 bg-[#141418] p-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-zinc-300">
              Embedding Engine
            </span>
            <Badge variant="ai">DUT AI / BGE</Badge>
          </div>
          <p className="text-sm font-bold text-white">
            Dense Vector Embeddings
          </p>
          <p className="font-mono text-xs text-zinc-400">
            Dimension: 768 / 1536
          </p>
        </Card>
      </div>

      {/* Main Ingest Action Box */}
      <Card className="border-zinc-700 bg-[#141418]">
        <CardHeader>
          <CardTitle>Nạp Dữ Liệu Video Triệu View Vào Vector Store</CardTitle>
          <CardDescription>
            Đọc tập tin JSON chứa danh sách video mẫu (kèm transcript, caption,
            hook và MinIO URL) để thực hiện embedding và indexing.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-xs font-bold text-zinc-200">
              Đường dẫn tệp tin Dataset JSON
            </label>
            <div className="flex gap-3">
              <input
                type="text"
                value={filePath}
                onChange={(e) => setFilePath(e.target.value)}
                className="h-10 flex-1 rounded-lg border border-zinc-700 bg-[#16161a] px-3.5 font-mono text-xs font-medium text-white outline-none focus:border-zinc-300"
              />
              <Button
                onClick={handleIngest}
                disabled={isLoading || !filePath.trim()}
                className="h-10 px-5"
              >
                {isLoading ? (
                  <span className="flex items-center space-x-2">
                    <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                    <span>Đang xử lý & Index...</span>
                  </span>
                ) : (
                  <span>Bắt Đầu Ingestion</span>
                )}
              </Button>
            </div>
          </div>

          {/* Ingestion Results */}
          {result && (
            <div className="animate-in fade-in space-y-3 rounded-xl border border-emerald-400/40 bg-emerald-500/10 p-4 duration-200">
              <div className="flex items-center space-x-2 text-emerald-300">
                <CheckCircle2 className="h-4 w-4" />
                <span className="text-xs font-bold">
                  Ingestion Hoàn Tất Thành Công
                </span>
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs sm:grid-cols-4">
                <div className="rounded-lg border border-zinc-700 bg-black/60 p-3">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-zinc-400">
                    Đã xử lý
                  </span>
                  <p className="mt-1 text-base font-bold text-white">
                    {result.total_processed}
                  </p>
                </div>
                <div className="rounded-lg border border-zinc-700 bg-black/60 p-3">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-zinc-400">
                    Đã vector hóa
                  </span>
                  <p className="mt-1 text-base font-bold text-emerald-300">
                    {result.total_indexed}
                  </p>
                </div>
                <div className="col-span-2 rounded-lg border border-zinc-700 bg-black/60 p-3">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-zinc-400">
                    Hook Candidates
                  </span>
                  <p className="mt-1 text-base font-bold text-purple-300">
                    {result.extracted_hooks?.length || 0} hooks
                  </p>
                </div>
              </div>

              {result.extracted_hooks?.length > 0 && (
                <div className="space-y-1.5 border-t border-emerald-400/20 pt-2">
                  <span className="text-xs font-bold text-white">
                    Mẫu Hook Đã Trích Xuất:
                  </span>
                  <ul className="list-inside list-disc space-y-1 text-xs text-zinc-200">
                    {result.extracted_hooks.slice(0, 5).map((hook, i) => (
                      <li key={i} className="truncate italic text-zinc-100">
                        &ldquo;{hook}&rdquo;
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
