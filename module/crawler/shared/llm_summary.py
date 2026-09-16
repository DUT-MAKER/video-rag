"""LLMSummaryAdapter implementing ISummaryPort (shared across all platforms)."""

import httpx
from loguru import logger

from core.config import get_llm_settings
from module.crawler.domain import LLMUnavailableError
from module.crawler.port import ISummaryPort


class LLMSummaryAdapter(ISummaryPort):
    """Summarizer calling a real OpenAI-compatible LLM endpoint (vLLM / Ollama).
    
    Strictly adheres to data integrity: raises LLMUnavailableError if the
    LLM server is unreachable, rather than fabricating fallback text.
    """

    def __init__(self, timeout_seconds: float = 30.0):
        self.settings = get_llm_settings()
        self.timeout_seconds = timeout_seconds

    def summarize(self, caption: str, transcript: str) -> str:
        caption_clean = caption.strip()
        transcript_clean = transcript.strip()

        if not caption_clean and not transcript_clean:
            return "Video ngắn không có lời thoại hoặc mô tả."

        prompt = (
            "Dưới đây là thông tin và transcript của một video ngắn dạng shorts/reels/tiktok.\n"
            "Hãy tóm tắt ngắn gọn nội dung cốt lõi và thông điệp chính của video trong tối đa 2-3 câu:\n\n"
            f"Caption: {caption_clean}\n"
            f"Transcript: {transcript_clean}\n\n"
            "Tóm tắt:"
        )

        endpoint = f"{self.settings.api_base_url.rstrip('/')}/chat/completions"
        payload = {
            "model": self.settings.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.settings.temperature,
            "max_tokens": self.settings.max_tokens,
        }
        headers = {
            "Content-Type": "application/json",
        }
        if self.settings.api_key and self.settings.api_key.strip():
            headers["Authorization"] = f"Bearer {self.settings.api_key.strip()}"

        last_error = ""
        for attempt in range(1, 4):
            try:
                with httpx.Client(timeout=self.timeout_seconds) as client:
                    res = client.post(endpoint, json=payload, headers=headers)
                    if res.status_code == 200:
                        data = res.json()
                        choices = data.get("choices", [])
                        if choices and "message" in choices[0]:
                            return choices[0]["message"].get("content", "").strip()
                        raise LLMUnavailableError(f"LLM returned 200 but unexpected body: {data}")

                    last_error = f"LLM returned HTTP {res.status_code}: {res.text}"
                    logger.warning(f"[LLM Retry {attempt}/3] {last_error}")
                    if res.status_code in (429, 500, 502, 503, 504) and attempt < 3:
                        import time
                        time.sleep(1.5 * attempt)
                        continue
                    raise LLMUnavailableError(last_error)

            except httpx.RequestError as e:
                last_error = f"Connection error contacting LLM at {endpoint}: {e}"
                logger.warning(f"[LLM Retry {attempt}/3] {last_error}")
                if attempt < 3:
                    import time
                    time.sleep(1.5 * attempt)
                    continue
                raise LLMUnavailableError(last_error) from e

        raise LLMUnavailableError(last_error)
