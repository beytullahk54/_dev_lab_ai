# Proje: Qwen3 Multi-Agent Asistan

Bu bölümde `run.py` dosyasındaki çok ajanlı sistemin tamamını adım adım inceliyoruz. Önceki bölümlerde öğrendiklerimizin bu projede nasıl bir araya geldiğini göreceğiz.

## Sistem Mimarisi

```
┌─────────────────────────────────────────────────────────────┐
│                    AgentState                               │
│   user_query (str) │ intent (str) │ final_answer (str)      │
└─────────────────────────────────────────────────────────────┘
                            │
                   ┌────────▼────────┐
                   │   main_agent    │
                   │ (Router Agent)  │
                   │ intent belirler │
                   └────────┬────────┘
                            │
         ┌──────────────────┼──────────────────────┐
         │          ┌───────┴──────┐               │
    ┌────▼────┐ ┌───▼────┐ ┌──────▼──────┐ ┌──────▼──────┐
    │  math   │ │ legal  │ │  it_legal   │ │  greeting   │
    │ expert  │ │ expert │ │ rag expert  │ │   expert    │
    └────┬────┘ └───┬────┘ └──────┬──────┘ └──────┬──────┘
         │          │             │                │
         │    ┌─────┘    ┌────────┘        ┌──────┘
         │    │          │   ┌─────────────▼──────┐
         │    │          │   │  vektor_rag_expert  │
         │    │          │   └─────────────┬───────┘
         │    │          │                 │
         │    │          │   ┌─────────────▼──────┐
         │    │          │   │  support_rag_expert │
         │    │          │   └─────────────┬───────┘
         │    │          │                 │
         └────┴──────────┴─────────────────┘
                                │
                              [END]
```

## Dosya Yapısı

```
agents/
├── run.py                     # Graf tanımı — tüm sistemi birleştirir
├── core/
│   ├── state.py               # AgentState — paylaşılan veri yapısı
│   ├── llm.py                 # LLM örnekleri
│   └── embedding_engine.py    # text_to_vector fonksiyonu
└── agents/
    ├── main_router_agent.py   # Niyet tespiti
    ├── math_expert_node.py    # Matematik uzmanı
    ├── legal_expert_node.py   # Hukuk uzmanı
    ├── it_legal_rag_node.py   # Bilişim hukuku (RAG)
    ├── greeting_node.py       # Selamlama
    ├── vector_rag_node.py     # Genel RAG
    └── support_rag_node.py    # Teknik destek (RAG)
```

## run.py — Tam Kod Analizi

```python
from langgraph.graph import StateGraph, END
from typing import Literal

# Core
from .core.state import AgentState
from .core.llm import llm, llm_qwen1
from .core.embedding_engine import text_to_vector

# Ajanlar
from .agents.it_legal_rag_node import it_legal_rag_node
from .agents.main_router_agent import main_router_agent
from .agents.math_expert_node import math_expert_node
from .agents.legal_expert_node import legal_expert_node
from .agents.greeting_node import greeting_node
from .agents.vector_rag_node import vektor_rag_node
from .agents.support_rag_node import support_rag_node
```

### Yönlendirme Fonksiyonu

```python
def route_decision(state: AgentState) -> Literal["math", "legal", "greeting", "vektor"]:
    return state["intent"]
```

Bu tek satır, grafın hangi yönde ilerleyeceğini belirler. `main_agent` state'e yazdığı `intent` değeri, burada okunur ve conditional edges tarafından kullanılır.

### Graf Tanımı

```python
workflow = StateGraph(AgentState)

# Node'ları kaydet
workflow.add_node("main_agent", main_router_agent)
workflow.add_node("it_legal_expert", it_legal_rag_node)
workflow.add_node("math_expert", math_expert_node)
workflow.add_node("legal_expert", legal_expert_node)
workflow.add_node("greeting_expert", greeting_node)
workflow.add_node("vektor_rag_expert", vektor_rag_node)
workflow.add_node("support_rag_expert", support_rag_node)

# Başlangıç
workflow.set_entry_point("main_agent")

# Koşullu yönlendirme
workflow.add_conditional_edges(
    "main_agent",
    route_decision,
    {
        "math":     "math_expert",
        "it_legal": "it_legal_expert",
        "legal":    "legal_expert",
        "greeting": "greeting_expert",
        "vektor":   "vektor_rag_expert",
        "support":  "support_rag_expert"
    }
)

# Tüm uzmanlar END'e gidiyor
workflow.add_edge("it_legal_expert", END)
workflow.add_edge("math_expert", END)
workflow.add_edge("legal_expert", END)
workflow.add_edge("greeting_expert", END)
workflow.add_edge("vektor_rag_expert", END)
workflow.add_edge("support_rag_expert", END)

app = workflow.compile()
```

### Chat Döngüsü

```python
def start_chat():
    while True:
        user_input = input("Siz: ")

        if user_input.lower() in ["exit", "quit"]:
            break

        result = app.invoke({
            "user_query": user_input,
            "intent": "",
            "final_answer": ""
        })

        print(f"[{result['intent'].upper()}] → {result['final_answer']}")
```

## Veri Akışı Örneği

```
Input:  {"user_query": "İnternet dolandırıcılığı suç mudur?", "intent": "", "final_answer": ""}

[main_agent]:
  → LLM "it_legal" döndürür
  → State: {"...", "intent": "it_legal", "final_answer": ""}

[it_legal_expert]:
  → Vektör araması yapılır
  → LLM yanıt üretir
  → State: {"...", "intent": "it_legal", "final_answer": "Evet, TCK 158..."}

[END]

Output: {"user_query": "...", "intent": "it_legal", "final_answer": "Evet, TCK 158..."}
```

## Sonraki Adım

[AgentState Tasarımı →](/project/agent-state)
