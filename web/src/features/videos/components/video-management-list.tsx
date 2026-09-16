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
      <div className="flex flex-col justify-between gap-4 border-b border-border/60 pb-6 md:flex-row md:items-end">
        <div className="space-y-1.5">
          <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-3 py-0.5 text-xs font-medium text-primary">
            <Layers className="h-3.5 w-3.5" />
            <span>Kho Dữ Liệu Video RAG</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground md:text-3xl">
            Quản Lý Dữ Liệu Video
          </h1>
          <p className="text-sm text-muted-foreground">
            Danh sách toàn bộ các video đã được trích xuất AI, phân vai giọng nói và lập chỉ mục vào pgvector.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            onClick={fetchVideos}
            disabled={isLoading}
            className="gap-2 text-xs"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? "animate-spin" : ""}`} />
            Làm mới
          </Button>
          <Link href="/dashboard/ingest">
            <Button size="sm" className="gap-2 text-xs font-semibold">
              <Film className="h-3.5 w-3.5" />
              Nạp Video Mới
            </Button>
          </Link>
        </div>
      </div>

      {/* Filter and Stats Bar */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative w-full max-w-md">
          <Search className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Tìm kiếm theo tiêu đề, hashtag, nội dung..."
            className="pl-10 text-sm"
          />
        </div>

        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span>Tổng số video đã nạp:</span>
          <span className="rounded-md bg-surface px-2.5 py-1 font-mono font-bold text-foreground border border-border">
            {total}
          </span>
        </div>
      </div>

      {/* Videos Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <Card key={i} className="animate-pulse border-border/40 bg-surface/30">
              <div className="aspect-video w-full bg-surface/70" />
              <CardContent className="space-y-3 p-5">
                <div className="h-4 w-3/4 rounded bg-surface/80" />
                <div className="h-3 w-1/2 rounded bg-surface/60" />
                <div className="h-10 w-full rounded bg-surface/50" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : videos.length === 0 ? (
        <div className="flex min-h-[360px] flex-col items-center justify-center rounded-xl border border-dashed border-border/80 bg-surface/20 p-8 text-center">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-surface text-muted-foreground">
            <Video className="h-6 w-6" />
          </div>
          <h3 className="mt-4 text-base font-semibold text-foreground">
            {debouncedSearch ? "Không tìm thấy video nào phù hợp" : "Chưa có video nào trong hệ thống"}
          </h3>
          <p className="mt-1 max-w-sm text-xs text-muted-foreground">
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
                className="group flex flex-col overflow-hidden border-border/60 bg-surface/40 transition-all duration-200 hover:-translate-y-1 hover:border-primary/40 hover:bg-surface/80 hover:shadow-xl hover:shadow-primary/5"
              >
                {/* Thumbnail Header */}
                <div className="relative aspect-video w-full overflow-hidden bg-zinc-950">
                  {hasThumb ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      src={thumbUrl}
                      alt={item.caption || "Video thumbnail"}
                      className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
                      loading="lazy"
                    />
                  ) : (
                    <div className="flex h-full w-full items-center justify-center text-zinc-700">
                      <Film className="h-10 w-10 stroke-[1.5]" />
                    </div>
                  )}

                  {/* Gradient Overlay */}
                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />

                  {/* Badges on Thumbnail */}
                  <div className="absolute bottom-2.5 left-3 right-3 flex items-center justify-between text-xs text-zinc-200">
                    <div className="flex items-center gap-1.5 rounded-md bg-black/60 px-2 py-0.5 backdrop-blur-md">
                      <Users className="h-3 w-3 text-primary" />
                      <span className="font-mono text-[11px] font-medium">
                        {item.speaker_count} người nói
                      </span>
                    </div>

                    {item.duration_seconds > 0 && (
                      <div className="flex items-center gap-1 rounded-md bg-black/60 px-2 py-0.5 backdrop-blur-md">
                        <Clock className="h-3 w-3 text-zinc-400" />
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
                    <h3 className="line-clamp-2 text-sm font-semibold leading-snug text-foreground transition-colors group-hover:text-primary">
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
                              className="bg-surface text-[10px] font-normal text-muted-foreground border-border/50"
                            >
                              <Hash className="mr-0.5 h-2.5 w-2.5 opacity-60" />
                              {tag.replace(/^#/, "")}
                            </Badge>
                          ))}
                      </div>
                    )}

                    {/* Summary Preview */}
                    {item.summary && (
                      <p className="line-clamp-2 text-xs leading-relaxed text-muted-foreground">
                        {item.summary}
                      </p>
                    )}
                  </div>

                  {/* Action Link to Detail */}
                  <div className="mt-5 border-t border-border/50 pt-4">
                    <Link
                      href={`/dashboard/videos/${item.id}`}
                      className="inline-flex w-full items-center justify-between rounded-lg bg-surface/80 px-3.5 py-2 text-xs font-semibold text-foreground transition-colors hover:bg-primary hover:text-primary-foreground"
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
