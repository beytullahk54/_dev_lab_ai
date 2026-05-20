# VitePress Dokümantasyonu

Bu klasör, [VitePress](https://vitepress.dev/) ile oluşturulmuş statik dokümantasyon sitesini içerir.

## Geliştirme

### Bağımlılıkları Kur

```bash
cd docs
npm install
```

### Geliştirme Sunucusu

```bash
npm run dev
```

### Derleme

```bash
npm run build
```

### Önizleme

```bash
npm run preview
```

## Yapı

```
docs/
├── .vitepress/
│   └── config.js          # VitePress konfigürasyonu
├── guide/                 # Ana dokümantasyon
│   ├── index.md           # Proje özeti
│   ├── installation.md    # Kurulum
│   ├── architecture.md    # Sistem mimarisi
│   ├── data-flow.md       # Veri akışı
│   ├── gestures.md        # Gesture algılama
│   ├── landmarks.md       # MediaPipe landmarks
│   ├── configuration.md   # Ayarlar
│   └── thresholds.md      # Threshold değerleri
├── api/                   # API referansı
│   ├── index.md           # Endpoints
│   └── functions.md       # Fonksiyonlar
├── index.md               # Ana sayfa (hero)
└── README.md              # Bu dosya
```

## Özellikler

- 📝 Markdown tabanlı
- 🏷️ Frontmatter desteği
- 🎨 Dark theme (varsayılan)
- 🔍 Arama (build sonrası)
- 📱 Responsive
- 🚀 Hızlı (Vite tabanlı)

## Yayınlama

### GitHub Pages

```bash
npm run build
# dist/ klasörünü gh-pages branch'e push et
```

### Netlify

```bash
npm run build
# dist/ klasörünü deploy et
```

## İçerik Yazma

### Yeni Sayfa Ekleme

1. `docs/guide/` veya `docs/api/` içine `.md` dosyası oluştur
2. Frontmatter ekle:
   ```md
   ---
   title: Sayfa Başlığı
   ---
   ```
3. `.vitepress/config.js` içinde sidebar'a ekle

### Markdown Özellikleri

```md
# Başlık

> Bilgi kutusu

::: tip İpucu
İpucu kutusu
:::

::: warning Uyarı
Uyarı kutusu
:::

```python
# Kod bloğu
print("Merhaba")
```

| Tablo | Kolon |
|-------|-------|
| Veri  | Veri  |
```

## Konfigürasyon

### Navigasyon

```js
// .vitepress/config.js
themeConfig: {
  nav: [
    { text: 'Ana Sayfa', link: '/' },
    { text: 'Dokümantasyon', link: '/guide/' }
  ]
}
```

### Sidebar

```js
sidebar: {
  '/guide/': [
    {
      text: 'Başlangıç',
      items: [
        { text: 'Proje Özeti', link: '/guide/' }
      ]
    }
  ]
}
```
