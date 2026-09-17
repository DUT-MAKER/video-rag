"use client";

import * as React from "react";
import Link from "next/link";
import {
  Search,
  Video,
  Film,
  Clock,
  Users,
  ExternalLink,
  ChevronRight,
  RefreshCw,
  Layers,
  Sparkles,
  Hash,
} from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { getVideoList, formatMediaUrl } from "@/lib/api";
import type { VideoListItem } from "@/lib/types";

export function VideoManagementList() {
  const [videos, setVideos] = React.useState<VideoListItem[]>([]);
  const [total, setTotal] = React.useState<number>(0);
  const [isLoading, setIsLoading] = React.useState(true);
  const [search, setSearch] = React.useState("");
  const [debouncedSearch, setDebouncedSearch] = React.useState("");

  // Debounce search input
  React.useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(search.trim());
    }, 400);
    return () => clearTimeout(handler);
  }, [search]);

  // Fetch videos
  const fetchVideos = React.useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await getVideoList(50, 0, debouncedSearch);
      setVideos(data.items || []);
      setTotal(data.total || 0);
    } catch (err) {
      console.error("Failed to load videos:", err);
    } finally {
      setIsLoading(false);
    }
  }, [debouncedSearch]);

  React.useEffect(() => {
    fetchVideos();
  }, [fetchVideos]);

  return (
    <div className="mx-auto max-w-7xl space-y-8 p-6 md:p-8">
      {/* Header Section */}
      <div className="flex flex-col justify-between gap-4 border-b border-[#ffe6dc] pb-6 md:flex-row md:items-end">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 rounded-full border border-[#ff7442]/20 bg-[#fff0eb] px-3.5 py-1 text-xs font-black uppercase tracking-wider text-[#ff7442]">
            <Layers className="h-3.5 w-3.5" />
            <span>Kho Dữ Liệu Video RAG</span>
          </div>
          <h1 className="text-2xl font-black tracking-tight text-[#0f172a] [font-family:var(--font-heading)] md:text-3xl">
            Quản Lý Dữ Liệu Video
          </h1>
          <p className="text-xs font-medium text-[#667085]">
            Danh sách toàn bộ các video đã được trích xuất AI, phân vai giọng nói và lập chỉ mục vào pgvector.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button
            variant="secondary"
            size="sm"
            onClick={fetchVideos}
            disabled={isLoading}
            className="gap-2 text-xs"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? "animate-spin" : ""}`} />
            Làm mới
          </Button>
          <Link href="/dashboard/ingest">
            <Button size="sm" className="gap-2 text-xs font-extrabold">
              <Film className="h-3.5 w-3.5" />
              Nạp Video Mới
            </Button>
          </Link>
        </div>
      </div>

      {/* Filter and Stats Bar */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative w-full max-w-md">
          <Search className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-[#94a3b8]" />
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Tìm kiếm theo tiêu đề, hashtag, nội dung..."
            className="pl-10"
          />
        </div>

        <div className="flex items-center gap-2 text-xs font-bold text-[#667085]">
          <span>Tổng số video đã nạp:</span>
          <span className="rounded-full border border-[#ffe0d5] bg-[#fff0eb] px-3 py-1 font-mono font-black text-[#ff7442]">
            {total}
          </span>
        </div>
      </div>

      {/* Videos Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <Card key={i} className="animate-pulse border-[#f1f5f9] bg-[#f8fafc]">
              <div className="aspect-video w-full bg-slate-200" />
              <CardContent className="space-y-3 p-5">
                <div className="h-4 w-3/4 rounded bg-slate-200" />
                <div className="h-3 w-1/2 rounded bg-slate-200" />
                <div className="h-10 w-full rounded-full bg-slate-200" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : videos.length === 0 ? (
        <div className="flex min-h-[360px] flex-col items-center justify-center rounded-[28px] border border-dashed border-[#ffe6dc] bg-[#fffcfb] p-8 text-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-full border border-[#ffe0d5] bg-[#fff0eb] text-[#ff7442]">
            <Video className="h-7 w-7" />
          </div>
          <h3 className="mt-4 text-base font-black text-[#0f172a] [font-family:var(--font-heading)]">
            {debouncedSearch ? "Không tìm thấy video nào phù hợp" : "Chưa có video nào trong hệ thống"}
          </h3>
          <p className="mt-1 max-w-sm text-xs font-medium text-[#667085]">
            {debouncedSearch
              ? "Thử tìm kiếm với từ khóa khác hoặc xóa bộ lọc."
              : "Hãy tải lên video đầu tiên để hệ thống tự động bóc tách âm thanh, nhận diện người nói và lưu trữ."}
          </p>
          {!debouncedSearch && (
            <Link href="/dashboard/ingest" className="mt-5">
              <Button size="sm" className="gap-2 text-xs">
                <Film className="h-4 w-4" />
                Nạp Video Ngay
              </Button>
            </Link>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {videos.map((item) => {
            const hasThumb = Boolean(item.image_url);
            const thumbUrl = formatMediaUrl(item.image_url);

            return (
              <Card
                key={item.id}
                className="group flex flex-col overflow-hidden rounded-[24px] border border-[#f1f5f9] bg-white shadow-[0_12px_28px_rgba(15,23,42,0.04)] transition-all duration-200 hover:-translate-y-1 hover:border-[#ffe0d5] hover:shadow-[0_20px_45px_rgba(255,116,66,0.1)]"
              >
                {/* Thumbnail Header */}
                <div className="relative aspect-video w-full overflow-hidden bg-slate-100">
                  {hasThumb ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      src={thumbUrl}
                      alt={item.caption || "Video thumbnail"}
                      className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
                      loading="lazy"
                    />
                  ) : (
                    <div className="flex h-full w-full items-center justify-center text-[#94a3b8]">
                      <Film className="h-10 w-10 stroke-[1.5]" />
                    </div>
                  )}

                  {/* Gradient Overlay */}
                  <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/10 to-transparent" />

                  {/* Badges on Thumbnail */}
                  <div className="absolute bottom-2.5 left-3 right-3 flex items-center justify-between text-xs text-white">
                    <div className="flex items-center gap-1.5 rounded-full bg-black/60 px-2.5 py-0.5 backdrop-blur-md">
                      <Users className="h-3 w-3 text-[#ffbd2e]" />
                      <span className="font-mono text-[11px] font-bold">
                        {item.speaker_count} người nói
                      </span>
                    </div>

                    {item.duration_seconds > 0 && (
                      <div className="flex items-center gap-1 rounded-full bg-black/60 px-2.5 py-0.5 backdrop-blur-md">
                        <Clock className="h-3 w-3 text-slate-300" />
                        <span className="font-mono text-[11px]">
                          {Math.round(item.duration_seconds)}s
                        </span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Content Body */}
                <CardContent className="flex flex-1 flex-col justify-between p-5">
                  <div className="space-y-3">
                    {/* Caption */}
                    <h3 className="line-clamp-2 text-sm font-black leading-snug text-[#0f172a] transition-colors group-hover:text-[#ff7442]">
                      {item.caption || "Video không có tiêu đề"}
                    </h3>

                    {/* Hashtags */}
                    {item.hashtag && (
                      <div className="flex flex-wrap gap-1.5">
                        {item.hashtag
                          .split(/[\s,]+/)
                          .filter(Boolean)
                          .slice(0, 3)
                          .map((tag, idx) => (
                            <Badge
                              key={idx}
                              variant="secondary"
                              className="text-[10px]"
                            >
                              <Hash className="mr-0.5 h-2.5 w-2.5 opacity-60" />
                              {tag.replace(/^#/, "")}
                            </Badge>
                          ))}
                      </div>
                    )}

                    {/* Summary Preview */}
                    {item.summary && (
                      <p className="line-clamp-2 text-xs leading-relaxed text-[#667085]">
                        {item.summary}
                      </p>
                    )}
                  </div>

                  {/* Action Link to Detail */}
                  <div className="mt-5 border-t border-[#f1f5f9] pt-4">
                    <Link
                      href={`/dashboard/videos/${item.id}`}
                      className="inline-flex w-full items-center justify-between rounded-full border border-[#ffe0d5] bg-[#fff0eb] px-4 py-2.5 text-xs font-bold text-[#ff7442] transition-colors hover:bg-[#ffe4d9]"
                    >
                      <span>Xem Chi Tiết Video</span>
                      <ChevronRight className="h-3.5 w-3.5 transition-transform group-hover:translate-x-0.5" />
                    </Link>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

    </div>
  );
}
