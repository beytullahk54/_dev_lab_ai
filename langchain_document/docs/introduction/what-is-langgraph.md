# LangGraph Nedir?

**LangGraph**, LangChain üzerine inşa edilmiş, **graf tabanlı** çok adımlı ajan sistemleri geliştirmeye yarayan bir kütüphanedir.

## Temel Fikir

LangGraph'ta uygulamanı bir **yönlü graf** (directed graph) olarak modellersin:

- **Node (Düğüm):** Bir iş yapan fonksiyon (LLM çağrısı, araç kullanımı, veri işleme)
- **Edge (Kenar):** Düğümler arası bağlantı
- **State (Durum):** Grafın tamamında paylaşılan veri yapısı

```
                    ┌─────────────────────────────┐
                    │        AgentState           │
                    │  user_query, intent,        │
                    │  final_answer               │
                    └─────────────────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │    main_agent         │  ← Router
                    │  (intent belirler)    │
                    └───────────┬───────────┘
                                │
              ┌─────────────────┼──────────────────┐
              │                 │                  │
    ┌─────────▼──────┐ ┌───────▼────────┐ ┌──────▼────────┐
    │  math_expert   │ │ legal_expert   │ │greeting_expert│
    └─────────┬──────┘ └───────┬────────┘ └──────┬────────┘
              │                │                  │
              └────────────────┼──────────────────┘
                               │
                             [END]
```

## StateGraph

LangGraph'ın kalbi `StateGraph`'tır. Durumu otomatik olarak yönetir ve düğümler arasında taşır:

```python
from langgraph.graph import StateGraph, END

workflow = StateGraph(AgentState)

# Düğüm ekle
workflow.add_node("main_agent", main_router_agent)
workflow.add_node("math_expert", math_expert_node)

# Başlangıç noktası
workflow.set_entry_point("main_agent")

# Koşullu kenar
workflow.add_conditional_edges(
    "main_agent",
    route_decision,          # Hangi düğüme gideceğini döndüren fonksiyon
    {
        "math": "math_expert",
        "legal": "legal_expert",
    }
)

# Bitiş kenarı
workflow.add_edge("math_expert", END)

# Graf'ı derle
app = workflow.compile()
```

## Çalıştırma

```python
result = app.invoke({
    "user_query": "5 * 8 kaçtır?",
    "intent": "",
    "final_answer": ""
})

print(result["intent"])       # "math"
print(result["final_answer"]) # "40"
```

## Önemli Kavramlar

### `invoke` vs `stream`

```python
# Tüm sonucu bekle
result = app.invoke(initial_state)

# Adım adım akış (streaming)
for chunk in app.stream(initial_state):
    print(chunk)
```

### Döngüler (Cycles)

LangGraph, döngüleri destekler — bir ajan kendi kendini tekrar çağırabilir:

```python
# Bir düğümden aynı düğüme kenar eklenebilir
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "agent",  # Geri döner
        "end": END
    }
)
```

::: info
Projenizde döngü yok — her ajan bir kez çalışıp END'e gidiyor. Bu **basit yönlendirme** mimarisidir.
:::

## Sonraki Adım

[Kurulum →](/introduction/installation)
