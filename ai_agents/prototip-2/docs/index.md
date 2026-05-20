---
layout: home

hero:
  name: "AI Agent Sistemi"
  text: "LangGraph + Groq + SQLite"
  tagline: Doğal dil ile kullanıcı kaydı açan ve sorgulayan çok ajanlı sistem prototipi
  actions:
    - theme: brand
      text: Mimari'ye Git
      link: /architecture
    - theme: alt
      text: Kurulum
      link: /setup

features:
  - icon: 🧠
    title: LangGraph Orkestrasyon
    details: Her agent izole bir node'dur. Router LLM mesajı analiz eder, doğru node'a yönlendirir. Yeni agent eklemek sadece yeni node + edge eklemektir.
  - icon: ⚡
    title: Groq ile Hızlı LLM
    details: llama-3.3-70b-versatile modeli Groq altyapısında sub-second gecikme ile çalışır. Router ve kayıt agent'ı için kullanılır.
  - icon: 🗄️
    title: SQLite Veritabanı
    details: Sıfır konfigürasyon, tek dosya veritabanı. Kullanıcı kayıtları app.db dosyasında saklanır. Prototip için idealdir.
  - icon: 🔌
    title: WebSocket Chat
    details: FastAPI WebSocket endpoint'i üzerinden gerçek zamanlı mesajlaşma. Frontend sade HTML/JS ile çalışır, build adımı gerekmez.
---
