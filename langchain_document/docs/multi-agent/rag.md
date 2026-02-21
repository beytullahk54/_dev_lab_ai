# RAG Entegrasyonu

**RAG (Retrieval-Augmented Generation)**, LLM'in kendi bilgisiyle sınırlı kalmadan bir bilgi tabanından (vektör veritabanı) ilgili belgeleri çekerek yanıt üretmesini sağlar.

## RAG Neden Gerekli?

```
Saf LLM:
  Kullanıcı → LLM → Yanıt
  (Sadece eğitim verisi — güncel değil, şirkete özel bilgi yok)

RAG ile:
  Kullanıcı → [Vektör Arama] → İlgili Belgeler → LLM → Yanıt
  (Güncel, şirkete özel, kaynaklı yanıtlar)
```

## Vektör Veritabanı ve Embedding

### Embedding Nedir?

Metni sayısal bir vektöre dönüştürme işlemi. Anlamca benzer metinler birbirine yakın vektörler üretir:

```python
# core/embedding_engine.py
from langchain_ollama import OllamaEmbeddings

embeddings = OllamaEmbeddings(
    model="nomic-embed-text",  # veya mxbai-embed-large
    base_url="http://localhost:11434"
)

def text_to_vector(text: str) -> list[float]:
    return embeddings.embed_query(text)
```

### Vektör Veritabanı Kurma

```python
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 1. Belgeleri yükle
loader = DirectoryLoader("./data/legal_docs/", glob="**/*.txt")
documents = loader.load()

# 2. Parçalara böl
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
chunks = splitter.split_documents(documents)

# 3. Vektörleştir ve kaydet
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db"
)
```

## RAG Node Yapısı

### Temel RAG Node

```python
from langchain_community.vectorstores import Chroma

# Veritabanını yükle (uygulama başlangıcında bir kez)
vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings
)

def it_legal_rag_node(state: AgentState) -> dict:
    user_query = state["user_query"]

    # 1. Semantik arama — en ilgili 3 belgeyi getir
    docs = vectorstore.similarity_search(user_query, k=3)

    # 2. Belgeleri birleştir
    context = "\n\n---\n\n".join([
        f"Kaynak: {doc.metadata.get('source', 'Bilinmeyen')}\n{doc.page_content}"
        for doc in docs
    ])

    # 3. LLM'e bağlam ver
    messages = [
        SystemMessage(content=f"""Sen bir bilişim hukuku uzmanısın.
Aşağıdaki yasal belgeler sana yardımcı olmak için seçildi.
SADECE bu belgelerden yararlanarak yanıt ver.
Belgede olmayan bir bilgiyi bilmiyorsan "Bu konuda belgelerimde bilgi yok" de.

=== BELGELER ===
{context}
===============
"""),
        HumanMessage(content=user_query)
    ]

    response = llm.invoke(messages)
    return {"final_answer": response.content}
```

### Embedding ile Arama (text_to_vector kullanımı)

Projenizde `text_to_vector` fonksiyonu var. Manuel embedding araması için:

```python
def vektor_rag_node(state: AgentState) -> dict:
    user_query = state["user_query"]

    # Sorguyu vektöre çevir
    query_vector = text_to_vector(user_query)

    # Vektör benzerliğiyle ara
    docs = vectorstore.similarity_search_by_vector(query_vector, k=3)

    context = "\n\n".join([doc.page_content for doc in docs])

    messages = [
        SystemMessage(content=f"Aşağıdaki bilgileri kullanarak soruyu yanıtla:\n\n{context}"),
        HumanMessage(content=user_query)
    ]

    response = llm.invoke(messages)
    return {"final_answer": response.content}
```

## Retriever Pattern

LangChain'de daha temiz bir yaklaşım `retriever` nesnesi kullanmaktır:

```python
# Retriever oluştur (bir kez)
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 4}
)

# Node içinde kullan
def support_rag_node(state: AgentState) -> dict:
    docs = retriever.invoke(state["user_query"])
    context = "\n".join([d.page_content for d in docs])
    ...
```

## RAG Kalitesini Artırma

### MMR (Maximal Marginal Relevance)

Tekrar eden belgelerden kaçın, çeşitlilik sağla:

```python
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 4, "fetch_k": 20}
)
```

### Metadata Filtreleme

Sadece belirli kaynaklardan ara:

```python
retriever = vectorstore.as_retriever(
    search_kwargs={
        "k": 3,
        "filter": {"category": "it_legal"}  # Sadece bilişim hukuku belgelerinden
    }
)
```

### Chunk Boyutu Seçimi

| İçerik Türü | Önerilen Chunk |
|-------------|----------------|
| Hukuki metinler | 300-500 token |
| Teknik dokümantasyon | 500-800 token |
| Genel belgeler | 400-600 token |

Küçük chunk → daha hassas arama, az bağlam
Büyük chunk → daha fazla bağlam, gürültü riski

## Sonraki Adım

[Proje Genel Bakış →](/project/overview)
