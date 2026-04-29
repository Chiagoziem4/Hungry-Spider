from __future__ import annotations

import httpx
from loguru import logger

from spider.ai.retrying import retry, stop_after_attempt, wait_exponential


class OllamaClient:
    """Async client for local Ollama inference."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "mistral"):
        self.base_url = base_url.rstrip("/")
        self.model = model

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def extract(self, prompt: str, max_tokens: int = 1024) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": max_tokens, "temperature": 0.1},
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(f"{self.base_url}/api/generate", json=payload)
                response.raise_for_status()
                return response.json().get("response", "").strip()
            except httpx.ConnectError as exc:
                logger.error("Cannot connect to Ollama. Start it with `ollama serve`.")
                raise RuntimeError("Ollama is not reachable") from exc
