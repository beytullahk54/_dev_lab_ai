# Multi-Agent Mimari

Tek bir LLM çağrısıyla çözülemeyen karmaşık problemler için **birden fazla uzman ajanın** bir arada çalıştığı sistemler kurulur. LangGraph bu yapıyı doğal olarak destekler.

## Neden Çok Ajan?

| Tek Ajan | Çok Ajan |
|----------|----------|
| Her şeyi tek prompt'a sığdırmak zor | Her uzman kendi alanında optimize |
| Uzun promptlar hallüsinasyona yol açar | Kısa, odaklı sistem promptları |
| Ölçeklenme zorlu | Yeni uzman eklemek kolay |
| Hata tespiti güç | Her ajanı bağımsız test edebilirsin |

## Temel Mimari Deseni

Projenizin uyguladığı **Hub-and-Spoke** (merkez-uç) deseni:

```
Kullanıcı
    │
    ▼
┌──────────────┐
│  Router Agent │  ← Niyet tespiti yapar
│  (Hub/Merkez) │     ve yönlendirir
└──────┬───────┘
       │
   ┌───┴───────────────────────────────┐
   │           intent değerine göre    │
   │                                   │
   ▼           ▼           ▼           ▼
[math]     [legal]   [it_legal]   [greeting]
   │           │           │           │
   └───────────┴───────────┴───────────┘
                      │
                    [END]
                      │
                 Kullanıcıya yanıt
```

Bu desende:
- **Router** niyet analizi yapar, asla yanıt üretmez
- **Uzmanlar** sadece kendi alanlarına odaklanır
- Her uzman **paralel geliştirilebilir**

## LangGraph'ta Uygulama

### Adım 1: Ortak State

Tüm ajanlar bu state'i paylaşır:

```python
from typing import TypedDict

class AgentState(TypedDict):
    user_query: str     # Değişmez — hiçbir ajan bunu güncellemez
    intent: str         # Router tarafından doldurulur
    final_answer: str   # Uzman tarafından doldurulur
```

### Adım 2: Router Agent

```python
from langchain_core.messages import HumanMessage

def main_router_agent(state: AgentState) -> dict:
    user_query = state["user_query"]

    # LLM'den sadece bir etiket iste
    prompt = f"""Aşağıdaki soruyu sınıflandır. Yalnızca şu etiketlerden birini yaz:
math | legal | it_legal | greeting | vektor | support

Soru: {user_query}
Etiket:"""

    response = llm.invoke([HumanMessage(content=prompt)])
    intent = response.content.strip().lower()

    return {"intent": intent}
```

### Adım 3: Uzman Ajanlar

Her uzman kendi sistem promptuyla çalışır:

```python
def math_expert_node(state: AgentState) -> dict:
    messages = [
        SystemMessage(content="Sen deneyimli bir matematik öğretmenisin. "
                               "Adım adım çöz, her adımı açıkla."),
        HumanMessage(content=state["user_query"])
    ]
    response = llm.invoke(messages)
    return {"final_answer": response.content}

def legal_expert_node(state: AgentState) -> dict:
    messages = [
        SystemMessage(content="Sen Türk hukuku konusunda uzman bir avukatsın. "
                               "Yasal dayanakları belirt, tarafsız ol."),
        HumanMessage(content=state["user_query"])
    ]
    response = llm.invoke(messages)
    return {"final_answer": response.content}
```

### Adım 4: Yönlendirme Fonksiyonu

```python
from typing import Literal

def route_decision(state: AgentState) -> Literal[
    "math", "legal", "it_legal", "greeting", "vektor", "support"
]:
    return state["intent"]
```

Bu fonksiyon state'i okur ve bir string döndürür. LangGraph bu string'i mapping'deki node ismiyle eşleştirir.

### Adım 5: Graf Kurulumu

```python
from langgraph.graph import StateGraph, END

workflow = StateGraph(AgentState)

# Tüm node'ları kaydet
workflow.add_node("main_agent", main_router_agent)
workflow.add_node("math_expert", math_expert_node)
workflow.add_node("legal_expert", legal_expert_node)
workflow.add_node("it_legal_expert", it_legal_rag_node)
workflow.add_node("greeting_expert", greeting_node)
workflow.add_node("vektor_rag_expert", vektor_rag_node)
workflow.add_node("support_rag_expert", support_rag_node)

# Akış
workflow.set_entry_point("main_agent")

workflow.add_conditional_edges(
    "main_agent",
    route_decision,
    {
        "math":     "math_expert",
        "legal":    "legal_expert",
        "it_legal": "it_legal_expert",
        "greeting": "greeting_expert",
        "vektor":   "vektor_rag_expert",
        "support":  "support_rag_expert",
    }
)

# Her uzman END'e bağlanır
for node in ["math_expert", "legal_expert", "it_legal_expert",
             "greeting_expert", "vektor_rag_expert", "support_rag_expert"]:
    workflow.add_edge(node, END)

app = workflow.compile()
```

## Sistemi Çalıştırma

```python
result = app.invoke({
    "user_query": "Kira artışı ne kadar olabilir?",
    "intent": "",
    "final_answer": ""
})

# Hangi uzman devreye girdi?
print(result["intent"])       # "legal"
print(result["final_answer"]) # Hukuki açıklama...
```

## Sonraki Adım

[Router Agent →](/multi-agent/router-agent)
