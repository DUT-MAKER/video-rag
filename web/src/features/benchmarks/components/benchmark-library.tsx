"use client";

import * as React from "react";
import { Search, ExternalLink, Play, X } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { searchBenchmarkPatterns } from "@/lib/api";
import type { SearchPatternItem } from "@/lib/types";

const DEFAULT_BENCHMARKS: SearchPatternItem[] = [
  {
    id: "sample_001",
    caption: "Quy tắc 2 phút thay đổi hoàn toàn năng suất làm việc của tôi",
    matched_hook:
      "Nếu bạn không thể làm việc này trong 2 phút, bạn sẽ hối hận...",
    summary:
      "Video phân tích thói quen hành động ngay lập tức, sử dụng visual before-after để giữ chân 70% người xem sau 10s đầu.",
    video_url: "http://localhost:9000/viral-videos/sample1.mp4",
    image_url: "",
    similarity_score: 0.94,
  },
  {
    id: "sample_002",
    caption: "Sai lầm tài chính 99% người trẻ mắc phải khi vừa có lương",
    matched_hook:
      "Dừng ngay việc gửi tiết kiệm ngân hàng kiểu này nếu bạn muốn tự do tài chính!",
    summary:
      "Hook dạng contrarian gây tranh cãi mạnh mẽ ở phần bình luận, cấu trúc nhịp điệu nhanh 3s chuyển cảnh 1 lần.",
    video_url: "http://localhost:9000/viral-videos/sample2.mp4",
    image_url: "",
    similarity_score: 0.89,
  },
  {
    id: "sample_003",
    caption: "Kỷ luật thép 21 ngày: Không ai có thể ngăn bạn thành công",
    matched_hook:
      "3 thói quen buổi sáng biến bạn thành cỗ máy làm việc trong 3 tuần.",
    summary:
      "Video dạng danh sách (listicle) kết hợp B-roll thức dậy sớm và âm thanh đồng hồ tích tắc tạo cảm giác cấp bách.",
    video_url: "http://localhost:9000/viral-videos/sample3.mp4",
    image_url: "",
    similarity_score: 0.86,
  },
];

