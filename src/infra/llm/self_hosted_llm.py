"""SelfHostedLLMAdapter implementation."""

import asyncio
import json
import re
from collections.abc import AsyncIterator

import httpx

from src.core.domain.entities.chat_message import ChatMessage
from src.core.domain.entities.reference_pattern import ReferencedPattern, SimilarVideoContext
from src.core.domain.entities.viral_script import CallToAction, Hook, Scene, ViralScript
from src.core.domain.exceptions import ScriptGenerationError
from src.core.domain.value_objects.hook_type import HookType
from src.core.domain.value_objects.platform_target import PlatformTarget
from src.core.ports.llm_port import ILLMPort


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
        fallback_mode: bool = True,
    ) -> None:
        self._api_base_url = api_base_url.rstrip("/")
        self._api_key = api_key
        self._model_name = model_name
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._timeout = timeout
        self._fallback_mode = fallback_mode

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

        # Hook parsing
        raw_hook = data.get("hook", {})
        hook_type_val = raw_hook.get("hook_type", "problem_agitate")
        try:
            hook_type = HookType(hook_type_val)
        except ValueError:
            hook_type = HookType.PROBLEM_AGITATE

        hook = Hook(
            hook_type=hook_type,
            script=raw_hook.get("script", ""),
            visual_action=raw_hook.get("visual_action", ""),
            retention_rationale=raw_hook.get("retention_rationale", ""),
            duration_seconds=int(raw_hook.get("duration_seconds", 4)),
        )

        # Scenes parsing
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

        # CTA parsing
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

    def _generate_fallback_script(
        self,
        topic: str,
        target_audience: str,
        duration_seconds: int,
        platform: PlatformTarget,
        hook_style: str | None,
        reference_contexts: list[SimilarVideoContext],
    ) -> ViralScript:
        """High-structure fallback viral script generator for local testing and offline execution."""
        ref_title = reference_contexts[0].caption if reference_contexts else "Smart Strategic Framework"
        ref_hook = (
            reference_contexts[0].hook_candidate
            if reference_contexts
            else "90% of people make this critical mistake..."
        )

        hook_text = f"Stop dealing with '{topic}' the traditional way! {ref_hook}"

        scenes = [
            Scene(
                scene_number=1,
                time_range="00:00 - 00:04",
                narration=hook_text[:120],
                visual_action="Close-up of a shocked face, bold neon warning text flashes across the screen.",
                image_prompt=(
                    f"Close-up dramatic face expressing shock, neon red alert typography about '{topic}', "
                    "cinematic lighting, 8k photorealistic, hyper-detailed, depth of field."
                ),
                video_prompt=(
                    "Slow zoom in on character with shocked expression, rapid camera shake, 4k cinematic motion, 60fps."
                ),
                audio_sfx_cue="Loud whoosh sound followed by deep bass drop.",
            ),
            Scene(
                scene_number=2,
                time_range="00:04 - 00:15",
                narration=(
                    f"Most people approach {topic} focusing on vanity metrics, wasting months "
                    "without meaningful progress."
                ),
                visual_action="Character looking stressed at desk, dynamic cut transition to falling analytics charts.",
                image_prompt=(
                    "Frustrated creator sitting in front of glowing laptop screens with falling trend charts, "
                    "moody cyberpunk office, photorealistic."
                ),
                video_prompt=(
                    "Pan from cluttered desk to frustrated person, dynamic glitch transition, cinematic film grain."
                ),
                audio_sfx_cue="Subtle clock ticking speeding up.",
            ),
            Scene(
                scene_number=3,
                time_range="00:15 - 00:30",
                narration=(
                    f"Here is the 3-step proven formula: First, eliminate friction. "
                    f"Second, adopt the benchmark model: '{ref_title}'. Third, compound daily."
                ),
                visual_action=(
                    "3D floating holographic checklist illuminates the frame, character confidently takes action."
                ),
                image_prompt=(
                    "Futuristic holographic 3-step checklist floating in air, glowing cyan and gold light, "
                    "sleek modern minimalist studio background, 8k."
                ),
                video_prompt="Smooth 3D orbit around floating glowing checklist, sleek motion blur.",
                audio_sfx_cue="Upbeat synth-wave background music kicking in, crisp ding sound on each step.",
            ),
            Scene(
                scene_number=4,
                time_range="00:30 - 00:45",
                narration=(
                    "Apply this starting today and experience exponential results within 7 days. "
                    "What is your take? Drop a comment below!"
                ),
                visual_action=(
                    "Creator smiles confidently, points down toward the comment section as the save icon glows."
                ),
                image_prompt=(
                    "Confident friendly person smiling at camera, modern creator studio with soft ambient ring light, "
                    "bokeh background, photorealistic."
                ),
                video_prompt="Medium shot of creator gesturing towards bottom comments, smooth push in, warm lighting.",
                audio_sfx_cue="Positive chime sound effect.",
            ),
        ]

        hook = Hook(
            hook_type=HookType.CONTRARIAN if not hook_style else HookType.PROBLEM_AGITATE,
            script=hook_text[:140],
            visual_action="High-contrast typography over dark background, snap zoom into eyes.",
            retention_rationale=(
                "Leverages loss aversion and directly challenges conventional assumptions, "
                "forcing viewers to stop scrolling."
            ),
            duration_seconds=4,
        )

        cta = CallToAction(
            script="Save this video for later and comment your thoughts below!",
            visual_cue="Pulsing bookmark and share icon animation.",
        )

        return ViralScript(
            title=f"The Viral Blueprint for {topic}",
            target_niche=target_audience,
            platform=platform,
            target_duration_seconds=duration_seconds,
            hook=hook,
            scenes=scenes,
            call_to_action=cta,
            references=[
                ReferencedPattern(
                    original_caption=ctx.caption,
                    matched_hook=ctx.hook_candidate,
                    minio_video_url=ctx.video_url,
                    similarity_score=ctx.score,
                    summary=ctx.summary,
                    image_url=ctx.image_url,
                )
                for ctx in reference_contexts
            ],
            suggested_hashtags=[
                "#viral",
                "#trending",
                f"#{platform.value}",
                f"#{re.sub(r'[^a-zA-Z0-9_]', '', topic.lower())[:15]}",
            ],
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
        """Submit prompt to LLM or generate structured fallback if offline."""
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
        except Exception as err:
            if not self._fallback_mode:
                raise ScriptGenerationError(
                    "Unable to connect to Self-hosted LLM API and fallback_mode is disabled."
                ) from err

        # Activate Fallback
        return self._generate_fallback_script(
            topic=topic,
            target_audience=target_audience,
            duration_seconds=duration_seconds,
            platform=platform,
            hook_style=hook_style,
            reference_contexts=reference_contexts,
        )

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

    async def _stream_fallback_chat(
        self,
        messages: list[ChatMessage],
        reference_contexts: list[SimilarVideoContext],
    ) -> AsyncIterator[str]:
        """Generate structured contextual streaming response when LLM server is offline."""
        last_query = messages[-1].content if messages else "video strategy"
        ref_hook = (
            reference_contexts[0].hook_candidate
            if reference_contexts
            else "90% of creators make this fatal mistake in the first 3 seconds..."
        )
        ref_caption = reference_contexts[0].caption if reference_contexts else "High-Retention Benchmark Video"

        response_text = (
            f"Here is a viral co-pilot strategy crafted for: **{last_query}**\n\n"
            "### 1. High-CTR Hook Options (First 3s):\n"
            f'- **Option A (Benchmark-derived):** "{ref_hook}"\n'
            f'- **Option B (Contrarian):** "Stop doing {last_query[:40]} the traditional way."\n'
            '- **Option C (Curiosity Gap):** "The secret framework top creators use to 10x retention in 7 days."\n\n'
            "### 2. Benchmark Inspiration:\n"
            f"Grounding insights in *{ref_caption}*: Keep transitions under 4 seconds per shot, "
            "introduce visual movement immediately, and pair on-screen captions with dynamic sound effects.\n\n"
            "### 3. Recommended Next Steps:\n"
            "- Would you like me to generate a complete 45-second script with camera directions?\n"
            "- Or generate Flux / Midjourney prompts for each scene?"
        )

        tokens = response_text.split(" ")
        for i, token in enumerate(tokens):
            yield token + (" " if i < len(tokens) - 1 else "")
            await asyncio.sleep(0.005)

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
        except Exception as err:
            if not self._fallback_mode:
                raise ScriptGenerationError(
                    "Unable to stream from Self-hosted LLM API and fallback_mode is disabled."
                ) from err

        # Fallback stream
        async for token in self._stream_fallback_chat(messages, reference_contexts):
            yield token
