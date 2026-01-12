# Google AI (Gemini) Node.js Örnek Kurulum

Bu proje, Node.js ile Google AI (Gemini) API'sine basit bir istek atmak için hazır bir örnek içerir.

## Kurulum

1. Bağımlılıklar yüklü değilse:

```bash
npm install
```

2. Ortam değişkeninizi ayarlayın. Kök dizinde `.env` dosyası oluşturun ve Google AI Studio API anahtarınızı ekleyin:

```bash
# .env
GOOGLE_API_KEY=YOUR_GOOGLE_AI_STUDIO_API_KEY
```

> Not: `.env.example` oluşturulamıyorsa, yukarıdaki örneği kullanarak `.env` dosyasını manuel ekleyebilirsiniz.

## Çalıştırma

```bash
npm start
```

Başarılı çalıştırmada konsolda model yanıtını görürsünüz.

## Kaynaklar
- Google AI Studio: `https://aistudio.google.com`
- Paket (yeni SDK): `@google/genai`
