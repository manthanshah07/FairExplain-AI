"""
FairExplain AI — Google Gemini LLM Provider Adapter
=====================================================
Integrates Gemini 2.0 / 1.5 with structured JSON responses and graceful fallback.
"""

from __future__ import annotations

import os
from typing import Any

from app.services.llm.base import BaseLLMProvider
from app.services.llm.prompt_templates import SYSTEM_PROMPT
from app.services.llm.template_provider import DeterministicTemplateProvider


class GeminiLLMProvider(BaseLLMProvider):
    """Provider communicating with Google Gemini API."""

    name: str = "gemini"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.fallback = DeterministicTemplateProvider()

    async def generate_explanation(self, telemetry: dict[str, Any]) -> str:
        """Call Gemini if key configured, otherwise use fallback."""
        if not self.api_key:
            return await self.fallback.generate_explanation(telemetry)

        try:
            from google import genai  # type: ignore

            client = genai.Client(api_key=self.api_key)
            prompt = f"System:\n{SYSTEM_PROMPT}\n\nInput Telemetry:\n{telemetry}"

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={"response_mime_type": "application/json"},
            )
            if response.text:
                return response.text
        except Exception:
            pass

        return await self.fallback.generate_explanation(telemetry)
