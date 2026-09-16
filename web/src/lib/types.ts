export type PlatformTarget = "tiktok" | "youtube_shorts" | "instagram_reels";

export type HookType =
  | "problem_agitate"
  | "contrarian"
  | "curiosity_gap"
  | "shocking_fact"
  | "story_loop"
  | "custom";

export type MessageRole = "user" | "assistant" | "system";

export type ChatIntent =
  | "general_chat"
  | "generate_script"
  | "refine_hook"
  | "refine_scene"
  | "search_benchmark"
  | "export_prompts";

export interface ReferencedPattern {
  original_caption: string;
  matched_hook: string;
  minio_video_url: string;
  similarity_score: number;
  summary: string;
  image_url: string;
}

export interface HookData {
  hook_type: HookType;
  script: string;
  visual_action: string;
  retention_rationale: string;
  duration_seconds: number;
}

export interface SceneData {
  scene_number: number;
  time_range: string;
  narration: string;
  visual_action: string;
  image_prompt: string;
  video_prompt: string;
  audio_sfx_cue: string;
}

export interface CallToActionData {
  script: string;
  visual_cue: string;
}

export interface ViralScript {
  title: string;
  target_niche: string;
  platform: PlatformTarget;
  target_duration_seconds: number;
  hook: HookData;
  scenes: SceneData[];
  call_to_action: CallToActionData;
  references: ReferencedPattern[];
  suggested_hashtags: string[];
}

export interface ChatMessage {
  role: MessageRole;
  content: string;
  timestamp: number;
  referenced_patterns?: ReferencedPattern[];
}

export interface ChatResponse {
  session_id: string;
  reply: string;
  role: MessageRole;
  intent: ChatIntent;
  referenced_patterns: ReferencedPattern[];
  created_at: number;
}

export interface SessionDetail {
  session_id: string;
  message_count: number;
  created_at: number;
  updated_at: number;
  messages: ChatMessage[];
  current_script?: ViralScript | null;
}

export interface SessionListResponse {
  total_sessions: number;
  session_ids: string[];
}

export interface SearchPatternItem {
  id: string;
  caption: string;
  matched_hook: string;
  summary: string;
  video_url: string;
  image_url: string;
  similarity_score: number;
}

export interface IngestionResponseData {
  total_processed: number;
  total_indexed: number;
  extracted_hooks: string[];
  indexed_ids: string[];
}

export interface GenerateScriptPayload {
  topic: string;
  target_audience?: string;
  duration_seconds?: number;
  platform?: PlatformTarget;
  hook_style?: string;
  top_k_patterns?: number;
}
