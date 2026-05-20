# Agent'lar

Sistemde **3 aktif node** (agent) bulunur; bunları yönlendiren 1 router vardır.

---

## Router Node

**Dosya**: `agents.py` → `router_node()`

Gelen her mesajı Groq LLM'e gönderir, LLM yalnızca şu etiketlerden birini döner:

| Etiket | Anlamı |
|---|---|
| `kayit_ac` | Yeni kullanıcı kaydı açılacak |
| `kullanici_say` | Kaç kullanıcı var sorgusu |
| `bilinmiyor` | Başka bir şey |

::: warning
Router LLM'den **sadece etiket** ister. Başka metin dönerse `bilinmiyor` kabul edilir.
:::

---

## kayit_ac Node

**Dosya**: `agents.py` → `kayit_ac_node()`

### Akış
1. Groq LLM'e mesajı gönder → sadece ismi çıkar
2. `database.insert_user(name)` çağır
3. Başarı veya "zaten var" mesajı döndür

### Örnek

```
Girdi : "Beytullah için kayıt aç"
LLM   : "Beytullah"
SQLite: INSERT INTO users (name) VALUES ('Beytullah')
Çıktı : ✅ 'Beytullah' için kayıt başarıyla oluşturuldu.
```

::: tip
Aynı isim tekrar gönderilirse SQLite `UNIQUE` kısıtı devreye girer, hata fırlatmak yerine `"zaten var"` mesajı döner.
:::

---

## kullanici_say Node

**Dosya**: `agents.py` → `kullanici_say_node()`

LLM kullanmaz. Doğrudan SQLite'tan toplam sayıyı okur.

### Akış
1. `database.count_users()` çağır → `SELECT COUNT(*) FROM users`
2. Sayıyı cevaba göm

### Örnek

```
Girdi : "Kaç kullanıcımız var?"
SQLite: SELECT COUNT(*) → 3
Çıktı : 📊 Sistemde toplam 3 kullanıcı kayıtlı.
```

---

## bilinmiyor Node

**Dosya**: `agents.py` → `bilinmiyor_node()`

Hiçbir intent eşleşmediğinde devreye girer. Kullanıcıya kullanım ipuçları verir. LLM veya DB çağrısı yapmaz.

---

## LLM Konfigürasyonu

```python
ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.1-8b-instant",
    temperature=0,
)
```

- **`temperature=0`**: Deterministik çıktı — router her seferinde aynı etiketi döner
- **Lazy init**: LLM nesnesi ilk çağrıda oluşturulur, `.env` okunduktan sonra
