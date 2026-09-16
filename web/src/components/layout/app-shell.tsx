"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Sparkles,
  Zap,
  Film,
  Database,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface AppShellProps {
  children: React.ReactNode;
}

const navItems = [
  {
    href: "/dashboard",
    label: "Studio Co-Pilot",
    icon: Sparkles,
    badge: "Live",
  },
  {
    href: "/dashboard/generator",
    label: "1-Click Generator",
    icon: Zap,
  },
  {
    href: "/dashboard/benchmarks",
    label: "Benchmark Library",
    icon: Film,
  },
  {
    href: "/dashboard/ingest",
    label: "Knowledge Ingest",
    icon: Database,
  },
];

export function AppShell({ children }: AppShellProps) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-[#09090b] text-neutral-100 flex flex-col antialiased selection:bg-neutral-800 selection:text-white">
      {/* Top Universal App Navigation Bar */}
      <header className="h-14 border-b border-neutral-800 bg-[#0c0c0e]/90 backdrop-blur-md px-4 md:px-6 flex items-center justify-between shrink-0 z-40 sticky top-0">
        {/* Left: Brand Logo & Workspace */}
        <div className="flex items-center space-x-6">
          <Link href="/dashboard" className="flex items-center space-x-2.5 group">
            <div className="w-7 h-7 rounded-lg bg-neutral-100 text-neutral-950 flex items-center justify-center font-bold shadow-xs group-hover:bg-neutral-200 transition-colors">
              <Sparkles className="w-4 h-4 fill-neutral-950" />
            </div>
            <div className="flex items-center space-x-2">
              <span className="font-semibold text-sm tracking-tight text-white">
                ViralCopilot
              </span>
              <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded-sm bg-neutral-900 text-neutral-400 border border-neutral-800 tracking-wider">
                Studio
              </span>
            </div>
          </Link>

          {/* Horizontal Nav Links for Desktop */}
          <nav className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive =
                item.href === "/dashboard"
                  ? pathname === "/dashboard"
                  : pathname.startsWith(item.href);

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center space-x-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all",
                    isActive
                      ? "bg-[#18181b] text-white border border-neutral-700/60 shadow-xs"
                      : "text-neutral-400 hover:text-neutral-200 hover:bg-neutral-900/60"
                  )}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{item.label}</span>
                  {item.badge && (
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  )}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Right: Quick Indicators & User Status */}
        <div className="flex items-center space-x-3 text-xs">
          <div className="hidden lg:flex items-center space-x-2 text-[11px] text-neutral-400">
            <span className="flex items-center gap-1 px-2 py-0.5 rounded-md bg-neutral-900 border border-neutral-800">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
              pgvector online
            </span>
            <span className="flex items-center gap-1 px-2 py-0.5 rounded-md bg-neutral-900 border border-neutral-800">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-400"></span>
              MinIO ready
            </span>
          </div>

          <div className="h-4 w-[1px] bg-neutral-800 hidden sm:block" />

          {/* User profile capsule */}
          <div className="flex items-center space-x-2">
            <div className="w-7 h-7 rounded-full bg-neutral-800 border border-neutral-700 flex items-center justify-center text-xs font-mono font-medium text-neutral-300">
              VC
            </div>
            <span className="text-xs text-neutral-300 hidden sm:inline">
              Creator Studio
            </span>
          </div>
        </div>
      </header>

      {/* Main Page Content */}
      <main className="flex-1 flex flex-col overflow-hidden bg-[#09090b]">
        {children}
      </main>
    </div>
  );
}
