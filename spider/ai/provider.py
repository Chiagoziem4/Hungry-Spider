from __future__ import annotations

from spider.ai.anthropic_client import AnthropicClient
from spider.ai.ollama_client import OllamaClient
from spider.ai.openai_client import OpenAIClient
from spider.utils.config import settings


class NullAIClient:
    """No-op AI client used when extraction is disabled."""

    async def extract(self, prompt: str, max_tokens: int = 1024) -> str:
        return ""



def get_ai_client():
    provider = settings.AI_PROVIDER.lower()
    if provider == "ollama":
        return OllamaClient(base_url=settings.OLLAMA_BASE_URL, model=settings.OLLAMA_MODEL)
    if provider == "openai":
        return OpenAIClient(api_key=settings.OPENAI_API_KEY, model=settings.OPENAI_MODEL)
    if provider == "anthropic":
        return AnthropicClient(api_key=settings.ANTHROPIC_API_KEY, model=settings.ANTHROPIC_MODEL)
    if provider == "none":
        return None
    raise ValueError(f"Unknown AI provider: {settings.AI_PROVIDER}")
