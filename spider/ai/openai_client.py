from __future__ import annotations

from spider.ai.retrying import retry, stop_after_attempt, wait_exponential


class OpenAIClient:
    """Async wrapper around the OpenAI chat completions API."""

    def __init__(self, *, api_key: str, model: str):
        try:
            from openai import AsyncOpenAI
        except ImportError as exc:
            raise RuntimeError("OpenAI SDK is not installed") from exc
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=30))
    async def extract(self, prompt: str, max_tokens: int = 1024) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""
