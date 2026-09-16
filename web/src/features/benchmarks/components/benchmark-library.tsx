"use client";

import * as React from "react";
import {
  Search,
  Database,
  ExternalLink,
  Film,
  Zap,
  Play,
  X,
  Sparkles,
} from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { searchBenchmarkPatterns } from "@/lib/api";
import type { SearchPatternItem } from "@/lib/types";

// Default curated benchmark videos matching MinIO & sample data
const DEFAULT_BENCHMARKS: SearchPatternItem[] = [
  {
    id: "sample_001",
    caption: "Quy tắc 2 phút thay đổi hoàn toàn năng suất làm việc của tôi",
    matched_hook: "Nếu bạn không thể làm việc này trong 2 phút, bạn sẽ hối hận...",
    summary: "Video phân tích thói quen hành động ngay lập tức, sử dụng visual before-after để giữ chân 70% người xem sau 10s đầu.",
    video_url: "http://localhost:9000/viral-videos/sample1.mp4",
    image_url: "",
    similarity_score: 0.94,
  },
  {
    id: "sample_002",
    caption: "Sai lầm tài chính 99% người trẻ mắc phải khi vừa có lương",
    matched_hook: "Dừng ngay việc gửi tiết kiệm ngân hàng kiểu này nếu bạn muốn tự do tài chính!",
    summary: "Hook dạng contrarian gây tranh cãi mạnh mẽ ở phần bình luận, cấu trúc nhịp điệu nhanh 3s chuyển cảnh 1 lần.",
    video_url: "http://localhost:9000/viral-videos/sample2.mp4",
    image_url: "",
    similarity_score: 0.89,
  },
  {
    id: "sample_003",
    caption: "Kỷ luật thép 21 ngày: Không ai có thể ngăn bạn thành công",
    matched_hook: "3 thói quen buổi sáng biến bạn thành cỗ máy làm việc trong 3 tuần.",
    summary: "Video dạng danh sách (listicle) kết hợp B-roll thức dậy sớm và âm thanh đồng hồ tích tắc tạo cảm giác cấp bách.",
    video_url: "http://localhost:9000/viral-videos/sample3.mp4",
    image_url: "",
    similarity_score: 0.86,
  },
];

