# Yeni Agent Ekleme Rehberi

Sisteme yeni bir agent eklemek **5 adım** sürer.

---

## Örnek: "kullanici_sil" Agent'ı

### Adım 1 — Node Fonksiyonu Yaz

`agents.py` içine ekle:

```python
def kullanici_sil_node(state: AgentState) -> AgentState:
    system_prompt = (
        "Kullanıcı mesajından silinecek kişinin adını çıkar. "
        "Sadece ismi yaz, başka hiçbir şey yazma."
    )
    result = get_llm().invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=state["user_message"]),
    ])
    name = result.content.strip()
    # database.py'ye delete_user() eklemen gerekir
    response = f"🗑️ '{name}' kaydı silindi."
    return {**state, "response": response}
```

### Adım 2 — Graf'a Node Ekle

`build_graph()` içinde:

```python
graph.add_node("kullanici_sil", kullanici_sil_node)
```

### Adım 3 — Router Prompt'unu Güncelle

`router_node()` içindeki `system_prompt`'a yeni satır ekle:

```python
"- kullanici_sil → bir kullanıcı silinmek isteniyorsa\n"
```

### Adım 4 — Conditional Edge'e Dal Ekle

```python
graph.add_conditional_edges(
    "router",
    route_decision,
    {
        "kayit_ac":      "kayit_ac",
        "kullanici_say": "kullanici_say",
        "kullanici_sil": "kullanici_sil",   # ← yeni
        "bilinmiyor":    "bilinmiyor",
    },
)
```

### Adım 5 — END'e Bağla

```python
graph.add_edge("kullanici_sil", END)
```

---

## Checklist

- [ ] `agents.py`'e node fonksiyonu eklendi
- [ ] `graph.add_node(...)` çağrıldı
- [ ] Router sistem promptuna yeni etiket eklendi
- [ ] `conditional_edges` sözlüğüne yeni dal eklendi
- [ ] `graph.add_edge("...", END)` çağrıldı
- [ ] Gerekiyorsa `database.py`'e yeni CRUD fonksiyonu eklendi

::: warning
`_llm` cache'ini sıfırlamak için lazy init'te `global _llm = None` çağırmaya gerek yoktur — yeni node `get_llm()` kullandığı sürece aynı LLM nesnesi yeniden kullanılır.
:::
