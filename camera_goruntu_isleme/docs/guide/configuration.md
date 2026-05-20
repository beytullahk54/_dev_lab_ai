# Konfigürasyon

## Ayarlar Dosyası (settings.json)

```json
{
  "music_file": "song.mp3",
  "restart_mode": false
}
```

### Alanlar

| Alan | Tip | Varsayılan | Açıklama |
|------|-----|------------|----------|
| `music_file` | string | `null` | Son seçilen müzik dosyası adı |
| `restart_mode` | boolean | `false` | Müzik durdurulduğunda baştan başlat veya devam et |

### restart_mode Davranışı

| Değer | El Kaldırıldığında |
|-------|-------------------|
| `false` | Durduğun yerden devam et (resume_pos) |
| `true` | Her seferinde baştan başla (0:00) |

## Kod İçinde Kullanım

### Ayarları Yükleme

```python
@/Volumes/Kodlooper/kodlooperYazilim/htdocs/camera_goruntu_isleme/web_app.py:21-27
def load_settings():
    try:
        with open(SETTINGS_FILE) as f:
            import json
            return json.load(f)
    except Exception:
        return {}
```

### Ayarları Kaydetme

```python
@/Volumes/Kodlooper/kodlooperYazilim/htdocs/camera_goruntu_isleme/web_app.py:30-33
def save_settings(data):
    import json
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f)
```

### Toggle Restart Mode

```python
@app.route("/music/restart_mode", methods=["POST"])
def toggle_restart_mode():
    with lock:
        state["restart_mode"] = not state["restart_mode"]
        new_mode = state["restart_mode"]
    
    settings = load_settings()
    settings["restart_mode"] = new_mode
    save_settings(settings)
    
    return jsonify({"restart_mode": new_mode})
```

## Dosya Yapısı

```
camera_goruntu_isleme/
├── settings.json          # Kullanıcı ayarları
├── music/                 # Müzik dosyaları
│   ├── song1.mp3
│   └── song2.mp3
└── ...
```

::: tip Otomatik Yükleme
Uygulama başlatıldığında `load_settings()` otomatik çağrılır ve state başlatılır:
```python
state = {
    "restart_mode": load_settings().get("restart_mode", False)
}
```
:::
