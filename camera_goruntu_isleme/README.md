# El Hareketi ile Müzik Kontrolü

Kameradan el hareketlerinizi algılayarak müzik çalma/durdurma uygulaması.

## Özellikler

- ✋ El kaldırıldığında müzik çalar
- ✊ El indirildiğinde müzik durur
- 🎯 Gerçek zamanlı el izleme
- 📹 Canlı kamera görüntüsü

## Kurulum

```bash
pip install -r requirements.txt
```

## Kullanım

1. Müzik dosyanızı `muzik.mp3` olarak kaydedin (veya herhangi bir .mp3/.wav/.ogg dosyası)
2. Uygulamayı çalıştırın:

```bash
python el_muzik.py
```

3. Web kameranıza bakın ve elinizi kaldırın
4. Çıkmak için `q` tuşuna basın

## Gereksinimler

- Python 3.7+
- Web kamera
- OpenCV
- MediaPipe
- Pygame
