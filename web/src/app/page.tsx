import Link from "next/link";
import { ArrowRight, Check, X, ExternalLink, Sparkles, Play, ShieldCheck, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col bg-white text-[#0f172a] antialiased selection:bg-[#ff7442]/20 selection:text-[#0f172a] [font-family:var(--font-body)]">
      {/* Top Brand Header */}
      <header className="sticky top-0 z-40 flex h-16 shrink-0 items-center justify-between border-b border-[#ffe6dc] bg-[#fffcfb]/95 px-6 backdrop-blur-md md:px-12">
        <div className="flex items-center space-x-8">
          <Link href="/" className="flex items-center space-x-3">
            <div className="relative flex h-10 w-10 items-center justify-center rounded-full bg-[linear-gradient(135deg,#ff7442,#ffa382)] text-sm font-black text-white shadow-[0_8px_20px_rgba(255,116,66,0.22)]">
              VC
              <span className="absolute right-1 top-1 h-2 w-2 rounded-full bg-white shadow-xs" />
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-black tracking-tight text-[#0f172a] [font-family:var(--font-heading)]">
                ViralCopilot
              </span>
              <span className="text-[10px] font-extrabold text-[#ff7442] tracking-wider">
                MARKEE STUDIO
              </span>
            </div>
          </Link>

          <nav className="hidden items-center space-x-6 text-xs font-bold text-[#475569] md:flex">
            <a
              href="#showcase"
              className="transition-colors hover:text-[#ff7442]"
            >
              Giao Diện Studio
            </a>
            <a
              href="#comparison"
              className="transition-colors hover:text-[#ff7442]"
            >
              So Sánh RAG
            </a>
            <a
              href="#how-it-works"
              className="transition-colors hover:text-[#ff7442]"
            >
              Quy Trình 3 Bước
            </a>
          </nav>
        </div>

        <div className="flex items-center space-x-3 text-xs">
          <Button variant="ghost" size="sm" asChild>
            <Link href="/login">Đăng Nhập</Link>
          </Button>
          <Button size="sm" asChild>
            <Link href="/dashboard" className="flex items-center">
              <span>Vào Studio</span>
              <ArrowRight className="ml-1.5 h-3.5 w-3.5" />
            </Link>
          </Button>
        </div>
      </header>

      <main className="flex flex-1 flex-col items-center">
        {/* Section 1: Hero */}
        <section className="relative w-full overflow-hidden bg-[linear-gradient(135deg,#fff6f2_0%,#ffffff_48%,#ffeedd_100%)] px-6 pb-24 pt-20 text-center md:pb-32 md:pt-28">
          <div className="mx-auto max-w-4xl space-y-6">
            <div className="inline-flex items-center gap-2 rounded-full border border-[#ff7442]/20 bg-[#fff0eb] px-4 py-1.5 text-xs font-black uppercase tracking-[0.14em] text-[#ff7442] shadow-xs">
              <Sparkles className="h-3.5 w-3.5 fill-[#ff7442]" />
              <span>RAG Viral Video Operating Desk</span>
            </div>

            <h1 className="text-4xl font-black leading-[1.12] tracking-tight text-[#0f172a] sm:text-5xl md:text-6xl [font-family:var(--font-heading)]">
              Tự động hóa kịch bản video viral,{" "}
              <span className="markee-text-gradient">chuẩn từng giây</span>
            </h1>

            <p className="mx-auto max-w-2xl text-base leading-relaxed text-[#475569] md:text-lg">
              Phân tích công thức giữ chân người xem từ kho video triệu view để tạo Hook 3 giây,
              storyboard trực quan và prompt sẵn dùng cho Flux, Midjourney & Veo.
            </p>

            <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
              <Button size="lg" asChild>
                <Link href="/dashboard" className="flex items-center">
                  <span>Bắt Đầu Sáng Tạo Ngay</span>
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>

              <Button size="lg" variant="secondary" asChild>
                <Link href="/dashboard/benchmarks" className="flex items-center gap-2">
                  <Play className="h-4 w-4 fill-[#ff7442] text-[#ff7442]" />
                  <span>Khám Phá Video Mẫu</span>
                </Link>
              </Button>
            </div>

            <p className="font-mono-code pt-2 text-xs font-bold text-[#667085]">
              Đối sánh trên pgvector & MinIO video store
            </p>
          </div>
        </section>

        {/* Section 2: Product Showcase with Markee Window Header */}
        <section
          id="showcase"
          className="w-full border-y border-[#ffe6dc] bg-[#fffcfb] px-6 py-20 md:py-28"
        >
          <div className="mx-auto max-w-4xl">
            <div className="mb-12 space-y-2 text-center">
              <Badge variant="accent" className="mb-2">Trong Studio</Badge>
              <h2 className="text-3xl font-black tracking-tight text-[#0f172a] sm:text-4xl [font-family:var(--font-heading)]">
                Mọi kịch bản đều bắt đầu từ một Hook đối sánh dữ liệu
              </h2>
              <p className="text-sm font-medium text-[#667085]">
                Mô phỏng bảng điều khiển Storyboard chuẩn Markee Desk
              </p>
            </div>

            {/* Markee Style Header Panel with 3 window dots */}
            <div className="overflow-hidden rounded-[28px] border border-[#ffe6dc] bg-white shadow-[0_30px_70px_rgba(255,116,66,0.12)]">
              {/* Window dots */}
              <div className="flex items-center justify-between border-b border-[#f1f5f9] bg-[#f8fafc] px-6 py-3.5">
                <div className="flex gap-2">
                  <span className="h-3 w-3 rounded-full bg-[#ff5f56]" />
                  <span className="h-3 w-3 rounded-full bg-[#ffbd2e]" />
                  <span className="h-3 w-3 rounded-full bg-[#27c93f]" />
                </div>
                <span className="font-mono-code text-xs font-bold text-[#667085]">
                  Storyboard Inspector Co-Pilot
                </span>
                <Badge variant="accent">Preview Mode</Badge>
              </div>

              {/* Panel body with subtle dot pattern */}
              <div className="relative p-6 sm:p-8 md:p-10 markee-dot-pattern">
                <div className="absolute inset-0 bg-[linear-gradient(135deg,rgba(255,251,249,0.92),rgba(255,255,255,0.97))]" />

                <div className="relative space-y-6">
                  <div className="flex flex-wrap items-center gap-2.5">
                    <Badge variant="mono">TikTok</Badge>
                    <Badge variant="mono">45s</Badge>
                    <Badge variant="accent">curiosity_gap</Badge>
                    <Badge variant="success">94% Retention Score</Badge>
                  </div>

                  <div className="rounded-[20px] border border-[#ffe0d5] bg-[linear-gradient(135deg,#fff7f4,#ffffff)] p-5 shadow-xs">
                    <span className="text-xs font-black uppercase tracking-wider text-[#ff7442]">
                      Hook Giữ Chân 3 Giây Đầu
                    </span>
                    <p className="mt-2 text-lg font-extrabold leading-relaxed text-[#0f172a] [font-family:var(--font-heading)]">
                      &ldquo;Nếu bạn không thể hoàn thành việc này trong 2 phút, bạn sẽ tiếp tục hối hận suốt 24 giờ tới...&rdquo;
                    </p>
                  </div>

                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <div className="rounded-[18px] border border-[#f1f5f9] bg-white p-4 shadow-xs">
                      <p className="text-xs font-black uppercase tracking-wider text-[#667085]">
                        Visual B-Roll
                      </p>
                      <p className="mt-1 text-xs font-medium leading-relaxed text-[#475569]">
                        Cận cảnh tay gạt phắt màn hình điện thoại, chuyển sang đồng hồ cát đếm ngược gấp gáp.
                      </p>
                    </div>

                    <div className="rounded-[18px] border border-[#f1f5f9] bg-white p-4 shadow-xs">
                      <p className="text-xs font-black uppercase tracking-wider text-[#667085]">
                        Tâm lý giữ chân
                      </p>
                      <p className="mt-1 text-xs font-medium leading-relaxed text-[#475569]">
                        Kích hoạt khoảng trống tò mò (curiosity gap) và nỗi sợ bỏ lỡ trước khi người xem kịp lướt qua.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Section 3: Why RAG over generic LLMs */}
        <section id="comparison" className="w-full max-w-5xl px-6 py-20 md:py-28">
          <div className="mb-12 space-y-2 text-center">
            <Badge variant="accent">Đột Phá Thuật Toán Giữ Chân</Badge>
            <h2 className="text-3xl font-black tracking-tight text-[#0f172a] sm:text-4xl [font-family:var(--font-heading)]">
              Tại sao dùng Viral RAG thay vì LLM thông thường?
            </h2>
            <p className="mx-auto max-w-xl text-sm font-medium text-[#667085]">
              Thuật toán TikTok, Shorts và Reels đánh giá video dựa trên tỷ lệ xem hết. Kịch bản chung chung thất bại ngay từ giây thứ 3.
            </p>
          </div>

          <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
            {/* Generic LLM Card */}
            <div className="rounded-[24px] border border-[#e2e8f0] bg-[#f8fafc] p-7 shadow-xs">
              <div className="flex items-center justify-between">
                <span className="text-xs font-black uppercase tracking-wider text-[#667085]">
                  LLM Thông Thường
                </span>
                <span className="rounded-full bg-slate-200 px-2.5 py-0.5 text-[11px] font-bold text-[#475569]">
                  Chung chung
                </span>
              </div>
              <p className="mt-4 rounded-xl border border-slate-200 bg-white p-3 text-xs italic text-[#667085]">
                &ldquo;Chào mừng các bạn quay trở lại kênh của mình. Hôm nay mình sẽ chia sẻ 3 mẹo cực hay...&rdquo;
              </p>
              <ul className="mt-6 space-y-3 text-xs font-medium text-[#475569]">
                <li className="flex items-start gap-2.5">
                  <div className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-red-100 text-red-600">
                    <X className="h-3 w-3" />
                  </div>
                  <span>Mở đầu dài dòng, người xem lướt qua ngay trong 2s.</span>
                </li>
                <li className="flex items-start gap-2.5">
                  <div className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-red-100 text-red-600">
                    <X className="h-3 w-3" />
                  </div>
                  <span>Không có nhịp chuyển cảnh theo giây và phân tích drop-off.</span>
                </li>
                <li className="flex items-start gap-2.5">
                  <div className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-red-100 text-red-600">
                    <X className="h-3 w-3" />
                  </div>
                  <span>Không có sẵn AI prompts tối ưu cho Flux / Midjourney / Veo.</span>
                </li>
              </ul>
            </div>

            {/* ViralCopilot Markee Card */}
            <div className="rounded-[24px] border-2 border-[#ffe0d5] bg-[linear-gradient(135deg,#fffbf9,#ffffff)] p-7 shadow-[0_20px_45px_rgba(255,116,66,0.1)]">
              <div className="flex items-center justify-between">
                <span className="text-xs font-black uppercase tracking-wider text-[#ff7442]">
                  ViralCopilot RAG
                </span>
                <Badge variant="accent">Triệu View Verified</Badge>
              </div>
              <p className="mt-4 rounded-xl border border-[#ffe0d5] bg-[#fff0eb] p-3 text-xs font-bold text-[#0f172a]">
                &ldquo;99% người thất bại không phải vì thiếu tài năng, mà vì mở đầu ngày mới bằng việc kiểm tra email!&rdquo;
              </p>
              <ul className="mt-6 space-y-3 text-xs font-bold text-[#0f172a]">
                <li className="flex items-start gap-2.5">
                  <div className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-emerald-600">
                    <Check className="h-3 w-3" />
                  </div>
                  <span>Hook đối sánh trực tiếp từ video triệu view có sẵn trong pgvector.</span>
                </li>
                <li className="flex items-start gap-2.5">
                  <div className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-emerald-600">
                    <Check className="h-3 w-3" />
                  </div>
                  <span>Storyboard chi tiết từng giây: lời thoại, B-roll, SFX, góc máy quay.</span>
                </li>
                <li className="flex items-start gap-2.5">
                  <div className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-emerald-600">
                    <Check className="h-3 w-3" />
                  </div>
                  <span>Prompt sẵn dùng chuẩn studio cho Midjourney, Flux và Veo 3.1.</span>
                </li>
              </ul>
            </div>
          </div>
        </section>

        {/* Section 4: How It Works */}
        <section
          id="how-it-works"
          className="w-full border-y border-[#ffe6dc] bg-[#fff7f4] px-6 py-20 md:py-28"
        >
          <div className="mx-auto max-w-4xl">
            <div className="mb-12 space-y-2 text-center">
              <Badge variant="accent">Đơn Giản & Hiệu Quả</Badge>
              <h2 className="text-3xl font-black tracking-tight text-[#0f172a] sm:text-4xl [font-family:var(--font-heading)]">
                Quy trình tạo kịch bản 3 bước
              </h2>
            </div>

            <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
              <div className="rounded-[22px] border border-[#ffe0d5] bg-white p-6 shadow-xs transition-transform hover:-translate-y-1">
                <span className="flex h-8 w-8 items-center justify-center rounded-full bg-[#fff0eb] text-sm font-black text-[#ff7442]">
                  01
                </span>
                <h3 className="mt-4 text-base font-extrabold text-[#0f172a] [font-family:var(--font-heading)]">
                  Nhập Chủ Đề & Niche
                </h3>
                <p className="mt-2 text-xs font-medium leading-relaxed text-[#667085]">
                  Điền chủ đề, chọn thời lượng (15s–60s) và nền tảng (TikTok, Shorts, Reels).
                </p>
              </div>

              <div className="rounded-[22px] border border-[#ffe0d5] bg-white p-6 shadow-xs transition-transform hover:-translate-y-1">
                <span className="flex h-8 w-8 items-center justify-center rounded-full bg-[#fff0eb] text-sm font-black text-[#ff7442]">
                  02
                </span>
                <h3 className="mt-4 text-base font-extrabold text-[#0f172a] [font-family:var(--font-heading)]">
                  Truy Xuất Vector RAG
                </h3>
                <p className="mt-2 text-xs font-medium leading-relaxed text-[#667085]">
                  Hệ thống truy xuất pattern mở đầu giữ chân cao nhất từ pgvector & MinIO.
                </p>
              </div>

              <div className="rounded-[22px] border border-[#ffe0d5] bg-white p-6 shadow-xs transition-transform hover:-translate-y-1">
                <span className="flex h-8 w-8 items-center justify-center rounded-full bg-[#fff0eb] text-sm font-black text-[#ff7442]">
                  03
                </span>
                <h3 className="mt-4 text-base font-extrabold text-[#0f172a] [font-family:var(--font-heading)]">
                  Xuất Storyboard & Prompts
                </h3>
                <p className="mt-2 text-xs font-medium leading-relaxed text-[#667085]">
                  Nhận kịch bản từng giây và sao chép prompt sang Midjourney / Veo ngay lập tức.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Section 5: Bottom CTA */}
        <section className="w-full max-w-3xl space-y-6 px-6 py-24 text-center">
          <h2 className="text-3xl font-black tracking-tight text-[#0f172a] sm:text-4xl [font-family:var(--font-heading)]">
            Sẵn sàng tạo video triệu view tiếp theo?
          </h2>
          <p className="mx-auto max-w-md text-sm font-medium leading-relaxed text-[#667085]">
            Trải nghiệm bàn làm việc AI tạo kịch bản dựa trên dữ liệu đối sánh thực tế.
          </p>
          <div className="pt-2">
            <Button size="lg" asChild>
              <Link href="/dashboard" className="flex items-center">
                <span>Vào Studio Ngay</span>
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="w-full border-t border-[#ffe6dc] bg-[#fffcfb] px-6 py-8 text-xs text-[#667085] md:px-12">
        <div className="mx-auto flex max-w-5xl flex-col items-center justify-between gap-4 sm:flex-row">
          <div className="flex items-center space-x-2">
            <div className="relative flex h-6 w-6 items-center justify-center rounded-full bg-[linear-gradient(135deg,#ff7442,#ffa382)] text-[10px] font-black text-white">
              VC
            </div>
            <span className="font-bold text-[#0f172a]">ViralCopilot Studio &copy; 2026</span>
          </div>

          <div className="flex items-center space-x-6 font-semibold">
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-1 transition-colors hover:text-[#ff7442]"
            >
              <span>FastAPI Docs</span>
              <ExternalLink className="h-3 w-3" />
            </a>
            <Link
              href="/dashboard/benchmarks"
              className="transition-colors hover:text-[#ff7442]"
            >
              Video Benchmarks
            </Link>
            <Link
              href="/dashboard/ingest"
              className="transition-colors hover:text-[#ff7442]"
            >
              MinIO Ingest
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}

