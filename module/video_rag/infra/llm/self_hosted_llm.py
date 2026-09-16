"""SelfHostedLLMAdapter implementation."""

import json
import re
from collections.abc import AsyncIterator

import httpx

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
        self._api_key = api_key
        self._model_name = model_name
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._timeout = timeout

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
3. Image and video prompts must be in professional cinematographic English.
4. Return ONLY valid JSON, with no markdown code blocks or surrounding text."""

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
        """Submit prompt to LLM to generate structured viral video script."""
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(
            topic=topic,
            target_audience=target_audience,
            duration_seconds=duration_seconds,
            platform=platform,
            hook_style=hook_style,
            reference_contexts=reference_contexts,
        )

        try:
            headers = {"Content-Type": "application/json"}
            if self._api_key:
                headers["Authorization"] = f"Bearer {self._api_key}"

            url = f"{self._api_base_url}/chat/completions"
            payload = {
                "model": self._model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": self._temperature,
                "max_tokens": self._max_tokens,
                "response_format": {"type": "json_object"},
            }

            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    res_data = response.json()
                    raw_content = res_data["choices"][0]["message"]["content"]
                    return self._parse_llm_json(raw_content, platform, duration_seconds)

                raise ScriptGenerationError(f"LLM API returned HTTP {response.status_code}: {response.text}")
        except Exception as err:
            if isinstance(err, ScriptGenerationError):
                raise
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
            "3. Format recommendations with bullet points and bold highlights."
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

        url = f"{self._api_base_url}/chat/completions"
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        payload = {
            "model": self._model_name,
            "messages": formatted_messages,
            "temperature": self._temperature,
            "max_tokens": self._max_tokens,
            "stream": True,
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                async with client.stream("POST", url, json=payload, headers=headers) as response:
                    if response.status_code == 200:
                        async for line in response.aiter_lines():
                            line = line.strip()
                            if not line or not line.startswith("data:"):
                                continue
                            data_str = line[5:].strip()
                            if data_str == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                                delta = data["choices"][0].get("delta", {})
                                content = delta.get("content")
                                if content:
                                    yield content
                            except Exception:
                                continue
                        return

                    raise ScriptGenerationError(f"LLM streaming service returned HTTP {response.status_code}")
        except Exception as err:
            if isinstance(err, ScriptGenerationError):
                raise
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
        url = f"{self._api_base_url}/chat/completions"
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        payload = {
            "model": self._model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
            "temperature": 0.0,
            "max_tokens": 2048,
            "response_format": {"type": "json_object"},
        }

        try:
            async with httpx.AsyncClient(timeout=min(self._timeout, 10.0)) as client:
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    res_data = response.json()
                    content = res_data["choices"][0]["message"]["content"]
                    parsed = json.loads(content)
                    raw_intent = str(parsed.get("intent", "")).strip().lower()
                    if raw_intent == "generate_script":
                        return ChatIntent.GENERATE_SCRIPT
                    return ChatIntent.GENERAL_CHAT
                raise ScriptGenerationError(
                    f"LLM classify_intent returned HTTP {response.status_code}: {response.text}"
                )
        except Exception as err:
            if isinstance(err, ScriptGenerationError):
                raise
            raise ScriptGenerationError(f"Unable to classify intent via LLM: {err}") from err
