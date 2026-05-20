# Veritabanı

**Dosya**: `database.py`

SQLite kullanılır. Python'da yerleşik gelir, kurulum gerekmez.

---

## Tablo Yapısı

```sql
CREATE TABLE IF NOT EXISTS users (
    id         INTEGER  PRIMARY KEY AUTOINCREMENT,
    name       TEXT     NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

| Sütun | Tip | Açıklama |
|---|---|---|
| `id` | INTEGER | Otomatik artan birincil anahtar |
| `name` | TEXT UNIQUE | Kullanıcı adı, tekrar edilemez |
| `created_at` | DATETIME | Kayıt zamanı, otomatik atanır |

---

## Fonksiyonlar

### `create_tables()`
Uygulama başlarken `main.py`'den çağrılır. Tablo yoksa oluşturur, varsa dokunmaz.

### `insert_user(name: str) → dict`
```python
# Döndürdüğü değerler:
{"status": "created", "name": "Beytullah"}  # yeni kayıt
{"status": "exists",  "name": "Beytullah"}  # zaten vardı
```
`UNIQUE` kısıtı ihlalinde exception fırlatmaz, `exists` döner.

### `count_users() → int`
```python
# Toplam kullanıcı sayısını döndürür
count_users()  # → 3
```

---

## Veritabanı Dosyası

`app.db` dosyası proje kökünde otomatik oluşur. Git'e eklememek için `.gitignore`'a ekle:

```
app.db
```
