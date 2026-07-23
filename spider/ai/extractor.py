from __future__ import annotations

import json
import os
import re
from typing import Any

from loguru import logger

from spider.ai.schemas import ExtractedItem
from spider.parsers.html_cleaner import clean_html
from spider.parsers.text_extractor import extract_text

MAX_CONTENT_CHARS = int(os.getenv("MAX_CONTENT_CHARS", "12000"))

EXTRACTION_PROMPT_TEMPLATE = """You are a precise data extraction engine.
Analyse the following web page content and extract structured data.

Rules:
- Return ONLY a valid JSON object, no markdown fences, no explanation.
- Use null for any field you cannot determine from the content.
- Do NOT invent or hallucinate data; only extract what is clearly present.
- Schema to follow:
{schema}

Page URL: {url}
Page content:
---
{content}
---

JSON:"""


class DataExtractor:
    """HTML -> clean text -> LLM prompt -> validated structured model."""

    def __init__(self, ai_client: Any, schema_model: type = ExtractedItem):
        self.ai_client = ai_client
        self.schema_model = schema_model
        self.schema = schema_model.model_json_schema()

    async def extract(self, url: str, html: str):
        if not self.ai_client:
            logger.debug("AI disabled; skipping extraction")
            return None

        clean = clean_html(html)
        text = extract_text(clean)[:MAX_CONTENT_CHARS]
        if len(text.strip()) < 50:
            logger.warning(f"Insufficient text content for {url}")
            return None

        prompt = EXTRACTION_PROMPT_TEMPLATE.format(
            schema=json.dumps(self.schema, indent=2),
            url=url,
            content=text,
        )
        logger.info(f"[AI] Extracting structured data from {url}")
        raw_output = await self.ai_client.extract(prompt)
        return self._parse_output(raw_output, url)

    def _parse_output(self, raw: str, url: str):
        try:
            json_str = re.sub(r"```(?:json)?|```", "", raw or "").strip()
            data = json.loads(json_str)
            data["source_url"] = url
            return self.schema_model(**data)
        except (json.JSONDecodeError, ValueError, TypeError) as exc:
            logger.warning(f"[AI] Failed to parse output for {url}: {exc}")
            logger.debug(f"Raw output: {(raw or '')[:500]}")
            return None
