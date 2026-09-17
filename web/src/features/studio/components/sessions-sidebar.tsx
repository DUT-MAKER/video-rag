"use client";

import * as React from "react";
import { Plus, Trash2, MessageSquare } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface SessionsSidebarProps {
  sessions: string[];
  activeSessionId: string | null;
  onSelectSession: (id: string) => void;
  onNewSession: () => void;
  onDeleteSession: (id: string) => void;
}

export function SessionsSidebar({
  sessions,
  activeSessionId,
  onSelectSession,
  onNewSession,
  onDeleteSession,
}: SessionsSidebarProps) {
  return (
    <aside className="flex h-full w-64 shrink-0 select-none flex-col border-r border-[#ffe6dc] bg-[#fffcfb]">
      {/* Top Action */}
      <div className="border-b border-[#ffe6dc] p-3.5">
        <Button
          onClick={onNewSession}
          className="flex w-full items-center justify-center gap-2"
          size="sm"
        >
          <Plus className="h-4 w-4" />
          <span>New Co-Pilot Chat</span>
        </Button>
      </div>

      {/* Session List */}
      <div className="flex-1 space-y-1 overflow-y-auto p-3">
        <div className="px-3 py-2 text-[10px] font-black uppercase tracking-wider text-[#6a4f44]">
          Cuộc trò chuyện ({sessions.length})
        </div>

        {activeSessionId === null && (
          <div className="flex select-none items-center justify-between rounded-full border border-[#ffe0d5] bg-[#fff0eb] px-3.5 py-2 text-xs font-bold text-[#ff7442] shadow-xs">
            <span className="truncate text-xs">
              + Cuộc trò chuyện mới
            </span>
            <span className="h-2 w-2 animate-pulse rounded-full bg-[#ff7442]" />
          </div>
        )}

        {sessions.length === 0 && activeSessionId !== null ? (
          <div className="px-3 py-6 text-center text-xs text-[#667085]">
            Chưa có phiên chat nào. Hãy bấm tạo mới.
          </div>
        ) : (
          sessions.map((id) => {
            const isActive = activeSessionId === id;
            return (
              <div
                key={id}
                onClick={() => onSelectSession(id)}
                className={cn(
                  "group flex cursor-pointer items-center justify-between rounded-full px-3.5 py-2 text-xs transition-all",
                  isActive
                    ? "border border-[#ffe6dc] bg-white font-black text-[#ff7442] shadow-[0_4px_14px_rgba(255,116,66,0.12)]"
                    : "text-[#475569] hover:bg-[#fff0eb] hover:text-[#0f172a]"
                )}
              >
                <div className="flex items-center gap-2 truncate">
                  <MessageSquare className={cn("h-3.5 w-3.5 shrink-0", isActive ? "text-[#ff7442]" : "text-[#94a3b8]")} />
                  <span className="font-mono-code truncate text-[11px]">
                    {id.length > 20 ? `${id.slice(0, 18)}...` : id}
                  </span>
                </div>

                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteSession(id);
                  }}
                  className="cursor-pointer rounded-full p-1 text-[#94a3b8] opacity-0 transition-all hover:bg-[#fff0eb] hover:text-rose-600 group-hover:opacity-100"
                  title="Xóa phiên"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
            );
          })
        )}
      </div>
    </aside>
  );
}

