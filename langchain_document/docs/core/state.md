# State (Durum) Yönetimi

**State**, LangGraph grafındaki tüm düğümlerin okuyup yazabildiği ortak veri yapısıdır. Her düğüm çalıştığında state'i alır, günceller ve bir sonraki düğüme geçer.

## TypedDict ile State Tanımlama

```python
# core/state.py
from typing import TypedDict

class AgentState(TypedDict):
    user_query: str      # Kullanıcının sorusu
    intent: str          # Belirlenen niyet (math, legal, greeting...)
    final_answer: str    # Son yanıt
```

Bu 3 alan projenizin tüm akışını taşıyan temel yapıdır.

## State Nasıl Çalışır?

Her düğüm şu imzaya sahiptir:

```python
def my_node(state: AgentState) -> dict:
    # state'i oku
    query = state["user_query"]

    # işlem yap...
    result = do_something(query)

    # sadece değiştirdiğin alanları döndür
    return {"final_answer": result}
```

LangGraph dönen dict'i mevcut state ile **birleştirir (merge)**. Tüm state'i döndürmen gerekmez.

## Projenizde State Akışı

```
Başlangıç State:
{
  "user_query": "İki sayının toplamı nasıl hesaplanır?",
  "intent": "",
  "final_answer": ""
}

         ↓  main_router_agent çalışır

State (main_agent sonrası):
{
  "user_query": "İki sayının toplamı nasıl hesaplanır?",
  "intent": "math",          ← güncellendi
  "final_answer": ""
}

         ↓  math_expert_node çalışır

Final State:
{
  "user_query": "İki sayının toplamı nasıl hesaplanır?",
  "intent": "math",
  "final_answer": "İki sayıyı + operatörü ile toplayabilirsin..."  ← güncellendi
}
```

## State'e Yeni Alan Eklemek

Sistemi genişletirken state'e alan ekleyebilirsin:

```python
from typing import TypedDict, List

class AgentState(TypedDict):
    user_query: str
    intent: str
    final_answer: str
    # Yeni alanlar:
    retrieved_docs: List[str]    # RAG'dan gelen belgeler
    confidence: float            # Güven skoru
    language: str                # Tespit edilen dil
```

::: warning Dikkat
State alanlarını `TypedDict` ile tanımlarken varsayılan değer veremezsin. Başlangıç state'i `app.invoke()` çağrısında belirtmelisin:

```python
app.invoke({
    "user_query": "soru",
    "intent": "",
    "final_answer": ""
})
```
:::

## Annotated ile Gelişmiş State

Birden fazla düğümün aynı alana veri eklemesini istiyorsan `Annotated` kullan:

```python
from typing import Annotated
from langgraph.graph.message import add_messages

class ChatState(TypedDict):
    messages: Annotated[list, add_messages]  # Her düğüm mesaj ekler, silmez
```

Bu pattern sohbet geçmişi tutmak için idealdir.

## Sonraki Adım

[LLM Bağlantısı →](/core/llm)
