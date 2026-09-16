"use client";

import * as React from "react";
import { Plus, Trash2 } from "lucide-react";
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
    <aside className="border-border bg-background flex h-full w-64 shrink-0 select-none flex-col border-r">
      {/* Top Action */}
      <div className="border-border border-b p-3">
        <Button
          onClick={onNewSession}
          className="flex w-full items-center justify-center gap-2"
          size="sm"
        >
          <Plus className="h-3.5 w-3.5" />
          <span>New Co-Pilot Chat</span>
        </Button>
      </div>

      {/* Session List */}
      <div className="flex-1 space-y-1 overflow-y-auto p-2">
        <div className="text-muted-foreground px-2.5 py-1.5 text-[10px] font-bold uppercase tracking-wider">
          Cuộc trò chuyện ({sessions.length})
        </div>

        {activeSessionId === null && (
          <div className="bg-surface text-foreground border-accent/40 flex select-none items-center justify-between rounded-lg border px-3 py-2 text-xs font-semibold">
            <span className="text-accent truncate text-[11px] font-medium">
              + Cuộc trò chuyện mới
            </span>
            <span className="bg-accent h-1.5 w-1.5 animate-pulse rounded-full" />
          </div>
        )}

        {sessions.length === 0 && activeSessionId !== null ? (
          <div className="text-muted-foreground px-3 py-6 text-center text-xs">
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
                  "group flex cursor-pointer items-center justify-between rounded-lg px-3 py-2 text-xs transition-all",
                  isActive
                    ? "bg-surface text-foreground border-border border font-semibold"
                    : "text-muted-foreground hover:text-foreground hover:bg-surface-hover"
                )}
              >
                <span className="font-mono-code truncate text-[11px]">
                  {id.length > 22 ? `${id.slice(0, 20)}...` : id}
                </span>

                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteSession(id);
                  }}
                  className="hover:bg-surface-hover text-muted-foreground hover:text-foreground cursor-pointer rounded p-1 opacity-0 transition-all group-hover:opacity-100"
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
