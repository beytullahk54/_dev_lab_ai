# LLM Backend API

Python FastAPI kullanarak 2B'lik GPT-2 modeli ile basit bir soru-cevap API'si.

## Kurulum

1. **Sanal ortam oluştur (opsiyonel ama önerilir):**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. **Bağımlılıkları yükle:**
```bash
pip install -r requirements.txt
```

## Çalıştırma

```bash
python main.py
```

API `http://localhost:8000` adresinde çalışacak.

## API Endpoints

### 1. Ana Sayfa
```
GET /
```
API durumunu kontrol eder.

### 2. Soru Sor
```
POST /ask
Content-Type: application/json

{
  "question": "What is artificial intelligence?",
  "max_length": 100
}
```

**Cevap:**
```json
{
  "question": "What is artificial intelligence?",
  "answer": "What is artificial intelligence? It is the ability to..."
}
```

### 3. Sağlık Kontrolü
```
GET /health
```

## API Dokümantasyonu

Sunucu çalışırken:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Notlar

- İlk çalıştırmada GPT-2 modeli (~500MB) indirilecek
- Model CPU üzerinde çalışıyor (GPU için `device=0` yapın)
- CORS tüm originlere açık (production'da kısıtlayın)