export function BenchmarkLibrary() {
  const [query, setQuery] = React.useState("");
  const [items, setItems] =
    React.useState<SearchPatternItem[]>(DEFAULT_BENCHMARKS);
  const [isLoading, setIsLoading] = React.useState(false);
  const [activeVideoUrl, setActiveVideoUrl] = React.useState<string | null>(
    null
  );

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    try {
      const results = await searchBenchmarkPatterns(query, 6);
      if (results && results.length > 0) {
        setItems(results);
      } else {
        alert(
          "Không tìm thấy mẫu video tương đồng. Đang hiển thị danh mục mẫu."
        );
      }
    } catch (err) {
      console.error("Search failed:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-6xl space-y-8 p-6 text-white">
      {/* Header */}
      <div className="space-y-1.5 border-b border-zinc-800 pb-5">
        <span className="font-mono text-[11px] font-bold uppercase tracking-widest text-zinc-400">
          Knowledge Store Explorer
        </span>
        <h1 className="text-2xl font-bold tracking-tight text-white md:text-3xl">
          Thư Viện Video Chuẩn Đối Sánh
        </h1>
        <p className="max-w-2xl text-xs leading-relaxed text-zinc-300">
          Tra cứu ngữ nghĩa (Semantic Search) trên không gian vector pgvector và
          kho lưu trữ MinIO để phân tích công thức hook, nhịp độ và cấu trúc
          video viral đã được kiểm chứng.
        </p>
      </div>

      {/* Search Bar */}
      <form onSubmit={handleSearch} className="flex max-w-xl gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-zinc-400" />
          <Input
            className="pl-9"
            placeholder="Tìm theo chủ đề: kỷ luật 21 ngày, tài chính cá nhân, trì hoãn..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
        <Button
          type="submit"
          disabled={isLoading || !query.trim()}
          className="px-5"
        >
          {isLoading ? "Đang truy vấn..." : "Truy vấn Vector"}
        </Button>
      </form>

      {/* Video Grid */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        {items.map((item) => (
          <Card
            key={item.id}
            className="group flex flex-col justify-between overflow-hidden border-zinc-700 bg-[#141418] shadow-sm transition-all hover:border-zinc-500"
          >
            {/* Visual Frame */}
            <div className="relative flex aspect-video items-center justify-center overflow-hidden border-b border-zinc-700 bg-zinc-900">
              <button
                type="button"
                onClick={() => setActiveVideoUrl(item.video_url)}
                className="absolute inset-0 flex cursor-pointer items-center justify-center bg-black/40 transition-all hover:bg-black/15"
              >
                <div className="flex h-11 w-11 items-center justify-center rounded-full border border-white/40 bg-white/20 text-white shadow-md backdrop-blur-md transition-transform hover:scale-110">
                  <Play className="ml-0.5 h-5 w-5 fill-white" />
                </div>
              </button>

              <div className="absolute right-3 top-3">
                <Badge variant="mono">
                  {(item.similarity_score * 100).toFixed(0)}% Match
                </Badge>
              </div>
            </div>

            <CardContent className="flex flex-1 flex-col justify-between space-y-3 p-4">
              <div className="space-y-2.5">
                <h3 className="text-sm font-bold leading-snug text-white">
                  {item.caption}
                </h3>

                {/* Hook Box */}
                <div className="space-y-1 rounded-lg border border-orange-400/40 bg-orange-500/10 p-3">
                  <span className="block text-[10px] font-bold uppercase tracking-wider text-orange-300">
                    Viral Hook Formula
                  </span>
                  <p className="text-xs font-medium italic leading-relaxed text-orange-100">
                    &ldquo;{item.matched_hook}&rdquo;
                  </p>
                </div>

                <p className="text-xs leading-relaxed text-zinc-300">
                  {item.summary}
                </p>
              </div>

              <div className="flex items-center justify-between border-t border-zinc-800 pt-3 text-xs">
                <span className="font-mono text-[11px] font-semibold text-zinc-400">
                  {item.id}
                </span>

                {item.video_url && (
                  <button
                    type="button"
                    onClick={() => setActiveVideoUrl(item.video_url)}
                    className="inline-flex cursor-pointer items-center space-x-1.5 font-medium text-zinc-200 transition-colors hover:text-white"
                  >
                    <span>Xem video MinIO</span>
                    <ExternalLink className="h-3.5 w-3.5" />
                  </button>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Video Player Modal */}
      {activeVideoUrl && (
        <div className="animate-in fade-in fixed inset-0 z-50 flex items-center justify-center bg-black/85 p-4 backdrop-blur-sm duration-200">
          <div className="relative w-full max-w-2xl overflow-hidden rounded-2xl border border-zinc-700 bg-[#141418] shadow-2xl">
            <div className="flex items-center justify-between border-b border-zinc-700 p-4">
              <span className="text-xs font-bold uppercase tracking-wider text-white">
                MinIO Video Asset Player
              </span>
              <button
                type="button"
                onClick={() => setActiveVideoUrl(null)}
                className="cursor-pointer rounded-md p-1.5 text-zinc-400 transition-colors hover:bg-zinc-800 hover:text-white"
                title="Đóng"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="flex items-center justify-center bg-black p-4">
              <video
                controls
                autoPlay
                className="max-h-[70vh] w-full rounded-lg"
                src={activeVideoUrl}
              >
                Trình duyệt không hỗ trợ thẻ video HTML5.
              </video>
            </div>

            <div className="truncate border-t border-zinc-800 bg-[#0e0e12] p-3 font-mono text-[11px] text-zinc-300">
              Source: {activeVideoUrl}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
