"use client";

import * as React from "react";
import {
  Send,
  Sparkles,
  Zap,
  PenTool,
  Scissors,
  Camera,
  Layers,
  Bot,
  User,
  Link as LinkIcon,
  ExternalLink,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import type { ChatMessage } from "@/lib/types";

interface ChatFeedProps {
  messages: ChatMessage[];
  isLoading: boolean;
  onSendMessage: (message: string, topK: number) => void;
  onSelectQuickPrompt: (prompt: string) => void;
}

export function ChatFeed({
  messages,
  isLoading,
  onSendMessage,
  onSelectQuickPrompt,
}: ChatFeedProps) {
  const [input, setInput] = React.useState("");
  const [topK, setTopK] = React.useState(3);
  const scrollRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSubmit = () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;
    onSendMessage(trimmed, topK);
    setInput("");
  };

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-[#09090b] relative">
      {/* Messages Scroll Area */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto px-4 py-6 md:px-8 space-y-6 max-w-4xl w-full mx-auto"
      >
        {messages.length === 0 ? (
          /* Empty State Hero */
          <div className="flex flex-col items-center justify-center min-h-[65vh] text-center space-y-6">
            <div className="w-14 h-14 rounded-2xl border border-neutral-800 bg-[#121215] flex items-center justify-center shadow-lg">
              <Sparkles className="w-6 h-6 text-neutral-200" />
            </div>

            <div className="space-y-2 max-w-md">
              <h1 className="text-xl md:text-2xl font-semibold tracking-tight text-white">
                Viral Video AI Co-Pilot
              </h1>
              <p className="text-xs text-neutral-400 leading-relaxed">
                Đồng hành sáng tạo kịch bản video ngắn (TikTok, Reels, Shorts) dựa trên các pattern giữ chân người xem triệu view từ kho dữ liệu RAG.
              </p>
            </div>

            {/* 4 Quick Prompt Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 w-full max-w-xl text-left pt-2">
              <button
                type="button"
                onClick={() =>
                  onSelectQuickPrompt(
                    "Gợi ý 3 hook mở đầu giật gân cho video về thói quen kỷ luật trong 21 ngày"
                  )
                }
                className="p-3.5 rounded-xl border border-neutral-800 bg-[#121215] hover:border-neutral-700 hover:bg-[#16161a] transition-all text-left space-y-1.5 cursor-pointer"
              >
                <div className="flex items-center space-x-2 text-orange-400">
                  <Zap className="w-3.5 h-3.5" />
                  <span className="text-xs font-semibold">Brainstorm Hooks 3s</span>
                </div>
                <p className="text-[11px] text-neutral-400">
                  3 high-CTR hooks cho video thói quen kỷ luật 21 ngày
                </p>
              </button>

              <button
                type="button"
                onClick={() =>
                  onSelectQuickPrompt(
                    "Viết kịch bản 45s TikTok chi tiết về quản lý tài chính cá nhân cho Gen Z"
                  )
                }
                className="p-3.5 rounded-xl border border-neutral-800 bg-[#121215] hover:border-neutral-700 hover:bg-[#16161a] transition-all text-left space-y-1.5 cursor-pointer"
              >
                <div className="flex items-center space-x-2 text-neutral-200">
                  <PenTool className="w-3.5 h-3.5" />
                  <span className="text-xs font-semibold">Draft Full Script</span>
                </div>
                <p className="text-[11px] text-neutral-400">
                  Kịch bản 45s TikTok quản lý tài chính Gen Z
                </p>
              </button>

              <button
                type="button"
                onClick={() =>
                  onSelectQuickPrompt(
                    "Chỉnh sửa phân cảnh 2 để tăng kịch tính và giữ chân người xem sau 5 giây đầu"
                  )
                }
                className="p-3.5 rounded-xl border border-neutral-800 bg-[#121215] hover:border-neutral-700 hover:bg-[#16161a] transition-all text-left space-y-1.5 cursor-pointer"
              >
                <div className="flex items-center space-x-2 text-purple-400">
                  <Scissors className="w-3.5 h-3.5" />
                  <span className="text-xs font-semibold">Refine Scene Pacing</span>
                </div>
                <p className="text-[11px] text-neutral-400">
                  Tăng nhịp điệu phân cảnh 2 để chống drop-off người xem
                </p>
              </button>

              <button
                type="button"
                onClick={() =>
                  onSelectQuickPrompt(
                    "Xuất toàn bộ prompt Midjourney / Flux và gợi ý góc quay camera cho từng cảnh"
                  )
                }
                className="p-3.5 rounded-xl border border-neutral-800 bg-[#121215] hover:border-neutral-700 hover:bg-[#16161a] transition-all text-left space-y-1.5 cursor-pointer"
              >
                <div className="flex items-center space-x-2 text-emerald-400">
                  <Camera className="w-3.5 h-3.5" />
                  <span className="text-xs font-semibold">Export AI Prompts</span>
                </div>
                <p className="text-[11px] text-neutral-400">
                  Xuất prompt hình ảnh Flux/Midjourney cho từng phân cảnh
                </p>
              </button>
            </div>
          </div>
        ) : (
          /* Message List */
          <div className="space-y-6 pb-4">
            {messages.map((msg, index) => {
              const isUser = msg.role === "user";
              return (
                <div
                  key={index}
                  className={`flex gap-3.5 ${
                    isUser ? "justify-end" : "justify-start"
                  }`}
                >
                  {!isUser && (
                    <div className="w-7 h-7 rounded-lg border border-neutral-800 bg-[#121215] flex items-center justify-center shrink-0 mt-0.5">
                      <Bot className="w-4 h-4 text-neutral-300" />
                    </div>
                  )}

                  <div
                    className={`max-w-2xl rounded-xl text-xs leading-relaxed space-y-2.5 ${
                      isUser
                        ? "bg-white text-neutral-950 p-3.5 font-medium ml-12 shadow-sm"
                        : "bg-[#121215] border border-neutral-800 text-neutral-200 p-4 mr-12"
                    }`}
                  >
                    {/* Message content */}
                    <div className="whitespace-pre-wrap">{msg.content}</div>

                    {/* Referenced Patterns (if any) */}
                    {msg.referenced_patterns && msg.referenced_patterns.length > 0 && (
                      <div className="pt-2 border-t border-neutral-800/80 space-y-2">
                        <div className="flex items-center space-x-1.5 text-[11px] text-neutral-400 font-semibold uppercase tracking-wider">
                          <LinkIcon className="w-3 h-3 text-purple-400" />
                          <span>Mô hình đối sánh (Benchmark RAG)</span>
                        </div>

                        <div className="grid grid-cols-1 gap-2">
                          {msg.referenced_patterns.map((ref, rIdx) => (
                            <div
                              key={rIdx}
                              className="p-2.5 rounded-lg border border-neutral-800 bg-neutral-900/60 text-[11px] space-y-1"
                            >
                              <div className="flex items-center justify-between">
                                <span className="font-semibold text-neutral-200">
                                  Hook mẫu: &ldquo;{ref.matched_hook}&rdquo;
                                </span>
                                <Badge variant="mono">
                                  {(ref.similarity_score * 100).toFixed(0)}% Match
                                </Badge>
                              </div>
                              <p className="text-neutral-400 line-clamp-2">
                                {ref.summary || ref.original_caption}
                              </p>
                              {ref.minio_video_url && (
                                <a
                                  href={ref.minio_video_url}
                                  target="_blank"
                                  rel="noreferrer"
                                  className="inline-flex items-center space-x-1 text-[10px] text-neutral-400 hover:text-white pt-1"
                                >
                                  <span>Xem video MinIO gốc</span>
                                  <ExternalLink className="w-2.5 h-2.5" />
                                </a>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {isUser && (
                    <div className="w-7 h-7 rounded-lg border border-neutral-800 bg-neutral-800 flex items-center justify-center shrink-0 mt-0.5">
                      <User className="w-4 h-4 text-neutral-300" />
                    </div>
                  )}
                </div>
              );
            })}

            {/* Thinking Indicator */}
            {isLoading && (
              <div className="flex gap-3.5 justify-start">
                <div className="w-7 h-7 rounded-lg border border-neutral-800 bg-[#121215] flex items-center justify-center shrink-0">
                  <Bot className="w-4 h-4 text-neutral-300 animate-pulse" />
                </div>
                <div className="p-3.5 rounded-xl border border-neutral-800 bg-[#121215] text-xs text-neutral-400 flex items-center space-x-2">
                  <span className="w-2 h-2 rounded-full bg-purple-400 animate-ping" />
                  <span>ViralCopilot đang truy xuất pgvector & phân tích kịch bản...</span>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Sticky Input Dock */}
      <div className="border-t border-neutral-800 bg-[#0c0c0e]/95 backdrop-blur-md p-3 md:p-4 shrink-0">
        <div className="max-w-4xl mx-auto space-y-2">
          <div className="rounded-xl border border-neutral-800 bg-[#121215] p-2.5 focus-within:border-neutral-600 transition-all shadow-lg">
            <textarea
              rows={2}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Hỏi ViralCopilot: gợi ý hook, viết kịch bản 45s, hoặc tinh chỉnh phân cảnh..."
              className="w-full bg-transparent text-xs text-neutral-100 placeholder-neutral-500 resize-none outline-none px-2 py-1 leading-relaxed max-h-36"
            />

            <div className="flex items-center justify-between pt-2 border-t border-neutral-800/80 text-xs text-neutral-400">
              <div className="flex items-center space-x-2">
                <div className="flex items-center space-x-1.5 px-2 py-1 rounded-md bg-neutral-900 border border-neutral-800">
                  <Layers className="w-3 h-3 text-neutral-400" />
                  <span className="text-[11px]">RAG Patterns:</span>
                  <select
                    value={topK}
                    onChange={(e) => setTopK(Number(e.target.value))}
                    className="bg-transparent text-neutral-200 text-[11px] outline-none cursor-pointer"
                  >
                    <option value={1} className="bg-neutral-900">Top 1</option>
                    <option value={3} className="bg-neutral-900">Top 3</option>
                    <option value={5} className="bg-neutral-900">Top 5</option>
                  </select>
                </div>
                <span className="text-[10px] text-neutral-500 hidden sm:inline">
                  Shift+Enter xuống dòng
                </span>
              </div>

              <div className="flex items-center space-x-2">
                <Button
                  size="sm"
                  onClick={handleSubmit}
                  disabled={!input.trim() || isLoading}
                >
                  <span>Gửi</span>
                  <Send className="w-3.5 h-3.5" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
