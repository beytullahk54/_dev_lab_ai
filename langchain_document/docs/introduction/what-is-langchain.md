# LangChain Nedir?

**LangChain**, büyük dil modelleri (LLM) ile uygulama geliştirmeyi kolaylaştıran bir Python/JavaScript framework'üdür. LLM'leri araçlara, veritabanlarına ve diğer sistemlere bağlamana imkan tanır.

## Temel Bileşenler

### 1. LLM / Chat Models

LangChain, farklı model sağlayıcılarını tek bir arayüzle kullanmanı sağlar:

```python
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama  # Yerel modeller için

# OpenAI
llm = ChatOpenAI(model="gpt-4o")

# Yerel Ollama (projenizde kullanılan)
llm = ChatOllama(model="qwen3:8b", base_url="http://localhost:11434")
```

### 2. Messages (Mesajlar)

LLM ile konuşmalar mesaj nesneleriyle yönetilir:

```python
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

messages = [
    SystemMessage(content="Sen bir matematik uzmanısın."),
    HumanMessage(content="2 + 2 kaçtır?"),
]

response = llm.invoke(messages)
print(response.content)  # "4"
```

### 3. Chains (Zincirler)

Birden fazla adımı birbirine bağlamak için kullanılır:

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_messages([
    ("system", "Sen {role} uzmanısın."),
    ("human", "{question}")
])

chain = prompt | llm | StrOutputParser()
result = chain.invoke({"role": "matematik", "question": "Pi sayısı nedir?"})
```

### 4. Retrievers (Geri Getirici)

Vektör veritabanından ilgili belgeleri çekmek için:

```python
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
docs = retriever.invoke("hukuki sözleşme nedir?")
```

## LangChain vs LangGraph

| Özellik | LangChain | LangGraph |
|---------|-----------|-----------|
| Yapı | Zincirleme (linear) | Graf tabanlı (graph) |
| Dallanma | Sınırlı | Tam destek |
| Döngüler | Yok | Var |
| Durum yönetimi | Manuel | Otomatik (StateGraph) |
| Kullanım amacı | Basit pipeline | Çok adımlı ajan sistemleri |

## Neden LangGraph?

Projenizde birden fazla uzman ajan var: matematik, hukuk, bilişim, selamlama. Bu ajanlar arasında **niyet bazlı yönlendirme** gerekiyor. Bu tür dallanmalı, durumlu yapılar için LangGraph idealdir.

::: tip
Basit soru-cevap için LangChain chains yeterlidir.
Çok ajanlı, dallanmalı, döngüsel sistemler için LangGraph kullanın.
:::

## Sonraki Adım

[LangGraph Nedir? →](/introduction/what-is-langgraph)
