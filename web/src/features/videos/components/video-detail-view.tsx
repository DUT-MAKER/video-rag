"use client";

import * as React from "react";
import Link from "next/link";
import {
  ArrowLeft,
  Clock,
  Users,
  Film,
  Sparkles,
  Hash,
  FileText,
  Volume2,
  Share2,
  Copy,
  Check,
  Quote,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { getVideoDetail, formatMediaUrl } from "@/lib/api";
import type { VideoDetail } from "@/lib/types";

interface VideoDetailViewProps {
  videoId: string;
}

export function VideoDetailView({ videoId }: VideoDetailViewProps) {
  const [detail, setDetail] = React.useState<VideoDetail | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [copied, setCopied] = React.useState(false);

  React.useEffect(() => {
    async function loadData() {
      setIsLoading(true);
      setError(null);
      try {
        const data = await getVideoDetail(videoId);
        setDetail(data);
      } catch (err: any) {
        setError(err.message || "Không thể tải thông tin chi tiết video");
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, [videoId]);

  const handleCopyTranscript = () => {
    if (!detail) return;
    const textToCopy = detail.transcript_with_speakers || detail.transcript;
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (isLoading) {
    return (
      <div className="mx-auto max-w-6xl space-y-6 p-6 md:p-8 animate-pulse">
        <div className="h-8 w-48 rounded bg-surface/80" />
        <div className="h-12 w-3/4 rounded bg-surface/60" />
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-12">
          <div className="lg:col-span-5 space-y-4">
            <div className="aspect-video w-full rounded-xl bg-surface/70" />
            <div className="h-28 w-full rounded-xl bg-surface/50" />
          </div>
          <div className="lg:col-span-7 space-y-4">
            <div className="h-96 w-full rounded-xl bg-surface/60" />
          </div>
        </div>
      </div>
    );
  }

  if (error || !detail) {
    return (
      <div className="mx-auto flex min-h-[500px] max-w-lg flex-col items-center justify-center p-6 text-center">
        <div className="flex h-14 w-14 items-center justify-center rounded-full bg-destructive/10 text-destructive">
          <Film className="h-7 w-7" />
        </div>
        <h2 className="mt-4 text-lg font-bold text-foreground">Không tìm thấy video</h2>
        <p className="mt-1 text-xs text-muted-foreground">
          {error || "Video này có thể đã bị xóa hoặc không tồn tại trong hệ thống."}
        </p>
        <Link href="/dashboard/videos" className="mt-6">
          <Button variant="outline" size="sm" className="gap-2 text-xs">
            <ArrowLeft className="h-4 w-4" />
            Quay lại Danh sách Quản lý
          </Button>
        </Link>
      </div>
    );
  }

  const thumbUrl = formatMediaUrl(detail.image_url);
  const videoMediaUrl = formatMediaUrl(detail.video_url);
  const hashtags = detail.hashtag ? detail.hashtag.split(/[\s,]+/).filter(Boolean) : [];

  // Parse lines of speaker transcript
  const transcriptLines = (detail.transcript_with_speakers || detail.transcript)
    .split("\n")
    .map((l) => l.trim())
    .filter(Boolean);

  return (
    <div className="mx-auto max-w-7xl space-y-8 p-6 md:p-8">
      {/* Top Breadcrumb & Action */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-border/60 pb-5">
        <Link
          href="/dashboard/videos"
          className="inline-flex items-center gap-2 text-xs font-semibold text-muted-foreground transition-colors hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Quay lại Kho Dữ Liệu Video</span>
        </Link>

        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            onClick={handleCopyTranscript}
            className="gap-2 text-xs"
          >
            {copied ? <Check className="h-3.5 w-3.5 text-emerald-500" /> : <Copy className="h-3.5 w-3.5" />}
            {copied ? "Đã sao chép" : "Sao chép Transcript"}
          </Button>

          <Link href={`/dashboard/generator`}>
            <Button size="sm" className="gap-2 text-xs font-semibold">
              <Sparkles className="h-3.5 w-3.5" />
              Tạo Kịch Bản Từ Mẫu Này
            </Button>
          </Link>
        </div>
      </div>

      {/* Main Title & Metadata Badges */}
      <div className="space-y-3">
        <h1 className="text-2xl font-bold tracking-tight text-foreground md:text-3xl lg:leading-snug">
          {detail.caption || "Video Không Có Tiêu Đề"}
        </h1>

        <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
          {detail.duration_seconds > 0 && (
            <div className="flex items-center gap-1.5 rounded-md bg-surface px-2.5 py-1 border border-border">
              <Clock className="h-3.5 w-3.5 text-primary" />
              <span className="font-mono font-medium text-foreground">
                {Math.round(detail.duration_seconds)} giây
              </span>
            </div>
          )}

          <div className="flex items-center gap-1.5 rounded-md bg-surface px-2.5 py-1 border border-border">
            <Users className="h-3.5 w-3.5 text-emerald-500" />
            <span className="font-medium text-foreground">
              {detail.speaker_count} người tham gia hội thoại
            </span>
          </div>

          {hashtags.length > 0 && (
            <div className="flex flex-wrap items-center gap-1.5">
              {hashtags.map((tag, idx) => (
                <Badge
                  key={idx}
                  variant="secondary"
                  className="bg-surface text-[11px] font-normal text-muted-foreground border-border/60"
                >
                  <Hash className="mr-0.5 h-2.5 w-2.5 opacity-60" />
                  {tag.replace(/^#/, "")}
                </Badge>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Two-Column Responsive Layout */}
      <div className="grid grid-cols-1 gap-8 lg:grid-cols-12">
        {/* Left Column: Media Player / Thumbnail & Key Takeaways (5 Cols) */}
        <div className="space-y-6 lg:col-span-5">
          {/* Media Container */}
          <Card className="overflow-hidden border-border/80 bg-zinc-950 shadow-lg">
            <div className="relative aspect-video w-full overflow-hidden bg-black flex items-center justify-center">
              {videoMediaUrl && (videoMediaUrl.endsWith(".mp4") || videoMediaUrl.endsWith(".mov") || videoMediaUrl.endsWith(".webm")) ? (
                <video
                  src={videoMediaUrl}
                  controls
                  poster={thumbUrl}
                  className="h-full w-full object-contain"
                />
              ) : thumbUrl ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={thumbUrl}
                  alt={detail.caption}
                  className="h-full w-full object-cover"
                />
              ) : (
                <div className="flex flex-col items-center justify-center gap-2 text-zinc-600">
                  <Film className="h-10 w-10 stroke-[1.5]" />
                  <span className="text-xs">Không có xem trước media</span>
                </div>
              )}
            </div>
          </Card>

          {/* Hook Candidate Card */}
          {detail.hook_candidate && (
            <Card className="border-border/60 bg-surface/40 p-5 shadow-sm">
              <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-primary">
                <Quote className="h-3.5 w-3.5" />
                <span>Câu Hook Mở Đầu (3-5 Giây Đầu)</span>
              </div>
              <p className="mt-2.5 text-sm font-medium italic leading-relaxed text-foreground/90">
                &ldquo;{detail.hook_candidate}&rdquo;
              </p>
            </Card>
          )}

          {/* AI Summary Card */}
          <Card className="border-border/60 bg-surface/40 p-5 shadow-sm space-y-2.5">
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-foreground">
              <Sparkles className="h-3.5 w-3.5 text-amber-500" />
              <span>Tóm Tắt Ý Chính Từ Video</span>
            </div>
            <p className="text-xs leading-relaxed text-muted-foreground">
              {detail.summary || "Chưa có bản tóm tắt tự động cho video này."}
            </p>
          </Card>
        </div>

        {/* Right Column: Full Dialogue Transcript with Speaker Attribution (7 Cols) */}
        <div className="space-y-6 lg:col-span-7">
          <Card className="border-border/60 bg-surface/40 p-6 shadow-sm flex flex-col h-full">
            <div className="flex items-center justify-between border-b border-border/60 pb-4">
              <div className="flex items-center gap-2">
                <Volume2 className="h-4 w-4 text-primary" />
                <h3 className="text-sm font-semibold text-foreground">
                  Hội Thoại Chi Tiết Phân Theo Giọng Nói (WhisperX Diarization)
                </h3>
              </div>
              <Badge variant="outline" className="text-[10px] font-mono">
                {transcriptLines.length} câu
              </Badge>
            </div>

            {/* Transcript Messages Container */}
            <div className="mt-5 flex-1 space-y-4 max-h-[640px] overflow-y-auto pr-2">
              {transcriptLines.length > 0 ? (
                transcriptLines.map((line, idx) => {
                  // Check if line matches SPEAKER_XX format
                  const speakerMatch = line.match(/^(SPEAKER_\d+)\s*(\[.*?\])?:\s*(.*)$/);
                  if (speakerMatch) {
                    const speakerTag = speakerMatch[1];
                    const timestamp = speakerMatch[2] || "";
                    const speechText = speakerMatch[3];

                    const isSpeaker0 = speakerTag === "SPEAKER_00";

                    return (
                      <div
                        key={idx}
                        className={`flex flex-col gap-1 rounded-xl p-3.5 transition-colors ${
                          isSpeaker0
                            ? "bg-primary/5 border border-primary/10 ml-0 mr-8"
                            : "bg-surface/80 border border-border/60 ml-8 mr-0"
                        }`}
                      >
                        <div className="flex items-center justify-between text-[11px]">
                          <span
                            className={`font-semibold ${
                              isSpeaker0 ? "text-primary" : "text-emerald-400"
                            }`}
                          >
                            {speakerTag}
                          </span>
                          {timestamp && (
                            <span className="font-mono text-[10px] text-muted-foreground">
                              {timestamp}
                            </span>
                          )}
                        </div>
                        <p className="text-xs leading-relaxed text-foreground/95">
                          {speechText}
                        </p>
                      </div>
                    );
                  }

                  // Plain text line
                  return (
                    <div
                      key={idx}
                      className="rounded-lg bg-surface/40 p-3 text-xs leading-relaxed text-foreground/90 border border-border/40"
                    >
                      {line}
                    </div>
                  );
                })
              ) : (
                <div className="flex min-h-[200px] items-center justify-center text-xs text-muted-foreground italic">
                  Không có nội dung bản ghi âm thanh cho video này.
                </div>
              )}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
