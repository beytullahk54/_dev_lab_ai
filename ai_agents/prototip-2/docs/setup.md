# Kurulum ve Çalıştırma

## Gereksinimler

- Python 3.11+
- Node.js 18+ *(sadece bu docs sitesi için)*
- Groq API Key → [console.groq.com](https://console.groq.com) adresinden ücretsiz alınabilir

## Adım 1 — Repoyu Klonla / Klasöre Gir

```bash
cd prototip-2
```

## Adım 2 — Python Sanal Ortam

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

## Adım 3 — Bağımlılıkları Kur

```bash
pip install -r requirements.txt
```

## Adım 4 — Ortam Değişkenleri

```bash
cp .env.example .env
```

`.env` dosyasını aç ve key'i gir:

```dotenv
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
```

## Adım 5 — Sunucuyu Başlat

```bash
.venv/bin/uvicorn main:app --reload --port 8001
```

## Adım 6 — Tarayıcıda Aç

```
http://localhost:8001
```

---

## Deneme Komutları

Chat ekranına şunları yazabilirsin:

| Mesaj | Sonuç |
|---|---|
| `Beytullah için kayıt aç` | SQLite'a yeni kullanıcı ekler |
| `Ahmet için kayıt aç` | Başka bir kullanıcı ekler |
| `Kaç kullanıcımız var?` | Toplam sayıyı döndürür |

---

## Docs Sitesini Çalıştırma

```bash
cd docs
npm install
npm run docs:dev
```

Docs sitesi `http://localhost:5173` adresinde açılır.
