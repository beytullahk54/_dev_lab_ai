# API Endpointleri

**Dosya**: `main.py`  
**Framework**: FastAPI — `http://localhost:8001`

---

## `GET /`

Chat arayüzünü (`frontend/index.html`) sunar.

**Yanıt**: HTML sayfası

---

## `GET /health`

Sistemin ayakta olup olmadığını kontrol eder.

**Yanıt**:
```json
{ "status": "ok" }
```

---

## `WebSocket /ws`

Ana iletişim kanalı. Tüm chat mesajları buradan akar.

### Bağlantı

```javascript
const ws = new WebSocket('ws://localhost:8001/ws')
```

### Mesaj Gönderme

```javascript
ws.send("Beytullah için kayıt aç")
```

### Yanıt Alma

```javascript
ws.onmessage = (e) => console.log(e.data)
// → "✅ 'Beytullah' için kayıt başarıyla oluşturuldu."
```

### Lifecycle

| Olay | Açıklama |
|---|---|
| `onopen` | Bağlantı kuruldu |
| `onmessage` | Agent cevabı geldi |
| `onclose` | Bağlantı kesildi (auto-reconnect var) |
| `onerror` | Bağlantı hatası |

::: tip
Frontend otomatik yeniden bağlanma (`reconnect`) içerir. Sunucu yeniden başlasa bile 2 saniye içinde bağlantı yenilenir.
:::

---

## FastAPI Otomatik Dokümantasyon

Sunucu çalışırken:

- **Swagger UI**: [http://localhost:8001/docs](http://localhost:8001/docs)
- **ReDoc**: [http://localhost:8001/redoc](http://localhost:8001/redoc)
