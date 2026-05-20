# Threshold Değerleri

## Konfigürasyon Parametreleri

| Parametre | Değer | Açıklama | Konum |
|-----------|-------|----------|-------|
| `WIGGLE_THRESHOLD` | 0.04 | Parmak sallama eşiği | `web_app.py:71` |
| `WIGGLE_COOLDOWN` | 0.8s | Sallama cooldown süresi | `web_app.py:72` |
| `min_hand_detection_confidence` | 0.7 | El tespit güven skoru | `web_app.py:50` |
| `min_tracking_confidence` | 0.5 | Takip güven skoru | `web_app.py:52` |
| `min_hand_presence_confidence` | 0.5 | El varlığı güven skoru | `web_app.py:51` |

## WIGGLE_THRESHOLD

Parmak sallama algılaması için Y eksenindeki minimum değişim.

```python
@/Volumes/Kodlooper/kodlooperYazilim/htdocs/camera_goruntu_isleme/web_app.py:71
WIGGLE_THRESHOLD = 0.04
```

### Çalışma Mantığı

```python
delta = curr_y - prev_y  # Y değişimi
if abs(delta) < WIGGLE_THRESHOLD:
    return False  # Sallama yok (küçük hareket)
else:
    new_dir = "down" if delta > 0 else "up"
    # Yön değişimi varsa sallama tespit et
```

### Ayarlama Önerileri

| Değer | Sonuç |
|-------|-------|
| 0.02 | Çok hassas, yanlış pozitif artar |
| **0.04** | **Varsayılan, dengeli** |
| 0.08 | Daha az hassas, güçlü sallama gerekir |
| 0.15 | Sadece belirgin sallamalar algılanır |

## WIGGLE_COOLDOWN

Ardışık sallama algılamaları arasındaki minimum süre.

```python
@/Volumes/Kodlooper/kodlooperYazilim/htdocs/camera_goruntu_isleme/web_app.py:72
WIGGLE_COOLDOWN = 0.8  # saniye
```

### Amaç

Spam önleme - sürekli sallama durumunda her hareket için seek yapmasını engeller.

```python
if current_time > cooldown_until:
    triggered = True
    cooldown_until = current_time + WIGGLE_COOLDOWN
```

## MediaPipe Confidence Değerleri

```python
@/Volumes/Kodlooper/kodlooperYazilim/htdocs/camera_goruntu_isleme/web_app.py:47-54
_options = mp_vision.HandLandmarkerOptions(
    base_options=_base_options,
    num_hands=1,
    min_hand_detection_confidence=0.7,    # El tespiti
    min_hand_presence_confidence=0.5,      # El varlığı
    min_tracking_confidence=0.5,            # Takip kalitesi
    running_mode=mp_vision.RunningMode.VIDEO
)
```

### Confidence Seviyeleri

| Değer | Hassasiyet | Performans |
|-------|------------|------------|
| 0.3 | Yüksek algılama | Daha fazla yanlış pozitif |
| **0.5** | Dengeli | **Varsayılan** |
| 0.7 | **Daha katı** | **Proje değeri** |
| 0.9 | Çok katı | Düşük algılama, az hata |

## Zamanlama Parametreleri

| Parametre | Değer | Açıklama |
|-----------|-------|----------|
| Frame timestamp increment | 33ms | ~30 FPS |
| Status polling interval | 500ms | Frontend güncelleme |
| Process wait timeout | 1s | `ffplay` terminate bekleme |
| Cooldown süresi (hand_up) | 1.0s | El kaldırma tekrar eşiği |

## Özelleştirme

Kendi threshold değerlerinizi test edin:

```python
# web_app.py içinde değiştirin
WIGGLE_THRESHOLD = 0.06  # Daha az hassas
WIGGLE_COOLDOWN = 1.2    # Daha uzun bekleme
```

::: warning Not
Değişiklikler için uygulamayı yeniden başlatmanız gerekir.
:::
