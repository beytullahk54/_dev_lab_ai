# Proje Özeti

Bu proje, kamera aracılığıyla el hareketlerini algılayarak müzik oynatmayı kontrol eden bir web uygulamasıdır.

## Özellikler

- ✋ **El Kaldırma** → Müzik çal
- ✊ **Yumruk** → Müzik durdur
- 👆 **İşaret Parmağı Sallama** → +30sn ileri
- 🖕 **Orta Parmak Sallama** → -30sn geri

## Kullanılan Teknolojiler

| Teknoloji | Sürüm | Görevi |
|-----------|-------|--------|
| **Flask** | - | Web sunucusu, REST API |
| **OpenCV** | 4.9.0.80 | Kameradan görüntü yakalama |
| **MediaPipe Hands** | 0.10.35 | El izleme (21 nokta) |
| **ffplay** | - | Ses oynatıcı |
| **HTML5/JS/CSS3** | - | Kullanıcı arayüzü |

## Sistem Mimarisi

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                              │
│  index.html  ←──  JavaScript  ←──  CSS (Dark Theme)         │
└──────────────────────┬────────────────────────────────────────┘
                       │ HTTP
┌──────────────────────▼────────────────────────────────────────┐
│                      BACKEND (Flask)                          │
│  • /video_feed → MJPEG stream                                │
│  • /status → JSON polling                                    │
│  • /camera/on|off → Kamera kontrol                           │
│  • /music/* → Müzik yönetimi                                 │
└──────────────────────┬────────────────────────────────────────┘
                       │
┌──────────────────────▼────────────────────────────────────────┐
│                  VISION PIPELINE                              │
│  OpenCV → MediaPipe → Gesture Detection → Music Control      │
└───────────────────────────────────────────────────────────────┘
```

## Sonraki Adımlar

- [Kurulum](./installation) - Projeyi çalıştırma
- [Mimari](./architecture) - Detaylı sistem mimarisi
- [Gesture Algılama](./gestures) - El hareketi tespiti
- [İleri Düzey](./advanced-vision) - YOLO, Detectron2, Neo4j, Multi-Agent örnekleri
