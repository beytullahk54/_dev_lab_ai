# LangGraph Graf Yapısı

## Graf Nedir?

LangGraph'ta bir "graf", birbiriyle bağlı **node**'lardan (işlem adımları) ve bunlar arasındaki **edge**'lerden (yönlendirme kuralları) oluşur.

Her mesaj geldiğinde graf baştan sona çalışır:
1. `router_node`'a girer
2. Intent belirlenir
3. İlgili agent node'una yönlendirilir
4. `END`'e ulaşılır, cevap döner

---

## Graf Şeması

```
                    ┌─────────────────┐
   user_message ──> │  router_node    │
                    │  (Groq LLM)     │
                    └────────┬────────┘
                             │ intent
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
      ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
      │ kayit_ac     │ │kullanici_say │ │ bilinmiyor   │
      │ node         │ │ node         │ │ node         │
      │ (Groq+SQLite)│ │ (SQLite)     │ │ (sabit msg)  │
      └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
             │                │                │
             └────────────────┴────────────────┘
                              │
                             END
```

---

## State Yapısı

Graf boyunca taşınan `AgentState` TypedDict:

```python
class AgentState(TypedDict):
    user_message: str   # Kullanıcıdan gelen ham metin
    intent: str         # router'ın belirlediği niyet
    response: str       # Kullanıcıya dönecek son cevap
```

Her node `state` alır, değiştirilmiş `state` döner. Bu sayede veri her adımda birikir.

---

## Node'lar

### `router_node`
- **Girdi**: `user_message`
- **Çıktı**: `intent` (`kayit_ac` | `kullanici_say` | `bilinmiyor`)
- **Kullandığı**: Groq LLM (sadece etiket döndürür)

### `kayit_ac_node`
- **Girdi**: `user_message`
- **Çıktı**: `response`
- **Kullandığı**: Groq LLM (isim çıkarma) + SQLite (INSERT)

### `kullanici_say_node`
- **Girdi**: *(state, ancak mesaja ihtiyaç yok)*
- **Çıktı**: `response`
- **Kullandığı**: Yalnızca SQLite (COUNT)

### `bilinmiyor_node`
- **Girdi**: *(state)*
- **Çıktı**: `response` (sabit yardım mesajı)
- **Kullandığı**: Hiçbir dış servis

---

## Edge Türleri

| Edge Türü | Kullanım Yeri | Açıklama |
|---|---|---|
| `set_entry_point` | `router` | Grafın giriş noktası |
| `add_conditional_edges` | `router → *` | Intent'e göre dallanma |
| `add_edge` | `* → END` | Her agent node'u END'e bağlar |

---

## Yeni Node Ekleme

```python
# 1. Node fonksiyonu yaz
def yeni_agent_node(state: AgentState) -> AgentState:
    response = "Yeni agent çalıştı"
    return {**state, "response": response}

# 2. Graf'a ekle
graph.add_node("yeni_agent", yeni_agent_node)

# 3. Router prompt'una ekle
# "- yeni_intent → açıklama"

# 4. Conditional edge'e ekle
# "yeni_intent": "yeni_agent"

# 5. END'e bağla
graph.add_edge("yeni_agent", END)
```
