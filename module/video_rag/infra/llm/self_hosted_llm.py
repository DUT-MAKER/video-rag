"""SelfHostedLLMAdapter implementation."""

import json
import re
from collections.abc import AsyncIterator

from loguru import logger
from openai import AsyncOpenAI

from module.video_rag.domain.entities.chat_message import ChatMessage
from module.video_rag.domain.entities.reference_pattern import (
    SimilarVideoContext,
)
from module.video_rag.domain.entities.viral_script import (
    CallToAction,
    Hook,
    Scene,
    ViralScript,
)
from module.video_rag.domain.exceptions import ScriptGenerationError
from module.video_rag.domain.value_objects.chat_intent import ChatIntent
from module.video_rag.domain.value_objects.hook_type import HookType
from module.video_rag.domain.value_objects.platform_target import PlatformTarget
from module.video_rag.port.llm_port import ILLMPort


class SelfHostedLLMAdapter(ILLMPort):
    """Adapter for connecting to Self-hosted LLM via OpenAI-compatible Chat Completions API."""

    def __init__(
        self,
        api_base_url: str = "http://localhost:8000/v1",
        api_key: str | None = None,
        model_name: str = "default",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        timeout: float = 60.0,
    ) -> None:
        self._api_base_url = api_base_url.rstrip("/")
        self._api_key = api_key or "EMPTY"
        self._model_name = model_name
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._timeout = timeout

        # Initialize AsyncOpenAI client
        self._client = AsyncOpenAI(
            base_url=self._api_base_url,
            api_key=self._api_key,
            timeout=self._timeout,
        )

    def _build_system_prompt(self) -> str:
        return """You are a World-Class Director and Viral Short-Form Video Scriptwriter (TikTok, Reels, Shorts).
Your mission is to analyze benchmark viral patterns from the knowledge store and create an end-to-end,
production-ready script with second-by-second precision.

You MUST respond with valid, parseable JSON matching this schema:
{
  "title": "High-CTR, curiosity-driven video title",
  "target_niche": "Target audience niche",
  "target_duration_seconds": 45,
  "hook": {
    "hook_type": "problem_agitate | contrarian | curiosity_gap | shocking_fact | story_origin | secret_hack",
    "script": "Attention-grabbing opening line delivered in the first 3-5 seconds",
    "visual_action": "B-roll description and character action in the first 3s to stop the scroll",
    "retention_rationale": "Psychological breakdown of why this hook retains viewers",
    "duration_seconds": 4
  },
  "scenes": [
    {
      "scene_number": 1,
      "time_range": "00:00 - 00:04",
      "narration": "Voiceover narration",
      "visual_action": "Visual description, camera movement, and on-screen graphics",
      "image_prompt": "Photorealistic image prompt for Midjourney/Flux: shot angle, lighting, 8k",
      "video_prompt": "Cinematic prompt for Veo 3.1/Runway/Kling: camera movement, motion, 60fps",
      "audio_sfx_cue": "Sound effect cue (e.g., Whoosh, dramatic bass drop)"
    }
  ],
  "call_to_action": {
    "script": "Compelling closing CTA to drive comments, saves, or follows",
    "visual_cue": "Visual animation or on-screen CTA badge description"
  },
  "suggested_hashtags": ["#viral", "#trend"]
}

Quality Guidelines:
1. No generic greetings (NEVER start with 'Hey guys', 'Welcome back'). Jump straight into the conflict or revelation.
2. Fast-paced storytelling (each scene 3-6 seconds).
3. Language Matching: All spoken and written script elements (title, target_niche, hook script, retention_rationale,
scene narration, visual_action, call_to_action, and hashtags) MUST strictly match the primary language of the user's
input Topic/Target Audience (e.g., if Vietnamese, write in authentic Vietnamese; if English, in English).
4. Image and video prompts: The 'image_prompt' and 'video_prompt' fields MUST ALWAYS remain in professional
cinematographic English for AI generation tools (Midjourney, Flux, Veo, Kling).
5. Return ONLY valid JSON, with no markdown code blocks or surrounding text."""

    def _build_user_prompt(
        self,
        topic: str,
        target_audience: str,
        duration_seconds: int,
        platform: PlatformTarget,
        hook_style: str | None,
        reference_contexts: list[SimilarVideoContext],
    ) -> str:
        prompt_lines = [
            f"Topic: {topic}",
            f"Target Audience: {target_audience}",
            f"Desired Duration: {duration_seconds} seconds",
            f"Target Platform: {platform.value}",
        ]
        if hook_style:
            prompt_lines.append(f"Preferred Hook Style: {hook_style}")

        if reference_contexts:
            prompt_lines.append("\n--- BENCHMARK VIRAL VIDEO PATTERNS FROM KNOWLEDGE STORE ---")
            for idx, ref in enumerate(reference_contexts, 1):
                prompt_lines.append(
                    f"Pattern #{idx}:\n"
                    f"- Title: {ref.caption}\n"
                    f"- Proven Hook: {ref.hook_candidate}\n"
                    f"- Summary: {ref.summary}\n"
                    f"- Reference URL: {ref.video_url}"
                )
            prompt_lines.append(
                "Extract pacing, psychological curiosity, and structural rhythm from these benchmark patterns."
            )

        prompt_lines.append(
            "\nLANGUAGE REQUIREMENT: Detect the language of the provided Topic and Target Audience. "
            "You MUST compose all script narrative elements (title, hook, scene narrations, visual actions, "
            "call-to-action) in that exact matching language."
        )

        return "\n".join(prompt_lines)

    def _parse_llm_json(self, raw_text: str, platform: PlatformTarget, duration_seconds: int) -> ViralScript:
        """Parse and validate JSON response from LLM."""
        clean_json = raw_text.strip()
        clean_json = re.sub(r"^```(?:json)?\s*", "", clean_json, flags=re.MULTILINE)
        clean_json = re.sub(r"\s*```$", "", clean_json, flags=re.MULTILINE)

        data = json.loads(clean_json)

        raw_hook = data.get("hook", {})
        hook_type_val = raw_hook.get("hook_type", "curiosity_gap")
        hook_type = HookType.from_str(hook_type_val)

        hook = Hook(
            hook_type=hook_type,
            script=raw_hook.get("script", ""),
            visual_action=raw_hook.get("visual_action", ""),
            retention_rationale=raw_hook.get("retention_rationale", ""),
            duration_seconds=int(raw_hook.get("duration_seconds", 4)),
        )

        scenes: list[Scene] = []
        for s in data.get("scenes", []):
            scene = Scene(
                scene_number=int(s.get("scene_number", len(scenes) + 1)),
                time_range=str(s.get("time_range", "")),
                narration=str(s.get("narration", "")),
                visual_action=str(s.get("visual_action", "")),
                image_prompt=str(s.get("image_prompt", "")),
                video_prompt=str(s.get("video_prompt", "")),
                audio_sfx_cue=str(s.get("audio_sfx_cue", "")),
            )
            scenes.append(scene)

        raw_cta = data.get("call_to_action", {})
        cta = CallToAction(
            script=raw_cta.get("script", "Follow for more actionable insights!"),
            visual_cue=raw_cta.get("visual_cue", "Animated follow icon pulse"),
        )

        return ViralScript(
            title=data.get("title", "Viral Video Script"),
            target_niche=data.get("target_niche", "Personal Development"),
            platform=platform,
            target_duration_seconds=int(data.get("target_duration_seconds", duration_seconds)),
            hook=hook,
            scenes=scenes,
            call_to_action=cta,
            suggested_hashtags=data.get("suggested_hashtags", ["#viral", "#trending", f"#{platform.value}"]),
        )

    async def generate_script(
        self,
        topic: str,
        target_audience: str,
        duration_seconds: int,
        platform: PlatformTarget,
        hook_style: str | None,
        reference_contexts: list[SimilarVideoContext],
    ) -> ViralScript:
        """Submit prompt to LLM to generate structured viral video script with real-time log streaming."""
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(
            topic=topic,
            target_audience=target_audience,
            duration_seconds=duration_seconds,
            platform=platform,
            hook_style=hook_style,
            reference_contexts=reference_contexts,
        )

        logger.debug(f"📝 [LLM User Prompt]\n{user_prompt}")

        try:
            response = await self._client.chat.completions.create(
                model=self._model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self._temperature,
                max_tokens=self._max_tokens,
                response_format={"type": "json_object"},
                stream=True,
            )

            raw_content = ""
            if hasattr(response, "__aiter__"):
                collected_chunks: list[str] = []
                collected_reasoning: list[str] = []
                is_reasoning_logged = False

                async for chunk in response:
                    delta = chunk.choices[0].delta if chunk.choices else None
                    if not delta:
                        continue

                    reasoning = getattr(delta, "reasoning_content", None)
                    if reasoning:
                        if not is_reasoning_logged:
                            logger.info("🧠 [LLM Thinking]:")
                            is_reasoning_logged = True
                        collected_reasoning.append(reasoning)
                        logger.opt(raw=True).info(reasoning)

                    content = delta.content
                    if content:
                        collected_chunks.append(content)

                if is_reasoning_logged:
                    logger.opt(raw=True).info("\n")

                raw_content = "".join(collected_chunks).strip()
                if not raw_content and collected_reasoning:
                    reasoning_text = "".join(collected_reasoning)
                    json_in_reasoning = re.search(r"\{[\s\S]*\}", reasoning_text)
                    if json_in_reasoning:
                        raw_content = json_in_reasoning.group(0)
            elif hasattr(response, "choices"):
                first_choice = response.choices[0]
                raw_content = (getattr(first_choice.message, "content", None) or "").strip()

            return self._parse_llm_json(raw_content, platform, duration_seconds)
        except Exception as err:
            logger.warning(f"⚠️ [LLM] Lỗi generate_script ({type(err).__name__}: {err}).")
            raise ScriptGenerationError(f"Unable to connect to Self-hosted LLM API: {err}") from err

    def _build_chat_system_prompt(
        self,
        reference_contexts: list[SimilarVideoContext],
        current_script_json: str | None,
    ) -> str:
        prompt = (
            "You are a World-Class Viral Video Co-Pilot and Creative Director for TikTok, Reels, and Shorts. "
            "Your role is to assist creators in brainstorming viral hooks, refining script pacing, "
            "improving visual retention, and designing cinematographic image/video prompts.\n\n"
            "Style & Tone Guidelines:\n"
            "1. Be direct, concise, and structured.\n"
            "2. Ground your advice in high-CTR retention psychology (first 3-second rule, pattern interrupts).\n"
            "3. Format recommendations with bullet points and bold highlights.\n"
            "4. Language Consistency: ALWAYS detect and respond in the EXACT SAME LANGUAGE as the user's messages "
            "(e.g., if the user writes in Vietnamese, reply in Vietnamese; if in English, reply in English). "
            "Only keep AI visual generation prompts (image_prompt, video_prompt) in descriptive English."
        )
        if current_script_json:
            prompt += f"\n\nCURRENT WORKING DRAFT SCRIPT:\n{current_script_json}"
        if reference_contexts:
            prompt += "\n\n--- BENCHMARK VIRAL VIDEO PATTERNS FROM KNOWLEDGE STORE ---"
            for idx, ref in enumerate(reference_contexts, 1):
                prompt += (
                    f"\nPattern #{idx}:\n"
                    f"- Title / Caption: {ref.caption}\n"
                    f"- Proven Hook: {ref.hook_candidate}\n"
                    f"- Summary: {ref.summary}\n"
                    f"- Reference URL: {ref.video_url}"
                )
            prompt += "\nIncorporate structural rhythm and retention techniques from these proven patterns."
        return prompt

    async def stream_chat(
        self,
        messages: list[ChatMessage],
        reference_contexts: list[SimilarVideoContext],
        current_script_json: str | None = None,
    ) -> AsyncIterator[str]:
        """Stream conversational responses chunk by chunk via an async iterator."""
        system_prompt = self._build_chat_system_prompt(reference_contexts, current_script_json)
        formatted_messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
        for msg in messages:
            formatted_messages.append({"role": msg.role.value, "content": msg.content})

        try:
            stream = await self._client.chat.completions.create(
                model=self._model_name,
                messages=formatted_messages,  # type: ignore[arg-type]
                temperature=self._temperature,
                max_tokens=self._max_tokens,
                stream=True,
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta if chunk.choices else None
                content = delta.content if delta else None
                if content:
                    yield content
            return
        except Exception as err:
            logger.warning(f"⚠️ [LLM] Lỗi stream_chat ({type(err).__name__}: {err}).")
            raise ScriptGenerationError(f"Unable to stream from Self-hosted LLM API: {err}") from err

    async def classify_intent(self, message: str) -> ChatIntent:
        """Classify user query intent into ChatIntent using LLM with structured format."""
        system_prompt = (
            "You are an Intent Classifier for an AI Viral Video Creation Assistant.\n"
            "Classify the user's message into EXACTLY one of two intents:\n"
            "- 'generate_script': The user is asking to create, brainstorm, structure, rewrite, "
            "edit, or get ideas/prompts for a video, script, hook, scene, or viral content.\n"
            "- 'general_chat': Casual conversation, greetings, general questions, "
            "chitchat, or topics unrelated to creating video scripts.\n\n"
            "Respond ONLY with a JSON object in this format:\n"
            '{"intent": "generate_script"} or {"intent": "general_chat"}'
        )

        try:
            response = await self._client.chat.completions.create(
                model=self._model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message},
                ],
                temperature=0.0,
                max_tokens=2048,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content or ""
            parsed = json.loads(content)
            raw_intent = str(parsed.get("intent", "")).strip().lower()
            if raw_intent == "generate_script":
                return ChatIntent.GENERATE_SCRIPT
            return ChatIntent.GENERAL_CHAT
        except Exception as err:
            logger.warning(f"⚠️ [LLM] classify_intent failed ({err}). Defaulting to GENERAL_CHAT.")
            return ChatIntent.GENERAL_CHAT

    async def enrich_video_metadata(
        self,
        transcript: str,
        language: str = "vi",
    ) -> dict[str, str]:
        """Generate caption, summary, and hashtags from a speaker-labeled transcript."""
        system_prompt = (
            "You are a viral video metadata analyst and strategist for short-form platforms (TikTok, Reels, Shorts).\n"
            "Given a speaker-labeled transcript, generate:\n"
            "1. caption: A high-CTR, curiosity-driven viral video title (under 100 characters).\n"
            "2. summary: A concise 2-3 sentence summary capturing the core message, dialogue dynamics, "
            "and key takeaway.\n"
            "3. hashtag: 5-8 relevant, high-traffic trending hashtags as a single space-separated string "
            "(e.g. '#phattrienbanthan #kỷluat #viral #learnontiktok').\n"
            "4. language: The caption and summary MUST be generated in the SAME language as the transcript "
            "(matching the specified Language).\n\n"
            "The transcript contains speaker labels (SPEAKER_00, SPEAKER_01, etc.) and timestamps.\n"
            "Respond ONLY with valid JSON matching:\n"
            '{"caption": "...", "summary": "...", "hashtag": "..."}\n'
            "Do not wrap with markdown code blocks or add any additional commentary."
        )

        user_prompt = f"Transcript:\n{transcript}\n\nLanguage: {language}"
        logger.info(f"📄 [LLM] Độ dài transcript gửi lên: {len(transcript)} ký tự. Preview: '{transcript[:150]}'")

        try:
            logger.info(
                f"🤖 [LLM] Đang gọi AsyncOpenAI enrich_video_metadata "
                f"(base_url='{self._api_base_url}', model='{self._model_name}')..."
            )
            response = await self._client.chat.completions.create(
                model=self._model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=2048,
            )
            content = ""
            if response.choices:
                first_choice = response.choices[0]
                logger.info(f"📦 [LLM] Choice finish_reason='{first_choice.finish_reason}'")
                content = (first_choice.message.content or "").strip()
                # Nếu model là reasoning model (thinking model) và để output ở reasoning_content
                if not content:
                    reasoning = getattr(first_choice.message, "reasoning_content", None) or ""
                    if reasoning:
                        logger.info("ℹ️ [LLM] Tìm thấy reasoning_content trong message, đang thử parse...")
                        json_in_reasoning = re.search(r"\{[\s\S]*\}", reasoning)
                        if json_in_reasoning:
                            content = json_in_reasoning.group(0)

            logger.info(f"📝 [LLM] Raw output từ AsyncOpenAI: '{content[:300]}'")
            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group(0))
                logger.info(f"✨ [LLM] Parse JSON thành công! Caption: '{parsed.get('caption', '')[:50]}...'")
                return {
                    "caption": str(parsed.get("caption", "")).strip(),
                    "summary": str(parsed.get("summary", "")).strip(),
                    "hashtag": str(parsed.get("hashtag", "")).strip(),
                }
            else:
                logger.warning(
                    f"⚠️ [LLM] AsyncOpenAI trả về thành công nhưng content trống hoặc không có JSON: '{content}'"
                )
        except Exception as err:
            logger.warning(
                f"⚠️ [LLM] Lỗi exception khi gọi AsyncOpenAI ({type(err).__name__}: {err}). Sẽ dùng chế độ Fallback."
            )

        logger.info("ℹ️ [LLM] Đang chạy Offline Fallback để trích xuất caption & summary từ transcript...")
        return self._fallback_enrich_video_metadata(transcript)

    def _fallback_enrich_video_metadata(self, transcript: str) -> dict[str, str]:
        """Offline fallback metadata extraction when LLM API is unavailable."""
        clean_lines = [
            line.strip() for line in transcript.splitlines() if line.strip() and not line.strip().startswith("#")
        ]

        raw_text = " ".join(clean_lines)
        # Strip speaker labels for caption extraction if present
        stripped_text = re.sub(r"SPEAKER_\d+\s*\[.*?\]:\s*", "", raw_text)

        first_sentence = stripped_text.split(".")[0].strip() if stripped_text else "Video Chia Sẻ Bài Học Hay"
        if len(first_sentence) > 80:
            first_sentence = first_sentence[:77] + "..."

        caption = (
            f"{first_sentence} - Bí Quyết Viral Triệu View"
            if first_sentence
            else "Bí Quyết Tạo Kịch Bản Video Viral Triệu View"
        )

        summary = (
            f"Video chia sẻ nội dung thảo luận với các luận điểm chính: "
            f"{stripped_text[:200]}... Giúp người xem nắm bắt nhanh kiến thức hữu ích."
            if stripped_text
            else "Tóm tắt kịch bản video viral với nội dung hấp dẫn, cấu trúc hook mạnh mẽ và thông điệp giá trị."
        )

        hashtag = "#viral #learnontiktok #shortform #trending #videotrieuview #xuhuong"

        return {
            "caption": caption,
            "summary": summary,
            "hashtag": hashtag,
        }
