# Sistem Mimarisi

## Genel Bakış

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

## Komponent Detayları

### Frontend (`static/index.html`)

- **HTML**: Temel yapı, video container, kontrol butonları
- **CSS**: Dark theme, responsive design, progress bar
- **JavaScript**: 
  - Event handlers (buton tıklamaları)
  - Status polling (`/status` her 500ms)
  - File upload handling

### Backend (`web_app.py`)

::: info Global State
```python
state = {
    "hand_up": False,
    "status": "El Algılanmadı",
    "music_playing": False,
    "camera_on": False,
    "music_file": None,
    "music_duration": 0.0,
    "restart_mode": False
}
```
Thread-safe erişim için `threading.Lock()` kullanılır.
:::

### Vision Pipeline

```
cap.read() → frame
    ↓
cv2.flip(frame, 1)  # Yatay aynalama
    ↓
mp.Image(format=SRGB, data=rgb)
    ↓
hhands.detect_for_video(mp_image, timestamp)
    ↓
results.hand_landmarks[0]  # 21 nokta
    ↓
is_hand_up() / is_fist() / _check_wiggle()
    ↓
_music_proc kontrolü
```

## Veri Akışı

### 1. Kamera Açma

```
Kullanıcı buton tıklar
    ↓
POST /camera/on
    ↓
cv2.VideoCapture(0)
    ↓
state["camera_on"] = True
    ↓
<img src="/video_feed"> başlar
```

### 2. Video Stream

```
generate_frames() (sonsuz döngü)
    ↓
cap.read() → frame
    ↓
MediaPipe detection
    ↓
Gesture analysis
    ↓
Music action (thread)
    ↓
Overlay render
    ↓
MJPEG yield
```

### 3. Status Polling

```
setInterval(500ms)
    ↓
GET /status
    ↓
JSON response
    ↓
UI update (dots, progress, labels)
```
