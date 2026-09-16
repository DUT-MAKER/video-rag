"use client";

import * as React from "react";
import {
  Sparkles,
  Zap,
  Check,
  Download,
  ArrowRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { generateViralScript } from "@/lib/api";
import type { GenerateScriptPayload, HookType, PlatformTarget, ViralScript } from "@/lib/types";

export function ScriptGeneratorForm() {
  const [topic, setTopic] = React.useState("");
  const [audience, setAudience] = React.useState(
    "Nhân viên văn phòng và sinh viên muốn tối ưu năng suất làm việc"
  );
  const [duration, setDuration] = React.useState<number>(45);
  const [platform, setPlatform] = React.useState<PlatformTarget>("tiktok");
  const [hookStyle, setHookStyle] = React.useState<HookType>("curiosity_gap");
  const [topK, setTopK] = React.useState<number>(3);

  const [isLoading, setIsLoading] = React.useState(false);
  const [generatedScript, setGeneratedScript] = React.useState<ViralScript | null>(null);
  const [copiedKey, setCopiedKey] = React.useState<string | null>(null);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) return;

    setIsLoading(true);
    try {
      const payload: GenerateScriptPayload = {
        topic,
        target_audience: audience,
        duration_seconds: duration,
        platform,
        hook_style: hookStyle,
        top_k_patterns: topK,
      };
      const result = await generateViralScript(payload);
      setGeneratedScript(result);
    } catch (err) {
      console.error("Failed to generate script:", err);
      alert("Không thể sinh kịch bản. Hãy đảm bảo backend đang chạy ở http://localhost:8000.");
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const downloadJson = () => {
    if (!generatedScript) return;
    const blob = new Blob([JSON.stringify(generatedScript, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `viral-script-${generatedScript.platform}-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-8">
      {/* Header */}
      <div className="space-y-1.5">
        <div className="flex items-center space-x-2 text-orange-400">
          <Zap className="w-4 h-4" />
          <span className="text-xs font-semibold uppercase tracking-wider">
            1-Click Generation Engine
          </span>
        </div>
        <h1 className="text-2xl font-bold tracking-tight text-white">
          Sinh Kịch Bản Video Viral Chuẩn Từng Giây
        </h1>
        <p className="text-xs text-neutral-400 max-w-2xl leading-relaxed">
          Áp dụng công thức Hook 3s giữ chân người xem cao nhất từ kho video triệu view kết hợp AI sinh lời thoại, visual B-roll và prompt tạo ảnh/video.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Form: 5 cols */}
        <div className="lg:col-span-5 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Cấu Hình Kịch Bản</CardTitle>
              <CardDescription>
                Điền thông tin định hướng kịch bản để AI truy xuất pattern phù hợp
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleGenerate} className="space-y-4">
                {/* Topic */}
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-neutral-300">
                    Chủ đề video (Topic) *
                  </label>
                  <Textarea
                    rows={3}
                    required
                    placeholder="Ví dụ: Cách áp dụng quy tắc 2 phút để đánh bại sự trì hoãn..."
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                  />
                </div>

                {/* Target Audience */}
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-neutral-300">
                    Đối tượng người xem (Target Audience)
                  </label>
                  <Input
                    placeholder="Nhân viên văn phòng, Gen Z..."
                    value={audience}
                    onChange={(e) => setAudience(e.target.value)}
                  />
                </div>

                {/* Platform */}
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-neutral-300">
                    Nền tảng mục tiêu
                  </label>
                  <div className="grid grid-cols-3 gap-2">
                    {(
                      [
                        { id: "tiktok", label: "TikTok" },
                        { id: "youtube_shorts", label: "Shorts" },
                        { id: "instagram_reels", label: "Reels" },
                      ] as const
                    ).map((p) => (
                      <button
                        key={p.id}
                        type="button"
                        onClick={() => setPlatform(p.id)}
                        className={`py-2 px-3 rounded-lg border text-xs font-medium transition-all cursor-pointer ${
                          platform === p.id
                            ? "bg-white text-neutral-950 border-white font-semibold"
                            : "bg-neutral-900 border-neutral-800 text-neutral-400 hover:text-white"
                        }`}
                      >
                        {p.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Duration */}
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-neutral-300">
                    Thời lượng dự kiến ({duration}s)
                  </label>
                  <div className="grid grid-cols-4 gap-2">
                    {[15, 30, 45, 60].map((sec) => (
                      <button
                        key={sec}
                        type="button"
                        onClick={() => setDuration(sec)}
                        className={`py-1.5 rounded-lg border text-xs font-mono transition-all cursor-pointer ${
                          duration === sec
                            ? "bg-neutral-100 text-neutral-950 border-neutral-100 font-semibold"
                            : "bg-neutral-900 border-neutral-800 text-neutral-400 hover:text-white"
                        }`}
                      >
                        {sec}s
                      </button>
                    ))}
                  </div>
                </div>

                {/* Hook Style */}
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-neutral-300">
                    Công thức Hook mở đầu
                  </label>
                  <select
                    value={hookStyle}
                    onChange={(e) => setHookStyle(e.target.value as HookType)}
                    className="w-full h-9 rounded-lg border border-neutral-800 bg-[#121215] px-3 text-xs text-neutral-200 outline-none cursor-pointer focus:border-neutral-600"
                  >
                    <option value="curiosity_gap">Curiosity Gap (Khoảng trống tò mò)</option>
                    <option value="problem_agitate">Problem Agitate (Nêu nỗi đau gay gắt)</option>
                    <option value="contrarian">Contrarian (Đi ngược số đông)</option>
                    <option value="shocking_fact">Shocking Fact (Sự thật gây sốc)</option>
                    <option value="story_loop">Story Loop (Mở vòng lặp câu chuyện)</option>
                  </select>
                </div>

                {/* Top-K Patterns */}
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-neutral-300">
                    Mẫu RAG tham chiếu từ pgvector ({topK} patterns)
                  </label>
                  <div className="flex items-center gap-3">
                    <input
                      type="range"
                      min={1}
                      max={5}
                      value={topK}
                      onChange={(e) => setTopK(Number(e.target.value))}
                      className="flex-1 accent-neutral-200 cursor-pointer"
                    />
                    <span className="font-mono text-xs text-neutral-300">{topK}</span>
                  </div>
                </div>

                <Button
                  type="submit"
                  disabled={isLoading || !topic.trim()}
                  className="w-full mt-2"
                  size="lg"
                >
                  {isLoading ? (
                    <span className="flex items-center space-x-2">
                      <Sparkles className="w-4 h-4 animate-spin" />
                      <span>Đang truy xuất RAG & Sinh kịch bản...</span>
                    </span>
                  ) : (
                    <span className="flex items-center space-x-2">
                      <Sparkles className="w-4 h-4" />
                      <span>1-Click Generate Script</span>
                    </span>
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>

        {/* Right Output: 7 cols */}
        <div className="lg:col-span-7 space-y-6">
          {!generatedScript ? (
            <div className="h-full min-h-[420px] rounded-xl border border-neutral-800/80 bg-[#121215]/50 flex flex-col items-center justify-center text-center p-8 space-y-3">
              <div className="w-12 h-12 rounded-xl border border-neutral-800 bg-neutral-900 flex items-center justify-center">
                <ArrowRight className="w-5 h-5 text-neutral-600" />
              </div>
              <p className="text-xs font-medium text-neutral-300">
                Kịch bản sinh tự động sẽ hiển thị tại đây
              </p>
              <p className="text-[11px] text-neutral-500 max-w-sm">
                Điền chủ đề ở khung bên trái và bấm nút Tạo Kịch Bản để AI thiết lập Hook, Storyboard và Prompt chi tiết.
              </p>
            </div>
          ) : (
            <div className="space-y-6 animate-in fade-in duration-300">
              {/* Script Header Bar */}
              <div className="p-4 rounded-xl border border-neutral-800 bg-[#121215] flex items-center justify-between">
                <div>
                  <h2 className="text-base font-semibold text-white">
                    {generatedScript.title}
                  </h2>
                  <div className="flex items-center space-x-2 pt-1">
                    <Badge variant="mono">{generatedScript.platform}</Badge>
                    <Badge variant="mono">{generatedScript.target_duration_seconds}s</Badge>
                    <Badge variant="secondary">{generatedScript.target_niche}</Badge>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <Button variant="secondary" size="sm" onClick={downloadJson}>
                    <Download className="w-3.5 h-3.5" />
                    <span>JSON</span>
                  </Button>
                </div>
              </div>

              {/* Hook Card */}
              <div className="p-4 rounded-xl border border-orange-500/20 bg-orange-500/[0.03] space-y-2.5">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-1.5 text-orange-400">
                    <Zap className="w-4 h-4" />
                    <span className="text-xs font-semibold uppercase tracking-wider">
                      Hook Giữ Chân 3s Đầu
                    </span>
                  </div>
                  <Badge variant="hook">{generatedScript.hook.hook_type}</Badge>
                </div>

                <p className="text-xs text-white font-medium bg-black/50 p-3 rounded-lg border border-neutral-800 leading-relaxed italic">
                  &ldquo;{generatedScript.hook.script}&rdquo;
                </p>

                <p className="text-[11px] text-neutral-400">
                  <span className="font-semibold text-neutral-300">Visual:</span>{" "}
                  {generatedScript.hook.visual_action}
                </p>

                <p className="text-[10px] text-orange-300/90 leading-relaxed border-t border-orange-500/10 pt-2">
                  💡 <span className="font-semibold text-orange-200">Retention:</span>{" "}
                  {generatedScript.hook.retention_rationale}
                </p>
              </div>

              {/* Storyboard List */}
              <div className="space-y-3">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-neutral-400">
                  Storyboard Phân Cảnh ({generatedScript.scenes.length})
                </h3>

                {generatedScript.scenes.map((scene) => (
                  <div
                    key={scene.scene_number}
                    className="p-3.5 rounded-xl border border-neutral-800 bg-[#121215] space-y-2.5"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold text-white">
                        Cảnh {scene.scene_number}
                      </span>
                      <Badge variant="mono">{scene.time_range}</Badge>
                    </div>

                    <p className="text-xs text-neutral-200 font-medium">
                      {scene.narration}
                    </p>

                    <p className="text-[11px] text-neutral-400">
                      <span className="text-neutral-500 font-semibold">B-Roll:</span>{" "}
                      {scene.visual_action}
                    </p>

                    {scene.audio_sfx_cue && (
                      <p className="text-[11px] text-neutral-500">
                        <span className="font-semibold">SFX:</span> {scene.audio_sfx_cue}
                      </p>
                    )}

                    <div className="pt-2 border-t border-neutral-800/60 flex gap-2">
                      {scene.image_prompt && (
                        <button
                          type="button"
                          onClick={() =>
                            copyToClipboard(
                              scene.image_prompt,
                              `g_img_${scene.scene_number}`
                            )
                          }
                          className="flex-1 py-1.5 px-2 rounded-md bg-neutral-900 border border-neutral-800 text-[10px] text-neutral-300 hover:text-white transition-all cursor-pointer flex items-center justify-center space-x-1"
                        >
                          {copiedKey === `g_img_${scene.scene_number}` ? (
                            <>
                              <Check className="w-3 h-3 text-emerald-400" />
                              <span className="text-emerald-400">Copied Prompt</span>
                            </>
                          ) : (
                            <span>Copy Midjourney Prompt</span>
                          )}
                        </button>
                      )}

                      {scene.video_prompt && (
                        <button
                          type="button"
                          onClick={() =>
                            copyToClipboard(
                              scene.video_prompt,
                              `g_vid_${scene.scene_number}`
                            )
                          }
                          className="flex-1 py-1.5 px-2 rounded-md bg-neutral-900 border border-neutral-800 text-[10px] text-neutral-300 hover:text-white transition-all cursor-pointer flex items-center justify-center space-x-1"
                        >
                          {copiedKey === `g_vid_${scene.scene_number}` ? (
                            <>
                              <Check className="w-3 h-3 text-emerald-400" />
                              <span className="text-emerald-400">Copied Prompt</span>
                            </>
                          ) : (
                            <span>Copy Veo/Kling Prompt</span>
                          )}
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
