export default {
  title: 'El Hareketi Müzik Kontrolü',
  description: 'Kamera ile el hareketlerini algılayarak müzik kontrolü',
  base: '/',
  
  themeConfig: {
    nav: [
      { text: 'Ana Sayfa', link: '/' },
      { text: 'Dokümantasyon', link: '/guide/' },
      { text: 'API', link: '/api/' }
    ],
    
    sidebar: {
      '/guide/': [
        {
          text: 'Başlangıç',
          items: [
            { text: 'Proje Özeti', link: '/guide/' },
            { text: 'Kurulum', link: '/guide/installation' }
          ]
        },
        {
          text: 'Mimari',
          items: [
            { text: 'Sistem Mimarisi', link: '/guide/architecture' },
            { text: 'Veri Akışı', link: '/guide/data-flow' }
          ]
        },
        {
          text: 'El Hareketleri',
          items: [
            { text: 'Gesture Algılama', link: '/guide/gestures' },
            { text: 'MediaPipe Landmarks', link: '/guide/landmarks' }
          ]
        },
        {
          text: 'Konfigürasyon',
          items: [
            { text: 'Ayarlar', link: '/guide/configuration' },
            { text: 'Threshold Değerleri', link: '/guide/thresholds' }
          ]
        },
        {
          text: 'İleri Düzey',
          items: [
            { text: 'YOLO, Detectron2, Graf Analizi', link: '/guide/advanced-vision' }
          ]
        }
      ],
      '/api/': [
        {
          text: 'API Referansı',
          items: [
            { text: 'Endpoints', link: '/api/' },
            { text: 'Fonksiyonlar', link: '/api/functions' }
          ]
        }
      ]
    },
    
    socialLinks: [
      { icon: 'github', link: 'https://github.com/yourusername/camera_goruntu_isleme' }
    ],
    
    footer: {
      message: 'MIT Lisansı altında yayınlanmıştır.',
      copyright: 'Copyright © 2024'
    }
  }
}
