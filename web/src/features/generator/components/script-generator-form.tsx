"use client";

import * as React from "react";
import { Check, Download, FileText } from "lucide-react";
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
    <div className="mx-auto max-w-7xl space-y-8 p-6 md:p-8">
      {/* Header */}
      <div className="space-y-2 border-b border-[#ffe6dc] pb-6">
        <div className="inline-flex items-center gap-2 rounded-full border border-[#ff7442]/20 bg-[#fff0eb] px-3.5 py-1 text-xs font-black uppercase tracking-wider text-[#ff7442]">
          1-Click Generation Engine
        </div>
        <h1 className="text-2xl font-black tracking-tight text-[#0f172a] md:text-3xl [font-family:var(--font-heading)]">
          Sinh Kịch Bản Video Viral Chuẩn Từng Giây
        </h1>
        <p className="max-w-2xl text-xs font-medium leading-relaxed text-[#667085]">
          Áp dụng công thức Hook 3s giữ chân người xem cao nhất từ kho video triệu view kết hợp AI sinh lời thoại, visual B-roll và prompt tạo ảnh/video.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-12">
        {/* Left Form: 5 cols */}
        <div className="space-y-6 lg:col-span-5">
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
                  <label className="text-xs font-bold text-[#475569]">
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
                  <label className="text-xs font-bold text-[#475569]">
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
                  <label className="text-xs font-bold text-[#475569]">
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
                        className={`cursor-pointer rounded-full border py-2 text-xs font-bold transition-all ${
                          platform === p.id
                            ? "border-[#ffe6dc] bg-[linear-gradient(90deg,#ff7442,#ff8c64)] text-white shadow-[0_4px_12px_rgba(255,116,66,0.25)]"
                            : "border-[#e2e8f0] bg-white text-[#475569] hover:bg-[#fff0eb] hover:text-[#0f172a]"
                        }`}
                      >
                        {p.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Duration */}
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-[#475569]">
                    Thời lượng dự kiến ({duration}s)
                  </label>
                  <div className="grid grid-cols-4 gap-2">
                    {[15, 30, 45, 60].map((sec) => (
                      <button
                        key={sec}
                        type="button"
                        onClick={() => setDuration(sec)}
                        className={`cursor-pointer rounded-full border py-1.5 font-mono text-xs font-bold transition-all ${
                          duration === sec
                            ? "border-[#ffe6dc] bg-[linear-gradient(90deg,#ff7442,#ff8c64)] text-white shadow-[0_4px_12px_rgba(255,116,66,0.25)]"
                            : "border-[#e2e8f0] bg-white text-[#475569] hover:bg-[#fff0eb] hover:text-[#0f172a]"
                        }`}
                      >
                        {sec}s
                      </button>
                    ))}
                  </div>
                </div>

                {/* Hook Style */}
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-[#475569]">
                    Công thức Hook mở đầu
                  </label>
                  <select
                    value={hookStyle}
                    onChange={(e) => setHookStyle(e.target.value as HookType)}
                    className="h-10 w-full cursor-pointer rounded-xl border border-[#e2e8f0] bg-[#f8fafc] px-3.5 text-xs font-medium text-[#0f172a] outline-none transition-all focus:border-[#ff7442] focus:bg-white focus:ring-4 focus:ring-[#ff7442]/10"
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
                  <label className="text-xs font-bold text-[#475569]">
                    Mẫu RAG tham chiếu từ pgvector ({topK} patterns)
                  </label>
                  <div className="flex items-center gap-3">
                    <input
                      type="range"
                      min={1}
                      max={5}
                      value={topK}
                      onChange={(e) => setTopK(Number(e.target.value))}
                      className="flex-1 cursor-pointer accent-[#ff7442]"
                    />
                    <span className="rounded-full border border-[#ffe0d5] bg-[#fff0eb] px-3 py-1 font-mono text-xs font-bold text-[#ff7442]">
                      {topK}
                    </span>
                  </div>
                </div>

                <Button
                  type="submit"
                  disabled={isLoading || !topic.trim()}
                  className="mt-3 w-full"
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
            <div className="flex h-full min-h-[420px] flex-col items-center justify-center space-y-3 rounded-[24px] border border-[#ffe6dc] bg-[#fffcfb] p-8 text-center shadow-xs">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-[#fff0eb] text-[#ff7442]">
                <FileText className="h-6 w-6" />
              </div>
              <p className="text-base font-bold text-[#0f172a]">
                Kịch bản sinh tự động sẽ hiển thị tại đây
              </p>
              <p className="max-w-sm text-xs leading-relaxed text-[#667085]">
                Điền chủ đề ở khung bên trái và bấm nút Tạo Kịch Bản để AI thiết
                lập Hook, Storyboard và Prompt chi tiết.
              </p>
            </div>
          ) : (
            <div className="animate-in fade-in space-y-6 duration-300">
              {/* Script Header Bar */}
              <div className="flex items-center justify-between rounded-[24px] border border-[#f1f5f9] bg-white p-5 shadow-xs">
                <div>
                  <h2 className="text-base font-bold text-[#0f172a]">
                    {generatedScript.title}
                  </h2>
                  <div className="flex items-center space-x-2 pt-2">
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
                    <Download className="mr-1.5 h-3.5 w-3.5 text-[#ff7442]" />
                    <span>JSON</span>
                  </Button>
                </div>
              </div>

              {/* Hook Card */}
              <div className="space-y-3 rounded-[24px] border border-[#ffe0d5] bg-gradient-to-br from-[#fff6f2] to-[#ffeedd] p-5 shadow-xs">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold uppercase tracking-wider text-[#ea580c]">
                    Hook Giữ Chân 3s Đầu
                  </span>
                  <Badge variant="hook">{generatedScript.hook.hook_type}</Badge>
                </div>

                <p className="rounded-[16px] border border-[#ffe0d5] bg-white/90 p-3.5 text-xs font-semibold italic leading-relaxed text-[#0f172a] shadow-xs">
                  &ldquo;{generatedScript.hook.script}&rdquo;
                </p>

                <p className="text-xs text-[#475569]">
                  <span className="font-bold text-[#0f172a]">Visual:</span>{" "}
                  {generatedScript.hook.visual_action}
                </p>

                <p className="border-t border-[#ffe6dc] pt-2.5 text-xs leading-relaxed text-[#9a3412]">
                  <span className="font-bold text-[#0f172a]">Tâm lý giữ chân:</span>{" "}
                  {generatedScript.hook.retention_rationale}
                </p>
              </div>

              {/* Storyboard List */}
              <div className="space-y-3">
                <span className="block text-xs font-bold uppercase tracking-wider text-[#667085]">
                  Storyboard Phân Cảnh ({generatedScript.scenes.length})
                </span>

                {generatedScript.scenes.map((scene) => (
                  <div
                    key={scene.scene_number}
                    className="space-y-3 rounded-[20px] border border-[#f1f5f9] bg-white p-5 shadow-xs transition-shadow hover:shadow-md"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-[#0f172a]">
                        Cảnh {scene.scene_number}
                      </span>
                      <Badge variant="mono">{scene.time_range}</Badge>
                    </div>

                    <div>
                      <span className="block text-[10px] font-bold uppercase tracking-wider text-[#94a3b8]">
                        Lời thoại
                      </span>
                      <p className="text-xs font-medium leading-relaxed text-[#0f172a]">
                        {scene.narration}
                      </p>
                    </div>

                    <div>
                      <span className="block text-[10px] font-bold uppercase tracking-wider text-[#94a3b8]">
                        Visual B-Roll
                      </span>
                      <p className="text-xs leading-relaxed text-[#475569]">
                        {scene.visual_action}
                      </p>
                    </div>

                    {scene.audio_sfx_cue && (
                      <p className="text-xs text-[#667085]">
                        <span className="font-bold text-[#0f172a]">SFX:</span>{" "}
                        {scene.audio_sfx_cue}
                      </p>
                    )}

                    <div className="flex gap-2 border-t border-[#f1f5f9] pt-3">
                      {scene.image_prompt && (
                        <button
                          type="button"
                          onClick={() =>
                            copyToClipboard(
                              scene.image_prompt,
                              `g_img_${scene.scene_number}`
                            )
                          }
                          className="flex flex-1 cursor-pointer items-center justify-center space-x-1.5 rounded-full border border-[#ffe0d5] bg-[#fff0eb] px-3.5 py-1.5 text-[11px] font-medium text-[#ff7442] transition-all hover:bg-[#ffe6dc]"
                        >
                          {copiedKey === `g_img_${scene.scene_number}` ? (
                            <>
                              <Check className="mr-1 h-3.5 w-3.5 text-emerald-600" />
                              <span className="font-bold text-emerald-600">
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
                          className="flex flex-1 cursor-pointer items-center justify-center space-x-1.5 rounded-full border border-[#f1f5f9] bg-[#f8fafc] px-3.5 py-1.5 text-[11px] font-medium text-[#475569] transition-all hover:bg-[#f1f5f9] hover:text-[#0f172a]"
                        >
                          {copiedKey === `g_vid_${scene.scene_number}` ? (
                            <>
                              <Check className="mr-1 h-3.5 w-3.5 text-emerald-600" />
                              <span className="font-bold text-emerald-600">
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
