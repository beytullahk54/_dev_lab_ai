# Yönlendirme Mantığı

Yönlendirme (routing), multi-agent sistemin en kritik parçasıdır. Yanlış yönlendirme, kullanıcıya yanlış uzmanın yanıt vermesine yol açar.

## İki Katmanlı Yönlendirme

Projenizde yönlendirme iki aşamada gerçekleşir:

```
Kullanıcı sorusu
       │
       ▼
[main_router_agent]         ← 1. Aşama: LLM ile intent tespiti
  state["intent"] = "legal"
       │
       ▼
[route_decision]            ← 2. Aşama: intent → node mapping
  return state["intent"]
       │
       ▼
[legal_expert_node]         ← Doğru uzman devreye girer
```

## route_decision Fonksiyonu

```python
from typing import Literal

def route_decision(state: AgentState) -> Literal[
    "math", "legal", "greeting", "vektor"
]:
    return state["intent"]
```

Bu fonksiyon son derece basit — state'ten intent'i alır ve döndürür. Asıl iş `main_router_agent` içinde yapılmıştır.

`Literal` tip ipucu, hangi değerlerin geçerli olduğunu hem IDE'ye hem de LangGraph'a söyler.

## Intent Değerleri

| Intent | Tetikleyen Node | Örnek Soru |
|--------|-----------------|------------|
| `math` | math_expert | "İntegral nedir?" |
| `legal` | legal_expert | "Boşanma davası nasıl açılır?" |
| `it_legal` | it_legal_expert | "KVKK cezaları nelerdir?" |
| `greeting` | greeting_expert | "Merhaba, nasılsın?" |
| `vektor` | vektor_rag_expert | "Python nedir?" |
| `support` | support_rag_expert | "Uygulama neden çöküyor?" |

## Fallback Stratejisi

Router yanlış/bilinmeyen bir intent üretirse ne olur?

```python
def route_decision(state: AgentState) -> str:
    intent = state["intent"].strip().lower()

    # Mapping'de olmayan değer için fallback
    VALID_INTENTS = {
        "math", "legal", "it_legal",
        "greeting", "vektor", "support"
    }

    if intent not in VALID_INTENTS:
        print(f"⚠️ Bilinmeyen intent: '{intent}' → 'vektor' olarak yönlendiriliyor")
        return "vektor"

    return intent
```

## Intent Debug

Hangi soruların hangi intente yönlendirildiğini logla:

```python
def route_decision(state: AgentState) -> str:
    intent = state["intent"]
    query_preview = state["user_query"][:50]
    print(f"🔀 Yönlendirme: '{query_preview}...' → [{intent.upper()}]")
    return intent
```

Örnek çıktı:
```
🔀 Yönlendirme: 'Türk ceza kanununda bilişim suçları neler...' → [IT_LEGAL]
🔀 Yönlendirme: 'Merhaba!' → [GREETING]
🔀 Yönlendirme: '∫x²dx formülü nedir?' → [MATH]
```

## Çok Boyutlu Yönlendirme

Daha karmaşık senaryolar için yönlendirme birden fazla parametreye bakabilir:

```python
def route_decision(state: AgentState) -> str:
    intent = state["intent"]
    query = state["user_query"].lower()

    # Özel durum: hem math hem de code içeriyorsa
    if intent == "math" and "python" in query:
        return "code_expert"  # Matematik + kodlama → kod uzmanı

    return intent
```

## Sonraki Adım

[Tüm Sistemi Çalıştırma →](/project/running)
