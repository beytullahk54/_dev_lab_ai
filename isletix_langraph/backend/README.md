# 🤖 Groq AI Dosya Oluşturucu Agent

Langchain ve Groq API kullanarak dosya oluşturan akıllı bir AI agent.

## 🌟 Özellikler

- ✅ **Groq API** entegrasyonu (Mixtral-8x7b-32768 modeli)
- ✅ **Langchain** framework ile agent yapısı
- ✅ Doğal dil ile dosya oluşturma
- ✅ Türkçe dil desteği
- ✅ Markdown, Text, JSON formatları
- ✅ İnteraktif komut satırı arayüzü

## 📋 Gereksinimler

- Python 3.8+
- Groq API Key ([buradan](https://console.groq.com) alabilirsiniz)

## 🚀 Kurulum

### 1. Bağımlılıkları yükleyin:

```bash
pip install -r requirements.txt
```

### 2. API Key'inizi ayarlayın:

`.env.example` dosyasını `.env` olarak kopyalayın ve Groq API key'inizi ekleyin:

```bash
copy .env.example .env
```

`.env` dosyasını düzenleyin:

```
GROQ_API_KEY=gsk_your_actual_api_key_here
```

## 💻 Kullanım

Agent'ı başlatın:

```bash
python agent.py
```

### Örnek Komutlar:

```
👤 Siz: Bir TODO listesi oluştur

👤 Siz: Python öğrenme notlarımı kaydet

👤 Siz: Proje planı hazırla

👤 Siz: Bugünkü toplantı notlarını markdown formatında oluştur
```

## 📁 Proje Yapısı

```
backend/
├── agent.py              # Ana agent dosyası
├── tools.py              # Dosya oluşturma aracı
├── requirements.txt      # Python bağımlılıkları
├── .env.example         # Örnek environment dosyası
├── .env                 # API key'iniz (git'e eklenmez)
├── .gitignore          # Git ignore kuralları
└── output/             # Oluşturulan dosyalar (otomatik oluşur)
```

## 🔧 Nasıl Çalışır?

1. **Kullanıcı** doğal dilde bir istek yapar
2. **Groq LLM** isteği analiz eder
3. **Agent** uygun dosya adı ve içeriği belirler
4. **FileCreatorTool** dosyayı oluşturur
5. **Sonuç** kullanıcıya bildirilir

## 🛠️ Özelleştirme

### Farklı Model Kullanma:

`agent.py` dosyasında model değiştirilebilir:

```python
self.llm = ChatGroq(
    temperature=0.7,
    model_name="llama2-70b-4096",  # veya başka bir Groq modeli
    groq_api_key=self.api_key
)
```

### Yeni Araçlar Ekleme:

`tools.py` dosyasına yeni tool'lar ekleyebilirsiniz.

## 📝 Lisans

MIT License

## 🤝 Katkıda Bulunma

Pull request'ler memnuniyetle karşılanır!

## 📧 İletişim

Sorularınız için issue açabilirsiniz.

---

**Not:** Bu proje eğitim amaçlıdır. Production kullanımı için ek güvenlik önlemleri alınmalıdır.
