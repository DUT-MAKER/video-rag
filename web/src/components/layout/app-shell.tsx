"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

interface AppShellProps {
  children: React.ReactNode;
}

const navItems = [
  { href: "/dashboard", label: "Studio" },
  { href: "/dashboard/generator", label: "1-Click Generator" },
  { href: "/dashboard/benchmarks", label: "Kho Video Mẫu" },
  { href: "/dashboard/ingest", label: "Nạp Dữ Liệu" },
];

export function AppShell({ children }: AppShellProps) {
  const pathname = usePathname();

  return (
    <div className="bg-background text-foreground selection:bg-accent/30 flex min-h-screen flex-col antialiased selection:text-white">
      {/* Top Universal App Navigation Bar */}
      <header className="border-border bg-background/95 sticky top-0 z-40 flex h-14 shrink-0 items-center justify-between border-b px-4 backdrop-blur-md md:px-6">
        {/* Left: Brand Logo & Navigation */}
        <div className="flex items-center space-x-6">
          <Link
            href="/dashboard"
            className="group flex items-center space-x-2.5"
          >
            <div className="bg-accent text-background flex h-6 w-6 items-center justify-center rounded-lg text-xs font-semibold tracking-tighter">
              VC
            </div>
            <span className="text-foreground text-sm font-semibold tracking-tight">
              ViralCopilot
            </span>
          </Link>

          {/* Clean Typography-first Navigation */}
          <nav className="hidden items-center space-x-1 md:flex">
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
                    "select-none rounded-md px-3 py-1.5 text-xs font-medium transition-all",
                    isActive
                      ? "bg-surface text-foreground border-border border font-semibold"
                      : "text-muted-foreground hover:text-foreground hover:bg-surface/60"
                  )}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Right: Profile */}
        <div className="flex items-center space-x-2">
          <div className="bg-surface border-border text-foreground flex h-7 w-7 items-center justify-center rounded-full border font-mono text-xs font-medium">
            VC
          </div>
          <span className="text-foreground hidden text-xs font-medium sm:inline">
            Creator Studio
          </span>
        </div>
      </header>

      {/* Main Page Content */}
      <main className="bg-background flex flex-1 flex-col overflow-hidden">
        {children}
      </main>
    </div>
  );
}
