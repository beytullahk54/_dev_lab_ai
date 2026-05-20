# Kurulum

## Hızlı Kurulum

```bash
cd /Volumes/Kodlooper/kodlooperYazilim/htdocs/ai_agents

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# .env dosyasını aç ve GROQ_API_KEY'i ekle
```

**API Key:** https://console.groq.com → API Keys → Create

## Test

```bash
python agent.py "23 * 47 kaç eder?"
```

## Hatalar

| Hata | Çözüm |
|------|-------|
| `groq` not found | `source .venv/bin/activate` |
| `GROQ_API_KEY` missing | `.env` dosyasına key ekle |
| `ddgs` import error | `pip install ddgs` |
