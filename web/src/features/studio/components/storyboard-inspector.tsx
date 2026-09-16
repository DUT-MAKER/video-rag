"use client";

import * as React from "react";
import {
  Clapperboard,
  Copy,
  Check,
  Download,
  Film,
  Sparkles,
  Zap,
  Volume2,
  Video,
  Image as ImageIcon,
  X,
} from "lucide-react";
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
    md += `## 🪝 HOOK (3-5s)\n`;
    md += `**Type:** ${script.hook.hook_type}\n`;
    md += `**Script:** "${script.hook.script}"\n`;
    md += `**Visual:** ${script.hook.visual_action}\n`;
    md += `**Retention Rationale:** ${script.hook.retention_rationale}\n\n`;
    md += `## 🎬 STORYBOARD\n\n`;
    script.scenes.forEach((scene) => {
      md += `### Cảnh ${scene.scene_number} (${scene.time_range})\n`;
      md += `- **Thoại:** ${scene.narration}\n`;
      md += `- **Hình ảnh (B-roll):** ${scene.visual_action}\n`;
      md += `- **Âm thanh SFX:** ${scene.audio_sfx_cue}\n`;
      md += `- **Image Prompt:** \`${scene.image_prompt}\`\n`;
      md += `- **Video Prompt:** \`${scene.video_prompt}\`\n\n`;
    });
    if (script.call_to_action) {
      md += `## 🎯 CALL TO ACTION\n`;
      md += `- **Lời thoại:** ${script.call_to_action.script}\n`;
      md += `- **Visual:** ${script.call_to_action.visual_cue}\n\n`;
    }
    if (script.suggested_hashtags?.length) {
      md += `**Hashtags:** ${script.suggested_hashtags.map((h) => (h.startsWith("#") ? h : `#${h}`)).join(" ")}\n`;
    }
    copyToClipboard(md, "full_md");
  };

  return (
    <aside className="w-96 border-l border-neutral-800 bg-[#0c0c0e] flex flex-col h-full shrink-0 overflow-hidden text-neutral-200">
      {/* Header */}
      <div className="h-14 px-4 border-b border-neutral-800 flex items-center justify-between shrink-0 bg-[#09090b]/60 backdrop-blur-sm">
        <div className="flex items-center space-x-2">
          <Film className="w-4 h-4 text-orange-400" />
          <span className="text-xs font-semibold tracking-wider uppercase text-neutral-200">
            Script Studio Draft
          </span>
        </div>
        {onClose && (
          <button
            type="button"
            onClick={onClose}
            className="p-1 rounded-md text-neutral-400 hover:text-white hover:bg-neutral-800/60 transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-5 text-xs">
        {!script ? (
          <div className="flex flex-col items-center justify-center py-24 text-center space-y-3 text-neutral-500">
            <Clapperboard className="w-10 h-10 text-neutral-700 stroke-[1.2]" />
            <p className="text-xs font-medium text-neutral-400">
              Chưa có kịch bản đang mở
            </p>
            <p className="text-[11px] text-neutral-500 max-w-[200px] leading-relaxed">
              Yêu cầu AI &quot;Viết kịch bản...&quot; hoặc dùng nút 1-Click Generate để bắt đầu.
            </p>
          </div>
        ) : (
          <div className="space-y-5 animate-in fade-in duration-200">
            {/* Title & Metadata */}
            <div className="space-y-2 p-3.5 rounded-xl border border-neutral-800 bg-[#121215]">
              <div className="flex items-center justify-between gap-2">
                <Badge variant="mono">{script.platform}</Badge>
                <Badge variant="mono">{script.target_duration_seconds}s</Badge>
              </div>
              <h2 className="text-sm font-semibold text-white tracking-tight leading-snug">
                {script.title}
              </h2>
              <p className="text-[11px] text-neutral-400">
                Niche: <span className="text-neutral-200">{script.target_niche}</span>
              </p>
            </div>

            {/* 3s Hook Section */}
            {script.hook && (
              <div className="space-y-2.5 p-3.5 rounded-xl border border-orange-500/20 bg-orange-500/[0.03]">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-1.5 text-orange-400">
                    <Zap className="w-3.5 h-3.5" />
                    <span className="text-xs font-semibold uppercase tracking-wider">
                      Hook Giữ Chân 3s
                    </span>
                  </div>
                  <Badge variant="hook">
                    {script.hook.hook_type || "viral_hook"}
                  </Badge>
                </div>

                <div className="space-y-1.5 pt-1">
                  <p className="text-[11px] text-neutral-400 font-medium">Lời thoại mở đầu:</p>
                  <p className="text-xs text-white font-medium bg-black/40 p-2.5 rounded-lg border border-neutral-800/80 leading-relaxed italic">
                    &ldquo;{script.hook.script}&rdquo;
                  </p>
                </div>

                <div className="space-y-1">
                  <p className="text-[11px] text-neutral-400 font-medium">Hành động Visual:</p>
                  <p className="text-[11px] text-neutral-300 leading-relaxed">
                    {script.hook.visual_action}
                  </p>
                </div>

                {script.hook.retention_rationale && (
                  <div className="pt-1.5 border-t border-orange-500/10 text-[10px] text-orange-300/80 leading-relaxed">
                    💡 <span className="font-semibold text-orange-200">Tâm lý giữ chân:</span>{" "}
                    {script.hook.retention_rationale}
                  </div>
                )}
              </div>
            )}

            {/* Storyboard Scenes */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-semibold uppercase tracking-wider text-neutral-400">
                  Storyboard Phân Cảnh ({script.scenes?.length || 0})
                </span>
              </div>

              {script.scenes?.map((scene) => (
                <div
                  key={scene.scene_number}
                  className="space-y-2.5 p-3 rounded-xl border border-neutral-800/90 bg-[#121215] hover:border-neutral-700 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-white">
                      Cảnh {scene.scene_number}
                    </span>
                    <Badge variant="mono">{scene.time_range}</Badge>
                  </div>

                  <div className="space-y-1">
                    <p className="text-[10px] uppercase font-semibold text-neutral-400 tracking-wider">
                      Lời thoại
                    </p>
                    <p className="text-xs text-neutral-100 font-medium leading-relaxed">
                      {scene.narration}
                    </p>
                  </div>

                  <div className="space-y-1">
                    <p className="text-[10px] uppercase font-semibold text-neutral-400 tracking-wider">
                      Visual (B-Roll)
                    </p>
                    <p className="text-[11px] text-neutral-300 leading-relaxed">
                      {scene.visual_action}
                    </p>
                  </div>

                  {scene.audio_sfx_cue && (
                    <div className="flex items-center space-x-1.5 text-[11px] text-neutral-400">
                      <Volume2 className="w-3 h-3 text-neutral-500" />
                      <span>{scene.audio_sfx_cue}</span>
                    </div>
                  )}

                  {/* AI Prompts buttons */}
                  <div className="pt-2 border-t border-neutral-800/60 flex items-center gap-1.5">
                    {scene.image_prompt && (
                      <button
                        type="button"
                        onClick={() =>
                          copyToClipboard(
                            scene.image_prompt,
                            `img_${scene.scene_number}`
                          )
                        }
                        className="flex-1 flex items-center justify-center space-x-1 py-1 px-2 rounded-md bg-neutral-900 border border-neutral-800 hover:border-neutral-700 text-[10px] text-neutral-300 transition-all cursor-pointer"
                        title={scene.image_prompt}
                      >
                        {copiedKey === `img_${scene.scene_number}` ? (
                          <>
                            <Check className="w-3 h-3 text-emerald-400" />
                            <span className="text-emerald-400">Copied</span>
                          </>
                        ) : (
                          <>
                            <ImageIcon className="w-3 h-3 text-purple-400" />
                            <span>Midjourney Prompt</span>
                          </>
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
                        className="flex-1 flex items-center justify-center space-x-1 py-1 px-2 rounded-md bg-neutral-900 border border-neutral-800 hover:border-neutral-700 text-[10px] text-neutral-300 transition-all cursor-pointer"
                        title={scene.video_prompt}
                      >
                        {copiedKey === `vid_${scene.scene_number}` ? (
                          <>
                            <Check className="w-3 h-3 text-emerald-400" />
                            <span className="text-emerald-400">Copied</span>
                          </>
                        ) : (
                          <>
                            <Video className="w-3 h-3 text-blue-400" />
                            <span>Veo / Kling Prompt</span>
                          </>
                        )}
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Call To Action */}
            {script.call_to_action && (
              <div className="space-y-1.5 p-3 rounded-xl border border-neutral-800 bg-[#121215]">
                <div className="flex items-center space-x-1.5 text-neutral-300">
                  <Sparkles className="w-3.5 h-3.5 text-yellow-400" />
                  <span className="text-xs font-semibold uppercase tracking-wider">
                    Call To Action
                  </span>
                </div>
                <p className="text-xs text-white font-medium">
                  &ldquo;{script.call_to_action.script}&rdquo;
                </p>
                <p className="text-[11px] text-neutral-400">
                  {script.call_to_action.visual_cue}
                </p>
              </div>
            )}

            {/* Suggested Hashtags */}
            {script.suggested_hashtags?.length > 0 && (
              <div className="space-y-1.5 pt-1">
                <span className="text-[10px] uppercase font-semibold text-neutral-500 tracking-wider">
                  Hashtags Gợi Ý
                </span>
                <div className="flex flex-wrap gap-1">
                  {script.suggested_hashtags.map((tag, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-0.5 rounded-md bg-neutral-900 border border-neutral-800 text-[10px] text-neutral-400"
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
        <div className="p-3 border-t border-neutral-800 bg-[#09090b]/80 backdrop-blur-sm flex items-center space-x-2 shrink-0">
          <Button
            variant="secondary"
            size="sm"
            className="flex-1"
            onClick={copyFullMarkdown}
          >
            {copiedKey === "full_md" ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-400" />
                <span>Copied Markdown</span>
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5" />
                <span>Copy Markdown</span>
              </>
            )}
          </Button>

          <Button
            variant="secondary"
            size="sm"
            onClick={downloadJson}
            title="Download JSON"
          >
            <Download className="w-3.5 h-3.5" />
          </Button>
        </div>
      )}
    </aside>
  );
}
