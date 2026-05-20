# El Hareketi Müzik Kontrolü - Proje Dokümantasyonu

## 📋 Proje Özeti

Bu proje, kamera aracılığıyla el hareketlerini algılayarak müzik oynatmayı kontrol eden bir web uygulamasıdır. Flask backend + HTML/JS frontend + MediaPipe el izleme teknolojisi kullanır.

---

## 🛠️ Kullanılan Teknolojiler

| Teknoloji | Sürüm | Görevi |
|-----------|-------|--------|
| **Flask** | - | Web sunucusu, REST API sağlar |
| **OpenCV** | 4.9.0.80 | Kameradan görüntü yakalama, görsel işleme |
| **MediaPipe Hands** | 0.10.35 | Google'ın el izleme modeli, 21 noktalı landmark tespiti |
| **ffplay (ffmpeg)** | - | Harici ses oynatıcı subprocess |
| **HTML5/JS/CSS3** | - | Kullanıcı arayüzü |

---

## 🏗️ Sistem Mimarisi

```
┌─────────────────────────────────────────────────────────────────┐
│                          FRONTEND                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  index.html │  │  JavaScript │  │  CSS Styling            │  │
│  │  (UI)       │  │  (Event/    │  │  (Dark Theme)           │  │
│  │             │  │   Polling)  │  │                         │  │
│  └──────┬──────┘  └──────┬──────┘  └─────────────────────────┘  │
└─────────┼────────────────┼───────────────────────────────────────┘
          │ HTTP Requests
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                         BACKEND (Flask)                         │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                      API Endpoints                         │  │
│  │  GET  /              → index.html servis et               │  │
│  │  GET  /video_feed    → MJPEG video stream                 │  │
│  │  GET  /status        → Durum JSON (polling)              │  │
│  │  POST /camera/on     → Kamerayı aç                       │  │
│  │  POST /camera/off    → Kamerayı kapat                    │  │
│  │  POST /music/upload  → Müzik yükle                       │  │
│  │  POST /music/select  → Müzik seç                         │  │
│  │  GET  /music/list    → Müzik listesi                     │  │
│  │  POST /music/restart_mode → Toggle mod                   │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼ Internal Calls
┌─────────────────────────────────────────────────────────────────┐
│                    VISION & MEDIA PIPELINE                      │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │  OpenCV     │───→│  MediaPipe  │───→│  Gesture Detection  │  │
│  │  VideoCapture│   │  HandLandmarker│  │  (21 Landmarks)     │  │
│  └─────────────┘    └─────────────┘    └─────────────────────┘  │
│                                               │                 │
│                                               ▼                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │  ffplay     │←───│  Music      │←───│  is_hand_up()       │  │
│  │  subprocess │    │  Controller │    │  is_fist()          │  │
│  └─────────────┘    └─────────────┘    │  _check_wiggle()    │  │
│                                        └─────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Veri Akış Diyagramı

### 1. Başlangıç (Initialization)

```
┌─────────┐     ┌─────────────┐     ┌─────────────────┐
│  python │────→│  Model      │────→│  Flask Server   │
│web_app.py│    │  Download   │     │  (port 5001)    │
└─────────┘     │  (hand_)    │     └────────┬────────┘
                └─────────────┘              │
                              ┌──────────────▼────────┐
                              │  state{} initialized  │
                              │  - camera_on: False   │
                              │  - music_playing: F   │
                              │  - hand_up: False     │
                              └───────────────────────┘
```

### 2. Kamera Açma Akışı

```
┌─────────────┐      POST /camera/on       ┌─────────────┐
│   Kullanıcı │───────────────────────────→│   Flask     │
│   Buton Tık │                            │   camera_on │
└─────────────┘                            └──────┬──────┘
                                                  │
                                                  ▼
                                         ┌─────────────────┐
                                         │ cv2.VideoCapture│
                                         │ (0, CAP_AVFND)  │
                                         └────────┬────────┘
                                                  │
                                                  ▼
                                         ┌─────────────────┐
                                         │ state.camera_on │
                                         │ = True          │
                                         └────────┬────────┘
                                                  │
                                                  ▼
                                         ┌─────────────────┐
                                         │  <img src="/    │
                                         │   video_feed">   │
                                         └─────────────────┘
