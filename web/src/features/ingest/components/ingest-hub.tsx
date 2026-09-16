"use client";

import * as React from "react";
import {
  CheckCircle2,
  Database,
  FileCode,
  RefreshCw,
  Zap,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ingestKnowledge } from "@/lib/api";
import type { IngestionResponseData } from "@/lib/types";

export function IngestHub() {
  const [filePath, setFilePath] = React.useState(
    "data/samples/sample_viral_videos.json"
  );
  const [isLoading, setIsLoading] = React.useState(false);
  const [result, setResult] = React.useState<IngestionResponseData | null>(null);

  const handleIngest = async () => {
    setIsLoading(true);
    try {
      const data = await ingestKnowledge(filePath);
      setResult(data);
    } catch (err) {
      console.error("Ingestion failed:", err);
      alert("Nạp dữ liệu thất bại. Hãy kiểm tra kết nối tới backend FastAPI (port 8000).");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-8">
      {/* Header */}
      <div className="space-y-1.5">
        <div className="flex items-center space-x-2 text-emerald-400">
          <Database className="w-4 h-4" />
          <span className="text-xs font-semibold uppercase tracking-wider">
            Vector Ingestion & MinIO Storage
          </span>
        </div>
        <h1 className="text-2xl font-bold tracking-tight text-white">
          Knowledge Ingestion Hub
        </h1>
        <p className="text-xs text-neutral-400 max-w-2xl leading-relaxed">
          Nạp tập dữ liệu mẫu video triệu view, trích xuất đặc trưng văn bản, vector hóa bằng embedding model và lưu trữ vào PostgreSQL HNSW pgvector.
        </p>
      </div>

      {/* Grid: Infrastructure status */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-neutral-400">Vector Database</span>
            <Badge variant="success">Active</Badge>
          </div>
          <p className="text-sm font-semibold text-white">PostgreSQL + pgvector</p>
          <p className="text-[11px] text-neutral-500 font-mono">
            Table: viral_video_embeddings
          </p>
        </Card>

        <Card className="p-4 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-neutral-400">Object Storage</span>
            <Badge variant="success">Online</Badge>
          </div>
          <p className="text-sm font-semibold text-white">MinIO S3 Compatible</p>
          <p className="text-[11px] text-neutral-500 font-mono">
            Bucket: viral-videos
          </p>
        </Card>

        <Card className="p-4 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-neutral-400">Embedding Engine</span>
            <Badge variant="ai">DUT AI / BGE</Badge>
          </div>
          <p className="text-sm font-semibold text-white">Dense Vector Embeddings</p>
          <p className="text-[11px] text-neutral-500 font-mono">
            Dimension: 768 / 1536
          </p>
        </Card>
      </div>

      {/* Main Ingest Action Box */}
      <Card>
        <CardHeader>
          <CardTitle>Nạp Dữ Liệu Video Triệu View Vào Vector Store</CardTitle>
          <CardDescription>
            Đọc tập tin JSON chứa danh sách video mẫu (kèm transcript, caption, hook và MinIO URL) để thực hiện embedding và indexing.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-neutral-300">
              Đường dẫn tệp tin Dataset JSON
            </label>
            <div className="flex gap-2">
              <div className="relative flex-1">
                <FileCode className="w-4 h-4 absolute left-3 top-2.5 text-neutral-500" />
                <input
                  type="text"
                  value={filePath}
                  onChange={(e) => setFilePath(e.target.value)}
                  className="h-9 w-full rounded-lg border border-neutral-800 bg-[#121215] pl-9 pr-3 text-xs text-neutral-100 outline-none focus:border-neutral-600 font-mono"
                />
              </div>
              <Button
                onClick={handleIngest}
                disabled={isLoading || !filePath.trim()}
              >
                {isLoading ? (
                  <span className="flex items-center space-x-2">
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    <span>Đang xử lý & Index...</span>
                  </span>
                ) : (
                  <span className="flex items-center space-x-2">
                    <Zap className="w-3.5 h-3.5 text-yellow-400" />
                    <span>Bắt Đầu Ingestion</span>
                  </span>
                )}
              </Button>
            </div>
          </div>

          {/* Ingestion Results */}
          {result && (
            <div className="p-4 rounded-xl border border-emerald-500/20 bg-emerald-500/[0.03] space-y-3 animate-in fade-in duration-200">
              <div className="flex items-center space-x-2 text-emerald-400">
                <CheckCircle2 className="w-4 h-4" />
                <span className="text-xs font-semibold">
                  Ingestion Hoàn Tất Thành Công
                </span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                <div className="p-2.5 rounded-lg bg-black/40 border border-neutral-800">
                  <span className="text-neutral-500 text-[10px] uppercase">
                    Đã xử lý
                  </span>
                  <p className="text-base font-bold text-white mt-0.5">
                    {result.total_processed}
                  </p>
                </div>
                <div className="p-2.5 rounded-lg bg-black/40 border border-neutral-800">
                  <span className="text-neutral-500 text-[10px] uppercase">
                    Đã vector hóa
                  </span>
                  <p className="text-base font-bold text-emerald-400 mt-0.5">
                    {result.total_indexed}
                  </p>
                </div>
                <div className="p-2.5 rounded-lg bg-black/40 border border-neutral-800 col-span-2">
                  <span className="text-neutral-500 text-[10px] uppercase">
                    Hook Candidates
                  </span>
                  <p className="text-base font-bold text-purple-400 mt-0.5">
                    {result.extracted_hooks?.length || 0} hooks
                  </p>
                </div>
              </div>

              {result.extracted_hooks?.length > 0 && (
                <div className="space-y-1.5 pt-2 border-t border-neutral-800/80">
                  <span className="text-[11px] font-semibold text-neutral-300">
                    Mẫu Hook Đã Trích Xuất:
                  </span>
                  <ul className="list-disc list-inside space-y-1 text-[11px] text-neutral-400">
                    {result.extracted_hooks.slice(0, 5).map((hook, i) => (
                      <li key={i} className="italic text-neutral-300 truncate">
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
