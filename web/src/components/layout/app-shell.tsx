"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

interface AppShellProps {
  children: React.ReactNode;
}

const navItems = [
  { href: "/dashboard", label: "Studio" },
  { href: "/dashboard/videos", label: "Quản Lý Video" },
  { href: "/dashboard/generator", label: "1-Click Generator" },
  { href: "/dashboard/benchmarks", label: "Kho Video Mẫu" },
  { href: "/dashboard/ingest", label: "Nạp Dữ Liệu" },
];

export function AppShell({ children }: AppShellProps) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-white text-[#0f172a] [font-family:var(--font-body)]">
      {/* Top Universal App Navigation Bar */}
      <header className="sticky top-0 z-40 border-b border-[#ffe6dc] bg-[#fffcfb]/95 px-4 backdrop-blur-md md:px-8">
        <div className="mx-auto flex h-16 max-w-[1520px] items-center justify-between">
          {/* Left: Brand Logo & Navigation */}
          <div className="flex items-center space-x-8">
            <Link
              href="/dashboard"
              className="group flex items-center space-x-3"
            >
              {/* Markee Style Circular Logo */}
              <div className="relative flex h-10 w-10 items-center justify-center rounded-full bg-[linear-gradient(135deg,#ff7442,#ffa382)] text-sm font-black text-white shadow-[0_8px_20px_rgba(255,116,66,0.25)] transition-transform group-hover:scale-105">
                VC
                <span className="absolute right-1 top-1 h-2 w-2 rounded-full bg-white shadow-xs" />
              </div>
              <div className="flex flex-col">
                <span className="text-sm font-black tracking-tight text-[#0f172a] [font-family:var(--font-heading)]">
                  ViralCopilot
                </span>
                <span className="text-[10px] font-bold text-[#ff7442]">
                  MARKEE DESK
                </span>
              </div>
            </Link>

            {/* Clean Typography-first Navigation */}
            <nav className="hidden items-center space-x-1.5 md:flex">
              {navItems.map((item) => {
                const isActive =
                  item.href === "/dashboard"
                    ? pathname === "/dashboard"
                    : pathname.startsWith(item.href);

                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn(
                      "select-none rounded-full px-4 py-2 text-xs font-bold transition-all",
                      isActive
                        ? "bg-[linear-gradient(90deg,#ff7442,#ff8c64)] text-white shadow-[0_8px_20px_rgba(255,116,66,0.25)]"
                        : "text-[#475569] hover:bg-[#fff0eb] hover:text-[#0f172a]"
                    )}
                  >
                    {item.label}
                  </Link>
                );
              })}
            </nav>
          </div>

          {/* Right: Creator Studio Status */}
          <div className="flex items-center space-x-3">
            <div className="hidden items-center gap-1.5 rounded-full border border-[#ffe0d5] bg-[#fff0eb] px-3 py-1 text-xs font-bold text-[#ff7442] sm:flex">
              <Sparkles className="h-3.5 w-3.5 fill-[#ff7442]" />
              <span>AI Active</span>
            </div>
            <div className="flex h-9 w-9 items-center justify-center rounded-full border border-[#ffe6dc] bg-white font-bold text-[#ff7442] shadow-xs">
              VC
            </div>
          </div>
        </div>
      </header>

      {/* Main Page Content with Markee Shell */}
      <main className="bg-[linear-gradient(135deg,#fff6f2_0%,#ffffff_48%,#ffeedd_100%)] p-3 sm:p-5 lg:p-6">
        <div className="mx-auto min-h-[calc(100vh-6.5rem)] max-w-[1520px] rounded-[28px] border border-[#ffe6dc] bg-[#fffcfb]/95 p-3 shadow-[0_30px_80px_rgba(255,116,66,0.08)] sm:p-5 lg:p-6">
          {children}
        </div>
      </main>
    </div>
  );
}

