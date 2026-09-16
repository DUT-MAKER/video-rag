"use client";

import * as React from "react";
import { Plus, MessageSquare, Trash2, Database, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface SessionsSidebarProps {
  sessions: string[];
  activeSessionId: string | null;
  onSelectSession: (id: string) => void;
  onNewSession: () => void;
  onDeleteSession: (id: string) => void;
  onRefreshKnowledge?: () => void;
  isRefreshing?: boolean;
}

export function SessionsSidebar({
  sessions,
  activeSessionId,
  onSelectSession,
  onNewSession,
  onDeleteSession,
  onRefreshKnowledge,
  isRefreshing = false,
}: SessionsSidebarProps) {
  return (
    <aside className="w-64 border-r border-neutral-800 bg-[#0c0c0e] flex flex-col h-full shrink-0 select-none">
      {/* Top Action */}
      <div className="p-3 border-b border-neutral-800">
        <Button
          onClick={onNewSession}
          className="w-full flex items-center justify-center gap-2"
          size="sm"
        >
          <Plus className="w-4 h-4" />
          <span>New Co-Pilot Chat</span>
        </Button>
      </div>

      {/* Session List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        <div className="text-[10px] font-semibold tracking-wider uppercase text-neutral-500 px-2.5 py-1.5">
          Conversations ({sessions.length})
        </div>

        {sessions.length === 0 ? (
          <div className="px-3 py-6 text-center text-xs text-neutral-500">
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
                  "group flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-all cursor-pointer",
                  isActive
                    ? "bg-[#18181b] text-white border border-neutral-700/60 shadow-xs"
                    : "text-neutral-400 hover:text-neutral-200 hover:bg-neutral-900/60"
                )}
              >
                <div className="flex items-center space-x-2 truncate">
                  <MessageSquare className="w-3.5 h-3.5 shrink-0 opacity-60 group-hover:opacity-100" />
                  <span className="truncate font-mono-code text-[11px]">
                    {id.length > 20 ? `${id.slice(0, 18)}...` : id}
                  </span>
                </div>

                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteSession(id);
                  }}
                  className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-neutral-800 text-neutral-500 hover:text-red-400 transition-all cursor-pointer"
                  title="Delete session"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </div>
            );
          })
        )}
      </div>

      {/* Benchmark Store Footer */}
      <div className="p-3 border-t border-neutral-800 bg-black/30 text-xs space-y-1.5">
        <div className="flex items-center justify-between text-neutral-400 text-[11px]">
          <span className="flex items-center gap-1.5">
            <Database className="w-3 h-3 text-neutral-500" />
            Knowledge Store
          </span>
          <span className="font-mono text-[10px] text-neutral-300">pgvector</span>
        </div>

        {onRefreshKnowledge && (
          <button
            type="button"
            onClick={onRefreshKnowledge}
            disabled={isRefreshing}
            className="w-full text-left text-[10px] text-neutral-400 hover:text-white flex items-center space-x-1.5 py-1 cursor-pointer transition-colors disabled:opacity-50"
          >
            <RefreshCw
              className={cn("w-3 h-3 text-neutral-500", isRefreshing && "animate-spin")}
            />
            <span>Refresh Benchmark Data</span>
          </button>
        )}
      </div>
    </aside>
  );
}
