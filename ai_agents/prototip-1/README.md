# Basit AI Agent (Groq + Python)

Groq API üzerinden seçilebilir bir LLM ile çalışan, tool-calling döngüsüne sahip minimal bir Python agent.

## Kurulum

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# .env içine GROQ_API_KEY değerini yaz
```

API anahtarını https://console.groq.com adresinden alabilirsin.

## Kullanım

Tek atış:

```bash
python agent.py "23 * 47 kaç eder?"
```

Model seçimi:

```bash
python agent.py --model llama-3.3-70b-versatile "Groq'un en yeni modellerini araştır"
```

İnteraktif REPL:

```bash
python agent.py
```

Verbose (tool çağrılarını göster):

```bash
python agent.py --verbose "https://example.com sayfasının başlığı ne?"
```

## Toollar

- **calculator** — `ast` tabanlı güvenli matematik hesabı
- **web_search** — DuckDuckGo (anahtar gerektirmez)
- **read_file** / **write_file** — Proje kökü altına kısıtlı dosya işlemleri
- **http_get** — URL içeriği (10s timeout, 20KB cap)

## Örnek prompt'lar

- "Pi sayısının karesini hesapla" → calculator
- "Llama 3.1 hakkında bilgi ara" → web_search
- "README.md'yi oku ve 2 cümleyle özetle" → read_file
- "https://example.com adresinden başlığı çıkar" → http_get

## Mimari

`agent.py` → LLM çağırır → `tool_calls` varsa `tools/` altındaki fonksiyonları çalıştırır → sonucu `role=tool` ile geri besler → final cevaba kadar (maks. 8 iterasyon) döngü.
