"""
FairExplain AI — LLM Provider Interface
=========================================
Abstract protocol for LLM explanation generation engines.
"""

from __future__ import annotations

from typing import Any, Protocol


class BaseLLMProvider(Protocol):
    """Protocol for LLM explanation providers."""

    async def generate_explanation(self, telemetry: dict[str, Any]) -> str:
        """Generate plain-text or structured JSON explanation from input telemetry."""
        ...
