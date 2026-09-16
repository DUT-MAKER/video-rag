"use client";

import * as React from "react";
import {
  CheckCircle2,
  FileVideo,
  Sparkles,
  Users,
  Clock,
  UploadCloud,
  FileText,
  Hash,
  Globe,
  Loader2,
  X,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ingestVideoFile } from "@/lib/api";
import type { VideoFileIngestionResponseData } from "@/lib/types";

export function IngestHub() {
  // Single Video Upload State
  const [selectedFile, setSelectedFile] = React.useState<File | null>(null);
  const [caption, setCaption] = React.useState("");
  const [hashtag, setHashtag] = React.useState("");
  const [language, setLanguage] = React.useState("vi");

  const [isDragging, setIsDragging] = React.useState(false);
  const [isVideoLoading, setIsVideoLoading] = React.useState(false);
  const [videoResult, setVideoResult] =
    React.useState<VideoFileIngestionResponseData | null>(null);
  const [videoError, setVideoError] = React.useState<string | null>(null);

  const fileInputRef = React.useRef<HTMLInputElement>(null);

  // Handle Drag & Drop
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      setSelectedFile(file);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFile(e.target.files[0]);
    }
  };

  // Handle Video Ingestion
  const handleSingleVideoIngest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      setVideoError("Vui lòng chọn 1 tệp tin video hoặc audio.");
      return;
    }

    setIsVideoLoading(true);
    setVideoError(null);
    setVideoResult(null);

    try {
      const data = await ingestVideoFile({
        file: selectedFile,
        caption: caption.trim() || undefined,
        hashtag: hashtag.trim() || undefined,
        language: language.trim() || "vi",
      });
      setVideoResult(data);
    } catch (err: unknown) {
      console.error("Video ingestion failed:", err);
      const msg =
        err instanceof Error
          ? err.message
          : "Nạp video thất bại. Hãy kiểm tra kết nối API backend.";
      setVideoError(msg);
    } finally {
      setIsVideoLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-5xl space-y-8 p-6 text-white">
      {/* Page Header */}
      <div className="space-y-1.5 border-b border-[#2e3352] pb-5">
        <div className="flex items-center gap-2">
          <Badge variant="ai">AI Ingestion Pipeline</Badge>
          <span className="font-mono text-[11px] font-bold uppercase tracking-widest text-zinc-400">
            WhisperX • Pyannote Diarization • pgvector
          </span>
        </div>
        <h1 className="text-2xl font-bold tracking-tight text-white md:text-3xl">
          Video Ingestion
        </h1>
        <p className="max-w-2xl text-xs leading-relaxed text-zinc-300">
          Upload 1 video/audio để trích xuất tự động: BentoML WhisperX STT,
          nhận diện người nói (Speaker Diarization), tạo thumbnail và vector hóa vào PostgreSQL pgvector.
        </p>
      </div>

      {/* Infrastructure Status Cards */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <Card className="space-y-2 border-[#2e3352] bg-[#141418] p-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-zinc-300">Vector Store</span>
            <Badge variant="success">Active</Badge>
          </div>
          <p className="text-sm font-bold text-white">PostgreSQL + pgvector</p>
          <p className="font-mono text-xs text-zinc-400">
            Table: viral_video_embeddings
          </p>
        </Card>

        <Card className="space-y-2 border-[#2e3352] bg-[#141418] p-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-zinc-300">STT & Diarization</span>
            <Badge variant="ai">BentoML WhisperX</Badge>
          </div>
          <p className="text-sm font-bold text-white">large-v3-turbo + Pyannote</p>
          <p className="font-mono text-xs text-zinc-400">Port 3001 • CUDA GPU</p>
        </Card>

        <Card className="space-y-2 border-[#2e3352] bg-[#141418] p-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-zinc-300">Embedding Engine</span>
            <Badge variant="success">BAAI/bge-m3</Badge>
          </div>
          <p className="text-sm font-bold text-white">Dense Vector Embeddings</p>
          <p className="font-mono text-xs text-zinc-400">Dimension: 1024 / HNSW</p>
        </Card>
      </div>

      {/* SINGLE VIDEO UPLOAD FORM */}
      <Card className="border-[#2e3352] bg-[#141418]">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base text-white">
            <UploadCloud className="h-4 w-4 text-[#9184d9]" />
            <span>Upload Tệp Tin Video / Audio</span>
          </CardTitle>
          <CardDescription>
            Kéo thả hoặc duyệt file video từ máy tính của bạn để kích hoạt Use Case{" "}
            <code className="rounded bg-black/40 px-1.5 py-0.5 font-mono text-[11px] text-[#c5bdf0]">
              IngestVideoDataUseCase
            </code>
            .
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSingleVideoIngest} className="space-y-4">
            {/* File Dropzone */}
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`group relative flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed p-6 transition-all ${
                isDragging
                  ? "border-[#9184d9] bg-[#9184d9]/10"
                  : selectedFile
                  ? "border-emerald-500/50 bg-emerald-500/5"
                  : "border-[#2e3352] bg-[#161826]/60 hover:border-[#9184d9]/50 hover:bg-[#161826]"
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="video/*,audio/*,.mp4,.mkv,.mov,.webm,.mp3,.wav,.m4a"
                onChange={handleFileChange}
                className="hidden"
              />

              {selectedFile ? (
                <div className="flex w-full items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="rounded-lg bg-emerald-500/20 p-2.5 text-emerald-300">
                      <FileVideo className="h-6 w-6" />
                    </div>
                    <div>
                      <p className="font-semibold text-sm text-white">
                        {selectedFile.name}
                      </p>
                      <p className="text-xs text-zinc-400">
                        {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB •{" "}
                        {selectedFile.type || "video/audio file"}
                      </p>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedFile(null);
                      if (fileInputRef.current) fileInputRef.current.value = "";
                    }}
                    className="rounded-lg p-1.5 text-zinc-400 hover:bg-zinc-800 hover:text-white cursor-pointer"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              ) : (
                <div className="text-center">
                  <div className="mx-auto mb-2 flex h-11 w-11 items-center justify-center rounded-full bg-[#9184d9]/15 text-[#9184d9]">
                    <UploadCloud className="h-5 w-5" />
                  </div>
                  <p className="text-xs font-semibold text-white">
                    Kéo thả video vào đây hoặc{" "}
                    <span className="text-[#9184d9] underline underline-offset-2">
                      chọn từ máy tính
                    </span>
                  </p>
                  <p className="mt-1 text-[11px] text-zinc-400">
                    MP4, MKV, MOV, WebM, MP3, WAV...
                  </p>
                </div>
              )}
            </div>

            {/* Inputs: Caption, Hashtag, Language */}
            <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
              {/* Caption */}
              <div className="space-y-1.5">
                <label className="flex items-center gap-1.5 text-xs font-bold text-zinc-200">
                  <FileText className="h-3.5 w-3.5 text-zinc-400" />
                  <span>Caption (tuỳ chọn)</span>
                </label>
                <input
                  type="text"
                  value={caption}
                  onChange={(e) => setCaption(e.target.value)}
                  placeholder="Nhập caption nếu có..."
                  className="h-9 w-full rounded-lg border border-[#2e3352] bg-[#161826] px-3 text-xs text-white outline-none transition focus:border-[#9184d9]"
                />
              </div>

              {/* Hashtag */}
              <div className="space-y-1.5">
                <label className="flex items-center gap-1.5 text-xs font-bold text-zinc-200">
                  <Hash className="h-3.5 w-3.5 text-zinc-400" />
                  <span>Hashtags (tuỳ chọn)</span>
                </label>
                <input
                  type="text"
                  value={hashtag}
                  onChange={(e) => setHashtag(e.target.value)}
                  placeholder="#review #trend..."
                  className="h-9 w-full rounded-lg border border-[#2e3352] bg-[#161826] px-3 text-xs text-white outline-none transition focus:border-[#9184d9]"
                />
              </div>

              {/* Language */}
              <div className="space-y-1.5">
                <label className="flex items-center gap-1.5 text-xs font-bold text-zinc-200">
                  <Globe className="h-3.5 w-3.5 text-zinc-400" />
                  <span>Ngôn ngữ STT</span>
                </label>
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="h-9 w-full rounded-lg border border-[#2e3352] bg-[#161826] px-3 text-xs text-white outline-none transition focus:border-[#9184d9]"
                >
                  <option value="vi">Tiếng Việt (vi)</option>
                  <option value="en">English (en)</option>
                  <option value="auto">Tự động phát hiện (Auto)</option>
                </select>
              </div>
            </div>

            {/* Error message */}
            {videoError && (
              <div className="rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-xs text-red-300">
                {videoError}
              </div>
            )}

            {/* Submit button */}
            <div className="pt-2">
              <Button
                type="submit"
                disabled={isVideoLoading || !selectedFile}
                className="h-10 px-6 font-semibold"
              >
                {isVideoLoading ? (
                  <span className="flex items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin text-white" />
                    <span>Đang upload, nhận diện giọng nói & vector hóa...</span>
                  </span>
                ) : (
                  <span className="flex items-center gap-2">
                    <Sparkles className="h-4 w-4" />
                    <span>Upload & Bắt Đầu Ingest Video</span>
                  </span>
                )}
              </Button>
            </div>
          </form>

          {/* Ingestion Results */}
          {videoResult && (
            <div className="mt-6 animate-in fade-in space-y-4 rounded-xl border border-emerald-400/30 bg-emerald-500/5 p-5 duration-200">
              <div className="flex items-center justify-between border-b border-emerald-400/20 pb-3">
                <div className="flex items-center space-x-2 text-emerald-300">
                  <CheckCircle2 className="h-4 w-4" />
                  <span className="text-sm font-bold">
                    Video Đã Được Ingest & Vector Hóa Thành Công!
                  </span>
                </div>
                <Badge variant="success">Indexed in pgvector</Badge>
              </div>

              {/* Summary Metric Badges */}
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                <div className="rounded-lg border border-[#2e3352] bg-black/60 p-3">
                  <div className="flex items-center gap-1 text-[10px] font-bold uppercase text-zinc-400">
                    <Users className="h-3 w-3 text-purple-300" />
                    <span>Số người nói</span>
                  </div>
                  <p className="mt-1 text-base font-bold text-purple-300">
                    {videoResult.speaker_count} speaker(s)
                  </p>
                </div>

                <div className="rounded-lg border border-[#2e3352] bg-black/60 p-3">
                  <div className="flex items-center gap-1 text-[10px] font-bold uppercase text-zinc-400">
                    <Clock className="h-3 w-3 text-cyan-300" />
                    <span>Thời lượng</span>
                  </div>
                  <p className="mt-1 text-base font-bold text-cyan-300">
                    {videoResult.duration_seconds > 0
                      ? `${videoResult.duration_seconds.toFixed(1)}s`
                      : "Auto"}
                  </p>
                </div>

                <div className="rounded-lg border border-[#2e3352] bg-black/60 p-3">
                  <span className="text-[10px] font-bold uppercase text-zinc-400">
                    Vector Indexed
                  </span>
                  <p className="mt-1 text-base font-bold text-emerald-300">
                    {videoResult.total_indexed} record
                  </p>
                </div>

                <div className="rounded-lg border border-[#2e3352] bg-black/60 p-3">
                  <span className="text-[10px] font-bold uppercase text-zinc-400">
                    Hashtags
                  </span>
                  <p className="mt-1 truncate text-xs font-semibold text-zinc-200">
                    {videoResult.hashtag || "(Trống)"}
                  </p>
                </div>
              </div>

              {/* Caption & Summary */}
              {videoResult.caption && (
                <div className="space-y-1">
                  <span className="text-xs font-bold text-zinc-300">
                    Caption:
                  </span>
                  <p className="text-xs text-white bg-black/40 p-2.5 rounded-lg border border-[#2e3352]">
                    {videoResult.caption}
                  </p>
                </div>
              )}

              {videoResult.summary && (
                <div className="space-y-1">
                  <span className="text-xs font-bold text-zinc-300">
                    Tóm tắt nội dung (LLM Summary):
                  </span>
                  <p className="text-xs text-zinc-300 bg-black/40 p-2.5 rounded-lg border border-[#2e3352]">
                    {videoResult.summary}
                  </p>
                </div>
              )}

              {/* Diarized Transcript Segments */}
              {videoResult.transcript_segments &&
                videoResult.transcript_segments.length > 0 && (
                  <div className="space-y-2 pt-2 border-t border-[#2e3352]">
                    <span className="text-xs font-bold text-white flex items-center gap-1.5">
                      <Users className="h-3.5 w-3.5 text-[#9184d9]" />
                      <span>Hội thoại phân chia theo người nói (Diarization):</span>
                    </span>
                    <div className="max-h-60 overflow-y-auto space-y-1.5 rounded-lg border border-[#2e3352] bg-black/40 p-3 text-xs">
                      {videoResult.transcript_segments.map((seg, idx) => (
                        <div
                          key={idx}
                          className="flex items-start gap-2 border-b border-zinc-800/60 pb-1.5 last:border-0"
                        >
                          <span className="rounded bg-[#9184d9]/20 px-1.5 py-0.5 font-mono text-[10px] font-semibold text-[#c5bdf0] shrink-0">
                            {seg.speaker || "SPEAKER"}
                          </span>
                          <span className="font-mono text-[10px] text-zinc-400 shrink-0">
                            [{seg.start.toFixed(1)}s - {seg.end.toFixed(1)}s]
                          </span>
                          <span className="text-zinc-200">{seg.text}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

              {/* Fallback Preview */}
              {(!videoResult.transcript_segments ||
                videoResult.transcript_segments.length === 0) &&
                (videoResult.transcript_with_speakers ||
                  videoResult.transcript) && (
                  <div className="space-y-1 pt-2 border-t border-[#2e3352]">
                    <span className="text-xs font-bold text-white">
                      Nội dung Transcript:
                    </span>
                    <p className="font-mono text-xs text-zinc-300 bg-black/40 p-3 rounded-lg border border-[#2e3352] whitespace-pre-wrap max-h-48 overflow-y-auto">
                      {videoResult.transcript_with_speakers ||
                        videoResult.transcript}
                    </p>
                  </div>
                )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
