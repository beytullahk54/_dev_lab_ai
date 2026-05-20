import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'AI Agent Sistemi',
  description: 'LangGraph + Groq + SQLite + FastAPI tabanlı çok ajanlı sistem dokümantasyonu',
  lang: 'tr-TR',

  themeConfig: {
    logo: '🤖',
    siteTitle: 'AI Agent Docs',

    nav: [
      { text: 'Ana Sayfa', link: '/' },
      { text: 'Mimari', link: '/architecture' },
      { text: 'Agent\'lar', link: '/agents' },
      { text: 'API', link: '/api' },
    ],

    sidebar: [
      {
        text: 'Başlangıç',
        items: [
          { text: 'Giriş', link: '/' },
          { text: 'Kurulum', link: '/setup' },
        ]
      },
      {
        text: 'Mimari',
        items: [
          { text: 'Genel Bakış', link: '/architecture' },
          { text: 'Sequence Diagram\'lar', link: '/sequence-diagrams' },
          { text: 'LangGraph Grafı', link: '/langgraph' },
        ]
      },
      {
        text: 'Bileşenler',
        items: [
          { text: 'Agent\'lar', link: '/agents' },
          { text: 'Veritabanı', link: '/database' },
          { text: 'API Endpointleri', link: '/api' },
        ]
      },
      {
        text: 'Geliştirme',
        items: [
          { text: 'Yeni Agent Ekleme', link: '/extending' },
        ]
      }
    ],

    socialLinks: [],

    footer: {
      message: 'Prototip-2 — LangGraph + Groq + SQLite',
    },

    search: {
      provider: 'local'
    }
  },

  markdown: {
    theme: {
      light: 'github-light',
      dark: 'github-dark'
    }
  }
})
