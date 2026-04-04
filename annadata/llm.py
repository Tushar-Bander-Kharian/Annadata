"""LLM Backend Abstraction — Grok (xAI), Claude, or local Ollama.

Usage:
    ANNADATA_BACKEND=grok   python -m annadata.main   # Grok API (default)
    ANNADATA_BACKEND=claude python -m annadata.main   # Claude API
    ANNADATA_BACKEND=ollama python -m annadata.main   # Local Ollama
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import httpx

from annadata.config import ANTHROPIC_API_KEY, GROK_API_KEY, LLM_BACKEND, OLLAMA_BASE_URL


@dataclass
class LLMResponse:
    text: str


class LLMClient(Protocol):
    async def generate(self, model: str, system: str, prompt: str, max_tokens: int = 300) -> LLMResponse:
        ...


class GrokClient:
    """xAI Grok API client — OpenAI-compatible endpoint."""
    BASE_URL = "https://api.x.ai/v1/chat/completions"

    def __init__(self) -> None:
        self.api_key = GROK_API_KEY

    async def generate(self, model: str, system: str, prompt: str, max_tokens: int = 300) -> LLMResponse:
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(self.BASE_URL, headers=headers, json=payload)
            response.raise_for_status()
            return LLMResponse(text=response.json()["choices"][0]["message"]["content"])


class ClaudeClient:
    """Anthropic Claude API client."""

    def __init__(self) -> None:
        import anthropic
        self.client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

    async def generate(self, model: str, system: str, prompt: str, max_tokens: int = 300) -> LLMResponse:
        response = await self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        return LLMResponse(text=response.content[0].text)


class OllamaClient:
    """Local Ollama client."""

    def __init__(self) -> None:
        self.base_url = OLLAMA_BASE_URL

    async def generate(self, model: str, system: str, prompt: str, max_tokens: int = 300) -> LLMResponse:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt},
                    ],
                    "stream": False,
                    "options": {"num_predict": max_tokens, "temperature": 0.4},
                },
            )
            response.raise_for_status()
            return LLMResponse(text=response.json()["message"]["content"])


def create_client() -> LLMClient:
    if LLM_BACKEND == "ollama":
        return OllamaClient()
    elif LLM_BACKEND == "grok":
        return GrokClient()
    else:
        return ClaudeClient()
