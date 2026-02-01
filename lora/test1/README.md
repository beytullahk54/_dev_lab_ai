# LoRA Eğitimi - Basit Başlangıç 🍎

Apple Silicon için optimize edilmiş, **çok basit** LoRA eğitim projesi.

## 🎯 LoRA Nedir?

**Normal Eğitim:**

- 1.1 milyar parametre eğitilir
- Çok fazla bellek gerekir (16GB+)
- Çok yavaş

**LoRA ile:**

- Sadece 2 milyon parametre eğitilir (%99.8 daha az!)
- Az bellek gerekir (4-8GB)
- Çok hızlı

## 📋 Gereksinimler

- **Mac:** M1, M2 veya M3 chip
- **RAM:** En az 8GB
- **Python:** 3.8+

## 🚀 Kurulum (3 Adım)

### 1. Kütüphaneleri Yükle

```bash
pip install -r requirements.txt
```

⏱️ İlk kurulum 5-10 dakika sürebilir.

### 2. Eğitimi Başlat

```bash
python train.py
```

⏱️ Eğitim 2-5 dakika sürer.

### 3. Modeli Test Et

```bash
python test.py
```

## 📁 Dosyalar

```
.
├── requirements.txt    # Gerekli kütüphaneler (5 adet)
├── train.py           # Eğitim scripti (8 adım)
├── test.py            # Test scripti (interaktif)
└── README.md          # Bu dosya
```

## 📖 Kod Açıklaması

### train.py - 8 Basit Adım

```python
# ADIM 1: Cihaz kontrolü (Apple GPU var mı?)
device = "mps" if torch.backends.mps.is_available() else "cpu"

# ADIM 2: 1B model yükle
model = AutoModelForCausalLM.from_pretrained("TinyLlama-1.1B")

# ADIM 3: LoRA uygula (1.1B → 2M parametre!)
lora_config = LoraConfig(r=8)
model = get_peft_model(model, lora_config)

# ADIM 4: Eğitim verisi hazırla
train_data = ["Merhaba!", "Python nedir?", ...]

# ADIM 5: Eğitim ayarları
training_args = TrainingArguments(num_train_epochs=3, ...)

# ADIM 6: Eğit!
trainer = Trainer(model=model, ...)
trainer.train()

# ADIM 7: Kaydet
model.save_pretrained("./lora-model")

# ADIM 8: Test
outputs = model.generate(inputs)
```

## ⚙️ Parametreler

### LoRA Rank (r)

```python
r=8   # Hızlı, az parametre (başlangıç için iyi) ✅
r=16  # Daha iyi sonuçlar
r=32  # En iyi sonuçlar ama yavaş
```

### Epoch Sayısı

```python
num_train_epochs=3  # Normal ✅
num_train_epochs=5  # Daha iyi öğrenir
num_train_epochs=1  # Hızlı test için
```

### Batch Size

```python
per_device_train_batch_size=2  # Az bellek ✅
per_device_train_batch_size=4  # Daha hızlı (M2/M3 için)
```

## 🎓 Kendi Verinizle Eğitin

### train.py içinde değiştirin:

```python
# Eski:
train_data = [
    "Merhaba! Nasılsın?",
    "Python nedir?",
]

# Yeni:
train_data = [
    "Kendi cümlelerinizi buraya yazın",
    "Ne kadar çok veri o kadar iyi",
    "En az 50-100 cümle olmalı",
    # ... daha fazla
]
```

veya dosyadan yükleyin:

```python
with open("veriler.txt", "r", encoding="utf-8") as f:
    train_data = f.readlines()
```

## 📊 Performans

| Mac | Eğitim Süresi (8 örnek) | Gerçek Veri (1000 örnek) |
| --- | ----------------------- | ------------------------ |
| M1  | 3-5 dakika              | 20-30 dakika             |
| M2  | 2-4 dakika              | 15-20 dakika             |
| M3  | 2-3 dakika              | 10-15 dakika             |

## 🐛 Sorun Giderme

### "MPS backend not available"

```bash
# PyTorch güncelleyin:
pip install --upgrade torch
```

### "Out of memory"

```python
# train.py içinde:
per_device_train_batch_size=1  # 2 yerine 1
max_length=64  # 128 yerine 64
```

### Model saçma yanıtlar veriyor

- Daha fazla veri ekleyin (100+)
- Daha fazla epoch kullanın (5-10)
- r değerini artırın (16 veya 32)

## 💡 İpuçları

1. **İlk deneme:** Kodu olduğu gibi çalıştırın
2. **Veri ekleyin:** 50-100 örnek ekleyin
3. **Parametrelerle oynayın:** r, epochs, batch_size
4. **Test edin:** Her değişiklikten sonra test edin

## ❓ SSS

**S: GPU şart mı?**  
C: Hayır ama Apple GPU (MPS) çok daha hızlı. CPU ile de çalışır.

**S: Kaç veri gerekli?**  
C: Minimum 10-20, ideal 100-1000+

**S: Eğitim ne kadar sürer?**  
C: 8 örnek için 2-5 dakika, 1000 örnek için 15-30 dakika

**S: Model ne kadar yer kaplar?**  
C: LoRA adapter sadece 10-20MB! Base model 2GB ama bir kez indirilir.

**S: Türkçe çalışır mı?**  
C: Evet! TinyLlama İngilizce ama Türkçe de öğrenir.

## 🎉 Başarılar!

Artık LoRA'nın temellerini öğrendiniz:

- ✅ %99.8 daha az parametre eğittiniz
- ✅ Çok daha hızlı eğittiniz
- ✅ Kendi modelinizi oluşturdunuz

Sorularınız için issue açabilirsiniz!