```

### 3. Video Stream Döngüsü (generate_frames)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ cap.read()  │────→│ frame flip  │────→│ BGR→RGB    │────→│ MediaPipe   │
│ (kare al)   │     │ (aynalama)  │     │ dönüşüm     │     │ detect()    │
└─────────────┘     └─────────────┘     └─────────────┘     └──────┬──────┘
                                                                   │
                                                                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ MJPEG Yield │←────│ JPEG Encode │←────│ Overlay UI  │←────│ Gesture     │
│ (browser)   │     │             │     │ (çizgiler)  │     │ Analysis    │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

### 4. El Hareketi Analizi

```
MediaPipe Landmarks (21 nokta)
         │
         ▼
    ┌────────┐
    │ WRIST=0│────→┌─────────────────┐
    └────────┘     │                 │
         │         │  is_hand_up()   │────→ El Kaldırıldı
    ┌────────┐     │  Orta+İşaret    │        → Müzik Çal
    │ TIP=12 │────→│  bilek üzerinde?│
    └────────┘     └─────────────────┘
         │
         │         ┌─────────────────┐
         │         │  is_fist()      │────→ Yumruk
    ┌────────┐     │  4 parmak ucu   │        → Müzik Durdur
    │ TIP=8  │────→│  eklem altında? │
    └────────┘     └─────────────────┘
         │
         │         ┌─────────────────┐
         │         │  _check_wiggle()│────→ İşaret sallama
    ┌────────┐     │  Yön değişimi?  │        → +30sn ileri
    │MCP=5,9│────→│  + cooldown     │
    └────────┘     └─────────────────┘────→ Orta sallama
                                              → -30sn geri
```

### 5. Müzik Kontrol Akışı

```
Gesture Detected
      │
      ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  hand_up    │────→│ !playing    │────→│ _play_music │
│  detected   │     │ & no cd     │     │ (ffplay)    │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                                               ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Process    │←────│ subprocess  │←────│ Popen()     │
│  Running    │     │ .terminate│     │ [ffplay,    │
└─────────────┘     └─────────────┘     │ -ss, pos]   │
                                        └─────────────┘
```

### 6. Frontend Polling (Status Updates)

```
setInterval(500ms)
       │
       ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  GET /status│────→│  JSON Resp  │────→│  UI Update  │
