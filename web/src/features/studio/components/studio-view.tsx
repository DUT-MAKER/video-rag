"use client";

import * as React from "react";
import {
  Menu,
  Film,
  Sparkles,
  Database,
  Cpu,
  BookOpen,
} from "lucide-react";
import { SessionsSidebar } from "./sessions-sidebar";
import { ChatFeed } from "./chat-feed";
import { StoryboardInspector } from "./storyboard-inspector";
import {
  deleteChatSession,
  getChatSessions,
  getSessionDetail,
  ingestKnowledge,
  sendChatMessage,
} from "@/lib/api";
import type { ChatMessage, ViralScript } from "@/lib/types";

export function StudioView() {
  const [sessions, setSessions] = React.useState<string[]>([]);
  const [activeSessionId, setActiveSessionId] = React.useState<string | null>(null);
  const [messages, setMessages] = React.useState<ChatMessage[]>([]);
  const [currentScript, setCurrentScript] = React.useState<ViralScript | null>(null);
  const [isLoading, setIsLoading] = React.useState(false);
  const [isRefreshingKnowledge, setIsRefreshingKnowledge] = React.useState(false);

  const [showSidebar, setShowSidebar] = React.useState(true);
  const [showInspector, setShowInspector] = React.useState(true);

  const selectSession = React.useCallback(async (sessionId: string) => {
    setActiveSessionId(sessionId);
    setIsLoading(true);
    try {
      const detail = await getSessionDetail(sessionId);
      if (detail) {
        setMessages(detail.messages || []);
        if (detail.current_script) {
          setCurrentScript(detail.current_script);
        }
      }
    } catch (err) {
      console.error("Failed to select session:", err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Load sessions on mount
  React.useEffect(() => {
    let ignore = false;
    getChatSessions()
      .then((sessionIds) => {
        if (!ignore) {
          setSessions(sessionIds);
          if (sessionIds.length > 0 && !activeSessionId) {
            selectSession(sessionIds[0]);
          }
        }
      })
      .catch((err) => {
        console.error("Failed to load sessions:", err);
      });

    return () => {
      ignore = true;
    };
  }, [activeSessionId, selectSession]);

  const handleNewSession = () => {
    setActiveSessionId(null);
    setMessages([]);
    setCurrentScript(null);
  };

  const handleDeleteSession = async (sessionId: string) => {
    await deleteChatSession(sessionId);
    const updated = sessions.filter((id) => id !== sessionId);
    setSessions(updated);
    if (activeSessionId === sessionId) {
      handleNewSession();
    }
  };

  const handleRefreshKnowledge = async () => {
    setIsRefreshingKnowledge(true);
    try {
      await ingestKnowledge();
      alert("Đã đồng bộ lại Knowledge Store pgvector thành công!");
    } catch (err) {
      console.error("Ingest failed:", err);
    } finally {
      setIsRefreshingKnowledge(false);
    }
  };

  const handleSendMessage = async (text: string, topK: number) => {
    const userMsg: ChatMessage = {
      role: "user",
      content: text,
      timestamp: Date.now() / 1000,
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const res = await sendChatMessage({
        message: text,
        session_id: activeSessionId || undefined,
        top_k_references: topK,
      });

      if (!activeSessionId && res.session_id) {
        setActiveSessionId(res.session_id);
        setSessions((prev) => [res.session_id, ...prev.filter((id) => id !== res.session_id)]);
      }

      const assistantMsg: ChatMessage = {
        role: "assistant",
        content: res.reply,
        timestamp: res.created_at,
        referenced_patterns: res.referenced_patterns,
      };

      setMessages((prev) => [...prev, assistantMsg]);

      // Check if session has a newly generated script
      if (res.session_id) {
        const detail = await getSessionDetail(res.session_id);
        if (detail?.current_script) {
          setCurrentScript(detail.current_script);
          setShowInspector(true);
        }
      }
    } catch (err) {
      console.error("Chat turn failed:", err);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "⚠️ Không thể kết nối tới Backend API. Hãy kiểm tra dịch vụ backend đang chạy ở cổng 8000.",
          timestamp: Date.now() / 1000,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-3.5rem)] w-full overflow-hidden bg-[#09090b] text-neutral-100">
      {/* Studio Subheader */}
      <div className="h-11 border-b border-neutral-800 bg-[#0c0c0e] px-4 flex items-center justify-between shrink-0 select-none">
        <div className="flex items-center space-x-3">
          <button
            type="button"
            onClick={() => setShowSidebar((prev) => !prev)}
            className="p-1.5 rounded-md text-neutral-400 hover:text-white hover:bg-neutral-800 transition-colors cursor-pointer"
            title="Toggle Sessions Sidebar"
          >
            <Menu className="w-4 h-4" />
          </button>

          <div className="flex items-center space-x-2">
            <Sparkles className="w-3.5 h-3.5 text-neutral-300" />
            <span className="text-xs font-semibold text-neutral-200">
              Conversational Studio
            </span>
          </div>
        </div>

        {/* System Status Badges */}
        <div className="hidden sm:flex items-center space-x-2 text-[11px]">
          <div className="flex items-center space-x-1.5 px-2 py-0.5 rounded-md bg-neutral-900 border border-neutral-800 text-emerald-400 font-mono">
            <Database className="w-3 h-3 text-emerald-500" />
            <span>pgvector</span>
          </div>

          <div className="flex items-center space-x-1.5 px-2 py-0.5 rounded-md bg-neutral-900 border border-neutral-800 text-neutral-300 font-mono">
            <Cpu className="w-3 h-3 text-neutral-400" />
            <span>DUT AI LLM</span>
          </div>
        </div>

        {/* Action button */}
        <div className="flex items-center space-x-2">
          <button
            type="button"
            onClick={() => setShowInspector((prev) => !prev)}
            className="flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-neutral-900 hover:bg-neutral-800 text-neutral-300 hover:text-white text-xs font-medium border border-neutral-800 transition-all cursor-pointer"
          >
            <Film className="w-3.5 h-3.5 text-orange-400" />
            <span>Script Inspector</span>
          </button>

          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noreferrer"
            className="p-1.5 rounded-md text-neutral-400 hover:text-white hover:bg-neutral-800 transition-colors"
            title="Open FastAPI Docs"
          >
            <BookOpen className="w-3.5 h-3.5" />
          </a>
        </div>
      </div>

      {/* Main 3 Columns */}
      <div className="flex-1 flex overflow-hidden relative">
        {showSidebar && (
          <SessionsSidebar
            sessions={sessions}
            activeSessionId={activeSessionId}
            onSelectSession={selectSession}
            onNewSession={handleNewSession}
            onDeleteSession={handleDeleteSession}
            onRefreshKnowledge={handleRefreshKnowledge}
            isRefreshing={isRefreshingKnowledge}
          />
        )}

        <ChatFeed
          messages={messages}
          isLoading={isLoading}
          onSendMessage={handleSendMessage}
          onSelectQuickPrompt={(prompt) => handleSendMessage(prompt, 3)}
        />

        {showInspector && (
          <StoryboardInspector
            script={currentScript}
            onClose={() => setShowInspector(false)}
          />
        )}
      </div>
    </div>
  );
}
