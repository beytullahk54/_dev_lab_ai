# Daha Fazlası Var

Bu dokümantasyonda multi-agent mimarinin temellerini öğrendik. Ama ekosistem çok daha geniş. Bu sayfada **henüz değinmediğimiz** ama bilmeni istediğimiz kavramlara kısaca bakıyoruz.

---

## 🔀 LangGraph — Keşfetmediğimiz Özellikler

### 1. Send API — Paralel Node Çalıştırma

Şimdiye kadar node'lar **sırayla** çalıştı. `Send` ile aynı anda **paralel** çalıştırabilirsin:

```python
from langgraph.types import Send

def dagit(state: SinifState):
    # 3 ders ajanını aynı anda başlat
    return [
        Send("matematik", state),
        Send("fizik", state),
        Send("kimya", state),
    ]

workflow.add_conditional_edges("__start__", dagit)
```

Üç ajan **eş zamanlı** çalışır — büyük sistemlerde ciddi hız kazancı sağlar.

---

### 2. Subgraph — Graf İçinde Graf

Karmaşık sistemleri alt graflara bölebilirsin:

```python
# Küçük bir alt graf
muhasebe_workflow = StateGraph(MuhasebeState)
muhasebe_workflow.add_node(...)
muhasebe_app = muhasebe_workflow.compile()

# Ana grafa entegre et
ana_workflow = StateGraph(AnaState)
ana_workflow.add_node("muhasebe", muhasebe_app)  # ← subgraph
```

Her ekip kendi alt grafını geliştirir, ana sistem bunları bir araya getirir.

---

### 3. Human-in-the-Loop — İnsan Onayı

Kritik bir adımdan önce sistemi durdur, insan onayı al:

```python
app = workflow.compile(
    interrupt_before=["odeme_node"]  # ödeme yapmadan önce dur
)

# Çalıştır — odeme_node'a gelince durur
app.invoke(state, config={"configurable": {"thread_id": "1"}})

# İnsan onayladı mı? → devam et
app.invoke(None, config={"configurable": {"thread_id": "1"}})
```

Kullanım alanı: Para transferi, e-posta gönderme, üretim ortamında deploy.

---

### 4. Streaming — Adım Adım Akış

Yanıtı kelime kelime al, kullanıcıya anlık göster:

```python
# Node bazlı stream
for event in app.stream(initial_state, stream_mode="updates"):
    node_adi = list(event.keys())[0]
    print(f"[{node_adi}] tamamlandı")

# Token bazlı stream (LLM yanıtını kelime kelime)
async for chunk in llm.astream([HumanMessage(content="Merhaba")]):
    print(chunk.content, end="", flush=True)
```

---

### 5. Persistence — Konuşma Geçmişi

Graf durumunu kaydet, konuşmayı kesip devam ettir:

```python
from langgraph.checkpoint.sqlite import SqliteSaver

# SQLite'a kaydet
with SqliteSaver.from_conn_string("chat_history.db") as checkpointer:
    app = workflow.compile(checkpointer=checkpointer)

    # thread_id ile konuşma kimliği ver
    config = {"configurable": {"thread_id": "kullanici_42"}}

    # İlk mesaj
    app.invoke({"messages": [HumanMessage("Merhaba")]}, config)

    # Saatler sonra — kaldığı yerden devam eder
    app.invoke({"messages": [HumanMessage("Devam edelim mi?")]}, config)
```

---

### 6. LangGraph Studio

LangGraph'ın görsel IDE'si — grafı çalıştır, debug et, state'i izle:

```bash
pip install langgraph-cli
langgraph dev
```

Tarayıcıda gerçek zamanlı olarak:
- Graf görselini izle
- Her node'un state'ini gör
- Adım adım ilerle
- Hataları yakala

> LangGraph Studio için `langgraph.json` config dosyası gerekir.

---

## 🔭 LangSmith — Gözlemlenebilirlik

LangSmith, LangChain uygulamalarını **izlemek, debug etmek ve değerlendirmek** için Anthropic'in resmi platformudur.

### Kurulum

```bash
pip install langsmith
```

```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "ls__..."
os.environ["LANGCHAIN_PROJECT"] = "sinif-gecme-agenti"
```

Bu 3 satırı ekledikten sonra **kod değişikliği yapmadan** her çağrı otomatik loglanır.

---

### 1. Tracing — İz Sürme

Her LLM çağrısını, her node'u, her token'ı kayıt altına alır:

```
Run: sinif_gecme_agenti
├── matematik_agent       ✅  42ms
├── fizik_agent           ✅  38ms
├── kimya_agent           ✅  41ms
├── karar_agent           ✅  12ms
└── kaldi_node            ✅   5ms

Toplam süre: 138ms  |  Toplam token: 847  |  Maliyet: $0.0012
```

LangSmith'in dashboard'unda her şeyi görebilirsin.

---

### 2. Evaluator — Otomatik Değerlendirme

LLM yanıtlarını otomatik puanla:

```python
from langsmith.evaluation import evaluate, LangChainStringEvaluator

# Test verisi
dataset = [
    {"input": "2+2", "expected": "4"},
    {"input": "Python nedir?", "expected": "programlama dili"},
]

# Değerlendir
results = evaluate(
    app.invoke,
    data=dataset,
    evaluators=[LangChainStringEvaluator("qa")],
    experiment_prefix="v1_test"
)
```

---

### 3. Prompt Hub

Prompt'larını LangSmith'te versiyonla ve takım arkadaşlarınla paylaş:

```python
from langchain import hub

# Prompt'u çek (versiyonlu)
prompt = hub.pull("kullanici_adi/matematik-uzmani:v2")

# Kullan
chain = prompt | llm
```

Prompt değişikliği yaparken kodu değiştirmene gerek kalmaz — hub'dan güncelle.

---

### 4. Playground

LangSmith arayüzünden herhangi bir geçmiş run'ı seç → "Playground'da Aç" → farklı model/prompt dene → karşılaştır.

---

## 📌 Özet Tablo

| Özellik | Nerede? | Ne İşe Yarar? |
|---------|---------|---------------|
| `Send` API | LangGraph | Paralel node çalıştırma |
| Subgraph | LangGraph | Graf içinde alt graf |
| Human-in-the-Loop | LangGraph | İnsan onayı ile dur/devam |
| Streaming | LangGraph | Anlık token akışı |
| Persistence | LangGraph | Konuşma geçmişi, SQLite/Redis |
| LangGraph Studio | LangGraph CLI | Görsel debug IDE |
| Tracing | LangSmith | Her çağrıyı izle ve logla |
| Evaluator | LangSmith | Otomatik yanıt kalitesi ölçümü |
| Prompt Hub | LangSmith | Versiyonlu prompt yönetimi |
| Playground | LangSmith | Model/prompt karşılaştırma |

---

::: info Nereden Devam Edersin?
- [LangGraph Dokümantasyonu](https://langchain-ai.github.io/langgraph/)
- [LangSmith Dokümantasyonu](https://docs.smith.langchain.com/)
- [LangGraph Studio](https://studio.langchain.com/)
- [LangChain Cookbook](https://github.com/langchain-ai/langchain/tree/master/cookbook)
:::
