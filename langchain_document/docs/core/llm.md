# LLM Bağlantısı

Projenizde LLM bağlantısı merkezi bir `core/llm.py` dosyasında yönetilir. Bu sayede tüm ajanlar aynı model konfigürasyonunu kullanır.

## Temel Yapı

```python
# core/llm.py
from langchain_ollama import ChatOllama

# Ana model (Qwen3 8B)
llm = ChatOllama(
    model="qwen3:8b",
    base_url="http://localhost:11434",
    temperature=0.7,
)

# Alternatif model (daha küçük/hızlı)
llm_qwen1 = ChatOllama(
    model="qwen2.5:1.5b",
    base_url="http://localhost:11434",
    temperature=0.3,
)
```

## Desteklenen Model Sağlayıcıları

### Ollama (Yerel - Projenizde kullanılan)
```python
from langchain_ollama import ChatOllama

llm = ChatOllama(model="qwen3:8b")
```

### OpenAI
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o", api_key="sk-...")
```

### Anthropic Claude
```python
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(model="claude-sonnet-4-6")
```

## LLM Parametreleri

| Parametre | Açıklama | Önerilen Değer |
|-----------|----------|----------------|
| `temperature` | Yaratıcılık (0=deterministik, 1=çok yaratıcı) | 0.3-0.7 |
| `max_tokens` | Maksimum yanıt uzunluğu | 1024-4096 |
| `top_p` | Token seçim çeşitliliği | 0.9 |
| `base_url` | Model sunucusunun adresi | `http://localhost:11434` |

## LLM Çağırma Yöntemleri

### `.invoke()` — Senkron

```python
from langchain_core.messages import HumanMessage, SystemMessage

response = llm.invoke([
    SystemMessage(content="Sen bir matematik uzmanısın."),
    HumanMessage(content="Pi sayısının değeri nedir?")
])

print(response.content)
```

### `.stream()` — Streaming

```python
for chunk in llm.stream([HumanMessage(content="Python nedir?")]):
    print(chunk.content, end="", flush=True)
```

### Prompt Template ile Zincir

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_messages([
    ("system", "Sen bir {alan} uzmanısın. Türkçe yanıt ver."),
    ("human", "{soru}")
])

chain = prompt | llm | StrOutputParser()

result = chain.invoke({
    "alan": "hukuk",
    "soru": "Kira sözleşmesi nedir?"
})
```

## Projenizde İki Model Kullanımı

Projeniz hem `llm` hem `llm_qwen1` import ediyor. Bu mimariyle:

- **Karmaşık görevler** (hukuki analiz, RAG) → `llm` (büyük model)
- **Basit görevler** (selamlama, niyet tespiti) → `llm_qwen1` (küçük/hızlı model)

```python
# main_router_agent.py
from ..core.llm import llm_qwen1  # Hızlı niyet tespiti için

# it_legal_rag_node.py
from ..core.llm import llm  # Detaylı analiz için
```

::: tip Maliyet ve Hız Optimizasyonu
Niyet tespiti (intent classification) için büyük model kullanmak gereksizdir. Küçük bir model bu iş için yeterlidir ve çok daha hızlı yanıt verir.
:::

## Sonraki Adım

[Node (Düğüm) Nedir? →](/core/nodes)
