import axios from "axios";
import { getAuthToken } from "./auth-token";
import type {
  ChatResponse,
  GenerateScriptPayload,
  IngestionResponseData,
  ReferencedPattern,
  SearchPatternItem,
  SessionDetail,
  SessionListResponse,
  ViralScript,
} from "./types";

export interface StandardApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
}

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  const token = getAuthToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// System Health Check
export async function getHealthStatus(): Promise<{
  status: string;
  service: string;
}> {
  try {
    const res = await api.get("/health");
    return res.data;
  } catch {
    return { status: "offline", service: "ViralCopilot API" };
  }
}

// Chat & Conversational Assistant
export async function getChatSessions(): Promise<string[]> {
  try {
    const res =
      await api.get<StandardApiResponse<SessionListResponse>>("/chat/sessions");
    return res.data.data.session_ids || [];
  } catch {
    return [];
  }
}

export async function getSessionDetail(
  sessionId: string
): Promise<SessionDetail | null> {
  try {
    const res = await api.get<StandardApiResponse<SessionDetail>>(
      `/chat/sessions/${sessionId}`
    );
    return res.data.data;
  } catch {
    return null;
  }
}

export async function deleteChatSession(sessionId: string): Promise<boolean> {
  try {
    await api.delete(`/chat/sessions/${sessionId}`);
    return true;
  } catch {
    return false;
  }
}

export async function sendChatMessage(payload: {
  message: string;
  session_id?: string;
  top_k_references?: number;
}): Promise<ChatResponse> {
  const res = await api.post<StandardApiResponse<ChatResponse>>(
    "/chat",
    payload
  );
  return res.data.data;
}

export interface StreamMetadataEvent {
  session_id: string;
  intent?: string;
  referenced_patterns?: ReferencedPattern[];
}

export async function streamChatMessage({
  payload,
  onMetadata,
  onToken,
  onDone,
  onError,
  signal,
}: {
  payload: {
    message: string;
    session_id?: string;
    top_k_references?: number;
  };
  onMetadata?: (meta: StreamMetadataEvent) => void;
  onToken?: (token: string) => void;
  onDone?: (sessionId: string) => void;
  onError?: (err: Error) => void;
  signal?: AbortSignal;
}): Promise<void> {
  const token = getAuthToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  let lastSessionId = payload.session_id || "";
  let isDoneTriggered = false;

  const triggerDone = (sid?: string) => {
    if (!isDoneTriggered) {
      isDoneTriggered = true;
      onDone?.(sid || lastSessionId);
    }
  };

  try {
    const response = await fetch(`${API_BASE_URL}/chat/stream`, {
      method: "POST",
      headers,
      body: JSON.stringify(payload),
      signal,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(
        `Stream failed (${response.status}): ${errorText || response.statusText}`
      );
    }

    if (!response.body) {
      throw new Error("Response body is not readable");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const normalized = buffer.replace(/\r\n/g, "\n");
        const parts = normalized.split("\n\n");
        buffer = parts.pop() ?? "";

        for (const part of parts) {
          const lines = part.split("\n");
          for (const line of lines) {
            const trimmed = line.trim();
            if (!trimmed.startsWith("data:")) continue;

            const dataStr = trimmed.replace(/^data:\s*/, "");
            if (dataStr === "[DONE]") {
              triggerDone();
              return;
            }

            try {
              const parsed = JSON.parse(dataStr);
              if (parsed.session_id) {
                lastSessionId = parsed.session_id;
              }

              if (parsed.event === "metadata") {
                onMetadata?.({
                  session_id: parsed.session_id,
                  intent: parsed.intent,
                  referenced_patterns: parsed.referenced_patterns || [],
                });
              } else if (parsed.event === "token") {
                if (typeof parsed.token === "string") {
                  onToken?.(parsed.token);
                }
              } else if (parsed.event === "done") {
                triggerDone(parsed.session_id);
                return;
              }
            } catch (jsonErr) {
              console.warn("Failed to parse SSE JSON chunk:", dataStr, jsonErr);
            }
          }
        }
      }

      // If buffer still has remaining data
      if (buffer.trim()) {
        const lines = buffer.split("\n");
        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed.startsWith("data:")) {
            const dataStr = trimmed.replace(/^data:\s*/, "");
            if (dataStr === "[DONE]") {
              triggerDone();
              return;
            }
          }
        }
      }

      triggerDone();
    } finally {
      reader.releaseLock();
    }
  } catch (err: unknown) {
    if (signal?.aborted) return;
    const error = err instanceof Error ? err : new Error(String(err));
    onError?.(error);
    throw error;
  }
}

// 1-Click Viral Script Generator
export async function generateViralScript(
  payload: GenerateScriptPayload
): Promise<ViralScript> {
  const res = await api.post<StandardApiResponse<ViralScript>>(
    "/generate",
    payload
  );
  return res.data.data;
}

// Semantic Search over Benchmark Patterns
export async function searchBenchmarkPatterns(
  query: string,
  top_k: number = 6
): Promise<SearchPatternItem[]> {
  try {
    const res = await api.post<StandardApiResponse<SearchPatternItem[]>>(
      "/search",
      {
        query,
        top_k,
      }
    );
    return res.data.data || [];
  } catch {
    return [];
  }
}

// Knowledge Store Ingestion
export async function ingestKnowledge(
  filePath: string = "data/samples/sample_viral_videos.json"
): Promise<IngestionResponseData> {
  const res = await api.post<StandardApiResponse<IngestionResponseData>>(
    "/ingest",
    {
      file_path: filePath,
    }
  );
  return res.data.data;
}
