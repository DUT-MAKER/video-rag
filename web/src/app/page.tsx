import Link from "next/link";
import { ArrowRight, Check, X, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export default function HomePage() {
  return (
    <div className="bg-background text-foreground selection:bg-accent/30 flex min-h-screen flex-col antialiased selection:text-white">
      {/* Top Brand Header */}
      <header className="border-border bg-background/95 sticky top-0 z-40 flex h-14 shrink-0 items-center justify-between border-b px-6 backdrop-blur-md md:px-12">
        <div className="flex items-center space-x-6">
          <Link href="/" className="flex items-center space-x-2.5">
            <div className="bg-accent text-background flex h-6 w-6 items-center justify-center rounded-lg text-xs font-semibold">
              VC
            </div>
            <span className="text-foreground text-sm font-semibold tracking-tight">
              ViralCopilot
            </span>
          </Link>

          <nav className="text-muted-foreground hidden items-center space-x-6 text-xs font-medium md:flex">
            <a
              href="#showcase"
              className="hover:text-foreground transition-colors"
            >
              Giao Diện Studio
            </a>
            <a
              href="#comparison"
              className="hover:text-foreground transition-colors"
            >
              So Sánh RAG
            </a>
            <a
              href="#how-it-works"
              className="hover:text-foreground transition-colors"
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
              <ArrowRight className="ml-1 h-3.5 w-3.5" />
            </Link>
          </Button>
        </div>
      </header>

      <main className="flex flex-1 flex-col items-center">
        {/* Section 1: Hero */}
        <section className="mx-auto max-w-3xl space-y-6 px-6 pb-20 pt-24 text-center">
          <h1 className="text-4xl font-semibold leading-[1.15] tracking-tight sm:text-5xl md:text-[3.25rem]">
            Tự động hóa kịch bản video viral, chuẩn từng giây
          </h1>

          <p className="text-muted-foreground mx-auto max-w-xl text-base leading-relaxed">
            Phân tích công thức giữ chân người xem từ kho video triệu view để
            tạo Hook 3 giây, storyboard trực quan và prompt sẵn dùng cho Flux,
            Midjourney & Veo.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
            <Button size="lg" asChild>
              <Link href="/dashboard" className="flex items-center">
                <span>Bắt Đầu Sáng Tạo</span>
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>

            <Button size="lg" variant="secondary" asChild>
              <Link href="/dashboard/benchmarks">Khám Phá Video Mẫu</Link>
            </Button>
          </div>

          <p className="text-muted-foreground font-mono-code pt-1 text-xs">
            Đối sánh trên pgvector & MinIO video store
          </p>
        </section>

        {/* Section 2: Product Showcase */}
        <section
          id="showcase"
          className="bg-surface border-border-subtle w-full border-y"
        >
          <div className="mx-auto max-w-3xl px-6 py-20">
            <div className="mb-10 space-y-2 text-center">
              <span className="text-muted-foreground font-mono text-xs uppercase tracking-widest">
                Trong Studio
              </span>
              <h2 className="text-2xl font-semibold tracking-tight sm:text-3xl">
                Mọi kịch bản đều bắt đầu từ một Hook được đối sánh dữ liệu
              </h2>
            </div>

            <div className="border-border bg-background overflow-hidden rounded-lg border">
              <div className="border-border-subtle flex h-10 select-none items-center justify-between border-b px-4">
                <span className="font-mono-code text-muted-foreground text-xs">
                  Storyboard Inspector
                </span>
                <Badge variant="mono">Preview</Badge>
              </div>

              <div className="space-y-4 p-6 md:p-8">
                <div className="flex flex-wrap items-center gap-2">
                  <Badge variant="mono">TikTok</Badge>
                  <Badge variant="mono">45s</Badge>
                  <Badge variant="accent">curiosity_gap</Badge>
                </div>

                <div className="space-y-1">
                  <span className="text-muted-foreground text-xs font-semibold uppercase tracking-wider">
                    Hook Giữ Chân 3s Đầu
                  </span>
                  <p className="text-base font-medium leading-relaxed">
                    &ldquo;Nếu bạn không thể hoàn thành việc này trong 2 phút,
                    bạn sẽ tiếp tục hối hận suốt 24 giờ tới...&rdquo;
                  </p>
                </div>

                <div className="border-border-subtle text-muted-foreground space-y-1.5 border-t pt-3 text-sm">
                  <p>
                    <span className="text-foreground font-medium">
                      Visual B-Roll —{" "}
                    </span>
                    Cận cảnh tay gạt phắt màn hình điện thoại, chuyển sang đồng
                    hồ cát đếm ngược gấp gáp.
                  </p>
                  <p>
                    <span className="text-foreground font-medium">
                      Tâm lý giữ chân —{" "}
                    </span>
                    Kích hoạt khoảng trống tò mò (curiosity gap) và nỗi sợ bỏ lỡ
                    trước khi người xem kịp lướt qua.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Section 3: Why RAG over generic LLMs */}
        <section id="comparison" className="w-full max-w-3xl px-6 py-20">
          <div className="mb-12 space-y-2 text-center">
            <span className="text-muted-foreground font-mono text-xs uppercase tracking-widest">
              Đột Phá Thuật Toán Giữ Chân
            </span>
            <h2 className="text-2xl font-semibold tracking-tight sm:text-3xl">
              Tại sao dùng Viral RAG thay vì LLM thông thường?
            </h2>
            <p className="text-muted-foreground mx-auto max-w-lg text-sm">
              Thuật toán TikTok, Shorts và Reels đánh giá video dựa trên tỷ lệ
              xem hết. Kịch bản chung chung thất bại ngay từ giây thứ 3.
            </p>
          </div>

          <div className="bg-border grid grid-cols-1 gap-px overflow-hidden rounded-lg md:grid-cols-2">
            <div className="bg-background space-y-4 p-6">
              <span className="text-muted-foreground text-xs font-semibold uppercase tracking-wider">
                LLM Thông Thường
              </span>
              <p className="text-muted-foreground text-sm italic leading-relaxed">
                &ldquo;Chào mừng các bạn quay trở lại kênh của mình. Hôm nay
                mình sẽ chia sẻ 3 mẹo cực hay...&rdquo;
              </p>
              <ul className="text-muted-foreground space-y-2.5 text-sm">
                <li className="flex items-start gap-2">
                  <X className="mt-0.5 h-4 w-4 shrink-0" />
                  <span>Mở đầu dài dòng, người xem lướt qua ngay.</span>
                </li>
                <li className="flex items-start gap-2">
                  <X className="mt-0.5 h-4 w-4 shrink-0" />
                  <span>Không có nhịp chuyển cảnh theo giây.</span>
                </li>
                <li className="flex items-start gap-2">
                  <X className="mt-0.5 h-4 w-4 shrink-0" />
                  <span>Không có sẵn AI prompt cho Midjourney hay Veo.</span>
                </li>
              </ul>
            </div>

            <div className="bg-background space-y-4 p-6">
              <span className="text-accent text-xs font-semibold uppercase tracking-wider">
                ViralCopilot RAG
              </span>
              <p className="text-sm font-medium italic leading-relaxed">
                &ldquo;99% người thất bại không phải vì thiếu tài năng, mà vì mở
                đầu ngày mới bằng việc kiểm tra email!&rdquo;
              </p>
              <ul className="space-y-2.5 text-sm">
                <li className="flex items-start gap-2">
                  <Check className="text-accent mt-0.5 h-4 w-4 shrink-0" />
                  <span>Hook đối sánh trực tiếp từ video triệu view.</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="text-accent mt-0.5 h-4 w-4 shrink-0" />
                  <span>
                    Storyboard chi tiết từng giây: lời thoại, B-roll, SFX, góc
                    máy.
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="text-accent mt-0.5 h-4 w-4 shrink-0" />
                  <span>Prompt sẵn dùng cho Midjourney, Flux, Veo 3.1.</span>
                </li>
              </ul>
            </div>
          </div>
        </section>

        {/* Section 4: How It Works */}
        <section
          id="how-it-works"
          className="bg-surface border-border-subtle w-full border-y"
        >
          <div className="mx-auto max-w-3xl px-6 py-20">
            <div className="mb-12 space-y-2 text-center">
              <span className="text-muted-foreground font-mono text-xs uppercase tracking-widest">
                Đơn Giản & Hiệu Quả
              </span>
              <h2 className="text-2xl font-semibold tracking-tight sm:text-3xl">
                Quy trình tạo kịch bản 3 bước
              </h2>
            </div>

            <div className="grid grid-cols-1 gap-8 sm:grid-cols-3">
              <div className="space-y-2">
                <span className="font-mono-code text-accent text-sm">01</span>
                <h3 className="text-sm font-semibold">Nhập Chủ Đề & Niche</h3>
                <p className="text-muted-foreground text-sm leading-relaxed">
                  Điền chủ đề, chọn thời lượng (15s–60s) và nền tảng (TikTok,
                  Shorts, Reels).
                </p>
              </div>

              <div className="space-y-2">
                <span className="font-mono-code text-accent text-sm">02</span>
                <h3 className="text-sm font-semibold">Truy Xuất Vector RAG</h3>
                <p className="text-muted-foreground text-sm leading-relaxed">
                  Hệ thống truy xuất pattern mở đầu giữ chân cao nhất từ
                  pgvector & MinIO.
                </p>
              </div>

              <div className="space-y-2">
                <span className="font-mono-code text-accent text-sm">03</span>
                <h3 className="text-sm font-semibold">
                  Xuất Kịch Bản & Prompts
                </h3>
                <p className="text-muted-foreground text-sm leading-relaxed">
                  Nhận storyboard từng giây và sao chép prompt sang Midjourney /
                  Veo ngay.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Section 5: Bottom CTA */}
        <section className="w-full max-w-3xl space-y-5 px-6 py-24 text-center">
          <h2 className="text-2xl font-semibold tracking-tight sm:text-3xl">
            Sẵn sàng tạo video triệu view tiếp theo?
          </h2>
          <p className="text-muted-foreground mx-auto max-w-md text-sm leading-relaxed">
            Trải nghiệm Studio tạo kịch bản dựa trên dữ liệu đối sánh thực tế.
          </p>
          <Button size="lg" asChild>
            <Link href="/dashboard" className="flex items-center">
              <span>Vào Studio Ngay</span>
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-border-subtle text-muted-foreground w-full border-t px-6 py-8 text-xs md:px-12">
        <div className="mx-auto flex max-w-3xl flex-col items-center justify-between gap-4 sm:flex-row">
          <span className="text-foreground font-medium">ViralCopilot AI</span>

          <div className="flex items-center space-x-6">
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noreferrer"
              className="hover:text-foreground flex items-center gap-1 transition-colors"
            >
              <span>FastAPI Docs</span>
              <ExternalLink className="h-3 w-3" />
            </a>
            <Link
              href="/dashboard/benchmarks"
              className="hover:text-foreground transition-colors"
            >
              Video Benchmarks
            </Link>
            <Link
              href="/dashboard/ingest"
              className="hover:text-foreground transition-colors"
            >
              MinIO Ingest
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
