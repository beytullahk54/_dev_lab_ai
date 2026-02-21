# Node (Düğüm) Nedir?

**Node**, LangGraph grafındaki temel çalışma birimidir. Her node bir Python fonksiyonudur: state alır, işler, güncellemiş state döndürür.

## Node Anatomisi

```python
from .core.state import AgentState

def math_expert_node(state: AgentState) -> dict:
    # 1. State'den veri oku
    user_query = state["user_query"]

    # 2. İş mantığı (LLM çağrısı, hesaplama, veri çekme...)
    response = llm.invoke([
        SystemMessage(content="Sen bir matematik uzmanısın."),
        HumanMessage(content=user_query)
    ])

    # 3. Sadece güncellenen alanları döndür
    return {"final_answer": response.content}
```

## Projenizin Node'ları

### Ana Yönlendirici — `main_router_agent`

```python
def main_router_agent(state: AgentState) -> dict:
    user_query = state["user_query"]

    # Kullanıcı niyetini belirle
    prompt = f"""Kullanıcının sorusunu analiz et ve aşağıdakilerden birini döndür:
    - math       : Matematik sorusu
    - legal      : Genel hukuk sorusu
    - it_legal   : Bilişim hukuku sorusu
    - greeting   : Selamlama / sohbet
    - vektor     : Genel bilgi sorusu
    - support    : Teknik destek

    Sadece bu kelimelerden birini döndür, başka hiçbir şey yazma.

    Kullanıcı sorusu: {user_query}
    """

    response = llm_qwen1.invoke([HumanMessage(content=prompt)])
    intent = response.content.strip().lower()

    return {"intent": intent}
```

Bu node sadece `intent` alanını günceller. Diğer alanlar değişmez.

### Uzman Node Örneği — `math_expert_node`

```python
def math_expert_node(state: AgentState) -> dict:
    user_query = state["user_query"]

    messages = [
        SystemMessage(content="""Sen bir matematik uzmanısın.
        Adım adım çözüm göster. Türkçe yanıt ver."""),
        HumanMessage(content=user_query)
    ]

    response = llm.invoke(messages)
    return {"final_answer": response.content}
```

### RAG Node Örneği — `it_legal_rag_node`

```python
def it_legal_rag_node(state: AgentState) -> dict:
    user_query = state["user_query"]

    # 1. Vektör araması
    query_vector = text_to_vector(user_query)
    docs = vectorstore.similarity_search_by_vector(query_vector, k=3)

    # 2. Bağlamı hazırla
    context = "\n\n".join([doc.page_content for doc in docs])

    # 3. LLM'e bağlamla sor
    messages = [
        SystemMessage(content=f"""Sen bir bilişim hukuku uzmanısın.
        Aşağıdaki belgeleri kullanarak soruyu yanıtla:

        {context}
        """),
        HumanMessage(content=user_query)
    ]

    response = llm.invoke(messages)
    return {"final_answer": response.content}
```

## Node Türleri

### 1. Basit LLM Node

```python
def greeting_node(state: AgentState) -> dict:
    response = llm.invoke([
        SystemMessage(content="Samimi ve kısa selamlama yap."),
        HumanMessage(content=state["user_query"])
    ])
    return {"final_answer": response.content}
```

### 2. RAG Node

Vektör veritabanından belge çekip LLM'e bağlam olarak verir.

### 3. Tool Node

Harici araç (hesap makinesi, web arama, API) çağırır.

```python
def calculator_node(state: AgentState) -> dict:
    # Güvenli matematiksel hesaplama
    expr = extract_math_expression(state["user_query"])
    result = eval_safe(expr)
    return {"final_answer": str(result)}
```

## Node Kaydetme

```python
workflow = StateGraph(AgentState)

# Her node isim + fonksiyon ile kaydedilir
workflow.add_node("main_agent", main_router_agent)
workflow.add_node("math_expert", math_expert_node)
workflow.add_node("legal_expert", legal_expert_node)
workflow.add_node("greeting_expert", greeting_node)
```

::: tip İsimlendirme Kuralı
Node isimleri (string) ile fonksiyon isimleri farklı olabilir. `"math_expert"` ismi graf içinde kullanılır, `math_expert_node` ise Python fonksiyonunun adıdır.
:::

## Sonraki Adım

[Graph Nedir? →](/core/graph)
