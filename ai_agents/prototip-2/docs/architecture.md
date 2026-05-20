# Mimari — Genel Bakış

## Genel Bakış

Bu sistem; bir **FastAPI** web sunucusu, **LangGraph** tabanlı iki ajan, **Groq** LLM ve **SQLite** veritabanından oluşur.  
Kullanıcı mesajları WebSocket üzerinden iletilir, LangGraph grafiği doğru ajana yönlendirir.

---

## Teknoloji Seçimleri

| Katman | Teknoloji | Neden? |
|---|---|---|
| LLM | **Groq** (llama-3.1-8b-instant) | Çok düşük gecikme (sub-second), ücretsiz tier |
| Agent Orkestrasyonu | **LangGraph** | Node/Edge yapısı; yeni ajan eklemek sadece yeni node demek |
| Veritabanı | **SQLite** | Sıfır konfigürasyon, tek dosya, prototip için ideal |
| Backend | **FastAPI** | Async WebSocket desteği, otomatik API dokümantasyonu |
| Frontend | Vanilla HTML/JS | Bağımlılık yok, anında çalışır |

---

## Sequence Diagram – Kullanıcı Kaydı

```
Kullanıcı (Browser)     FastAPI /ws       Router Node       kayit_ac Node     SQLite
       |                     |                  |                  |              |
       |--- "Beytullah için  |                  |                  |              |
       |     kayıt aç" ----->|                  |                  |              |
       |                     |-- user_message ->|                  |              |
       |                     |                  |-- Groq LLM call  |              |
       |                     |                  |   (intent=       |              |
       |                     |                  |   "kayit_ac") -->|              |
       |                     |                  |<-- "kayit_ac" ---|              |
       |                     |                  |                  |              |
       |                     |                  |-- route -------->|              |
       |                     |                  |                  |-- Groq LLM  |
       |                     |                  |                  |   (isim çek)|
       |                     |                  |                  |<-- "Beytullah"
       |                     |                  |                  |              |
       |                     |                  |                  |-- INSERT --> |
       |                     |                  |                  |<-- OK ------|
       |                     |<-- response -----|------------------|              |
       |<--- "✅ Beytullah   |                  |                  |              |
       |      kaydedildi" ---|                  |                  |              |
```

---

## Sequence Diagram – Kullanıcı Sayısı Sorgulama

```
Kullanıcı (Browser)     FastAPI /ws       Router Node     kullanici_say Node   SQLite
       |                     |                  |                  |              |
       |--- "Kaç             |                  |                  |              |
       |  kullanıcımız var?" >|                  |                  |              |
       |                     |-- user_message ->|                  |              |
       |                     |                  |-- Groq LLM call  |              |
       |                     |                  |   (intent=       |              |
       |                     |                  |  "kullanici_say")|              |
       |                     |                  |<-- "kullanici_say"              |
       |                     |                  |                  |              |
       |                     |                  |-- route -------->|              |
       |                     |                  |                  |-- COUNT(*) ->|
       |                     |                  |                  |<-- 3 --------|
       |                     |<-- response -----|------------------|              |
       |<--- "📊 3 kullanıcı |                  |                  |              |
       |      kayıtlı" ------|                  |                  |              |
```

---

## LangGraph Graf Yapısı

```
                    ┌─────────────────┐
   user_message ──> │  router_node    │
                    │  (Groq LLM)     │
                    └────────┬────────┘
                             │ intent
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
      ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
      │ kayit_ac     │ │kullanici_say │ │ bilinmiyor   │
      │ node         │ │ node         │ │ node         │
      │ (Groq+SQLite)│ │ (SQLite)     │ │ (sabit msg)  │
      └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
             │                │                │
             └────────────────┴────────────────┘
                              │
                             END
```

---

## Dosya Yapısı

```
prototip-2/
├── main.py          # FastAPI app, WebSocket endpoint
├── agents.py        # LangGraph graph, tüm node'lar
├── database.py      # SQLite bağlantı ve CRUD
├── .env             # GROQ_API_KEY (git'e ekleme!)
├── .env.example     # Örnek env dosyası
├── requirements.txt # Python bağımlılıkları
├── app.db           # SQLite veritabanı (otomatik oluşur)
├── frontend/
│   └── index.html   # Chat UI
└── docs/
    └── architecture.md  # Bu dosya
```

---

## Kurulum ve Çalıştırma

```bash
# 1. Bağımlılıkları kur
pip install -r requirements.txt

# 2. .env dosyasını oluştur
cp .env.example .env
# .env içine GROQ_API_KEY değerini gir

# 3. Sunucuyu başlat
uvicorn main:app --reload --port 8000

# 4. Tarayıcıda aç
# http://localhost:8000
```

---

## Yeni Agent Ekleme Rehberi

1. `agents.py` içine yeni bir `xxx_node(state)` fonksiyonu ekle.  
2. `build_graph()` içinde `graph.add_node("xxx", xxx_node)` ile kaydet.  
3. `router_node` sistem promptuna yeni etiketi tanıt.  
4. `route_decision` ve `conditional_edges` sözlüğüne yeni dal ekle.  
5. `graph.add_edge("xxx", END)` ile grafikten çıkışını bağla.
