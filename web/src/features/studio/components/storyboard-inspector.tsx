"use client";

import * as React from "react";
import { Copy, Check, Download, X, Film, Sparkles } from "lucide-react";
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
    <aside className="flex h-full w-96 shrink-0 flex-col overflow-hidden border-l border-[#ffe6dc] bg-[#fffcfb] text-[#0f172a]">
      {/* Header */}
      <div className="flex h-14 shrink-0 select-none items-center justify-between border-b border-[#ffe6dc] bg-[#fffcfb] px-5">
        <div className="flex items-center gap-2">
          <Film className="h-4 w-4 text-[#ff7442]" />
          <span className="text-xs font-black uppercase tracking-wider text-[#0f172a] [font-family:var(--font-heading)]">
            Script Studio Draft
          </span>
        </div>
        {onClose && (
          <button
            type="button"
            onClick={onClose}
            className="flex h-7 w-7 cursor-pointer items-center justify-center rounded-full border border-[#ffe6dc] bg-white text-[#667085] transition-colors hover:bg-[#fff0eb] hover:text-[#0f172a]"
            title="Đóng bảng"
          >
            <X className="h-3.5 w-3.5" />
          </button>
        )}
      </div>

      {/* Content */}
      <div className="flex-1 space-y-4 overflow-y-auto p-4 text-xs">
        {!script ? (
          <div className="flex flex-col items-center justify-center space-y-3 py-24 text-center">
            <div className="flex h-12 w-12 items-center justify-center rounded-full border border-[#ffe0d5] bg-[#fff0eb] text-[#ff7442]">
              <Sparkles className="h-6 w-6" />
            </div>
            <p className="text-xs font-extrabold text-[#0f172a]">
              Chưa có kịch bản đang mở
            </p>
            <p className="max-w-[220px] text-[11px] font-medium leading-relaxed text-[#667085]">
              Nhập yêu cầu vào khung chat hoặc dùng tính năng 1-Click Generator để tạo kịch bản.
            </p>
          </div>
        ) : (
          <div className="animate-in fade-in space-y-4 duration-200">
            {/* Title & Metadata */}
            <div className="space-y-2.5 rounded-[22px] border border-[#f1f5f9] bg-white p-4 shadow-[0_8px_20px_rgba(0,0,0,0.03)]">
              <div className="flex items-center justify-between gap-2">
                <Badge variant="mono">{script.platform}</Badge>
                <Badge variant="mono">{script.target_duration_seconds}s</Badge>
              </div>
              <h2 className="text-sm font-black leading-snug tracking-tight text-[#0f172a] [font-family:var(--font-heading)]">
                {script.title}
              </h2>
              <p className="text-[11px] font-medium text-[#667085]">
                Chủ đề: <span className="font-bold text-[#ff7442]">{script.target_niche}</span>
              </p>
            </div>

            {/* 3s Hook Section */}
            {script.hook && (
              <div className="space-y-2.5 rounded-[22px] border border-[#ffe0d5] bg-[linear-gradient(135deg,#fff7f4,#ffffff)] p-4 shadow-xs">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-black uppercase tracking-wider text-[#ff7442]">
                    Hook Giữ Chân 3s
                  </span>
                  <Badge variant="hook">
                    {script.hook.hook_type || "viral_hook"}
                  </Badge>
                </div>

                <div className="space-y-1 pt-0.5">
                  <p className="text-[10px] font-black uppercase tracking-wider text-[#d97706]">
                    Lời thoại mở đầu
                  </p>
                  <p className="rounded-xl border border-[#ffd866]/40 bg-[#fef9c3]/50 p-3 text-xs font-bold italic leading-relaxed text-[#0f172a]">
                    &ldquo;{script.hook.script}&rdquo;
                  </p>
                </div>

                <div className="space-y-0.5">
                  <p className="text-[10px] font-black uppercase tracking-wider text-[#6a4f44]">
                    Hành động Visual
                  </p>
                  <p className="text-[11px] font-medium leading-relaxed text-[#475569]">
                    {script.hook.visual_action}
                  </p>
                </div>

                {script.hook.retention_rationale && (
                  <div className="border-t border-[#ffe0d5] pt-2 text-[11px] leading-relaxed text-[#667085]">
                    <span className="font-bold text-[#0f172a]">Tâm lý giữ chân:</span>{" "}
                    {script.hook.retention_rationale}
                  </div>
                )}
              </div>
            )}

            {/* Storyboard Scenes */}
            <div className="space-y-3">
              <span className="block text-[11px] font-black uppercase tracking-wider text-[#6a4f44]">
                Storyboard Phân Cảnh ({script.scenes?.length || 0})
              </span>

              {script.scenes?.map((scene) => (
                <div
                  key={scene.scene_number}
                  className="space-y-2.5 rounded-[20px] border border-[#f1f5f9] bg-white p-4 shadow-xs"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-black text-[#0f172a]">
                      Cảnh {scene.scene_number}
                    </span>
                    <Badge variant="mono">{scene.time_range}</Badge>
                  </div>

                  <div className="space-y-0.5">
                    <span className="text-[10px] font-black uppercase tracking-wider text-[#667085]">
                      Lời thoại
                    </span>
                    <p className="text-xs font-bold leading-relaxed text-[#0f172a]">
                      {scene.narration}
                    </p>
                  </div>

                  <div className="space-y-0.5">
                    <span className="text-[10px] font-black uppercase tracking-wider text-[#667085]">
                      Visual B-Roll
                    </span>
                    <p className="text-[11px] font-medium leading-relaxed text-[#475569]">
                      {scene.visual_action}
                    </p>
                  </div>

                  {scene.audio_sfx_cue && (
                    <div className="text-[11px] text-[#667085]">
                      <span className="font-bold text-[#0f172a]">SFX:</span>{" "}
                      {scene.audio_sfx_cue}
                    </div>
                  )}

                  {/* Clean AI Prompts Copy Buttons */}
                  <div className="flex items-center gap-2 border-t border-[#f1f5f9] pt-2.5">
                    {scene.image_prompt && (
                      <button
                        type="button"
                        onClick={() =>
                          copyToClipboard(
                            scene.image_prompt,
                            `img_${scene.scene_number}`
                          )
                        }
                        className="flex flex-1 cursor-pointer items-center justify-center space-x-1 rounded-full border border-[#ffe6dc] bg-[#fff0eb] px-2.5 py-1.5 text-[10px] font-bold text-[#ff7442] transition-all hover:bg-[#ffe4d9]"
                        title={scene.image_prompt}
                      >
                        {copiedKey === `img_${scene.scene_number}` ? (
                          <>
                            <Check className="h-3 w-3 text-[#ff7442]" />
                            <span className="font-black text-[#ff7442]">Đã sao chép</span>
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
                        className="flex flex-1 cursor-pointer items-center justify-center space-x-1 rounded-full border border-[#ffe6dc] bg-[#fff0eb] px-2.5 py-1.5 text-[10px] font-bold text-[#ff7442] transition-all hover:bg-[#ffe4d9]"
                        title={scene.video_prompt}
                      >
                        {copiedKey === `vid_${scene.scene_number}` ? (
                          <>
                            <Check className="h-3 w-3 text-[#ff7442]" />
                            <span className="font-black text-[#ff7442]">Đã sao chép</span>
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
              <div className="space-y-1.5 rounded-[20px] border border-[#ffe0d5] bg-white p-4 shadow-xs">
                <span className="block text-xs font-black uppercase tracking-wider text-[#ff7442]">
                  Call To Action
                </span>
                <p className="text-xs font-extrabold text-[#0f172a]">
                  &ldquo;{script.call_to_action.script}&rdquo;
                </p>
                <p className="text-[11px] font-medium text-[#667085]">
                  {script.call_to_action.visual_cue}
                </p>
              </div>
            )}

            {/* Suggested Hashtags */}
            {script.suggested_hashtags?.length > 0 && (
              <div className="space-y-2 pt-1">
                <span className="block text-[10px] font-black uppercase tracking-wider text-[#6a4f44]">
                  Hashtags Gợi Ý
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {script.suggested_hashtags.map((tag, idx) => (
                    <span
                      key={idx}
                      className="rounded-full border border-[#ffe0d5] bg-[#fff0eb] px-2.5 py-1 font-mono text-[10px] font-bold text-[#ff7442]"
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
        <div className="flex shrink-0 items-center space-x-2 border-t border-[#ffe6dc] bg-[#fffcfb] p-3.5">
          <Button
            variant="primary"
            size="sm"
            className="flex-1"
            onClick={copyFullMarkdown}
          >
            {copiedKey === "full_md" ? (
              <>
                <Check className="mr-1 h-3.5 w-3.5 text-white" />
                <span>Đã sao chép</span>
              </>
            ) : (
              <>
                <Copy className="mr-1 h-3.5 w-3.5 text-white" />
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