export function BenchmarkLibrary() {
  const [query, setQuery] = React.useState("");
  const [items, setItems] = React.useState<SearchPatternItem[]>(DEFAULT_BENCHMARKS);
  const [isLoading, setIsLoading] = React.useState(false);
  const [activeVideoUrl, setActiveVideoUrl] = React.useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    try {
      const results = await searchBenchmarkPatterns(query, 6);
      if (results && results.length > 0) {
        setItems(results);
      } else {
        alert("Không tìm thấy mẫu video tương đồng. Đang hiển thị danh mục mẫu.");
      }
    } catch (err) {
      console.error("Search failed:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-8">
      {/* Header */}
      <div className="space-y-1.5">
        <div className="flex items-center space-x-2 text-purple-400">
          <Database className="w-4 h-4" />
          <span className="text-xs font-semibold uppercase tracking-wider">
            Knowledge Store Explorer
          </span>
        </div>
        <h1 className="text-2xl font-bold tracking-tight text-white">
          Thư Viện Video Chuẩn Đối Sánh (Benchmark Patterns)
        </h1>
        <p className="text-xs text-neutral-400 max-w-2xl leading-relaxed">
          Tra cứu ngữ nghĩa (Semantic Search) trên không gian vector pgvector và kho lưu trữ MinIO để phân tích công thức hook, nhịp độ và cấu trúc video viral đã được kiểm chứng.
        </p>
      </div>

      {/* Search Bar */}
      <form onSubmit={handleSearch} className="flex gap-2 max-w-xl">
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-neutral-500" />
          <Input
            className="pl-9"
            placeholder="Tìm theo chủ đề: kỷ luật 21 ngày, tài chính cá nhân, trì hoãn..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
        <Button type="submit" disabled={isLoading || !query.trim()}>
          {isLoading ? (
            <Sparkles className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <span>Truy vấn Vector</span>
          )}
        </Button>
      </form>

      {/* Video Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {items.map((item) => (
          <Card
            key={item.id}
            className="overflow-hidden hover:border-neutral-700 transition-all flex flex-col justify-between group"
          >
            {/* Visual Header / Simulated Video Frame */}
            <div className="relative aspect-video bg-neutral-900 border-b border-neutral-800 flex items-center justify-center overflow-hidden">
              <Film className="w-8 h-8 text-neutral-700 group-hover:scale-110 transition-transform" />
              <button
                type="button"
                onClick={() => setActiveVideoUrl(item.video_url)}
                className="absolute inset-0 bg-black/40 hover:bg-black/20 flex items-center justify-center transition-all cursor-pointer"
              >
                <div className="w-10 h-10 rounded-full bg-white/10 backdrop-blur-sm border border-white/20 flex items-center justify-center text-white hover:scale-110 transition-transform">
                  <Play className="w-4 h-4 fill-white ml-0.5" />
                </div>
              </button>

              <div className="absolute top-2.5 right-2.5">
                <Badge variant="mono">
                  {(item.similarity_score * 100).toFixed(0)}% Match
                </Badge>
              </div>
            </div>

            <CardContent className="p-4 space-y-3 flex-1 flex flex-col justify-between">
              <div className="space-y-2">
                <h3 className="text-xs font-semibold text-white leading-snug line-clamp-2">
                  {item.caption}
                </h3>

                {/* Hook Box */}
                <div className="p-2.5 rounded-lg border border-orange-500/20 bg-orange-500/[0.04] space-y-1">
                  <div className="flex items-center space-x-1 text-orange-400 text-[10px] font-semibold uppercase">
                    <Zap className="w-3 h-3" />
                    <span>Viral Hook Formula</span>
                  </div>
                  <p className="text-[11px] text-neutral-200 italic font-medium line-clamp-2">
                    &ldquo;{item.matched_hook}&rdquo;
                  </p>
                </div>

                <p className="text-[11px] text-neutral-400 leading-relaxed line-clamp-3">
                  {item.summary}
                </p>
              </div>

              <div className="pt-3 border-t border-neutral-800 flex items-center justify-between text-[11px]">
                <span className="font-mono text-[10px] text-neutral-500">
                  {item.id}
                </span>

                {item.video_url && (
                  <button
                    type="button"
                    onClick={() => setActiveVideoUrl(item.video_url)}
                    className="inline-flex items-center space-x-1 text-neutral-300 hover:text-white transition-colors cursor-pointer"
                  >
                    <span>Xem video MinIO</span>
                    <ExternalLink className="w-3 h-3" />
                  </button>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Video Player Modal */}
      {activeVideoUrl && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="relative w-full max-w-2xl rounded-2xl border border-neutral-800 bg-[#121215] overflow-hidden shadow-2xl">
            <div className="flex items-center justify-between p-4 border-b border-neutral-800">
              <div className="flex items-center space-x-2">
                <Film className="w-4 h-4 text-neutral-300" />
                <span className="text-xs font-semibold text-white">
                  MinIO Video Asset Player
                </span>
              </div>
              <button
                type="button"
                onClick={() => setActiveVideoUrl(null)}
                className="p-1 rounded-md text-neutral-400 hover:text-white hover:bg-neutral-800 transition-colors cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="p-4 bg-black flex items-center justify-center">
              <video
                controls
                autoPlay
                className="max-h-[70vh] rounded-lg w-full"
                src={activeVideoUrl}
              >
                Trình duyệt không hỗ trợ thẻ video HTML5.
              </video>
            </div>

            <div className="p-3 text-[11px] text-neutral-400 bg-[#0c0c0e] border-t border-neutral-800 truncate font-mono">
              Source: {activeVideoUrl}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
