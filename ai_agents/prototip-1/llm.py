"""Groq LLM client sarmalayıcısı."""
from __future__ import annotations

import os
from typing import Any


class LLMClient:
    def __init__(self, model: str | None = None, api_key: str | None = None):
        try:
            from groq import Groq
        except ImportError as e:
            raise SystemExit("`groq` paketi yüklü değil. `pip install -r requirements.txt`") from e

        key = api_key or os.environ.get("GROQ_API_KEY")
        if not key:
            raise SystemExit("GROQ_API_KEY tanımlı değil. `.env` veya ortam değişkeni olarak ayarla.")
        self.client = Groq(api_key=key)
        self.model = model or os.environ.get("MODEL") or "llama-3.1-8b-instant"

    def chat(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None):
        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        return self.client.chat.completions.create(**kwargs)
