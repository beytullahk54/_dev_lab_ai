# Veri Akışı

## 1. Başlangıç (Initialization)

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

### Kod

```python
# Model otomatik indirme
if not os.path.exists(MODEL_PATH):
    ssl_ctx = ssl.create_default_context(cafile=certifi.where())
    with urllib.request.urlopen(MODEL_URL, context=ssl_ctx) as response:
        f.write(response.read())

# MediaPipe başlatma
_base_options = mp_python.BaseOptions(model_asset_path=MODEL_PATH)
_options = mp_vision.HandLandmarkerOptions(...)
hhands = mp_vision.HandLandmarker.create_from_options(_options)

# State başlatma
state = {
    "hand_up": False,
    "status": "El Algılanmadı",
    "music_playing": False,
    "camera_on": False,
    ...
}
```

## 2. Kamera Açma Akışı

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

## 3. Video Stream Döngüsü

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

### generate_frames() Akışı

```python
while True:
    # 1. Frame oku
    ret, frame = cap.read()
    
    # 2. İşleme
    frame = cv2.flip(frame, 1)                    # Aynalama
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # Renk dönüşümü
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    
    # 3. Detection
    results = hhands.detect_for_video(mp_image, timestamp)
    
    # 4. Gesture analizi
    if results.hand_landmarks:
        if is_fist(lm_list): ...
        if is_hand_up(lm_list): ...
        if _check_wiggle(...): ...
    
    # 5. Müzik aksiyonları
    if hand_up and not playing: _play_music()
    if fist and playing: _stop_music_proc()
    if wiggle: _seek_music()
    
    # 6. Render ve stream
    cv2.line(...); cv2.circle(...); cv2.putText(...)
    yield jpeg_bytes
```

## 4. El Hareketi Analizi

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

## 5. Müzik Kontrol Akışı

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

### State Machine

```
        hand_up (cd geçtiyse)
    ┌─────────────────────────┐
    │                         ▼
┌───────┐                ┌─────────┐
│ IDLE  │◄───────────────│ PLAYING │
│       │     fist       │         │
└───────┘                └────┬────┘
    ▲                         │
    └─────────────────────────┘
         hand_up (resume)
```

## 6. Frontend Polling (Status Updates)

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

### JavaScript Polling

```javascript
function startPolling() {
  polling = setInterval(async () => {
    const r = await fetch('/status');
    const d = await r.json();
    
    // UI güncelleme
    setDot('dot-camera', d.camera_on ? 'green' : '');
    setDot('dot-hand', d.hand_up ? 'green' : '');
    setDot('dot-music', d.music_playing ? 'purple' : '');
    
    // Progress bar
    const pct = (d.music_pos / d.music_duration) * 100;
    document.getElementById('progress-fill').style.width = pct + '%';
  }, 500);
}
```
