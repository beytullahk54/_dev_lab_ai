# AgentState Tasarımı

`AgentState`, projenin omurgasıdır. Doğru tasarlanmış bir state, sistemin ne kadar genişleyebileceğini belirler.

## Mevcut State

```python
# core/state.py
from typing import TypedDict

class AgentState(TypedDict):
    user_query: str      # Kullanıcının sorusu — hiç değişmez
    intent: str          # main_agent tarafından doldurulur
    final_answer: str    # Uzman ajanlar tarafından doldurulur
```

Bu minimal tasarım projenin ihtiyaçlarını karşılar. Ama sistemi büyütürken state'i de geliştirebilirsin.

## State Genişletme Örnekleri

### Kaynak Takibi Ekleme

RAG node'larının hangi belgeleri kullandığını kaydet:

```python
from typing import TypedDict, List, Optional

class AgentState(TypedDict):
    user_query: str
    intent: str
    final_answer: str
    # Yeni:
    source_docs: List[str]          # Kullanılan belge isimleri
    confidence: Optional[float]     # Yanıt güven skoru
```

### Sohbet Geçmişi

```python
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class ChatAgentState(TypedDict):
    user_query: str
    intent: str
    final_answer: str
    # Sohbet geçmişi — her node mesaj ekler, silmez
    messages: Annotated[List[BaseMessage], add_messages]
```

### Çok Dilli Destek

```python
class MultiLangState(TypedDict):
    user_query: str
    intent: str
    final_answer: str
    # Dil tespiti
    detected_language: str   # "tr", "en", "de"
    original_query: str      # Çeviri yapılmışsa orijinal metin
```

## State Tasarım Kuralları

### Ne Kadar Sade?

```python
# ✓ İyi — sadece ihtiyaç duyulan alanlar
class AgentState(TypedDict):
    user_query: str
    intent: str
    final_answer: str

# ✗ Kötü — kullanılmayan alanlar
class AgentState(TypedDict):
    user_query: str
    intent: str
    final_answer: str
    session_id: str          # Kullanılmıyor
    timestamp: str           # Kullanılmıyor
    retry_count: int         # Kullanılmıyor
    metadata: dict           # Çok geniş
```

### Immutable Alanlar

`user_query` alanı hiçbir node tarafından değiştirilmemeli. Tüm ajanlar orijinal soruya erişmeli:

```python
def math_expert_node(state: AgentState) -> dict:
    query = state["user_query"]  # Oku
    ...
    return {"final_answer": "..."}  # Sadece bunu döndür
    # user_query döndürme! Zaten doğru değer var.
```

### Optional Alanlar

Python `TypedDict`'te Optional kullanımı:

```python
from typing import Optional

class AgentState(TypedDict):
    user_query: str
    intent: str
    final_answer: str
    error_message: Optional[str]   # None veya string olabilir
```

## State Debug Etme

Graf çalışırken state'i gözlemlemek için:

```python
# Her adımı yazdır
for step in app.stream({"user_query": "test", "intent": "", "final_answer": ""}):
    node_name = list(step.keys())[0]
    node_state = step[node_name]
    print(f"\n[{node_name}]")
    for key, value in node_state.items():
        print(f"  {key}: {repr(value)[:80]}")
```

Örnek çıktı:

```
[main_agent]
  intent: 'math'

[math_expert]
  final_answer: 'İki sayının toplamını bulmak için + operatörü...'
```

## Sonraki Adım

[Graph Kurulumu →](/project/graph-setup)