│             │     │  {hand_up,  │     │  - dot colors│
│             │     │   music_p,  │     │  - progress │
│             │     │   pos, dur} │     │  - labels   │
└─────────────┘     └─────────────┘     └─────────────┘
```

---

## 🎮 El Hareketi Kontrol Haritası

| Hareket | Landmark Kontrolü | Sonuç | Fonksiyon |
|---------|---------------------|-------|-----------|
| **El Kaldırma** | `TIP[8].y < WRIST.y` ve `TIP[12].y < WRIST.y` | 🎵 Müzik Çal | `is_hand_up()` |
| **Yumruk** | `TIP[8,12,16,20].y > MCP[5,9,13,17].y` | ⏹ Müzik Durdur | `is_fist()` |
| **İşaret Sallama** | `check_wiggle(INDEX_MCP→TIP)` | ⏩ +30sn İleri | `_check_wiggle()` |
| **Orta Sallama** | `check_wiggle(MIDDLE_MCP→TIP)` | ⏪ -30sn Geri | `_check_wiggle()` |

---

## 🗂️ Dosya Yapısı

```
camera_goruntu_isleme/
├── web_app.py              # Ana Flask uygulaması
├── static/
│   └── index.html          # Frontend arayüzü
├── music/                  # Yüklenen müzik dosyaları
├── docs/
│   └── ARCHITECTURE.md     # Bu dokümantasyon
├── requirements.txt        # Python bağımlılıkları
├── settings.json           # Kullanıcı ayarları
└── hand_landmarker.task    # MediaPipe model dosyası
```

---

## 🔧 API Referansı

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

### Status JSON Formatı

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

---

## 🎮 El Hareketi Tespit Fonksiyonları

### Ana Gesture Algılama

| Fonksiyon | Dosya | Satır | Açıklama | Tetikleyen Landmark |
|-----------|-------|-------|----------|---------------------|
| `is_hand_up()` | `web_app.py` | 191-193 | El kaldırma algılama | `INDEX_FINGER_TIP(8).y < WRIST(0).y` ve `MIDDLE_FINGER_TIP(12).y < WRIST(0).y` |
| `is_fist()` | `web_app.py` | 196-199 | Yumruk algılama | `TIP[8,12,16,20].y > MCP[5,9,13,17].y` |
| `_check_wiggle()` | `web_app.py` | 202-212 | Parmak sallama algılama | `INDEX_MCP(5) → INDEX_TIP(8)` veya `MIDDLE_MCP(9) → MIDDLE_TIP(12)` arası y değişimi |

### Müzik Kontrol Fonksiyonları

| Fonksiyon | Dosya | Satır | Açıklama |
|-----------|-------|-------|----------|
| `_play_music()` | `web_app.py` | 101-115 | `ffplay` subprocess ile müzik çalma |
| `_stop_music_proc()` | `web_app.py` | 118-127 | Müzik process'ini sonlandırma |
| `_seek_music()` | `web_app.py` | 130-146 | `-ss` parametresi ile seek yapma (process restart) |

### Yardımcı Fonksiyonlar

| Fonksiyon | Dosya | Satır | Açıklama |
|-----------|-------|-------|----------|
| `generate_frames()` | `web_app.py` | 215-356 | Ana video döngüsü - gesture algılama ve müzik kontrol mantığı burada |
| `get_music_duration()` | `web_app.py` | 173-182 | `ffprobe` ile ses dosyası süresi sorgulama |
| `list_music_files()` | `web_app.py` | 152-157 | `music/` dizinindeki dosyaları listeleme |
| `find_music_file()` | `web_app.py` | 160-170 | Ayarlara göre veya ilk bulunan müzik dosyasını döndürme |
| `load_settings()` | `web_app.py` | 21-27 | `settings.json` okuma |
| `save_settings()` | `web_app.py` | 30-33 | `settings.json` yazma |

---

## 🧠 MediaPipe Landmark Referansı

```
          8 (INDEX_TIP)        12 (MIDDLE_TIP)
          |                    |
    5────┘                    9────┐
    (INDEX_MCP)                  (MIDDLE_MCP)
         \                      /
          \    0 (WRIST)       /
           \     |            /
            \    |           /
             \   |          /
              \  |         /
               \ |        /
                \|       /
                 \      /
                  \    /
                   \  /
                    \/
```

### Landmark İndeks Tablosu

| Parmağın Bölümü | Index | Sabit Adı |
|-----------------|-------|-----------|
| Bilek | 0 | WRIST |
| Baş Parmak Uç | 4 | THUMB_TIP |
| İşaret Parmak Eklemi | 5 | INDEX_MCP |
| İşaret Parmak Uç | 8 | INDEX_FINGER_TIP |
| Orta Parmak Eklemi | 9 | MIDDLE_MCP |
| Orta Parmak Uç | 12 | MIDDLE_FINGER_TIP |
| Yüzük Parmak Uç | 16 | RING_FINGER_TIP |
| Serçe Parmak Uç | 20 | PINKY_TIP |

---

## ⚙️ Konfigürasyon

### Ayarlar (settings.json)

```json
{
  "music_file": "song.mp3",
  "restart_mode": false
}
```

- `music_file`: Son seçilen müzik dosyası
- `restart_mode`: 
  - `false` = Durduğun yerden devam et (resume)
  - `true` = Her seferinde baştan başla

### Threshold Değerleri

| Parametre | Değer | Açıklama |
|-----------|-------|----------|
| `WIGGLE_THRESHOLD` | 0.04 | Parmak sallama eşiği |
| `WIGGLE_COOLDOWN` | 0.8s | Sallama cooldown süresi |
| `min_hand_detection_confidence` | 0.7 | El tespit güven skoru |
| `min_tracking_confidence` | 0.5 | Takip güven skoru |

---

## 🚀 Çalıştırma Adımları

1. **Bağımlılıkları kur:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Uygulamayı başlat:**
   ```bash
   python web_app.py
   ```

3. **Tarayıcıda aç:**
   ```
   http://127.0.0.1:5001
   ```

4. **Kamera izni ver** ve "Kamerayı Aç" butonuna tıkla

5. **El hareketleriyle kontrol et:**
   - ✋ El kaldır → Müzik çal
   - ✊ Yumruk → Müzik dur
   - 👆 İşaret parmağı salla → +30sn
   - 🖕 Orta parmak salla → -30sn
