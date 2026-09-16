"use client";

import * as React from "react";
import { Menu } from "lucide-react";
import { SessionsSidebar } from "./sessions-sidebar";
import { ChatFeed } from "./chat-feed";
import { StoryboardInspector } from "./storyboard-inspector";
import {
  deleteChatSession,
  getChatSessions,
  getSessionDetail,
  sendChatMessage,
  streamChatMessage,
} from "@/lib/api";
import type { ChatMessage, ViralScript } from "@/lib/types";

export function StudioView() {
  const [sessions, setSessions] = React.useState<string[]>([]);
  const [activeSessionId, setActiveSessionId] = React.useState<string | null>(
    null
  );
  const [messages, setMessages] = React.useState<ChatMessage[]>([]);
  const [currentScript, setCurrentScript] = React.useState<ViralScript | null>(
    null
  );
  const [isLoading, setIsLoading] = React.useState(false);

  const [showSidebar, setShowSidebar] = React.useState(true);
  const [showInspector, setShowInspector] = React.useState(true);
  const abortControllerRef = React.useRef<AbortController | null>(null);

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

  const hasLoadedInitialSessionsRef = React.useRef(false);

  // Load sessions on mount once
  React.useEffect(() => {
    let ignore = false;
    getChatSessions()
      .then((sessionIds) => {
        if (!ignore) {
          setSessions(sessionIds);
          if (!hasLoadedInitialSessionsRef.current) {
            hasLoadedInitialSessionsRef.current = true;
            if (sessionIds.length > 0) {
              selectSession(sessionIds[0]);
            }
          }
        }
      })
      .catch((err) => {
        console.error("Failed to load sessions:", err);
      });

    return () => {
      ignore = true;
    };
  }, [selectSession]);

  const handleNewSession = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
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

  const handleSendMessage = async (text: string, topK: number) => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    const controller = new AbortController();
    abortControllerRef.current = controller;

    const userMsg: ChatMessage = {
      role: "user",
      content: text,
      timestamp: Date.now() / 1000,
    };
    const initialAssistantMsg: ChatMessage = {
      role: "assistant",
      content: "",
      timestamp: Date.now() / 1000,
      referenced_patterns: [],
    };

    setMessages((prev) => [...prev, userMsg, initialAssistantMsg]);
    setIsLoading(true);

    let resolvedSessionId = activeSessionId;
    let hasReceivedToken = false;

    try {
      await streamChatMessage({
        payload: {
          message: text,
          session_id: activeSessionId || undefined,
          top_k_references: topK,
        },
        signal: controller.signal,
        onMetadata: (meta) => {
          if (meta.session_id) {
            resolvedSessionId = meta.session_id;
            if (!activeSessionId) {
              setActiveSessionId(meta.session_id);
            }
            setSessions((prev) => [
              meta.session_id,
              ...prev.filter((id) => id !== meta.session_id),
            ]);
          }
          if (meta.referenced_patterns && meta.referenced_patterns.length > 0) {
            setMessages((prev) => {
              const lastIdx = prev.length - 1;
              if (lastIdx >= 0 && prev[lastIdx].role === "assistant") {
                const updated = [...prev];
                updated[lastIdx] = {
                  ...updated[lastIdx],
                  referenced_patterns: meta.referenced_patterns,
                };
                return updated;
              }
              return prev;
            });
          }
        },
        onToken: (token) => {
          hasReceivedToken = true;
          setMessages((prev) => {
            const lastIdx = prev.length - 1;
            if (lastIdx >= 0 && prev[lastIdx].role === "assistant") {
              const updated = [...prev];
              updated[lastIdx] = {
                ...updated[lastIdx],
                content: updated[lastIdx].content + token,
              };
              return updated;
            }
            return prev;
          });
        },
        onDone: async (finalSessionId) => {
          const sid = finalSessionId || resolvedSessionId;
          if (sid) {
            try {
              const detail = await getSessionDetail(sid);
              if (detail?.current_script) {
                setCurrentScript(detail.current_script);
                setShowInspector(true);
              }
            } catch (err) {
              console.error(
                "Failed to fetch session detail after stream:",
                err
              );
            }
          }
        },
      });
    } catch (err: unknown) {
      if (controller.signal.aborted) return;
      console.warn(
        "SSE stream failed or interrupted, falling back to sync:",
        err
      );

      // If no token was received yet, try fallback to sync sendChatMessage
      if (!hasReceivedToken) {
        try {
          const res = await sendChatMessage({
            message: text,
            session_id: activeSessionId || undefined,
            top_k_references: topK,
          });

          if (!activeSessionId && res.session_id) {
            setActiveSessionId(res.session_id);
            setSessions((prev) => [
              res.session_id,
              ...prev.filter((id) => id !== res.session_id),
            ]);
          }

          setMessages((prev) => {
            const lastIdx = prev.length - 1;
            if (lastIdx >= 0 && prev[lastIdx].role === "assistant") {
              const updated = [...prev];
              updated[lastIdx] = {
                role: "assistant",
                content: res.reply,
                timestamp: res.created_at,
                referenced_patterns: res.referenced_patterns,
              };
              return updated;
            }
            return prev;
          });

          if (res.session_id) {
            const detail = await getSessionDetail(res.session_id);
            if (detail?.current_script) {
              setCurrentScript(detail.current_script);
              setShowInspector(true);
            }
          }
          return;
        } catch (syncErr) {
          console.error("Sync fallback also failed:", syncErr);
        }
      }

      // If tokens were partially streamed or fallback failed, show error
      setMessages((prev) => {
        const lastIdx = prev.length - 1;
        if (lastIdx >= 0 && prev[lastIdx].role === "assistant") {
          const updated = [...prev];
          const currentContent = updated[lastIdx].content;
          updated[lastIdx] = {
            ...updated[lastIdx],
            content: currentContent
              ? currentContent + "\n\n*(Mất kết nối stream với máy chủ)*"
              : "Không thể kết nối với AI Assistant. Hãy chắc chắn Backend FastAPI đang chạy tại http://localhost:8000.",
          };
          return updated;
        }
        return prev;
      });
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  };

  React.useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return (
    <div className="bg-background text-foreground flex h-[calc(100vh-3.5rem)] w-full flex-col overflow-hidden">
      {/* Studio Subheader */}
      <div className="border-border bg-surface flex h-11 shrink-0 select-none items-center justify-between border-b px-4">
        <div className="flex items-center space-x-3">
          <button
            type="button"
            onClick={() => setShowSidebar((prev) => !prev)}
            className="text-muted-foreground hover:text-foreground hover:bg-surface-hover cursor-pointer rounded-md p-1.5 transition-colors"
            title="Toggle Sessions Sidebar"
          >
            <Menu className="h-4 w-4" />
          </button>

          <span className="text-foreground text-xs font-semibold tracking-tight">
            Conversational Studio
          </span>
        </div>

        {/* Right Actions */}
        <div className="flex items-center space-x-2">
          <button
            type="button"
            onClick={() => setShowInspector((prev) => !prev)}
            className={`cursor-pointer rounded-md border px-2.5 py-1 text-xs font-medium transition-all ${
              showInspector
                ? "bg-background text-foreground border-accent font-semibold"
                : "bg-background text-muted-foreground border-border hover:bg-surface-hover hover:text-foreground"
            }`}
          >
            Script Inspector
          </button>
        </div>
      </div>

      {/* Main 3 Columns */}
      <div className="relative flex flex-1 overflow-hidden">
        {showSidebar && (
          <SessionsSidebar
            sessions={sessions}
            activeSessionId={activeSessionId}
            onSelectSession={selectSession}
            onNewSession={handleNewSession}
            onDeleteSession={handleDeleteSession}
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
