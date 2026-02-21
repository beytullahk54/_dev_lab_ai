# Graph (Graf) Nedir?

**Graph**, LangGraph'ta node'ları ve aralarındaki bağlantıları (edge) bir araya getiren yapıdır. `StateGraph` sınıfı ile tanımlanır.

## Graf Oluşturma Adımları

```python
from langgraph.graph import StateGraph, END
from .core.state import AgentState

# 1. Graf oluştur
workflow = StateGraph(AgentState)

# 2. Node'ları ekle
workflow.add_node("main_agent", main_router_agent)
workflow.add_node("math_expert", math_expert_node)
workflow.add_node("legal_expert", legal_expert_node)
workflow.add_node("greeting_expert", greeting_node)

# 3. Başlangıç noktasını belirle
workflow.set_entry_point("main_agent")

# 4. Kenarları ekle
workflow.add_conditional_edges(
    "main_agent",
    route_decision,
    {
        "math": "math_expert",
        "legal": "legal_expert",
        "greeting": "greeting_expert",
    }
)

workflow.add_edge("math_expert", END)
workflow.add_edge("legal_expert", END)
workflow.add_edge("greeting_expert", END)

# 5. Derle
app = workflow.compile()
```

## Edge Türleri

### 1. Düz Kenar (Normal Edge)

A düğümünden B düğümüne her zaman gider:

```python
workflow.add_edge("math_expert", END)
```

### 2. Koşullu Kenar (Conditional Edge)

Bir fonksiyonun döndürdüğü değere göre farklı düğümlere gider:

```python
def route_decision(state: AgentState) -> str:
    return state["intent"]  # "math", "legal", "greeting"...

workflow.add_conditional_edges(
    "main_agent",          # Hangi node'dan sonra karar verilecek
    route_decision,        # Karar fonksiyonu
    {                      # Mapping: dönen değer → hedef node
        "math": "math_expert",
        "legal": "legal_expert",
        "greeting": "greeting_expert",
    }
)
```

### 3. END

Grafın bitiş noktası. `END` sabitiyle gösterilir:

```python
from langgraph.graph import END

workflow.add_edge("greeting_expert", END)
```

## Projenizin Graf Yapısı

```python
# run.py — Tam graf tanımı
from langgraph.graph import StateGraph, END
from typing import Literal

def route_decision(state: AgentState) -> Literal["math", "legal", "greeting", "vektor"]:
    return state["intent"]

workflow = StateGraph(AgentState)

# Node'lar
workflow.add_node("main_agent", main_router_agent)
workflow.add_node("it_legal_expert", it_legal_rag_node)
workflow.add_node("math_expert", math_expert_node)
workflow.add_node("legal_expert", legal_expert_node)
workflow.add_node("greeting_expert", greeting_node)
workflow.add_node("vektor_rag_expert", vektor_rag_node)
workflow.add_node("support_rag_expert", support_rag_node)

# Giriş
workflow.set_entry_point("main_agent")

# Yönlendirme
workflow.add_conditional_edges(
    "main_agent",
    route_decision,
    {
        "math": "math_expert",
        "it_legal": "it_legal_expert",
        "legal": "legal_expert",
        "greeting": "greeting_expert",
        "vektor": "vektor_rag_expert",
        "support": "support_rag_expert"
    }
)

# Bitiş kenarları
workflow.add_edge("it_legal_expert", END)
workflow.add_edge("math_expert", END)
workflow.add_edge("legal_expert", END)
workflow.add_edge("greeting_expert", END)
workflow.add_edge("vektor_rag_expert", END)
workflow.add_edge("support_rag_expert", END)

app = workflow.compile()
```

## Graf Görselleştirme

LangGraph, grafı Mermaid diyagramı olarak export edebilir:

```python
# Graf'ın Mermaid görselini al
print(app.get_graph().draw_mermaid())
```

Çıktı:

```
%%{init: {'flowchart': {'curve': 'linear'}}}%%
flowchart TD
    __start__ --> main_agent
    main_agent -. math .-> math_expert
    main_agent -. legal .-> legal_expert
    main_agent -. greeting .-> greeting_expert
    math_expert --> __end__
    legal_expert --> __end__
    greeting_expert --> __end__
```

## Compile ile Son Adım

```python
app = workflow.compile()
```

`compile()` grafı çalıştırılabilir hale getirir. Bu adımdan sonra `app.invoke()` ile çalıştırabilirsin.

Opsiyonel: **checkpointer** ekleyerek konuşma geçmişini kaydedebilirsin:

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)
```

## Sonraki Adım

[Multi-Agent Mimari →](/multi-agent/overview)
