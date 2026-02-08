# 🦙 Ollama ile LLM Kullanımı

## 📋 Gereksinimler

### 1. Ollama'yı Yükleyin
Windows için: https://ollama.ai/download

### 2. Ollama Servisini Başlatın
```bash
ollama serve
```

### 3. Gemma 2:2b Modelini İndirin
```bash
ollama pull gemma2:2b
```

**Not:** Eğer `gemma3:4b` kullanmak isterseniz:
```bash
ollama pull gemma3:4b
```

Sonra `main.py` dosyasında `MODEL_NAME` değişkenini değiştirin:
```python
MODEL_NAME = "gemma3:4b"  # veya "gemma2:2b"
```

## 🚀 Backend'i Başlatın

```bash
cd backend
python main.py
```

## ✅ Test Edin

1. **API Durumu:** http://localhost:8000
2. **Swagger Docs:** http://localhost:8000/docs
3. **Streaming Test:** Frontend'i çalıştırın

## 📊 Mevcut Modelleri Görüntüleyin

```bash
ollama list
```

## 🔄 Değişiklikler

### Önceki Sistem (Hugging Face):
- ❌ Yavaş (CPU'da çalışıyor)
- ❌ Büyük bağımlılıklar (torch, transformers)
- ❌ Model indirme karmaşık

### Yeni Sistem (Ollama):
- ✅ Hızlı (optimize edilmiş)
- ✅ Hafif bağımlılıklar
- ✅ Kolay model yönetimi
- ✅ Gerçek streaming desteği

## 🎯 Avantajlar

1. **Gerçek Streaming:** Token'lar gerçek zamanlı üretilir
2. **Daha Hızlı:** Ollama optimize edilmiş inference sağlar
3. **Kolay Yönetim:** `ollama pull`, `ollama list` gibi komutlar
4. **Daha İyi Modeller:** Gemma, Llama, Mistral vb. kolayca kullanılabilir
