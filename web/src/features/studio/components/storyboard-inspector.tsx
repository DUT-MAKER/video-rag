"use client";

import * as React from "react";
import { Copy, Check, Download, X } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { ViralScript } from "@/lib/types";

interface StoryboardInspectorProps {
  script: ViralScript | null;
  onClose?: () => void;
}

export function StoryboardInspector({
  script,
  onClose,
}: StoryboardInspectorProps) {
  const [copiedKey, setCopiedKey] = React.useState<string | null>(null);

  const copyToClipboard = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const downloadJson = () => {
    if (!script) return;
    const blob = new Blob([JSON.stringify(script, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `viral-script-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const copyFullMarkdown = () => {
    if (!script) return;
    let md = `# ${script.title}\n\n`;
    md += `**Niche:** ${script.target_niche} | **Platform:** ${script.platform} | **Duration:** ${script.target_duration_seconds}s\n\n`;
    md += `## HOOK (3-5s)\n`;
    md += `**Type:** ${script.hook.hook_type}\n`;
    md += `**Script:** "${script.hook.script}"\n`;
    md += `**Visual:** ${script.hook.visual_action}\n`;
    md += `**Retention Rationale:** ${script.hook.retention_rationale}\n\n`;
    md += `## STORYBOARD\n\n`;
    script.scenes.forEach((scene) => {
      md += `### Cảnh ${scene.scene_number} (${scene.time_range})\n`;
      md += `- **Thoại:** ${scene.narration}\n`;
      md += `- **Hình ảnh (B-roll):** ${scene.visual_action}\n`;
      md += `- **Âm thanh SFX:** ${scene.audio_sfx_cue}\n`;
      md += `- **Image Prompt:** \`${scene.image_prompt}\`\n`;
      md += `- **Video Prompt:** \`${scene.video_prompt}\`\n\n`;
    });
    if (script.call_to_action) {
      md += `## CALL TO ACTION\n`;
      md += `- **Lời thoại:** ${script.call_to_action.script}\n`;
      md += `- **Visual:** ${script.call_to_action.visual_cue}\n\n`;
    }
    if (script.suggested_hashtags?.length) {
      md += `**Hashtags:** ${script.suggested_hashtags.map((h) => (h.startsWith("#") ? h : `#${h}`)).join(" ")}\n`;
    }
    copyToClipboard(md, "full_md");
  };

  return (
    <aside className="border-border bg-background text-foreground flex h-full w-96 shrink-0 flex-col overflow-hidden border-l">
      {/* Header */}
      <div className="border-border bg-background flex h-11 shrink-0 select-none items-center justify-between border-b px-4">
        <span className="text-foreground text-xs font-semibold uppercase tracking-wider">
          Script Studio Draft
        </span>
        {onClose && (
          <button
            type="button"
            onClick={onClose}
            className="text-muted-foreground hover:text-foreground hover:bg-surface-hover cursor-pointer rounded-md p-1 transition-colors"
            title="Đóng bảng"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* Content */}
      <div className="flex-1 space-y-4 overflow-y-auto p-4 text-xs">
        {!script ? (
          <div className="text-muted-foreground flex flex-col items-center justify-center space-y-2 py-24 text-center">
            <p className="text-foreground text-xs font-semibold">
              Chưa có kịch bản đang mở
            </p>
            <p className="text-muted-foreground max-w-[220px] text-[11px] leading-relaxed">
              Nhập yêu cầu vào khung chat hoặc dùng tính năng 1-Click Generator
              để tạo kịch bản.
            </p>
          </div>
        ) : (
          <div className="animate-in fade-in space-y-4 duration-200">
            {/* Title & Metadata */}
            <div className="border-border bg-surface space-y-2 rounded-lg border p-3.5">
              <div className="flex items-center justify-between gap-2">
                <Badge variant="mono">{script.platform}</Badge>
                <Badge variant="mono">{script.target_duration_seconds}s</Badge>
              </div>
              <h2 className="text-foreground text-sm font-semibold leading-snug tracking-tight">
                {script.title}
              </h2>
              <p className="text-muted-foreground text-[11px]">
                Chủ đề:{" "}
                <span className="text-foreground font-medium">
                  {script.target_niche}
                </span>
              </p>
            </div>

            {/* 3s Hook Section */}
            {script.hook && (
              <div className="border-accent-hook/40 bg-accent-hook/10 space-y-2.5 rounded-lg border p-3.5">
                <div className="flex items-center justify-between">
                  <span className="text-accent-hook text-xs font-bold uppercase tracking-wider">
                    Hook Giữ Chân 3s
                  </span>
                  <Badge variant="hook">
                    {script.hook.hook_type || "viral_hook"}
                  </Badge>
                </div>

                <div className="space-y-1 pt-0.5">
                  <p className="text-accent-hook/80 text-[10px] font-semibold uppercase tracking-wider">
                    Lời thoại mở đầu
                  </p>
                  <p className="text-foreground bg-background border-border rounded-lg border p-2.5 text-xs font-semibold italic leading-relaxed">
                    &ldquo;{script.hook.script}&rdquo;
                  </p>
                </div>

                <div className="space-y-0.5">
                  <p className="text-accent-hook/80 text-[10px] font-semibold uppercase tracking-wider">
                    Hành động Visual
                  </p>
                  <p className="text-foreground text-[11px] font-medium leading-relaxed">
                    {script.hook.visual_action}
                  </p>
                </div>

                {script.hook.retention_rationale && (
                  <div className="border-accent-hook/20 text-accent-hook border-t pt-2 text-[11px] leading-relaxed">
                    <span className="text-foreground font-bold">
                      Tâm lý giữ chân:
                    </span>{" "}
                    {script.hook.retention_rationale}
                  </div>
                )}
              </div>
            )}

            {/* Storyboard Scenes */}
            <div className="space-y-3">
              <span className="text-muted-foreground block text-[11px] font-bold uppercase tracking-wider">
                Storyboard Phân Cảnh ({script.scenes?.length || 0})
              </span>

              {script.scenes?.map((scene) => (
                <div
                  key={scene.scene_number}
                  className="border-border bg-surface space-y-2.5 rounded-lg border p-3"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-foreground text-xs font-bold">
                      Cảnh {scene.scene_number}
                    </span>
                    <Badge variant="mono">{scene.time_range}</Badge>
                  </div>

                  <div className="space-y-0.5">
                    <span className="text-muted-foreground text-[10px] font-bold uppercase tracking-wider">
                      Lời thoại
                    </span>
                    <p className="text-foreground text-xs font-medium leading-relaxed">
                      {scene.narration}
                    </p>
                  </div>

                  <div className="space-y-0.5">
                    <span className="text-muted-foreground text-[10px] font-bold uppercase tracking-wider">
                      Visual B-Roll
                    </span>
                    <p className="text-foreground text-[11px] leading-relaxed">
                      {scene.visual_action}
                    </p>
                  </div>

                  {scene.audio_sfx_cue && (
                    <div className="text-muted-foreground text-[11px]">
                      <span className="text-foreground font-semibold">
                        SFX:
                      </span>{" "}
                      {scene.audio_sfx_cue}
                    </div>
                  )}

                  {/* Clean AI Prompts Copy Buttons (No Decorative Icons) */}
                  <div className="border-border flex items-center gap-2 border-t pt-2">
                    {scene.image_prompt && (
                      <button
                        type="button"
                        onClick={() =>
                          copyToClipboard(
                            scene.image_prompt,
                            `img_${scene.scene_number}`
                          )
                        }
                        className="bg-background border-border hover:bg-surface-hover text-foreground flex flex-1 cursor-pointer items-center justify-center space-x-1 rounded-md border px-2 py-1 text-[10px] font-medium transition-all"
                        title={scene.image_prompt}
                      >
                        {copiedKey === `img_${scene.scene_number}` ? (
                          <>
                            <Check className="text-accent h-3 w-3" />
                            <span className="text-accent font-semibold">
                              Đã sao chép
                            </span>
                          </>
                        ) : (
                          <span>Copy Image Prompt</span>
                        )}
                      </button>
                    )}

                    {scene.video_prompt && (
                      <button
                        type="button"
                        onClick={() =>
                          copyToClipboard(
                            scene.video_prompt,
                            `vid_${scene.scene_number}`
                          )
                        }
                        className="bg-background border-border hover:bg-surface-hover text-foreground flex flex-1 cursor-pointer items-center justify-center space-x-1 rounded-md border px-2 py-1 text-[10px] font-medium transition-all"
                        title={scene.video_prompt}
                      >
                        {copiedKey === `vid_${scene.scene_number}` ? (
                          <>
                            <Check className="text-accent h-3 w-3" />
                            <span className="text-accent font-semibold">
                              Đã sao chép
                            </span>
                          </>
                        ) : (
                          <span>Copy Video Prompt</span>
                        )}
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Call To Action */}
            {script.call_to_action && (
              <div className="border-border bg-surface space-y-1.5 rounded-lg border p-3">
                <span className="text-foreground block text-xs font-bold uppercase tracking-wider">
                  Call To Action
                </span>
                <p className="text-foreground text-xs font-semibold">
                  &ldquo;{script.call_to_action.script}&rdquo;
                </p>
                <p className="text-muted-foreground text-[11px]">
                  {script.call_to_action.visual_cue}
                </p>
              </div>
            )}

            {/* Suggested Hashtags */}
            {script.suggested_hashtags?.length > 0 && (
              <div className="space-y-1.5 pt-1">
                <span className="text-muted-foreground block text-[10px] font-bold uppercase tracking-wider">
                  Hashtags Gợi Ý
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {script.suggested_hashtags.map((tag, idx) => (
                    <span
                      key={idx}
                      className="bg-surface border-border text-foreground rounded-md border px-2 py-0.5 font-mono text-[10px]"
                    >
                      {tag.startsWith("#") ? tag : `#${tag}`}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Export Action Footer */}
      {script && (
        <div className="border-border bg-background flex shrink-0 items-center space-x-2 border-t p-3">
          <Button
            variant="secondary"
            size="sm"
            className="flex-1"
            onClick={copyFullMarkdown}
          >
            {copiedKey === "full_md" ? (
              <>
                <Check className="text-accent mr-1 h-3.5 w-3.5" />
                <span>Đã sao chép</span>
              </>
            ) : (
              <>
                <Copy className="mr-1 h-3.5 w-3.5" />
                <span>Copy Markdown</span>
              </>
            )}
          </Button>

          <Button
            variant="secondary"
            size="sm"
            onClick={downloadJson}
            title="Tải về JSON"
          >
            <Download className="h-3.5 w-3.5" />
          </Button>
        </div>
      )}
    </aside>
  );
}
