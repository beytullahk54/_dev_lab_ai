# Gesture Algılama

## El Hareketi Kontrol Haritası

| Hareket | Landmark Kontrolü | Sonuç | Fonksiyon |
|---------|---------------------|-------|-----------|
| **El Kaldırma** | `TIP[8].y < WRIST.y` ve `TIP[12].y < WRIST.y` | 🎵 Müzik Çal | `is_hand_up()` |
| **Yumruk** | `TIP[8,12,16,20].y > MCP[5,9,13,17].y` | ⏹ Müzik Durdur | `is_fist()` |
| **İşaret Sallama** | `check_wiggle(INDEX_MCP→TIP)` | ⏩ +30sn İleri | `_check_wiggle()` |
| **Orta Sallama** | `check_wiggle(MIDDLE_MCP→TIP)` | ⏪ -30sn Geri | `_check_wiggle()` |

## Fonksiyon Implementasyonları

### is_hand_up()

```python
@/Volumes/Kodlooper/kodlooperYazilim/htdocs/camera_goruntu_isleme/web_app.py:191-193
def is_hand_up(landmarks):
    return (landmarks[MIDDLE_FINGER_TIP].y < landmarks[WRIST].y and
            landmarks[INDEX_FINGER_TIP].y < landmarks[WRIST].y)
```

**Mantık**: İşaret ve orta parmak uçları, bilek seviyesinin **üzerinde** (y değeri küçük) ise el kaldırılmıştır.

::: tip Y Ekseni
MediaPipe'de `y` değeri:
- `0` = üst (küçük)
- `1` = alt (büyük)
:::

### is_fist()

```python
@/Volumes/Kodlooper/kodlooperYazilim/htdocs/camera_goruntu_isleme/web_app.py:196-199
def is_fist(landmarks):
    tips = [INDEX_FINGER_TIP, MIDDLE_FINGER_TIP, RING_FINGER_TIP, PINKY_TIP]
    mcps = [INDEX_MCP, MIDDLE_MCP, 13, 17]
    return all(landmarks[tip].y > landmarks[mcp].y for tip, mcp in zip(tips, mcps))
```

**Mantık**: 4 parmak ucu, karşılık gelen ekleminden **aşağıda** ise (y değeri büyük) yumruktur.

### _check_wiggle()

```python
@/Volumes/Kodlooper/kodlooperYazilim/htdocs/camera_goruntu_isleme/web_app.py:202-212
def _check_wiggle(prev_y, curr_y, last_dir, cooldown_until, current_time):
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

**Mantık**: 
1. Y eksenindeki değişimi hesapla
2. Threshold'u (0.04) geçiyorsa yön belirle
3. Yön değiştiyse ve cooldown bittiyse sallama tespit et

## generate_frames() İçinde Kullanım

```python
@/Volumes/Kodlooper/kodlooperYazilim/htdocs/camera_goruntu_isleme/web_app.py:265-283
# Parmağın göreceli y pozisyonu (MCP'den TIP'e)
idx_y = lm_list[INDEX_FINGER_TIP].y - lm_list[INDEX_MCP].y
mid_y = lm_list[MIDDLE_FINGER_TIP].y - lm_list[MIDDLE_MCP].y

# Sallama kontrolü
idx_trig, _index_last_dir = _check_wiggle(
    _prev_index_y, idx_y, _index_last_dir,
    _index_wiggle_cooldown, current_time
)
mid_trig, _middle_last_dir = _check_wiggle(
    _prev_middle_y, mid_y, _middle_last_dir,
    _middle_wiggle_cooldown, current_time
)

# Aksiyon belirle
if idx_trig:
    seek_action = 30      # +30sn
elif mid_trig:
    seek_action = -30     # -30sn
```

## State Machine

```
┌─────────────┐    hand_up    ┌─────────────┐
│   IDLE      │──────────────→│  PLAYING    │
│ (kapalı)    │               │ (çalıyor)   │
└──────┬──────┘               └──────┬──────┘
       ↑                            │
       └────────── fist ────────────┘
```

- `IDLE` + `hand_up` → `PLAYING` (müzik çal)
- `PLAYING` + `fist` → `IDLE` (müzik dur, pozisyon kaydet)
- `PLAYING` + `wiggle` → seek (±30sn)
