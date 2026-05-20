# Fonksiyon Referansı

## El Hareketi Tespit Fonksiyonları

### Ana Gesture Algılama

| Fonksiyon | Dosya | Satır | Açıklama | Tetikleyen Landmark |
|-----------|-------|-------|----------|---------------------|
| `is_hand_up()` | `web_app.py` | 191-193 | El kaldırma algılama | `INDEX_FINGER_TIP(8).y < WRIST(0).y` ve `MIDDLE_FINGER_TIP(12).y < WRIST(0).y` |
| `is_fist()` | `web_app.py` | 196-199 | Yumruk algılama | `TIP[8,12,16,20].y > MCP[5,9,13,17].y` |
| `_check_wiggle()` | `web_app.py` | 202-212 | Parmak sallama algılama | `INDEX_MCP(5) → INDEX_TIP(8)` veya `MIDDLE_MCP(9) → MIDDLE_TIP(12)` arası y değişimi |

### Implementasyonlar

#### is_hand_up()

```python
def is_hand_up(landmarks):
    """
    İşaret ve orta parmak ucu bilek üzerindeyse True döner.
    
    Args:
        landmarks: MediaPipe 21 nokta listesi
        
    Returns:
        bool: El kaldırılmışsa True
    """
    return (landmarks[MIDDLE_FINGER_TIP].y < landmarks[WRIST].y and
            landmarks[INDEX_FINGER_TIP].y < landmarks[WRIST].y)
```

#### is_fist()

```python
def is_fist(landmarks):
    """
    4 parmak ucu eklem altındaysa (bükülmüşse) True döner.
    
    Args:
        landmarks: MediaPipe 21 nokta listesi
        
    Returns:
        bool: Yumruk yapılmışsa True
    """
    tips = [INDEX_FINGER_TIP, MIDDLE_FINGER_TIP, RING_FINGER_TIP, PINKY_TIP]
    mcps = [INDEX_MCP, MIDDLE_MCP, 13, 17]
    return all(landmarks[tip].y > landmarks[mcp].y for tip, mcp in zip(tips, mcps))
```

#### _check_wiggle()

```python
def _check_wiggle(prev_y, curr_y, last_dir, cooldown_until, current_time):
    """
    Parmak sallama (wiggle) algılar.
    
    Args:
        prev_y: Önceki Y pozisyonu (göreceli)
        curr_y: Şu anki Y pozisyonu
        last_dir: Son yön ("up" veya "down")
        cooldown_until: Cooldown bitiş zamanı
        current_time: Şu anki zaman
        
    Returns:
        tuple: (triggered: bool, new_dir: str)
    """
    if prev_y is None:
        return False, last_dir
    
    delta = curr_y - prev_y
    
    if abs(delta) < WIGGLE_THRESHOLD:  # 0.04
        return False, last_dir
    
    new_dir = "down" if delta > 0 else "up"
    triggered = False
    
    # Yön değişimi + cooldown kontrolü
    if new_dir != last_dir and last_dir is not None and current_time > cooldown_until:
        triggered = True
    
    return triggered, new_dir
```

## Müzik Kontrol Fonksiyonları

| Fonksiyon | Dosya | Satır | Açıklama |
|-----------|-------|-------|----------|
| `_play_music()` | `web_app.py` | 101-115 | `ffplay` subprocess ile müzik çalma |
| `_stop_music_proc()` | `web_app.py` | 118-127 | Müzik process'ini sonlandırma |
| `_seek_music()` | `web_app.py` | 130-146 | `-ss` parametresi ile seek yapma (process restart) |

### _play_music()

```python
def _play_music(file_path, start_pos=0.0):
    """
    ffplay subprocess ile müzik çalar.
    
    Args:
        file_path: Ses dosyası yolu
        start_pos: Başlangıç pozisyonu (saniye)
    """
    global _music_proc, _music_pos, _music_start_time
    
    with _music_lock:
        # Önceki process'i sonlandır
        if _music_proc and _music_proc.poll() is None:
            _music_proc.terminate()
            try:
                _music_proc.wait(timeout=1)
            except Exception:
                _music_proc.kill()
        
        # Yeni process başlat
        _music_proc = subprocess.Popen(
            ["ffplay", "-nodisp", "-autoexit", "-ss", str(max(0.0, start_pos)), file_path],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        
        _music_start_time = time.time() - start_pos
        _music_pos = start_pos
```

## Yardımcı Fonksiyonlar

| Fonksiyon | Dosya | Satır | Açıklama |
|-----------|-------|-------|----------|
| `generate_frames()` | `web_app.py` | 215-356 | Ana video döngüsü - gesture algılama ve müzik kontrol mantığı burada |
| `get_music_duration()` | `web_app.py` | 173-182 | `ffprobe` ile ses dosyası süresi sorgulama |
| `list_music_files()` | `web_app.py` | 152-157 | `music/` dizinindeki dosyaları listeleme |
| `find_music_file()` | `web_app.py` | 160-170 | Ayarlara göre veya ilk bulunan müzik dosyasını döndürme |
| `load_settings()` | `web_app.py` | 21-27 | `settings.json` okuma |
| `save_settings()` | `web_app.py` | 30-33 | `settings.json` yazma |

### generate_frames()

Ana video döngüsü. Sürekli çalışır ve her frame için:

1. Kareden oku
2. MediaPipe detection
3. Gesture analizi
4. Müzik aksiyon kararı
5. Overlay render
6. MJPEG stream

```python
def generate_frames():
    """
    MJPEG video stream generator.
    Sonsuz döngüde çalışır, her frame için gesture algılama yapar.
    
    Yields:
        bytes: MJPEG frame verisi
    """
    while True:
        # ... frame okuma ve detection
        
        if results.hand_landmarks:
            for lm_list in results.hand_landmarks:
                # Gesture kontrolleri
                if is_fist(lm_list):
                    fist = True
                elif is_hand_up(lm_list):
                    hand_up = True
                
                # Wiggle kontrolü
                idx_y = lm_list[INDEX_FINGER_TIP].y - lm_list[INDEX_MCP].y
                idx_trig, _ = _check_wiggle(...)
        
        # State güncelleme ve aksiyon
        # ...
        
        yield mjpeg_frame
```

## Global Değişkenler

| Değişken | Tip | Açıklama |
|----------|-----|----------|
| `state` | dict | Uygulama durumu |
| `cap` | VideoCapture | OpenCV kamera nesnesi |
| `hhands` | HandLandmarker | MediaPipe modeli |
| `_music_proc` | Popen \| None | ffplay subprocess |
| `_music_lock` | Lock | Thread-safe müzik kontrolü |
