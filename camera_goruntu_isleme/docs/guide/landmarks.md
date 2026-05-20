# MediaPipe Landmark Referansı

## 21 Noktalı El Modeli

MediaPipe Hands, her el için 21 adet 3D landmark (x, y, z) döndürür.

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

## Landmark İndeks Tablosu

| Parmağın Bölümü | Index | Sabit Adı | Açıklama |
|-----------------|-------|-----------|----------|
| **Bilek** | 0 | `WRIST` | El kök noktası |
| **Baş Parmak** | | | |
| CMC (Taban) | 1 | - | Carpometacarpal |
| MCP (Eklem) | 2 | - | Metacarpophalangeal |
| IP (Ara Eklem) | 3 | - | Interphalangeal |
| Uç | 4 | `THUMB_TIP` | Baş parmak uç |
| **İşaret Parmağı** | | | |
| MCP (Eklem) | 5 | `INDEX_MCP` | İşaret parmağı taban |
| PIP | 6 | - | Proximal interphalangeal |
| DIP | 7 | - | Distal interphalangeal |
| Uç | 8 | `INDEX_FINGER_TIP` | İşaret parmağı uç |
| **Orta Parmak** | | | |
| MCP (Eklem) | 9 | `MIDDLE_MCP` | Orta parmak taban |
| PIP | 10 | - | - |
| DIP | 11 | - | - |
| Uç | 12 | `MIDDLE_FINGER_TIP` | Orta parmak uç |
| **Yüzük Parmağı** | | | |
| MCP (Eklem) | 13 | - | - |
| PIP | 14 | - | - |
| DIP | 15 | - | - |
| Uç | 16 | `RING_FINGER_TIP` | Yüzük parmağı uç |
| **Serçe Parmağı** | | | |
| MCP (Eklem) | 17 | - | - |
| PIP | 18 | - | - |
| DIP | 19 | - | - |
| Uç | 20 | `PINKY_TIP` | Serçe parmağı uç |

## Koordinat Sistemi

```python
landmark = {
    x: 0.5,  # 0.0 (sol) ~ 1.0 (sağ)
    y: 0.3,  # 0.0 (üst) ~ 1.0 (alt)
    z: 0.1   # Derinlik (bileğe göre göreceli)
}
```

::: warning Önemli
- `x` ve `y` normalize edilmiştir (0-1 arası)
- `y` değeri **ters**: 0 = üst, 1 = alt
- `z` bilek derinliğine göre görecelidir
:::

## HAND_CONNECTIONS

Projede kullanılan bağlantılar (iskelet çizgileri):

```python
HAND_CONNECTIONS = [
    # Baş parmak
    (0,1), (1,2), (2,3), (3,4),
    # İşaret parmak
    (0,5), (5,6), (6,7), (7,8),
    # Orta parmak
    (5,9), (9,10), (10,11), (11,12),
    # Yüzük parmak
    (9,13), (13,14), (14,15), (15,16),
    # Serçe parmak
    (13,17), (17,18), (18,19), (19,20),
    # Bilek tabanı
    (0,17)
]
```

## Landmark Kullanım Örnekleri

### İki nokta arası mesafe

```python
import math

def distance(lm1, lm2):
    return math.sqrt(
        (lm1.x - lm2.x)**2 + 
        (lm1.y - lm2.y)**2
    )

# İşaret ve orta parmak ucu mesafesi
dist = distance(landmarks[8], landmarks[12])
```

### Açı hesaplama

```python
import math

def angle(lm1, lm2, lm3):
    # lm2 köşe noktası
    v1 = (lm1.x - lm2.x, lm1.y - lm2.y)
    v2 = (lm3.x - lm2.x, lm3.y - lm2.y)
    
    dot = v1[0]*v2[0] + v1[1]*v2[1]
    mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
    mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
    
    return math.degrees(math.acos(dot / (mag1 * mag2)))

# Parmak bükülme açısı
angle_tip = angle(landmarks[8], landmarks[6], landmarks[5])
```
