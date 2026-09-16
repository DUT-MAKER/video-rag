"use client";

import * as React from "react";
import { Check, Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { generateViralScript } from "@/lib/api";
import type {
  GenerateScriptPayload,
  HookType,
  PlatformTarget,
  ViralScript,
} from "@/lib/types";

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
  const [generatedScript, setGeneratedScript] =
    React.useState<ViralScript | null>(null);
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
      alert(
        "Không thể sinh kịch bản. Hãy đảm bảo backend đang chạy ở http://localhost:8000."
      );
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
    <div className="mx-auto max-w-6xl space-y-8 p-6 text-white">
      {/* Header */}
      <div className="space-y-1.5 border-b border-zinc-800 pb-5">
        <span className="font-mono text-[11px] font-bold uppercase tracking-widest text-zinc-400">
          1-Click Generation Engine
        </span>
        <h1 className="text-2xl font-bold tracking-tight text-white md:text-3xl">
          Sinh Kịch Bản Video Viral Chuẩn Từng Giây
        </h1>
        <p className="max-w-2xl text-xs leading-relaxed text-zinc-300">
          Áp dụng công thức Hook 3s giữ chân người xem cao nhất từ kho video
          triệu view kết hợp AI sinh lời thoại, visual B-roll và prompt tạo
          ảnh/video.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-12">
        {/* Left Form: 5 cols */}
        <div className="space-y-6 lg:col-span-5">
          <Card>
            <CardHeader>
              <CardTitle>Cấu Hình Kịch Bản</CardTitle>
              <CardDescription>
                Điền thông tin định hướng kịch bản để AI truy xuất pattern phù
                hợp
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleGenerate} className="space-y-4">
                {/* Topic */}
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-zinc-200">
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
                  <label className="text-xs font-bold text-zinc-200">
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
                  <label className="text-xs font-bold text-zinc-200">
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
                        className={`cursor-pointer rounded-lg border px-3 py-2 text-xs transition-all ${
                          platform === p.id
                            ? "border-white bg-white font-bold text-black"
                            : "border-zinc-700 bg-zinc-900 font-medium text-zinc-300 hover:border-zinc-500 hover:text-white"
                        }`}
                      >
                        {p.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Duration */}
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-zinc-200">
                    Thời lượng dự kiến ({duration}s)
                  </label>
                  <div className="grid grid-cols-4 gap-2">
                    {[15, 30, 45, 60].map((sec) => (
                      <button
                        key={sec}
                        type="button"
                        onClick={() => setDuration(sec)}
                        className={`cursor-pointer rounded-lg border py-1.5 font-mono text-xs transition-all ${
                          duration === sec
                            ? "border-white bg-white font-bold text-black"
                            : "border-zinc-700 bg-zinc-900 font-medium text-zinc-300 hover:border-zinc-500 hover:text-white"
                        }`}
                      >
                        {sec}s
                      </button>
                    ))}
                  </div>
                </div>

                {/* Hook Style */}
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-zinc-200">
                    Công thức Hook mở đầu
                  </label>
                  <select
                    value={hookStyle}
                    onChange={(e) => setHookStyle(e.target.value as HookType)}
                    className="h-9 w-full cursor-pointer rounded-lg border border-zinc-700 bg-[#16161a] px-3 text-xs font-medium text-white outline-none focus:border-zinc-400"
                  >
                    <option value="curiosity_gap">
                      Curiosity Gap (Khoảng trống tò mò)
                    </option>
                    <option value="problem_agitate">
                      Problem Agitate (Nêu nỗi đau gay gắt)
                    </option>
                    <option value="contrarian">
                      Contrarian (Đi ngược số đông)
                    </option>
                    <option value="shocking_fact">
                      Shocking Fact (Sự thật gây sốc)
                    </option>
                    <option value="story_loop">
                      Story Loop (Mở vòng lặp câu chuyện)
                    </option>
                  </select>
                </div>

                {/* Top-K Patterns */}
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-zinc-200">
                    Mẫu RAG tham chiếu từ pgvector ({topK} patterns)
                  </label>
                  <div className="flex items-center gap-3">
                    <input
                      type="range"
                      min={1}
                      max={5}
                      value={topK}
                      onChange={(e) => setTopK(Number(e.target.value))}
                      className="flex-1 cursor-pointer accent-zinc-200"
                    />
                    <span className="rounded border border-zinc-700 bg-zinc-800 px-2 py-0.5 font-mono text-xs font-bold text-white">
                      {topK}
                    </span>
                  </div>
                </div>

                <Button
                  type="submit"
                  disabled={isLoading || !topic.trim()}
                  className="mt-2 w-full"
                  size="lg"
                >
                  {isLoading
                    ? "Đang truy xuất RAG & Sinh kịch bản..."
                    : "1-Click Generate Script"}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>

        {/* Right Output: 7 cols */}
        <div className="space-y-6 lg:col-span-7">
          {!generatedScript ? (
            <div className="flex h-full min-h-[420px] flex-col items-center justify-center space-y-2 rounded-xl border border-zinc-700 bg-[#141418] p-8 text-center">
              <p className="text-sm font-bold text-white">
                Kịch bản sinh tự động sẽ hiển thị tại đây
              </p>
              <p className="max-w-sm text-xs leading-relaxed text-zinc-300">
                Điền chủ đề ở khung bên trái và bấm nút Tạo Kịch Bản để AI thiết
                lập Hook, Storyboard và Prompt chi tiết.
              </p>
            </div>
          ) : (
            <div className="animate-in fade-in space-y-6 duration-300">
              {/* Script Header Bar */}
              <div className="flex items-center justify-between rounded-xl border border-zinc-700 bg-[#141418] p-4">
                <div>
                  <h2 className="text-base font-bold text-white">
                    {generatedScript.title}
                  </h2>
                  <div className="flex items-center space-x-2 pt-1.5">
                    <Badge variant="mono">{generatedScript.platform}</Badge>
                    <Badge variant="mono">
                      {generatedScript.target_duration_seconds}s
                    </Badge>
                    <Badge variant="secondary">
                      {generatedScript.target_niche}
                    </Badge>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <Button variant="secondary" size="sm" onClick={downloadJson}>
                    <Download className="mr-1 h-3.5 w-3.5" />
                    <span>JSON</span>
                  </Button>
                </div>
              </div>

              {/* Hook Card */}
              <div className="space-y-2.5 rounded-xl border border-orange-400/40 bg-orange-500/10 p-4">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold uppercase tracking-wider text-orange-300">
                    Hook Giữ Chân 3s Đầu
                  </span>
                  <Badge variant="hook">{generatedScript.hook.hook_type}</Badge>
                </div>

                <p className="rounded-lg border border-zinc-700 bg-black/60 p-3 text-xs font-semibold italic leading-relaxed text-white">
                  &ldquo;{generatedScript.hook.script}&rdquo;
                </p>

                <p className="text-xs text-zinc-200">
                  <span className="font-bold text-white">Visual:</span>{" "}
                  {generatedScript.hook.visual_action}
                </p>

                <p className="border-t border-orange-400/20 pt-2 text-xs leading-relaxed text-orange-200">
                  <span className="font-bold text-white">Tâm lý giữ chân:</span>{" "}
                  {generatedScript.hook.retention_rationale}
                </p>
              </div>

              {/* Storyboard List */}
              <div className="space-y-3">
                <span className="block text-xs font-bold uppercase tracking-wider text-zinc-300">
                  Storyboard Phân Cảnh ({generatedScript.scenes.length})
                </span>

                {generatedScript.scenes.map((scene) => (
                  <div
                    key={scene.scene_number}
                    className="space-y-2.5 rounded-xl border border-zinc-700 bg-[#141418] p-4"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-white">
                        Cảnh {scene.scene_number}
                      </span>
                      <Badge variant="mono">{scene.time_range}</Badge>
                    </div>

                    <div>
                      <span className="block text-[10px] font-bold uppercase tracking-wider text-zinc-400">
                        Lời thoại
                      </span>
                      <p className="text-xs font-medium leading-relaxed text-white">
                        {scene.narration}
                      </p>
                    </div>

                    <div>
                      <span className="block text-[10px] font-bold uppercase tracking-wider text-zinc-400">
                        Visual B-Roll
                      </span>
                      <p className="text-xs leading-relaxed text-zinc-200">
                        {scene.visual_action}
                      </p>
                    </div>

                    {scene.audio_sfx_cue && (
                      <p className="text-xs text-zinc-300">
                        <span className="font-bold text-zinc-400">SFX:</span>{" "}
                        {scene.audio_sfx_cue}
                      </p>
                    )}

                    <div className="flex gap-2 border-t border-zinc-700/80 pt-2">
                      {scene.image_prompt && (
                        <button
                          type="button"
                          onClick={() =>
                            copyToClipboard(
                              scene.image_prompt,
                              `g_img_${scene.scene_number}`
                            )
                          }
                          className="flex flex-1 cursor-pointer items-center justify-center space-x-1 rounded-md border border-zinc-600 bg-zinc-800 px-3 py-1.5 text-[11px] font-medium text-zinc-100 transition-all hover:bg-zinc-700"
                        >
                          {copiedKey === `g_img_${scene.scene_number}` ? (
                            <>
                              <Check className="mr-1 h-3.5 w-3.5 text-emerald-400" />
                              <span className="font-bold text-emerald-400">
                                Copied Prompt
                              </span>
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
                          className="flex flex-1 cursor-pointer items-center justify-center space-x-1 rounded-md border border-zinc-600 bg-zinc-800 px-3 py-1.5 text-[11px] font-medium text-zinc-100 transition-all hover:bg-zinc-700"
                        >
                          {copiedKey === `g_vid_${scene.scene_number}` ? (
                            <>
                              <Check className="mr-1 h-3.5 w-3.5 text-emerald-400" />
                              <span className="font-bold text-emerald-400">
                                Copied Prompt
                              </span>
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
