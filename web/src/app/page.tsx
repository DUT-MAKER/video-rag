import Link from "next/link";
import { Sparkles, Zap, Film, Database, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-[#09090b] text-white flex flex-col justify-between p-6 md:p-12 relative overflow-hidden">
      {/* Subtle Background Glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-neutral-800/20 blur-[120px] pointer-events-none rounded-full" />

      {/* Top Brand Header */}
      <header className="flex items-center justify-between z-10 max-w-6xl w-full mx-auto">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-white text-neutral-950 flex items-center justify-center font-bold">
            <Sparkles className="w-4 h-4 fill-neutral-950" />
          </div>
          <span className="font-semibold text-base tracking-tight text-white">
            ViralCopilot AI
          </span>
          <Badge variant="mono">Studio v1.0</Badge>
        </div>

        <div className="flex items-center space-x-3 text-xs">
          <Button variant="ghost" asChild>
            <Link href="/login">Đăng Nhập</Link>
          </Button>
          <Button asChild>
            <Link href="/dashboard">
              <span>Vào Studio</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </Button>
        </div>
      </header>

      {/* Center Hero Section */}
      <section className="max-w-4xl mx-auto py-20 z-10 text-center space-y-6">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full border border-neutral-800 bg-[#121215] text-xs text-neutral-400">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>RAG Grounding: pgvector & MinIO Video Store</span>
        </div>

        <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight text-white leading-[1.15]">
          Tự Động Hóa Kịch Bản Video Viral Chuẩn Từng Giây
        </h1>

        <p className="max-w-2xl mx-auto text-sm sm:text-base text-neutral-400 leading-relaxed">
          AI Agent phân tích pattern giữ chân người xem từ kho video triệu view. Sinh kịch bản TikTok, Shorts, Reels với Hook 3s giật gân, Storyboard trực quan và Prompt sẵn sàng cho Flux / Midjourney / Veo.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-3 pt-4">
          <Button size="lg" asChild className="h-11 px-6">
            <Link href="/dashboard">
              <Sparkles className="w-4 h-4" />
              <span>Mở Studio Co-Pilot</span>
            </Link>
          </Button>

          <Button size="lg" variant="secondary" asChild className="h-11 px-6">
            <Link href="/dashboard/generator">
              <Zap className="w-4 h-4 text-orange-400" />
              <span>1-Click Generator</span>
            </Link>
          </Button>

          <Button size="lg" variant="outline" asChild className="h-11 px-6">
            <Link href="/dashboard/benchmarks">
              <Film className="w-4 h-4 text-neutral-400" />
              <span>Khám Phá Video Mẫu</span>
            </Link>
          </Button>
        </div>
      </section>

      {/* Feature Pills */}
      <footer className="max-w-5xl mx-auto w-full grid grid-cols-1 sm:grid-cols-3 gap-4 pt-12 border-t border-neutral-800/80 z-10 text-xs">
        <div className="p-4 rounded-xl border border-neutral-800 bg-[#121215]/60 space-y-1.5">
          <div className="flex items-center space-x-2 text-orange-400 font-semibold">
            <Zap className="w-4 h-4" />
            <span>Hook Retention 3s</span>
          </div>
          <p className="text-neutral-400 leading-relaxed">
            Phân tích công thức mở đầu kích thích dopamine, ngăn người xem lướt qua video.
          </p>
        </div>

        <div className="p-4 rounded-xl border border-neutral-800 bg-[#121215]/60 space-y-1.5">
          <div className="flex items-center space-x-2 text-purple-400 font-semibold">
            <Film className="w-4 h-4" />
            <span>Live Storyboard Timeline</span>
          </div>
          <p className="text-neutral-400 leading-relaxed">
            Chi tiết lời thoại, visual B-roll, hiệu ứng âm thanh SFX và góc máy camera từng giây.
          </p>
        </div>

        <div className="p-4 rounded-xl border border-neutral-800 bg-[#121215]/60 space-y-1.5">
          <div className="flex items-center space-x-2 text-emerald-400 font-semibold">
            <Database className="w-4 h-4" />
            <span>pgvector RAG Grounding</span>
          </div>
          <p className="text-neutral-400 leading-relaxed">
            Truy xuất tương đồng các cấu trúc video thành công thực tế, không sinh kịch bản chung chung.
          </p>
        </div>
      </footer>
    </main>
  );
}
