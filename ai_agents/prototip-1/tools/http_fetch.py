"""HTTP GET tool: URL'den içerik çeker (timeout ve boyut limiti ile)."""
from __future__ import annotations

import httpx

MAX_BYTES = 20_000
TIMEOUT = 10.0


def http_get(url: str) -> str:
    if not (url.startswith("http://") or url.startswith("https://")):
        return "HATA: yalnızca http/https URL desteklenir."
    try:
        with httpx.Client(timeout=TIMEOUT, follow_redirects=True) as client:
            r = client.get(url, headers={"User-Agent": "simple-ai-agent/0.1"})
        body = r.text[:MAX_BYTES]
        truncated = len(r.text) > MAX_BYTES
        header = (
            f"status: {r.status_code}\n"
            f"content-type: {r.headers.get('content-type', '')}\n"
            f"final-url: {r.url}\n"
            f"truncated: {truncated}\n---\n"
        )
        return header + body
    except Exception as e:
        return f"HATA: {e}"


SCHEMA = {
    "type": "function",
    "function": {
        "name": "http_get",
        "description": "Verilen URL'e HTTP GET yapar ve gövdeyi döndürür (ilk ~20KB).",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "http/https URL."},
            },
            "required": ["url"],
        },
    },
}
