"""VisionThumbnailSelectorAdapter implementation."""

import base64
import json
import os
import re
from typing import Any

import cv2
import httpx
from loguru import logger

from module.video_rag.port.thumbnail_selector_port import IThumbnailSelectorPort


class VisionThumbnailSelectorAdapter(IThumbnailSelectorPort):
    """Selects the best thumbnail frame using OpenCV quality scoring and Vision LLM ranking."""

    def __init__(
        self,
        api_base_url: str = "http://localhost:8000/v1",
        api_key: str | None = None,
        model_name: str = "default",
        timeout: float = 30.0,
        min_brightness: float = 20.0,
        fallback_mode: bool = True,
    ) -> None:
        self._api_base_url = api_base_url.rstrip("/")
        self._api_key = api_key
        self._model_name = model_name
        self._timeout = timeout
        self._min_brightness = min_brightness
        self._fallback_mode = fallback_mode

    def _calculate_frame_quality(self, image_path: str) -> dict[str, float]:
        """Calculate sharpness (Laplacian variance) and brightness of a frame."""
        img = cv2.imread(image_path)
        if img is None:
            return {"sharpness": -1.0, "brightness": 0.0}

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        brightness = float(gray.mean())
        return {"sharpness": sharpness, "brightness": brightness}

    async def select_best_frame(
        self,
        candidate_paths: list[str],
        video_context: str = "",
    ) -> str:
        """Rank candidate frames and select the best one.

        1. Filter out overly dark or corrupted frames.
        2. Sort remaining frames by sharpness (Laplacian score).
        3. If multimodal LLM available, rank top 3-4 candidates with Vision LLM.
        4. Fallback: return the frame with highest sharpness score.
        """
        valid_paths = [p for p in candidate_paths if os.path.exists(p)]
        if not valid_paths:
            return ""

        if len(valid_paths) == 1:
            return valid_paths[0]

        # Step 1: Quality filter & score
        scored_candidates: list[tuple[str, float]] = []
        for path in valid_paths:
            metrics = self._calculate_frame_quality(path)
            if metrics["sharpness"] < 0:
                continue
            # Filter out black or nearly black frames
            if metrics["brightness"] < self._min_brightness:
                continue
            scored_candidates.append((path, metrics["sharpness"]))

        # If all frames were filtered out due to darkness, fallback to valid paths
        if not scored_candidates:
            scored_candidates = [(p, 0.0) for p in valid_paths]

        # Sort descending by sharpness
        scored_candidates.sort(key=lambda x: x[1], reverse=True)

        # Step 2: Vision LLM ranking for top candidates
        top_candidates = scored_candidates[:4]
        if not self._fallback_mode:
            try:
                best_by_llm = await self._rank_with_vision_llm(
                    [c[0] for c in top_candidates],
                    video_context=video_context,
                )
                if best_by_llm:
                    return best_by_llm
            except Exception as exc:
                logger.warning(f"Vision LLM ranking failed ({exc}), falling back to sharpest frame")

        # Fallback: Sharpest candidate
        return top_candidates[0][0]

    async def _rank_with_vision_llm(
        self,
        candidate_paths: list[str],
        video_context: str,
    ) -> str | None:
        """Call multimodal LLM to pick the highest CTR thumbnail frame."""
        image_contents: list[dict[str, Any]] = []
        for path in candidate_paths:
            try:
                with open(path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("utf-8")
                image_contents.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to read frame {path} for vision model: {e}")

        if not image_contents:
            return None

        prompt_text = (
            f"Given these candidate thumbnail frames for a viral video with context: '{video_context}', "
            f"select the single best frame for high CTR (curiosity, emotional expression, clarity). "
            f'Return JSON: {{"selected_index": 0, "reason": "..."}} with selected_index between '
            f"0 and {len(image_contents) - 1}."
        )

        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        payload = {
            "model": self._model_name,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt_text}, *image_contents],
                }
            ],
            "max_tokens": 100,
            "temperature": 0.2,
        }

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(
                f"{self._api_base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                json_match = re.search(r"\{.*?\}", content, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group(0))
                    selected_idx = int(parsed.get("selected_index", 0))
                    if 0 <= selected_idx < len(candidate_paths):
                        return candidate_paths[selected_idx]

        return None
