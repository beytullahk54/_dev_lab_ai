# Hata Yönetimi

Production ortamında LLM çağrıları başarısız olabilir, model beklenmedik çıktılar üretebilir, vektör araması boş dönebilir. Bu durumları ele almak gerekir.

## Node İçinde Try/Except

En basit yöntem — her node kendi hatalarını yakalar:

```python
def math_expert_node(state: AgentState) -> dict:
    try:
        response = llm.invoke([
            SystemMessage(content="Matematik uzmanısın."),
            HumanMessage(content=state["user_query"])
        ])
        return {"final_answer": response.content}

    except Exception as e:
        # Kullanıcıya anlamlı hata mesajı
        return {"final_answer": f"Üzgünüm, bir hata oluştu: {type(e).__name__}. Lütfen tekrar deneyin."}
```

## State'e Hata Alanı Ekleme

Hataları takip etmek için state'e alan ekle:

```python
class AgentState(TypedDict):
    user_query: str
    intent: str
    final_answer: str
    error: str          # Hata mesajı (varsa)
    had_error: bool     # Hata oldu mu?
```

```python
def safe_expert_node(state: AgentState) -> dict:
    try:
        response = llm.invoke([...])
        return {"final_answer": response.content, "had_error": False}
    except Exception as e:
        return {
            "final_answer": "Şu an yanıt veremiyorum, lütfen tekrar deneyin.",
            "had_error": True,
            "error": str(e)
        }
```

## Retry Mekanizması

LangChain'in built-in retry desteği:

```python
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="qwen3:8b",
    max_retries=3,          # 3 kez dene
)

# Veya zincir seviyesinde
chain = prompt | llm.with_retry(stop_after_attempt=3)
```

## Boş RAG Sonuçları

Vektör araması sonuç döndürmeyebilir:

```python
def rag_node(state: AgentState) -> dict:
    docs = retriever.invoke(state["user_query"])

    if not docs:
        # Belge bulunamadı
        return {
            "final_answer": "Bu konuda veritabanımda bilgi bulunamadı. "
                           "Sorunuzu farklı bir şekilde sormayı deneyin."
        }

    context = "\n\n".join([d.page_content for d in docs])
    response = llm.invoke([
        SystemMessage(content=f"Belgeler:\n{context}"),
        HumanMessage(content=state["user_query"])
    ])
    return {"final_answer": response.content}
```

## Timeout Yönetimi

Uzun süren LLM çağrıları için timeout:

```python
import asyncio
from langchain_ollama import ChatOllama

async def async_expert_node(state: AgentState) -> dict:
    try:
        response = await asyncio.wait_for(
            llm.ainvoke([HumanMessage(content=state["user_query"])]),
            timeout=30.0  # 30 saniye
        )
        return {"final_answer": response.content}
    except asyncio.TimeoutError:
        return {"final_answer": "Yanıt süresi aşıldı. Daha kısa bir soru deneyin."}
```

## Fallback Node

Tüm diğer node'lar başarısız olduğunda devreye giren güvenli bir fallback:

```python
def fallback_node(state: AgentState) -> dict:
    return {
        "final_answer": "Üzgünüm, şu anda bu soruyu yanıtlayamıyorum. "
                       "Lütfen daha sonra tekrar deneyin veya "
                       "sorunuzu farklı bir şekilde ifade edin."
    }

# Graf'ta fallback
workflow.add_node("fallback", fallback_node)

def safe_route(state: AgentState) -> str:
    intent = state.get("intent", "")
    if not intent or intent not in VALID_INTENTS:
        return "fallback"
    return intent

workflow.add_conditional_edges("main_agent", safe_route, {
    "math": "math_expert",
    "legal": "legal_expert",
    "fallback": "fallback",
    ...
})
workflow.add_edge("fallback", END)
```

## Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def math_expert_node(state: AgentState) -> dict:
    logger.info(f"math_expert çalışıyor | query: {state['user_query'][:50]}")

    try:
        response = llm.invoke([...])
        logger.info("math_expert başarılı")
        return {"final_answer": response.content}
    except Exception as e:
        logger.error(f"math_expert hatası: {e}", exc_info=True)
        return {"final_answer": "Hata oluştu."}
```
