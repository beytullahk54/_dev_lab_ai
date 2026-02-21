# Router Agent

Router Agent, multi-agent sistemin **trafik polisidir**. Kullanıcıdan gelen soruyu analiz eder, niyeti (intent) belirler ve uygun uzmana yönlendirir.

## Tasarım İlkeleri

Router Agent'ın tek sorumluluğu vardır: **sınıflandırma**. Asla yanıt üretmez, asla kullanıcıya cevap vermez. Sadece bir etiket döndürür.

```
İyi Router:   "math" → math_expert'e gider ✓
Kötü Router:  "Matematik sorusu, cevabı 42'dir" → Hem yönlendirdi hem yanıtladı ✗
```

## Yapılandırılmış Çıktı ile Router

En sağlam yöntem, LLM'i yapılandırılmış çıktıya zorlamaktır:

```python
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

ROUTER_TEMPLATE = """Kullanıcının sorusunu analiz et ve aşağıdaki kategorilerden
YALNIZCA BİRİNİ döndür. Başka hiçbir şey yazma.

Kategoriler:
- math      : Matematik, sayılar, hesaplama
- legal     : Genel hukuk, sözleşme, mevzuat
- it_legal  : Bilişim hukuku, siber suç, KVKK, yazılım lisansı
- greeting  : Selamlama, tanışma, genel sohbet
- vektor    : Genel bilgi, nasıl yapılır soruları
- support   : Teknik destek, yazılım/donanım sorunları

Kullanıcı sorusu: {query}

Kategori:"""

def main_router_agent(state: AgentState) -> dict:
    prompt = PromptTemplate.from_template(ROUTER_TEMPLATE)
    chain = prompt | llm | StrOutputParser()

    intent = chain.invoke({"query": state["user_query"]})
    intent = intent.strip().lower()

    # Bilinmeyen intent için fallback
    valid_intents = {"math", "legal", "it_legal", "greeting", "vektor", "support"}
    if intent not in valid_intents:
        intent = "vektor"  # Varsayılan uzman

    return {"intent": intent}
```

## Pydantic ile Tip Güvenli Router

Daha güvenli bir yaklaşım için Pydantic modeli kullan:

```python
from pydantic import BaseModel
from typing import Literal

class RouterDecision(BaseModel):
    intent: Literal["math", "legal", "it_legal", "greeting", "vektor", "support"]
    confidence: float  # 0.0 - 1.0

# LLM'i bu modeli üretmeye zorla
structured_llm = llm.with_structured_output(RouterDecision)

def main_router_agent(state: AgentState) -> dict:
    decision = structured_llm.invoke([
        SystemMessage(content="Kullanıcı sorusunu kategorile."),
        HumanMessage(content=state["user_query"])
    ])

    return {
        "intent": decision.intent,
        # İsteğe bağlı: güven skoru da state'e eklenebilir
    }
```

## Çok Adımlı Router

Bazı durumlarda iki aşamalı yönlendirme gerekebilir:

```python
def main_router_agent(state: AgentState) -> dict:
    query = state["user_query"]

    # Önce geniş kategori
    broad_category = classify_broad(query)  # "law" veya "science"

    # Sonra dar kategori
    if broad_category == "law":
        sub_category = classify_law(query)  # "legal" veya "it_legal"
        return {"intent": sub_category}
    else:
        return {"intent": "vektor"}
```

## Keyword Tabanlı Hızlı Router (LLM'siz)

Basit durumlar için LLM kullanmadan keyword matching:

```python
KEYWORD_MAP = {
    "math":    ["hesapla", "toplam", "çarp", "böl", "integral", "türev", "+", "-", "*", "/"],
    "legal":   ["sözleşme", "dava", "hukuk", "kanun", "madde", "yargı"],
    "it_legal": ["kvkk", "gdpr", "siber", "yazılım lisans", "veri ihlali"],
    "greeting": ["merhaba", "selam", "nasılsın", "günaydın", "iyi günler"],
}

def keyword_router(state: AgentState) -> dict:
    query = state["user_query"].lower()

    for intent, keywords in KEYWORD_MAP.items():
        if any(kw in query for kw in keywords):
            return {"intent": intent}

    return {"intent": "vektor"}  # Eşleşme yoksa varsayılan
```

::: tip Ne Zaman LLM, Ne Zaman Keyword?
- **Keyword:** Hız kritikse, basit ve öngörülebilir sorgular için
- **LLM:** Anlam belirsizliği varsa, dil nüansları önemliyse

Projeniz LLM tabanlı router kullanıyor — bu daha esnek ama daha yavaş.
:::

## Router'ı Test Etme

```python
test_cases = [
    ("2 + 2 kaçtır?", "math"),
    ("Kira sözleşmesi nasıl iptal edilir?", "legal"),
    ("KVKK'ya göre veri silme hakkım nedir?", "it_legal"),
    ("Merhaba!", "greeting"),
]

for query, expected in test_cases:
    result = app.invoke({"user_query": query, "intent": "", "final_answer": ""})
    status = "✓" if result["intent"] == expected else "✗"
    print(f"{status} '{query}' → {result['intent']} (beklenen: {expected})")
```

## Sonraki Adım

[Alt Ajanlar →](/multi-agent/sub-agents)
