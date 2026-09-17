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
    <div className="mx-auto max-w-5xl space-y-8 p-6 text-[#0f172a]">
      {/* Page Header */}
      <div className="space-y-1.5 border-b border-[#ffe6dc] pb-5">
        <div className="flex items-center gap-2">
          <Badge variant="secondary">AI Ingestion Pipeline</Badge>
          <span className="font-mono text-[11px] font-bold uppercase tracking-widest text-[#ea580c]">
            WhisperX • Pyannote Diarization • pgvector
          </span>
        </div>
        <h1 className="text-2xl font-extrabold tracking-tight text-[#0f172a] md:text-3xl font-heading">
          Video Ingestion
        </h1>
        <p className="max-w-2xl text-xs leading-relaxed text-[#667085]">
          Upload 1 video/audio để trích xuất tự động: BentoML WhisperX STT,
          nhận diện người nói (Speaker Diarization), tạo thumbnail và vector hóa vào PostgreSQL pgvector.
        </p>
      </div>

      {/* Infrastructure Status Cards */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <Card className="space-y-2 rounded-[22px] border-[#f1f5f9] bg-white p-5 shadow-xs transition-shadow hover:shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-[#667085]">Vector Store</span>
            <Badge variant="success">Active</Badge>
          </div>
          <p className="text-sm font-bold text-[#0f172a]">PostgreSQL + pgvector</p>
          <p className="font-mono text-xs text-[#94a3b8]">
            Table: viral_video_embeddings
          </p>
        </Card>

        <Card className="space-y-2 rounded-[22px] border-[#f1f5f9] bg-white p-5 shadow-xs transition-shadow hover:shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-[#667085]">STT & Diarization</span>
            <Badge variant="secondary">BentoML WhisperX</Badge>
          </div>
          <p className="text-sm font-bold text-[#0f172a]">large-v3-turbo + Pyannote</p>
          <p className="font-mono text-xs text-[#94a3b8]">Port 3001 • CUDA GPU</p>
        </Card>

        <Card className="space-y-2 rounded-[22px] border-[#f1f5f9] bg-white p-5 shadow-xs transition-shadow hover:shadow-md">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-[#667085]">Embedding Engine</span>
            <Badge variant="success">BAAI/bge-m3</Badge>
          </div>
          <p className="text-sm font-bold text-[#0f172a]">Dense Vector Embeddings</p>
          <p className="font-mono text-xs text-[#94a3b8]">Dimension: 1024 / HNSW</p>
        </Card>
      </div>

      {/* SINGLE VIDEO UPLOAD FORM */}
      <Card className="rounded-[24px] border-[#ffe6dc] bg-[#fffcfb] shadow-xs">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base text-[#0f172a]">
            <UploadCloud className="h-5 w-5 text-[#ff7442]" />
            <span>Upload Tệp Tin Video / Audio</span>
          </CardTitle>
          <CardDescription className="text-[#667085]">
            Kéo thả hoặc duyệt file video từ máy tính của bạn để kích hoạt Use Case{" "}
            <code className="rounded-full bg-[#fff0eb] px-2 py-0.5 font-mono text-[11px] text-[#ea580c] border border-[#ffe0d5]">
              IngestVideoDataUseCase
            </code>
            .
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSingleVideoIngest} className="space-y-5">
            {/* File Dropzone */}
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`group relative flex cursor-pointer flex-col items-center justify-center rounded-[20px] border-2 border-dashed p-8 transition-all ${
                isDragging
                  ? "border-[#ff7442] bg-[#fff0eb]"
                  : selectedFile
                  ? "border-emerald-500/50 bg-emerald-500/5"
                  : "border-[#ffe0d5] bg-white hover:border-[#ff7442] hover:bg-[#fff9f6]"
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
                    <div className="rounded-xl bg-emerald-100 p-2.5 text-emerald-600">
                      <FileVideo className="h-6 w-6" />
                    </div>
                    <div>
                      <p className="font-semibold text-sm text-[#0f172a]">
                        {selectedFile.name}
                      </p>
                      <p className="text-xs text-[#667085]">
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
                    className="rounded-full p-2 text-[#94a3b8] hover:bg-[#fff0eb] hover:text-[#ff7442] cursor-pointer transition-colors"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              ) : (
                <div className="text-center">
                  <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-[#fff0eb] text-[#ff7442]">
                    <UploadCloud className="h-6 w-6" />
                  </div>
                  <p className="text-xs font-semibold text-[#0f172a]">
                    Kéo thả video vào đây hoặc{" "}
                    <span className="text-[#ff7442] underline underline-offset-2">
                      chọn từ máy tính
                    </span>
                  </p>
                  <p className="mt-1 text-[11px] text-[#94a3b8]">
                    MP4, MKV, MOV, WebM, MP3, WAV...
                  </p>
                </div>
              )}
            </div>

            {/* Inputs: Caption, Hashtag, Language */}
            <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
              {/* Caption */}
              <div className="space-y-1.5">
                <label className="flex items-center gap-1.5 text-xs font-bold text-[#0f172a]">
                  <FileText className="h-3.5 w-3.5 text-[#ff7442]" />
                  <span>Caption (tuỳ chọn)</span>
                </label>
                <input
                  type="text"
                  value={caption}
                  onChange={(e) => setCaption(e.target.value)}
                  placeholder="Nhập caption nếu có..."
                  className="h-10 w-full rounded-xl border border-[#ffe0d5] bg-white px-3.5 text-xs text-[#0f172a] placeholder-[#94a3b8] outline-none transition focus:border-[#ff7442] focus:ring-2 focus:ring-[#ff7442]/10"
                />
              </div>

              {/* Hashtag */}
              <div className="space-y-1.5">
                <label className="flex items-center gap-1.5 text-xs font-bold text-[#0f172a]">
                  <Hash className="h-3.5 w-3.5 text-[#ff7442]" />
                  <span>Hashtags (tuỳ chọn)</span>
                </label>
                <input
                  type="text"
                  value={hashtag}
                  onChange={(e) => setHashtag(e.target.value)}
                  placeholder="#review #trend..."
                  className="h-10 w-full rounded-xl border border-[#ffe0d5] bg-white px-3.5 text-xs text-[#0f172a] placeholder-[#94a3b8] outline-none transition focus:border-[#ff7442] focus:ring-2 focus:ring-[#ff7442]/10"
                />
              </div>

              {/* Language */}
              <div className="space-y-1.5">
                <label className="flex items-center gap-1.5 text-xs font-bold text-[#0f172a]">
                  <Globe className="h-3.5 w-3.5 text-[#ff7442]" />
                  <span>Ngôn ngữ STT</span>
                </label>
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="h-10 w-full rounded-xl border border-[#ffe0d5] bg-white px-3.5 text-xs text-[#0f172a] outline-none transition focus:border-[#ff7442] focus:ring-2 focus:ring-[#ff7442]/10"
                >
                  <option value="vi">Tiếng Việt (vi)</option>
                  <option value="en">English (en)</option>
                  <option value="auto">Tự động phát hiện (Auto)</option>
                </select>
              </div>
            </div>

            {/* Error message */}
            {videoError && (
              <div className="rounded-xl border border-red-200 bg-red-50 p-3.5 text-xs text-red-600">
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
            <div className="mt-6 animate-in fade-in space-y-4 rounded-[20px] border border-emerald-200 bg-emerald-50/40 p-5 duration-200">
              <div className="flex items-center justify-between border-b border-emerald-200/60 pb-3">
                <div className="flex items-center space-x-2 text-emerald-800">
                  <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                  <span className="text-sm font-bold">
                    Video Đã Được Ingest & Vector Hóa Thành Công!
                  </span>
                </div>
                <Badge variant="success">Indexed in pgvector</Badge>
              </div>

              {/* Summary Metric Badges */}
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                <div className="rounded-[16px] border border-[#f1f5f9] bg-white p-3.5 shadow-xs">
                  <div className="flex items-center gap-1 text-[10px] font-bold uppercase text-[#667085]">
                    <Users className="h-3 w-3 text-[#ff7442]" />
                    <span>Số người nói</span>
                  </div>
                  <p className="mt-1 text-base font-extrabold text-[#0f172a] font-heading">
                    {videoResult.speaker_count} speaker(s)
                  </p>
                </div>

                <div className="rounded-[16px] border border-[#f1f5f9] bg-white p-3.5 shadow-xs">
                  <div className="flex items-center gap-1 text-[10px] font-bold uppercase text-[#667085]">
                    <Clock className="h-3 w-3 text-cyan-600" />
                    <span>Thời lượng</span>
                  </div>
                  <p className="mt-1 text-base font-extrabold text-[#0f172a] font-heading">
                    {videoResult.duration_seconds > 0
                      ? `${videoResult.duration_seconds.toFixed(1)}s`
                      : "Auto"}
                  </p>
                </div>

                <div className="rounded-[16px] border border-[#f1f5f9] bg-white p-3.5 shadow-xs">
                  <span className="text-[10px] font-bold uppercase text-[#667085]">
                    Vector Indexed
                  </span>
                  <p className="mt-1 text-base font-extrabold text-emerald-600 font-heading">
                    {videoResult.total_indexed} record
                  </p>
                </div>

                <div className="rounded-[16px] border border-[#f1f5f9] bg-white p-3.5 shadow-xs">
                  <span className="text-[10px] font-bold uppercase text-[#667085]">
                    Hashtags
                  </span>
                  <p className="mt-1 truncate text-xs font-semibold text-[#0f172a]">
                    {videoResult.hashtag || "(Trống)"}
                  </p>
                </div>
              </div>

              {/* Caption & Summary */}
              {videoResult.caption && (
                <div className="space-y-1">
                  <span className="text-xs font-bold text-[#475569]">
                    Caption:
                  </span>
                  <p className="text-xs text-[#0f172a] bg-white p-3 rounded-[14px] border border-[#f1f5f9] shadow-xs">
                    {videoResult.caption}
                  </p>
                </div>
              )}

              {videoResult.summary && (
                <div className="space-y-1">
                  <span className="text-xs font-bold text-[#475569]">
                    Tóm tắt nội dung (LLM Summary):
                  </span>
                  <p className="text-xs text-[#475569] bg-white p-3 rounded-[14px] border border-[#f1f5f9] shadow-xs">
                    {videoResult.summary}
                  </p>
                </div>
              )}

              {/* Diarized Transcript Segments */}
              {videoResult.transcript_segments &&
                videoResult.transcript_segments.length > 0 && (
                  <div className="space-y-2 pt-2 border-t border-[#f1f5f9]">
                    <span className="text-xs font-bold text-[#0f172a] flex items-center gap-1.5">
                      <Users className="h-3.5 w-3.5 text-[#ff7442]" />
                      <span>Hội thoại phân chia theo người nói (Diarization):</span>
                    </span>
                    <div className="max-h-60 overflow-y-auto space-y-1.5 rounded-[16px] border border-[#f1f5f9] bg-white p-3.5 text-xs shadow-xs">
                      {videoResult.transcript_segments.map((seg, idx) => (
                        <div
                          key={idx}
                          className="flex items-start gap-2 border-b border-[#f1f5f9] pb-2 last:border-0"
                        >
                          <span className="rounded-full bg-[#fff0eb] border border-[#ffe0d5] px-2 py-0.5 font-mono text-[10px] font-semibold text-[#ff7442] shrink-0">
                            {seg.speaker || "SPEAKER"}
                          </span>
                          <span className="font-mono text-[10px] text-[#94a3b8] shrink-0 pt-0.5">
                            [{seg.start.toFixed(1)}s - {seg.end.toFixed(1)}s]
                          </span>
                          <span className="text-[#0f172a]">{seg.text}</span>
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
                  <div className="space-y-1 pt-2 border-t border-[#f1f5f9]">
                    <span className="text-xs font-bold text-[#0f172a]">
                      Nội dung Transcript:
                    </span>
                    <p className="font-mono text-xs text-[#0f172a] bg-white p-3.5 rounded-[14px] border border-[#f1f5f9] whitespace-pre-wrap max-h-48 overflow-y-auto shadow-xs">
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
