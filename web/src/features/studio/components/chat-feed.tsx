"use client";

import * as React from "react";
import { Send, ExternalLink, Sparkles, MessageSquare } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { MarkdownRenderer } from "@/components/ui/markdown-renderer";
import type { ChatMessage } from "@/lib/types";

interface ChatFeedProps {
  messages: ChatMessage[];
  isLoading: boolean;
  onSendMessage: (message: string, topK: number) => void;
  onSelectQuickPrompt: (prompt: string) => void;
}

const QUICK_PROMPTS = [
  {
    tag: "Hook 3s",
    title: "Brainstorm Hooks 3s",
    description: "3 high-CTR hooks cho video thói quen kỷ luật 21 ngày",
    prompt:
      "Gợi ý 3 hook mở đầu giật gân cho video về thói quen kỷ luật trong 21 ngày",
  },
  {
    tag: "Kịch bản",
    title: "Draft Full Script 45s",
    description: "Kịch bản 45s TikTok quản lý tài chính Gen Z",
    prompt:
      "Viết kịch bản 45s TikTok chi tiết về quản lý tài chính cá nhân cho Gen Z",
  },
  {
    tag: "Nhịp điệu",
    title: "Tối ưu phân cảnh",
    description: "Tăng nhịp điệu phân cảnh 2 để chống drop-off người xem",
    prompt:
      "Chỉnh sửa phân cảnh 2 để tăng kịch tính và giữ chân người xem sau 5 giây đầu",
  },
  {
    tag: "Visual",
    title: "Xuất AI Prompts",
    description: "Xuất prompt hình ảnh Flux/Midjourney cho từng phân cảnh",
    prompt:
      "Xuất toàn bộ prompt Midjourney / Flux và gợi ý góc quay camera cho từng cảnh",
  },
];

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
    <div className="relative flex h-full flex-1 flex-col overflow-hidden bg-[#fffcfb]">
      {/* Messages Scroll Area */}
      <div
        ref={scrollRef}
        className="mx-auto w-full max-w-4xl flex-1 space-y-6 overflow-y-auto px-4 py-6 md:px-8"
      >
        {messages.length === 0 ? (
          /* Empty State Hero */
          <div className="flex min-h-[60vh] flex-col items-center justify-center space-y-6 text-center">
            <div className="max-w-lg space-y-3">
              <div className="inline-flex items-center gap-2 rounded-full border border-[#ffe0d5] bg-[#fff0eb] px-3.5 py-1 text-xs font-black uppercase tracking-wider text-[#ff7442]">
                <Sparkles className="h-3.5 w-3.5 fill-[#ff7442]" />
                <span>Markee Creative Desk</span>
              </div>
              <h1 className="text-3xl font-black tracking-tight text-[#0f172a] [font-family:var(--font-heading)] md:text-4xl">
                Viral Video AI Co-Pilot
              </h1>
              <p className="mx-auto max-w-md text-xs font-medium leading-relaxed text-[#667085]">
                Đồng hành sáng tạo kịch bản video ngắn (TikTok, Reels, Shorts) dựa trên các pattern giữ chân triệu view được đối sánh qua pgvector & MinIO.
              </p>
            </div>

            {/* 4 Clean Quick Prompt Cards in Markee Style */}
            <div className="grid w-full max-w-xl grid-cols-1 gap-3.5 pt-2 text-left sm:grid-cols-2">
              {QUICK_PROMPTS.map((item) => (
                <button
                  key={item.tag}
                  type="button"
                  onClick={() => onSelectQuickPrompt(item.prompt)}
                  className="group cursor-pointer space-y-2 rounded-[20px] border border-[#f1f5f9] bg-white p-4 text-left shadow-[0_8px_20px_rgba(0,0,0,0.03)] transition-all hover:-translate-y-0.5 hover:border-[#ffe0d5] hover:shadow-[0_12px_28px_rgba(255,116,66,0.08)]"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-extrabold text-[#0f172a] [font-family:var(--font-heading)]">
                      {item.title}
                    </span>
                    <span className="rounded-full border border-[#ffe0d5] bg-[#fff0eb] px-2 py-0.5 text-[10px] font-black text-[#ff7442]">
                      {item.tag}
                    </span>
                  </div>
                  <p className="text-[11px] font-medium leading-relaxed text-[#667085]">
                    {item.description}
                  </p>
                </button>
              ))}
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
                  className={`flex flex-col space-y-1.5 ${
                    isUser ? "items-end" : "items-start"
                  }`}
                >
                  {/* Sender Label */}
                  <span className="px-2 font-mono text-[10px] font-bold uppercase tracking-wider text-[#94a3b8]">
                    {isUser ? "Bạn" : "ViralCopilot AI"}
                  </span>

                  <div
                    className={`max-w-2xl space-y-3 rounded-[24px] text-xs leading-relaxed ${
                      isUser
                        ? "bg-[linear-gradient(90deg,#ff7442,#ff8c64)] p-4 font-bold text-white shadow-[0_8px_20px_rgba(255,116,66,0.2)]"
                        : "border border-[#f1f5f9] bg-white p-5 text-[#0f172a] shadow-[0_12px_28px_rgba(15,23,42,0.04)]"
                    }`}
                  >
                    {/* Message content */}
                    {isUser ? (
                      <div className="whitespace-pre-wrap text-sm font-semibold">{msg.content}</div>
                    ) : !msg.content ? (
                      <div className="flex items-center space-x-2.5 py-1 text-xs font-bold text-[#ff7442]">
                        <span className="h-2 w-2 animate-ping rounded-full bg-[#ff7442]" />
                        <span>Đang phân tích và khởi tạo câu trả lời...</span>
                      </div>
                    ) : (
                      <div className="relative">
                        <MarkdownRenderer content={msg.content} />
                        {isLoading && index === messages.length - 1 && (
                          <span className="ml-1 inline-block h-3.5 w-1.5 animate-pulse rounded-xs bg-[#ff7442] align-middle" />
                        )}
                      </div>
                    )}

                    {/* Referenced Patterns */}
                    {msg.referenced_patterns &&
                      msg.referenced_patterns.length > 0 && (
                        <div className="space-y-2.5 border-t border-[#f1f5f9] pt-3">
                          <div className="text-[11px] font-black uppercase tracking-wider text-[#6a4f44]">
                            Video Tham Khảo ({msg.referenced_patterns.length})
                          </div>

                          <div className="grid grid-cols-1 gap-2.5">
                            {msg.referenced_patterns.map((ref, rIdx) => (
                              <div
                                key={rIdx}
                                className="space-y-1.5 rounded-[18px] border border-[#ffe0d5] bg-[#fffbf9] p-3.5 text-[11px]"
                              >
                                <div className="flex items-center justify-between">
                                  <span className="font-extrabold text-[#0f172a]">
                                    Hook mẫu: &ldquo;{ref.matched_hook}&rdquo;
                                  </span>
                                  <Badge variant="accent">
                                    {(ref.similarity_score * 100).toFixed(0)}% Match
                                  </Badge>
                                </div>
                                <p className="leading-relaxed text-[#667085]">
                                  {ref.summary || ref.original_caption}
                                </p>
                                {ref.minio_video_url && (
                                  <a
                                    href={ref.minio_video_url}
                                    target="_blank"
                                    rel="noreferrer"
                                    className="inline-flex items-center space-x-1 pt-0.5 text-[11px] font-bold text-[#ff7442] underline underline-offset-2 hover:text-[#e6521e]"
                                  >
                                    <span>Xem video đối sánh gốc</span>
                                    <ExternalLink className="h-3 w-3" />
                                  </a>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                  </div>
                </div>
              );
            })}

            {/* Thinking Indicator */}
            {isLoading && messages[messages.length - 1]?.role === "user" && (
              <div className="flex flex-col items-start space-y-1.5">
                <span className="px-2 font-mono text-[10px] font-bold uppercase tracking-wider text-[#94a3b8]">
                  ViralCopilot AI
                </span>
                <div className="flex items-center space-x-2.5 rounded-full border border-[#ffe0d5] bg-white px-4 py-2.5 text-xs font-bold text-[#ff7442] shadow-xs">
                  <span className="h-2 w-2 animate-ping rounded-full bg-[#ff7442]" />
                  <span>Đang truy vấn kho pgvector và soạn kịch bản...</span>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Sticky Input Dock */}
      <div className="shrink-0 border-t border-[#ffe6dc] bg-[#fffcfb]/95 p-3.5 backdrop-blur-md md:p-4">
        <div className="mx-auto max-w-4xl space-y-2">
          <div className="rounded-[24px] border border-[#ffe0d5] bg-white p-3.5 shadow-[0_10px_30px_rgba(255,116,66,0.06)] transition-all focus-within:border-[#ff7442] focus-within:ring-4 focus-within:ring-[#ff7442]/10">
            <textarea
              rows={2}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Nhập yêu cầu: gợi ý hook, viết kịch bản 45s, hoặc tinh chỉnh phân cảnh..."
              className="max-h-36 w-full resize-none bg-transparent text-xs font-medium leading-relaxed text-[#0f172a] outline-none placeholder:text-[#94a3b8]"
            />

            <div className="flex items-center justify-between border-t border-[#f1f5f9] pt-2.5 text-xs">
              <div className="flex items-center space-x-3">
                <div className="flex items-center space-x-1.5 rounded-full border border-[#ffe0d5] bg-[#fff0eb] px-3 py-1">
                  <span className="text-[11px] font-bold text-[#6a4f44]">
                    Số video tham khảo:
                  </span>
                  <select
                    value={topK}
                    onChange={(e) => setTopK(Number(e.target.value))}
                    className="cursor-pointer bg-transparent text-[11px] font-black text-[#ff7442] outline-none"
                  >
                    <option value={1}>1</option>
                    <option value={3}>3</option>
                    <option value={5}>5</option>
                  </select>
                </div>
                <span className="hidden font-mono text-[11px] font-medium text-[#94a3b8] sm:inline">
                  Shift+Enter xuống dòng
                </span>
              </div>

              <Button
                size="sm"
                onClick={handleSubmit}
                disabled={!input.trim() || isLoading}
                className="px-5"
              >
                <span>Gửi</span>
                <Send className="ml-1.5 h-3.5 w-3.5" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

