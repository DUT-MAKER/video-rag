"use client";

import * as React from "react";
import { Send, ExternalLink } from "lucide-react";
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
    <div className="bg-background relative flex h-full flex-1 flex-col overflow-hidden">
      {/* Messages Scroll Area */}
      <div
        ref={scrollRef}
        className="mx-auto w-full max-w-4xl flex-1 space-y-6 overflow-y-auto px-4 py-6 md:px-8"
      >
        {messages.length === 0 ? (
          /* Empty State Hero */
          <div className="flex min-h-[65vh] flex-col items-center justify-center space-y-6 text-center">
            <div className="max-w-lg space-y-2">
              <span className="text-muted-foreground font-mono text-[11px] font-semibold uppercase tracking-widest">
                Creative Studio
              </span>
              <h1 className="text-foreground text-2xl font-semibold tracking-tight md:text-3xl">
                Viral Video AI Co-Pilot
              </h1>
              <p className="text-muted-foreground mx-auto max-w-md text-xs leading-relaxed">
                Đồng hành sáng tạo kịch bản video ngắn (TikTok, Reels, Shorts)
                dựa trên các pattern giữ chân người xem triệu view từ kho video
                mẫu.
              </p>
            </div>

            {/* 4 Clean Quick Prompt Cards (No decorative icon clutter) */}
            <div className="grid w-full max-w-xl grid-cols-1 gap-3 pt-2 text-left sm:grid-cols-2">
              {QUICK_PROMPTS.map((item) => (
                <button
                  key={item.tag}
                  type="button"
                  onClick={() => onSelectQuickPrompt(item.prompt)}
                  className="border-border bg-surface hover:border-accent/50 hover:bg-surface-hover group cursor-pointer space-y-1.5 rounded-lg border p-3.5 text-left transition-all"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-foreground text-xs font-semibold">
                      {item.title}
                    </span>
                    <span className="bg-background text-muted-foreground border-border rounded-sm border px-1.5 py-0.5 font-mono text-[10px]">
                      {item.tag}
                    </span>
                  </div>
                  <p className="text-muted-foreground text-[11px] leading-relaxed">
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
                  <span className="text-muted-foreground px-1 font-mono text-[10px] font-semibold uppercase tracking-wider">
                    {isUser ? "Bạn" : "ViralCopilot AI"}
                  </span>

                  <div
                    className={`max-w-2xl space-y-2.5 rounded-lg text-[15px] leading-relaxed ${
                      isUser
                        ? "bg-accent/10 border-accent/30 text-foreground border p-4 font-medium"
                        : "bg-surface border-border text-foreground border p-4"
                    }`}
                  >
                    {/* Message content */}
                    {isUser ? (
                      <div className="whitespace-pre-wrap">{msg.content}</div>
                    ) : !msg.content ? (
                      <div className="text-muted-foreground flex items-center space-x-2.5 py-1 text-xs font-medium">
                        <span className="bg-accent h-2 w-2 animate-ping rounded-full" />
                        <span>Đang phân tích và khởi tạo câu trả lời...</span>
                      </div>
                    ) : (
                      <div className="relative">
                        <MarkdownRenderer content={msg.content} />
                        {isLoading && index === messages.length - 1 && (
                          <span className="bg-accent rounded-xs ml-1 inline-block h-3.5 w-1.5 animate-pulse align-middle" />
                        )}
                      </div>
                    )}

                    {/* Referenced Patterns */}
                    {msg.referenced_patterns &&
                      msg.referenced_patterns.length > 0 && (
                        <div className="border-border space-y-2.5 border-t pt-3">
                          <div className="text-muted-foreground text-[11px] font-semibold uppercase tracking-wider">
                            Video tham khảo
                          </div>

                          <div className="grid grid-cols-1 gap-2">
                            {msg.referenced_patterns.map((ref, rIdx) => (
                              <div
                                key={rIdx}
                                className="border-border bg-background space-y-1.5 rounded-lg border p-3 text-[11px]"
                              >
                                <div className="flex items-center justify-between">
                                  <span className="text-foreground font-semibold">
                                    Hook mẫu: &ldquo;{ref.matched_hook}&rdquo;
                                  </span>
                                  <Badge variant="mono">
                                    {(ref.similarity_score * 100).toFixed(0)}%
                                    Match
                                  </Badge>
                                </div>
                                <p className="text-muted-foreground leading-relaxed">
                                  {ref.summary || ref.original_caption}
                                </p>
                                {ref.minio_video_url && (
                                  <a
                                    href={ref.minio_video_url}
                                    target="_blank"
                                    rel="noreferrer"
                                    className="text-foreground hover:text-accent inline-flex items-center space-x-1 pt-0.5 text-[11px] font-medium underline underline-offset-2"
                                  >
                                    <span>Xem video gốc</span>
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

            {/* Thinking Indicator when waiting for first response turn */}
            {isLoading && messages[messages.length - 1]?.role === "user" && (
              <div className="flex flex-col items-start space-y-1.5">
                <span className="text-muted-foreground px-1 font-mono text-[10px] font-semibold uppercase tracking-wider">
                  ViralCopilot AI
                </span>
                <div className="border-border bg-surface text-foreground flex items-center space-x-2.5 rounded-lg border p-3.5 text-xs font-medium">
                  <span className="bg-accent h-2 w-2 animate-ping rounded-full" />
                  <span>Đang phân tích và soạn kịch bản...</span>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Sticky Input Dock */}
      <div className="border-border bg-background/95 shrink-0 border-t p-3 backdrop-blur-md md:p-4">
        <div className="mx-auto max-w-4xl space-y-2">
          <div className="border-border bg-surface focus-within:border-accent rounded-lg border p-3 transition-all">
            <textarea
              rows={2}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Nhập yêu cầu: gợi ý hook, viết kịch bản 45s, hoặc tinh chỉnh phân cảnh..."
              className="text-foreground placeholder:text-muted-foreground max-h-36 w-full resize-none bg-transparent text-xs font-medium leading-relaxed outline-none"
            />

            <div className="border-border flex items-center justify-between border-t pt-2.5 text-xs">
              <div className="flex items-center space-x-2.5">
                <div className="bg-background border-border text-foreground flex items-center space-x-1.5 rounded-md border px-2.5 py-1">
                  <span className="text-muted-foreground text-[11px] font-medium">
                    Số video tham khảo:
                  </span>
                  <select
                    value={topK}
                    onChange={(e) => setTopK(Number(e.target.value))}
                    className="text-foreground cursor-pointer bg-transparent text-[11px] font-semibold outline-none"
                  >
                    <option value={1} className="bg-background text-foreground">
                      1
                    </option>
                    <option value={3} className="bg-background text-foreground">
                      3
                    </option>
                    <option value={5} className="bg-background text-foreground">
                      5
                    </option>
                  </select>
                </div>
                <span className="text-muted-foreground hidden font-mono text-[11px] sm:inline">
                  Shift+Enter xuống dòng
                </span>
              </div>

              <Button
                size="sm"
                onClick={handleSubmit}
                disabled={!input.trim() || isLoading}
                className="px-4"
              >
                <span>Gửi</span>
                <Send className="ml-1 h-3.5 w-3.5" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
