"""Proje kökü altına kısıtlı dosya okuma/yazma."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAX_READ_BYTES = 200_000
MAX_WRITE_BYTES = 200_000


def _safe_path(path: str) -> Path:
    p = (ROOT / path).resolve() if not Path(path).is_absolute() else Path(path).resolve()
    if ROOT not in p.parents and p != ROOT:
        raise ValueError(f"Yol proje kökü dışında: {p}")
    return p


def read_file(path: str) -> str:
    try:
        p = _safe_path(path)
        if not p.exists():
            return f"HATA: dosya yok: {path}"
        if not p.is_file():
            return f"HATA: dosya değil: {path}"
        data = p.read_bytes()[:MAX_READ_BYTES]
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            return data.decode("utf-8", errors="replace")
    except Exception as e:
        return f"HATA: {e}"


def write_file(path: str, content: str) -> str:
    try:
        p = _safe_path(path)
        if len(content.encode("utf-8")) > MAX_WRITE_BYTES:
            return f"HATA: içerik çok büyük (>{MAX_WRITE_BYTES} bayt)"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"OK: {p.relative_to(ROOT)} yazıldı ({len(content)} karakter)."
    except Exception as e:
        return f"HATA: {e}"


READ_SCHEMA = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Proje kökü altındaki bir dosyayı okur (UTF-8).",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Proje köküne göre dosya yolu."}
            },
            "required": ["path"],
        },
    },
}

WRITE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "write_file",
        "description": "Proje kökü altındaki bir dosyaya UTF-8 içerik yazar (üzerine yazar).",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Proje köküne göre dosya yolu."},
                "content": {"type": "string", "description": "Dosyaya yazılacak içerik."},
            },
            "required": ["path", "content"],
        },
    },
}
