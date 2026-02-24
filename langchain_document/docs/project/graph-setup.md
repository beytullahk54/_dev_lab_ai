# Graph Kurulumu

`run.py` dosyası, projenin tüm parçalarını birleştiren merkezi yerdir. Bu sayfada graf kurulumunu detaylı inceliyoruz.

## Import Organizasyonu

```python
# run.py

# 1. LangGraph core
from langgraph.graph import StateGraph, END
from typing import Literal

# 2. Shared modules (core)
from .core.state import AgentState
from .core.llm import llm, llm_qwen1
from .core.embedding_engine import text_to_vector

# 3. Agent node'ları
from .agents.main_router_agent import main_router_agent
from .agents.math_expert_node import math_expert_node
from .agents.legal_expert_node import legal_expert_node
from .agents.it_legal_rag_node import it_legal_rag_node
from .agents.greeting_node import greeting_node
from .agents.vector_rag_node import vektor_rag_node
from .agents.support_rag_node import support_rag_node
```

::: tip Import Sırası
Core modüller önce, agent node'ları sonra import edilir. Bu, dairesel import (circular import) sorunlarını önler.
:::

## `set_entry_point` vs `add_edge(__start__)`

İki yöntem aynı işi yapar:

```python
# Yöntem 1 — Tercih edilen
workflow.set_entry_point("main_agent")

# Yöntem 2 — Alternatif
from langgraph.graph import START
workflow.add_edge(START, "main_agent")
```

## Conditional Edges Detayı

```python
workflow.add_conditional_edges(
    "main_agent",      # Source node
    route_decision,    # Routing function
    {                  # Mapping: function output → target node
        "math":     "math_expert",
        "it_legal": "it_legal_expert",
        "legal":    "legal_expert",
        "greeting": "greeting_expert",
        "vektor":   "vektor_rag_expert",
        "support":  "support_rag_expert"
    }
)
```

**Ne olur ki `route_decision` mapping'de olmayan bir değer döndürürse?**

LangGraph bir `ValueError` fırlatır. Bu yüzden router'da fallback önemli:

```python
def route_decision(state: AgentState) -> str:
    intent = state["intent"]
    valid = {"math", "it_legal", "legal", "greeting", "vektor", "support"}

    if intent not in valid:
        return "vektor"  # Bilinmeyen → genel RAG

    return intent
```

## Compile Seçenekleri

```python
# Basit compile
app = workflow.compile()

# Memory ile compile (konuşma geçmişi)
from langgraph.checkpoint.memory import MemorySaver
app = workflow.compile(checkpointer=MemorySaver())

# Interrupt ile compile (insan onayı)
app = workflow.compile(interrupt_before=["legal_expert"])
# "legal_expert" çalışmadan önce dur ve insan onayı bekle
```

## Modül Olarak Kullanma

`run.py`, hem doğrudan çalıştırılabilir hem de başka modüllerden import edilebilir:

```python
# Başka bir dosyadan
from agents.run import app

result = app.invoke({
    "user_query": "Merhaba!",
    "intent": "",
    "final_answer": ""
})
```

## FastAPI ile Entegrasyon

```python
# api.py
from fastapi import FastAPI
from pydantic import BaseModel
from agents.run import app as langgraph_app

api = FastAPI()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    intent: str
    answer: str

@api.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    result = langgraph_app.invoke({
        "user_query": request.message,
        "intent": "",
        "final_answer": ""
    })
    return ChatResponse(
        intent=result["intent"],
        answer=result["final_answer"]
    )
```

## Sonraki Adım

[Yönlendirme Mantığı →](/project/routing)
