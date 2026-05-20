# API Referansı

## Endpoints

### Endpoints → Fonksiyon Eşlemesi

| Endpoint | Metod | Açıklama | **Flask Fonksiyonu** | **Tetiklenen Dahili Fonksiyonlar** |
|----------|-------|----------|----------------------|-----------------------------------|
| `/` | GET | Ana sayfa | `index()` | `send_from_directory()` |
| `/video_feed` | GET | MJPEG stream | `video_feed()` | `generate_frames()` → `is_hand_up()`, `is_fist()`, `_check_wiggle()`, `_play_music()`, `_stop_music_proc()`, `_seek_music()` |
| `/status` | GET | Durum bilgisi | `status()` | `load_settings()` |
| `/camera/on` | POST | Kamera aç | `camera_on()` | `cv2.VideoCapture()`, `find_music_file()`, `get_music_duration()` |
| `/camera/off` | POST | Kamera kapat | `camera_off()` | `_stop_music_proc()` |
| `/music/upload` | POST | Müzik yükle | `music_upload()` | `get_music_duration()`, `load_settings()`, `save_settings()` |
| `/music/select` | POST | Müzik seç | `music_select()` | `get_music_duration()`, `load_settings()`, `save_settings()` |
| `/music/list` | GET | Müzik listesi | `music_list()` | `list_music_files()` |
| `/music/restart_mode` | POST | Mod toggle | `toggle_restart_mode()` | `load_settings()`, `save_settings()` |

## Status JSON Formatı

```json
{
  "hand_up": true,
  "status": "El Kaldırıldı",
  "music_playing": true,
  "camera_on": true,
  "music_file": "/path/to/song.mp3",
  "music_pos": 45.2,
  "music_duration": 180.5,
  "restart_mode": false
}
```

### Alan Açıklamaları

| Alan | Tip | Açıklama |
|------|-----|----------|
| `hand_up` | boolean | El kaldırılmış mı |
| `status` | string | "El Algılanmadı", "El Kaldırıldı", "El İndirildi", "Yumruk - Dur" |
| `music_playing` | boolean | Müzik çalıyor mu |
| `camera_on` | boolean | Kamera açık mı |
| `music_file` | string \| null | Aktif müzik dosyası yolu |
| `music_pos` | number | Şu anki pozisyon (saniye) |
| `music_duration` | number | Toplam süre (saniye) |
| `restart_mode` | boolean | false=devam et, true=baştan başla |

## Request/Response Örnekleri

### Kamera Aç

::: code-group

```bash [Request]
curl -X POST http://127.0.0.1:5001/camera/on
```

```json [Response - Başarılı]
{
  "ok": true
}
```

```json [Response - Hata]
{
  "ok": false,
  "error": "Kamera açılamadı"
}
```

:::

### Müzik Yükle

::: code-group

```bash [Request]
curl -X POST http://127.0.0.1:5001/music/upload \
  -F "file=@song.mp3"
```

```json [Response]
{
  "ok": true,
  "filename": "song.mp3",
  "duration": 180.5
}
```

:::

### Müzik Seç

::: code-group

```bash [Request]
curl -X POST http://127.0.0.1:5001/music/select \
  -H "Content-Type: application/json" \
  -d '{"filename": "song.mp3"}'
```

```json [Response]
{
  "ok": true,
  "filename": "song.mp3",
  "duration": 180.5
}
```

:::

### Müzik Listesi

::: code-group

```bash [Request]
curl http://127.0.0.1:5001/music/list
```

```json [Response]
{
  "files": ["song1.mp3", "song2.mp3"]
}
```

:::

## Hata Kodları

| HTTP Kodu | Durum |
|-----------|-------|
| 200 | Başarılı |
| 400 | Bad Request (dosya yok, desteklenmeyen format) |
| 404 | Dosya bulunamadı |
| 500 | Kamera açılamadı |
