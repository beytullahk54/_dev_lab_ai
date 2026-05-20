# Kurulum

## Gereksinimler

- Python 3.8+
- macOS / Linux / Windows
- Kamera (built-in veya USB)
- ffmpeg (ffplay için)

## Adım Adım Kurulum

### 1. Repoyu Klonla

```bash
git clone <repo-url>
cd camera_goruntu_isleme
```

### 2. Python Bağımlılıklarını Kur

```bash
pip install -r requirements.txt
```

::: tip requirements.txt içeriği
```
opencv-python==4.9.0.80
mediapipe==0.10.35
pygame==2.6.1
```
:::

### 3. ffmpeg Kurulumu

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt-get install ffmpeg
```

**Windows:**
[ffmpeg.org](https://ffmpeg.org/download.html) adresinden indirin ve PATH'e ekleyin.

### 4. Uygulamayı Başlat

```bash
python web_app.py
```

### 5. Tarayıcıda Aç

```
http://127.0.0.1:5001
```

## İlk Kullanım

1. **"Kamerayı Aç"** butonuna tıklayın
2. Kamera izni verin
3. **Müzik Yükle** kısmından bir ses dosyası seçin
4. El hareketleriyle kontrol edin:
   - ✋ El kaldır → Müzik çal
   - ✊ Yumruk → Dur
   - 👆 İşaret salla → +30sn
   - 🖕 Orta salla → -30sn

## Sorun Giderme

### Kamera Açılmıyor

```python
# web_app.py line 444
cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)  # macOS
cv2.VideoCapture(0)  # Diğer sistemler
```

Farklı kamera indekslerini deneyin: `0`, `1`, `2`

### Müzik Çalmıyor

ffplay'in kurulu olduğundan emin olun:
```bash
which ffplay
ffplay -version
```
