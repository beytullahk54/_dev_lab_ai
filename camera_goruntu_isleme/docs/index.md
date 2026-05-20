---
layout: home

hero:
  name: "El Hareketi Müzik Kontrolü"
  text: "Kamera ile Müzik Kontrolü"
  tagline: "El hareketlerini algılayarak müzik oynatmayı kontrol eden web uygulaması"
  actions:
    - theme: brand
      text: "Başla"
      link: /guide/
    - theme: alt
      text: "GitHub'da Gör"
      link: https://github.com

features:
  - icon: ✋
    title: El Kaldırma
    details: El kaldırarak müziği başlatın
  - icon: ✊
    title: Yumruk
    details: Yumruk yaparak müziği durdurun
  - icon: 👆
    title: Parmağı Salla
    details: İşaret parmağı ile +30sn ileri atlayın
  - icon: 🖕
    title: Orta Parmak
    details: Orta parmak ile -30sn geri atlayın
---

## Hızlı Başlangıç

```bash
# Bağımlılıkları kur
pip install -r requirements.txt

# Uygulamayı başlat
python web_app.py

# Tarayıcıda aç
open http://127.0.0.1:5001
```

## Teknolojiler

- **Flask** - Web sunucusu
- **OpenCV** - Kamera yakalama
- **MediaPipe Hands** - El izleme
- **ffplay** - Ses oynatma
