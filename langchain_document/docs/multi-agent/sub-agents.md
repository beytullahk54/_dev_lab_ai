# Alt Ajanlar (Sub-Agents)

Alt ajanlar, yalnızca kendi uzmanlık alanlarına odaklanan, bağımsız node fonksiyonlarıdır. Her biri farklı sistem promptu, farklı model veya farklı araç kullanabilir.

## Alt Ajan Tasarım Prensipleri

### 1. Tek Sorumluluk

Her ajan **bir şey** yapar ve onu iyi yapar:

```python
# ✓ İyi: Odaklı sistem promptu
def math_expert_node(state: AgentState) -> dict:
    messages = [
        SystemMessage(content="""Sen bir matematik öğretmenisin.
        - Adım adım çöz
        - Her adımı açıkla
        - Sadece matematik konularını yanıtla
        """),
        HumanMessage(content=state["user_query"])
    ]
    ...

# ✗ Kötü: Çok geniş sistem promptu
def all_in_one_node(state: AgentState) -> dict:
    messages = [
        SystemMessage(content="Her soruyu yanıtlayabilirsin."),
        ...
    ]
```

### 2. Bağımsız Test Edilebilirlik

```python
# Her ajan tek başına test edilebilir
test_state = {
    "user_query": "Türev nedir?",
    "intent": "math",
    "final_answer": ""
}

result = math_expert_node(test_state)
print(result["final_answer"])
```

### 3. State'e Dokunma Minimizasyonu

Alt ajanlar genellikle sadece `final_answer` günceller. `user_query` ve `intent`'e dokunmazlar:

```python
def legal_expert_node(state: AgentState) -> dict:
    # state["user_query"] → oku (tamam)
    # state["intent"] → okuma bile gerek yok
    # state["final_answer"] → sadece bunu yaz

    response = llm.invoke([...])
    return {"final_answer": response.content}  # Sadece bu!
```

## Projenizin Alt Ajanları

### Greeting Node — En Basit Ajan

```python
def greeting_node(state: AgentState) -> dict:
    messages = [
        SystemMessage(content="""Samimi ve yardımsever bir asistansın.
        Kısa, sıcak bir selamlama yap. Kullanıcıya nasıl yardımcı olabileceğini sor."""),
        HumanMessage(content=state["user_query"])
    ]

    response = llm.invoke(messages)
    return {"final_answer": response.content}
```

### Math Expert Node — Hesaplama Uzmanı

```python
def math_expert_node(state: AgentState) -> dict:
    messages = [
        SystemMessage(content="""Sen ileri matematik konularında uzmansın.
        Cebirden analize, istatistikten lineer cebire her konuyu açıklayabilirsin.
        Formülleri açık yaz, adım adım çöz."""),
        HumanMessage(content=state["user_query"])
    ]

    response = llm.invoke(messages)
    return {"final_answer": response.content}
```

### Legal Expert Node — Hukuk Danışmanı

```python
def legal_expert_node(state: AgentState) -> dict:
    messages = [
        SystemMessage(content="""Sen Türk hukuku konusunda bilgi sahibi bir danışmansın.
        Medeni hukuk, ceza hukuku, ticaret hukuku konularında genel bilgi verebilirsin.
        ÖNEMLİ: Verilen bilgiler genel bilgilendirme amaçlıdır,
        kesin hukuki tavsiye için avukatlara başvurulmalıdır."""),
        HumanMessage(content=state["user_query"])
    ]

    response = llm.invoke(messages)
    return {"final_answer": response.content}
```

### Support RAG Node — Teknik Destek

Vektör veritabanından ilgili belgeleri çekip yanıt üretir:

```python
def support_rag_node(state: AgentState) -> dict:
    user_query = state["user_query"]

    # Belge ara
    docs = retriever.invoke(user_query)
    context = "\n\n---\n\n".join([doc.page_content for doc in docs])

    messages = [
        SystemMessage(content=f"""Teknik destek uzmanısın.
        Aşağıdaki dokümantasyon bilgilerini kullanarak soruyu yanıtla.
        Belgede yoksa "Bu konuda bilgim yok" de.

        Belgeler:
        {context}
        """),
        HumanMessage(content=user_query)
    ]

    response = llm.invoke(messages)
    return {"final_answer": response.content}
```

## Farklı Model Kullanan Ajanlar

Her ajan farklı model kullanabilir — bu büyük bir avantaj:

```python
# Hızlı modeller
from ..core.llm import llm_fast    # Küçük model
from ..core.llm import llm_strong  # Büyük model

def greeting_node(state: AgentState) -> dict:
    # Selamlama için küçük model yeterli
    response = llm_fast.invoke([...])
    return {"final_answer": response.content}

def it_legal_rag_node(state: AgentState) -> dict:
    # Hukuki analiz için güçlü model
    response = llm_strong.invoke([...])
    return {"final_answer": response.content}
```

## Yeni Ajan Ekleme

Sisteme yeni bir uzman eklemek için gereken adımlar:

### 1. Node fonksiyonu yaz

```python
# agents/finance_expert_node.py
def finance_expert_node(state: AgentState) -> dict:
    messages = [
        SystemMessage(content="Finansal analiz uzmanısın..."),
        HumanMessage(content=state["user_query"])
    ]
    response = llm.invoke(messages)
    return {"final_answer": response.content}
```

### 2. Graf'a ekle (`run.py`)

```python
from .agents.finance_expert_node import finance_expert_node

workflow.add_node("finance_expert", finance_expert_node)

# Conditional edges mapping'e ekle
workflow.add_conditional_edges(
    "main_agent",
    route_decision,
    {
        ...
        "finance": "finance_expert",  # ← Yeni satır
    }
)

workflow.add_edge("finance_expert", END)
```

### 3. Router'a öğret

Router'ın sistem promptuna yeni kategoriyi ekle:

```
- finance : Borsa, yatırım, finans, ekonomi soruları
```

::: info
Sadece bu 3 adım yeterli. Mevcut ajanlar etkilenmez, sistem genişlemeye hazır.
:::

## Sonraki Adım

[RAG Entegrasyonu →](/multi-agent/rag)
