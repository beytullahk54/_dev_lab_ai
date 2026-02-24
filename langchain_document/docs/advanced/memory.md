# Memory & Checkpointing

Varsayılan olarak LangGraph her `invoke` çağrısında sıfırdan başlar — geçmiş konuşma hatırlanmaz. **Checkpointing** ile konuşma geçmişini saklayabilirsin.

## Checkpointer Nedir?

Checkpointer, her graf adımından sonra state'i kaydeder. Aynı `thread_id` ile tekrar çağırıldığında kaldığı yerden devam eder.

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)
```

## Thread ID ile Konuşma Yönetimi

```python
# Her kullanıcı/oturum için benzersiz thread_id
config = {"configurable": {"thread_id": "user_123_session_1"}}

# İlk mesaj
result1 = app.invoke(
    {"user_query": "Merhaba!", "intent": "", "final_answer": ""},
    config=config
)

# İkinci mesaj — aynı thread_id, geçmişi hatırlar
result2 = app.invoke(
    {"user_query": "Az önce ne dedim?", "intent": "", "final_answer": ""},
    config=config
)
```

## Konuşma Geçmişi için State Tasarımı

Checkpointing sadece state'i kaydeder. Konuşma geçmişini state'e eklemelisin:

```python
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class ConversationalState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    intent: str
    final_answer: str
```

`add_messages` fonksiyonu, yeni mesajları listeye ekler (üzerine yazmaz).

## Tam Konuşmalı Ajan Örneği

```python
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

def conversational_expert(state: ConversationalState) -> dict:
    # Tüm geçmiş mesajlar dahil
    messages = [
        SystemMessage(content="Sen yardımsever bir asistansın.")
    ] + state["messages"]  # Geçmiş + yeni mesaj

    response = llm.invoke(messages)
    return {"messages": [AIMessage(content=response.content)]}

# Kullanım
config = {"configurable": {"thread_id": "conv_1"}}

# Tur 1
app.invoke({"messages": [HumanMessage("Adın ne?")]}, config)

# Tur 2 — ilk turu hatırlar
app.invoke({"messages": [HumanMessage("Bana tekrar söyle")]}, config)
```

## SQLite ile Kalıcı Hafıza

`MemorySaver` geçicidir (uygulama kapanınca silinir). SQLite ile kalıcı hale getir:

```bash
pip install langgraph-checkpoint-sqlite
```

```python
from langgraph.checkpoint.sqlite import SqliteSaver

with SqliteSaver.from_conn_string("./memory.db") as checkpointer:
    app = workflow.compile(checkpointer=checkpointer)
    # ... uygulamayı çalıştır
```

## Geçmiş Durumu Okuma

```python
config = {"configurable": {"thread_id": "user_123"}}

# Mevcut state'i oku
current_state = app.get_state(config)
print(current_state.values)

# Tüm geçmişi oku
for state in app.get_state_history(config):
    print(state.step, state.values)
```

::: tip Ne Zaman Checkpointing Kullanmalı?
- **Kullanmalısın:** Çok turlu sohbet, görev takibi, uzun vadeli oturumlar
- **Gerekmez:** Tek seferlik soru-cevap (projenizin mevcut hali)
:::
