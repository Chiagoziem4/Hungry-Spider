from __future__ import annotations


class AnthropicClient:
    """Async wrapper around the Anthropic messages API."""

    def __init__(self, *, api_key: str, model: str):
        try:
            from anthropic import AsyncAnthropic
        except ImportError as exc:
            raise RuntimeError("Anthropic SDK is not installed") from exc
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model

    async def extract(self, prompt: str, max_tokens: int = 1024) -> str:
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        parts = []
        for block in response.content:
            text = getattr(block, "text", None)
            if text:
                parts.append(text)
        return "".join(parts)
