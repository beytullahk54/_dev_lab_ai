# Sequence Diagram'lar

Sistemdeki iki ana akışın adım adım görselleştirmesi.

---

## Kullanıcı Kaydı Akışı

Kullanıcı "Beytullah için kayıt aç" yazdığında:

```
Kullanıcı (Browser)     FastAPI /ws       Router Node       kayit_ac Node     SQLite
       |                     |                  |                  |              |
       |--- "Beytullah için  |                  |                  |              |
       |     kayıt aç" ----->|                  |                  |              |
       |                     |-- user_message ->|                  |              |
       |                     |                  |-- Groq LLM call  |              |
       |                     |                  |   intent analizi |              |
       |                     |                  |<-- "kayit_ac" ---|              |
       |                     |                  |                  |              |
       |                     |                  |-- route -------->|              |
       |                     |                  |                  |-- Groq LLM  |
       |                     |                  |                  |   isim çek  |
       |                     |                  |                  |<-- "Beytullah"
       |                     |                  |                  |              |
       |                     |                  |                  |-- INSERT --> |
       |                     |                  |                  |<-- OK ------|
       |                     |<-- response -----|------------------|              |
       |<--- "✅ Beytullah   |                  |                  |              |
       |      kaydedildi" ---|                  |                  |              |
```

### Adım Açıklamaları

1. **Browser → FastAPI**: Kullanıcı mesajı WebSocket üzerinden gönderilir
2. **FastAPI → Router Node**: `user_message` state'e yazılır, `router_node` çalışır
3. **Router → Groq**: LLM mesajı analiz eder, `kayit_ac` etiketi döner
4. **Router → kayit_ac Node**: Conditional edge ile `kayit_ac_node`'a yönlendirilir
5. **kayit_ac → Groq**: LLM mesajdan ismi çıkarır ("Beytullah")
6. **kayit_ac → SQLite**: `INSERT INTO users` sorgusu çalışır
7. **FastAPI → Browser**: Başarı mesajı WebSocket üzerinden geri gönderilir

---

## Kullanıcı Sayısı Sorgulama Akışı

Kullanıcı "Kaç kullanıcımız var?" yazdığında:

```
Kullanıcı (Browser)     FastAPI /ws       Router Node     kullanici_say Node   SQLite
       |                     |                  |                  |              |
       |--- "Kaç             |                  |                  |              |
       |  kullanıcımız var?" >|                  |                  |              |
       |                     |-- user_message ->|                  |              |
       |                     |                  |-- Groq LLM call  |              |
       |                     |                  |   intent analizi |              |
       |                     |                  |<-- "kullanici_say"              |
       |                     |                  |                  |              |
       |                     |                  |-- route -------->|              |
       |                     |                  |                  |-- COUNT(*) ->|
       |                     |                  |                  |<-- 3 --------|
       |                     |<-- response -----|------------------|              |
       |<--- "📊 3 kullanıcı |                  |                  |              |
       |      kayıtlı" ------|                  |                  |              |
```

### Adım Açıklamaları

1. **Browser → FastAPI**: Sorgulama mesajı WebSocket üzerinden gönderilir
2. **FastAPI → Router Node**: `router_node` Groq ile intent analizi yapar
3. **Router → Groq**: LLM `kullanici_say` etiketi döner
4. **Router → kullanici_say Node**: Groq çağrısı **yapılmaz** — doğrudan SQLite'a gidilir
5. **kullanici_say → SQLite**: `SELECT COUNT(*) FROM users` sorgusu çalışır
6. **FastAPI → Browser**: Sayı mesajı WebSocket üzerinden döner

::: tip
`kullanici_say_node` LLM kullanmaz — sadece SQLite okur. Bu hem maliyet hem de hız avantajı sağlar.
:::
