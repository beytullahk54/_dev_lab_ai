# Conditional Edges (Koşullu Kenarlar)

Koşullu kenarlar, grafın state'e göre farklı yönlere dallanmasını sağlar. LangGraph'ın en güçlü özelliğidir.

## Temel Kullanım

```python
def routing_function(state: AgentState) -> str:
    # State'i oku ve hangi node'a gideceğini döndür
    return state["intent"]

workflow.add_conditional_edges(
    "source_node",       # Bu node'dan sonra karar ver
    routing_function,    # Bu fonksiyon karar verir
    {                    # Dönen değer → hedef node
        "A": "node_a",
        "B": "node_b",
        "C": END
    }
)
```

## Birden Fazla Conditional Edge

Bir node birden fazla koşullu kenar kaynağı olabilir, ama bir source node yalnızca **bir** conditional edge tanımına sahip olabilir:

```python
# ✓ Doğru — her source'dan bir kez
workflow.add_conditional_edges("router_1", fn_1, {...})
workflow.add_conditional_edges("router_2", fn_2, {...})

# ✗ Yanlış — aynı source'dan iki kez
workflow.add_conditional_edges("router", fn_1, {...})
workflow.add_conditional_edges("router", fn_2, {...})  # Hata!
```

## Lambda ile Kısa Yazım

```python
workflow.add_conditional_edges(
    "main_agent",
    lambda state: state["intent"],  # Route function yerine lambda
    {
        "math":  "math_expert",
        "legal": "legal_expert",
    }
)
```

## Döngüler (Cycles)

LangGraph'ta bir node kendisine geri dönebilir — bu iteratif işlemler için kullanılır:

```python
def should_retry(state: AgentState) -> str:
    if state["confidence"] < 0.7 and state["retry_count"] < 3:
        return "retry"
    return "done"

workflow.add_node("expert", expert_node)
workflow.add_node("quality_check", quality_check_node)

workflow.add_edge("expert", "quality_check")

workflow.add_conditional_edges(
    "quality_check",
    should_retry,
    {
        "retry": "expert",  # Geri dön!
        "done": END
    }
)
```

Bu döngü, kalite eşiğini geçene kadar veya 3 denemeden sonra durur.

## Paralel Dallanma (Fan-out)

Birden fazla node'u aynı anda çalıştır:

```python
from langgraph.graph import Send

def fan_out(state: AgentState):
    # Her belge için paralel işlem
    return [
        Send("process_doc", {"doc": doc, "query": state["user_query"]})
        for doc in state["documents"]
    ]

workflow.add_conditional_edges("fetch_docs", fan_out)
workflow.add_node("process_doc", process_single_doc)
workflow.add_edge("process_doc", "aggregate_results")
```

::: info
`Send` ile paralel dallanma, projenizde kullanılmıyor ama büyük ölçekli RAG sistemleri için çok değerlidir.
:::

## Mapping Olmadan Conditional Edge

Mapping belirtmezsen, fonksiyonun döndürdüğü string direkt node adı olarak kullanılır:

```python
def route(state):
    return "math_expert"  # Direkt node adı döner

# Mapping yok — string direkt node adı
workflow.add_conditional_edges("main_agent", route)
```

## Tip Güvenli Routing

```python
from typing import Literal

# Sadece geçerli değerleri kabul et
def route_decision(state: AgentState) -> Literal[
    "math_expert",
    "legal_expert",
    "greeting_expert"
]:
    mapping = {
        "math": "math_expert",
        "legal": "legal_expert",
        "greeting": "greeting_expert",
    }
    return mapping.get(state["intent"], "greeting_expert")

# Mapping'e gerek yok — fonksiyon direkt node adı döndürüyor
workflow.add_conditional_edges("main_agent", route_decision)
```

Bu yaklaşımda mapping dict'e gerek kalmaz çünkü fonksiyon zaten node adlarını döndürüyor.
