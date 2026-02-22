import { defineConfig } from "vitepress";

export default defineConfig({
  title: "LangChain & LangGraph",
  description:
    "Multi-Agent Sistemler için Kapsamlı Türkçe Eğitim Dokümantasyonu",
  lang: "tr-TR",

  themeConfig: {
    logo: "🤖",
    siteTitle: "LangGraph & Python Eğitimi ",

    nav: [
      { text: "Ana Sayfa", link: "/" },
      { text: "Başlangıç", link: "/introduction/what-is-langchain" },
      { text: "Proje Örneği", link: "/project/overview" },
      { text: "Python Öğreniyorum", link: "/python/index" },
    ],

    sidebar: {
      "/python/": [
        {
          text: "🐍 Python Eğitimi",
          items: [
            { text: "📋 Genel Bakış", link: "/python/index" },
            { text: "⚙️ Kurulum & Ortam", link: "/python/kurulum" },
          ],
        },
        {
          text: "🎯 LangGraph İçin Python",
          collapsed: false,
          items: [
            { text: "1. TypedDict — AgentState", link: "/python/typeddict" },
            { text: "2. Type Hints — Tip Bildirimleri", link: "/python/type-hints" },
            { text: "3. Fonksiyonlar & Decorator", link: "/python/functions-decorator" },
            { text: "4. Async / Await", link: "/python/async-await" },
            { text: "5. Class Yapısı", link: "/python/class-yapisi" },
            { text: "6. List & Dict Comprehension", link: "/python/comprehension" },
          ],
        },
        {
          text: "🧱 Temel Python",
          collapsed: false,
          items: [
            { text: "7. Değişkenler & Tipler", link: "/python/degiskenler" },
            { text: "8. Kütüphaneler & venv", link: "/python/kutuphaneler" },
          ],
        },
      ],
      "/": [
        {
          text: "🚀 Giriş",
          items: [
            {
              text: "LangChain Nedir?",
              link: "/introduction/what-is-langchain",
            },
            {
              text: "LangGraph Nedir?",
              link: "/introduction/what-is-langgraph",
            },
            { text: "Kurulum", link: "/introduction/installation" },
          ],
        },
        {
          text: "🧠 Temel Kavramlar",
          items: [
            { text: "State (Durum) Yönetimi", link: "/core/state" },
            { text: "LLM Bağlantısı", link: "/core/llm" },
            { text: "Node (Düğüm) Nedir?", link: "/core/nodes" },
            { text: "Graph Nedir?", link: "/core/graph" },
          ],
        },
        {
          text: "🤖 Multi-Agent Mimari",
          items: [
            { text: "Mimari Genel Bakış", link: "/multi-agent/overview" },
            { text: "Router Agent", link: "/multi-agent/router-agent" },
            { text: "Alt Ajanlar", link: "/multi-agent/sub-agents" },
            { text: "RAG Entegrasyonu", link: "/multi-agent/rag" },
          ],
        },
        {
          text: "🏗️ Proje: Asistan",
          items: [
            { text: "Projeye Genel Bakış", link: "/project/overview" },
            { text: "AgentState Tasarımı", link: "/project/agent-state" },
            { text: "Graph Kurulumu", link: "/project/graph-setup" },
            { text: "Yönlendirme Mantığı", link: "/project/routing" },
            { text: "Tüm Sistemi Çalıştırma", link: "/project/running" },
          ],
        },
        {
          text: "📚 İleri Seviye",
          items: [
            { text: "Conditional Edges", link: "/advanced/conditional-edges" },
            { text: "Memory & Checkpointing", link: "/advanced/memory" },
            { text: "Hata Yönetimi", link: "/advanced/error-handling" },
          ],
        },
        {
          text: "🎯 Pratik Örnekler",
          items: [
            { text: "Sınıf Geçme Ajanı", link: "/examples/sinif-gecme-agenti" },
            { text: "🚪 Daha Fazlası Var", link: "/examples/daha-fazlasi" },
          ],
        },
      ],
    },

    socialLinks: [
      { icon: "github", link: "https://github.com/langchain-ai/langgraph" },
    ],

    footer: {
      message: "LangChain & LangGraph Türkçe Eğitim Dokümantasyonu",
      copyright: "Qwen3 Multi-Agent Proje Örneği ile",
    },

    search: {
      provider: "local",
    },
  },
});
