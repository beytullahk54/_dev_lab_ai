"""DuckDuckGo üzerinden web arama (anahtar gerektirmez)."""
from __future__ import annotations

import json


def web_search(query: str, max_results: int = 5) -> str:
    try:
        from ddgs import DDGS
    except ImportError:
        return "HATA: 'ddgs' paketi yüklü değil. `pip install ddgs` çalıştır."

    try:
        max_results = max(1, min(int(max_results), 10))
    except (TypeError, ValueError):
        max_results = 5

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
    except Exception as e:
        return f"HATA: arama başarısız: {e}"

    if not results:
        return "Sonuç bulunamadı."

    items = []
    for r in results:
        items.append({
            "title": r.get("title"),
            "url": r.get("href") or r.get("url"),
            "snippet": r.get("body") or r.get("snippet"),
        })
    return json.dumps(items, ensure_ascii=False, indent=2)


SCHEMA = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "DuckDuckGo ile internette arama yapar ve başlık/url/snippet listesi döner.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Arama sorgusu."},
                "max_results": {
                    "type": "integer",
                    "description": "Maksimum sonuç sayısı (1-10, varsayılan 5).",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
    },
}
