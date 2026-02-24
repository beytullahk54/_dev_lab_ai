# 🐍 Python Eğitimi — LangGraph İçin

> **Sen kimsin?** Laravel & Vue.js geliştiricisi, LangGraph ile AI agent yazmak istiyor.  
> **Bu eğitim ne öğretir?** Sadece LangGraph'ta _gerçekten_ kullanacağın Python konularını.

---

## 🗺️ Öğrenme Yolu

LangGraph kodu yazmak için gereken Python konularını sıraya dizdik. Her konu bir öncekinin üzerine inşa eder.

```
TypedDict → Type Hints → Decorator → Async/Await → Class → List/Dict Comprehension
    ↓            ↓           ↓            ↓           ↓           ↓
  State       Tip        @node        LLM call    Agent      Veri Filtre
 Tanımı     Güvenliği   Tanımı       async        Sınıfı      & Dönüşüm
```

---

## 📚 Dersler

| #   | Konu                                              | Laravel Karşılığı       | LangGraph'taki Rolü    |
| --- | ------------------------------------------------- | ----------------------- | ---------------------- |
| 1   | [TypedDict](./typeddict)                          | PHP Typed Array         | `AgentState` tanımı    |
| 2   | [Type Hints](./type-hints)                        | PHP Type Declarations   | Fonksiyon sözleşmeleri |
| 3   | [Fonksiyonlar & Decorator](./functions-decorator) | Laravel Middleware      | `@node` tanımlama      |
| 4   | [Async / Await](./async-await)                    | Laravel Queue / Promise | LLM async çağrıları    |
| 5   | [Class Yapısı](./class-yapisi)                    | Laravel Eloquent Model  | Agent sınıfları        |
| 6   | [List & Dict Comprehension](./comprehension)      | Laravel Collection      | Mesaj listesi filtrele |
| 7   | [Değişkenler & Tipler](./degiskenler)             | PHP değişkenleri        | Genel Python temeli    |
| 8   | [Kütüphaneler & venv](./kutuphaneler)             | Composer + vendor/      | LangChain kurulum      |

---

## ⚡ Hızlı Başlangıç: LangGraph Kodu Nasıl Görünür?

Hedefin bu kodu anlayıp yazabilmek:

```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END

# 1. STATE — Laravel'deki request() gibi, veriyi taşır
class AgentState(TypedDict):
    messages: list[str]
    user_input: str
    response: str

# 2. NODE — Laravel'deki Controller method gibi
def process_node(state: AgentState) -> AgentState:
    user_msg = state["user_input"]
    return {"response": f"İşlendi: {user_msg}"}

# 3. GRAPH — Laravel'deki Router gibi, akışı yönetir
graph = StateGraph(AgentState)
graph.add_node("process", process_node)
graph.set_entry_point("process")
graph.add_edge("process", END)

app = graph.compile()
result = app.invoke({"user_input": "Merhaba", "messages": [], "response": ""})
print(result["response"])  # -> İşlendi: Merhaba
```

Bu kodu tam anlıyor olmak ile başla → [TypedDict Dersi →](./typeddict)
