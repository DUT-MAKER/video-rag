import axios from "axios";
import { getAuthToken } from "./auth-token";
import type {
  ChatResponse,
  GenerateScriptPayload,
  IngestionResponseData,
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

export const api = axios.create({
  baseURL:
    process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1",
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
export async function getHealthStatus(): Promise<{ status: string; service: string }> {
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
    const res = await api.get<StandardApiResponse<SessionListResponse>>("/chat/sessions");
    return res.data.data.session_ids || [];
  } catch {
    return [];
  }
}

export async function getSessionDetail(sessionId: string): Promise<SessionDetail | null> {
  try {
    const res = await api.get<StandardApiResponse<SessionDetail>>(`/chat/sessions/${sessionId}`);
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
  const res = await api.post<StandardApiResponse<ChatResponse>>("/chat", payload);
  return res.data.data;
}

// 1-Click Viral Script Generator
export async function generateViralScript(
  payload: GenerateScriptPayload
): Promise<ViralScript> {
  const res = await api.post<StandardApiResponse<ViralScript>>("/generate", payload);
  return res.data.data;
}

// Semantic Search over Benchmark Patterns
export async function searchBenchmarkPatterns(
  query: string,
  top_k: number = 6
): Promise<SearchPatternItem[]> {
  try {
    const res = await api.post<StandardApiResponse<SearchPatternItem[]>>("/search", {
      query,
      top_k,
    });
    return res.data.data || [];
  } catch {
    return [];
  }
}

// Knowledge Store Ingestion
export async function ingestKnowledge(
  filePath: string = "data/samples/sample_viral_videos.json"
): Promise<IngestionResponseData> {
  const res = await api.post<StandardApiResponse<IngestionResponseData>>("/ingest", {
    file_path: filePath,
  });
  return res.data.data;
}
