# Mimari

## Akış

```
Kullanıcı → agent.py → LLM (Groq) → Tool gerekli mi?
                                    ↓
                              EVET: Tool çalıştır → Sonucu LLM'e geri gönder
                              HAYIR: Cevabı kullanıcıya göster
```

**Tekrar:** Max 8 iterasyon (tool loop sınırı).

## Dosyalar

| Dosya | Görev |
|-------|-------|
| `agent.py` | CLI, mesaj yönetimi, döngü |
| `llm.py` | Groq client |
| `tools/__init__.py` | Tool registry |
| `tools/calculator.py` | Matematik (AST) |
| `tools/web_search.py` | DuckDuckGo arama |
| `tools/fs.py` | Dosya okuma/yazma |
| `tools/http_fetch.py` | HTTP GET |

## Toollar

- `calculator` — `2+2`, `sqrt(16)`, `sin(pi/2)`
- `web_search` — DuckDuckGo ile arama
- `read_file` / `write_file` — Proje kökü altında dosya işlemleri
- `http_get` — URL'den içerik çekme

## Registry

```python
TOOL_REGISTRY = {
    "calculator": calculator_fn,
    "web_search": web_search_fn,
    ...
}
```

LLM tool adı döner → registry'den fonksiyon bulunur → çalıştırılır.

## Frontend

Şu an: **Terminal/CLI only**. Web UI istenirse Gradio/Streamlit eklenebilir.

## Env

```
GROQ_API_KEY=gsk_xxx
MODEL=llama-3.1-8b-instant  # opsiyonel
```

## Limitler

- Max 8 iterasyon
- Dosya: 200KB, proje kökü altı
- HTTP: 10s timeout, 20KB
