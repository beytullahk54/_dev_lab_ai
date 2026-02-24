# Ders 2: Type Hints — Tip Bildirimleri

> **Laravel karşılığı:** PHP 8'de `function kullanici(string $ad, int $yas): array` yazarsın. Python'da aynısını `def kullanici(ad: str, yas: int) -> dict:` şeklinde yaparsın.

---

## 🔥 Direkt Koda Gir

```python
# PHP'de:
# function selamla(string $ad): string {
#     return "Merhaba " . $ad;
# }

# Python'da:
def selamla(ad: str) -> str:
    return f"Merhaba {ad}"

print(selamla("Ahmet"))  # -> Merhaba Ahmet
```

---

## 📦 Temel Tipler

```python
# PHP         → Python
# string      → str
# int         → int
# float       → float
# bool        → bool
# array       → list veya dict
# null        → None

def ornek(
    isim: str,
    yas: int,
    maas: float,
    aktif: bool,
    etiketler: list,
    ayarlar: dict,
) -> None:  # None = return etmiyor (PHP'deki void gibi)
    print(isim, yas, maas, aktif)

ornek("Ali", 25, 5500.50, True, ["python", "ai"], {"tema": "dark"})
```

---

## 🧩 Önemli Tipler — LangGraph'ta Kullandıkların

```python
from typing import Optional, Union, List, Dict, Any

# Optional — PHP'deki ?string gibi (null olabilir)
def node_calistir(input: Optional[str] = None) -> str:
    if input is None:
        return "Boş geldi"
    return input

# Union — birden fazla tip olabilir (PHP 8 union types gibi)
def isle(veri: Union[str, int]) -> str:
    return str(veri)

# List[str] — string listesi
def mesajlari_al() -> List[str]:
    return ["Merhaba", "Nasılsın?"]

# Dict[str, Any] — herhangi değerli dict
def state_al() -> Dict[str, Any]:
    return {"user": "Ali", "count": 5, "active": True}

# Modern syntax (Python 3.10+) — daha kısa:
def yeni_syntax(ad: str | None = None) -> list[str]:
    return [ad or "anonim"]
```

---

## 🔥 LangGraph'ta Type Hints Neden Kritik?

```python
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

# State içinde her field'a tip hint zorunlu
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]  # LangChain mesaj tipi
    user_input: str
    next_agent: str | None      # None veya string
    is_complete: bool
    retry_count: int

# Node fonksiyonunda hem input hem output tipi belirtilir
def router_node(state: AgentState) -> Dict[str, Any]:
    """
    Bu node kullanıcı inputunu analiz edip hangi agent'a gideceğini belirler.
    PHP'deki: public function route(Request $request): array
    """
    user_input = state["user_input"]

    if "hukuk" in user_input.lower():
        return {"next_agent": "law_agent"}
    elif "matematik" in user_input.lower():
        return {"next_agent": "math_agent"}
    else:
        return {"next_agent": "general_agent"}
```

---

## 🛠️ Callable Tip — Fonksiyon Parametre Tipi

```python
from typing import Callable

# PHP'deki Closure gibi — fonksiyon bir parametre olarak geçilebilir
def pipeline_calistir(
    input: str,
    islemci: Callable[[str], str]  # str alan, str dönen fonksiyon
) -> str:
    return islemci(input)

def buyuk_harf_yap(metin: str) -> str:
    return metin.upper()

sonuc = pipeline_calistir("merhaba", buyuk_harf_yap)
print(sonuc)  # -> MERHABA
```

---

## ⚠️ Sık Yapılan Hatalar

**Hata:** `TypeError: selamla() missing 1 required positional argument`

```python
def selamla(ad: str, soyad: str) -> str:
    return f"{ad} {soyad}"

# YANLIŞ
selamla("Ali")  # TypeError! soyad eksik

# DOĞRU — varsayılan değer ver
def selamla(ad: str, soyad: str = "") -> str:
    return f"{ad} {soyad}"

selamla("Ali")         # -> Ali
selamla("Ali", "Ak")   # -> Ali Ak
```

> 🔴 **Laravel analogisi:** PHP'de `function foo($a, $b)` deyip `foo("x")` çağırsan da aynı hata çıkar.

---

## 🎯 Görev

Aşağıdaki fonksiyonu type hint'lerle tamamla:

```python
# Bu fonksiyon bir LangGraph node'u olacak.
# - state parametresi AgentState tipinde
# - Eğer user_input "evet" içeriyorsa onaylandı, yoksa reddedildi dönsün
# - Dönen dict'te "karar" (str) ve "guvensiz_mi" (bool) key'leri olsun

from typing import TypedDict, Dict, Any

class AgentState(TypedDict):
    user_input: str

def karar_node(???):
    ???
```

<details>
<summary>💡 Çözümü göster</summary>

```python
from typing import TypedDict, Dict, Any

class AgentState(TypedDict):
    user_input: str

def karar_node(state: AgentState) -> Dict[str, Any]:
    evet_iceriyor = "evet" in state["user_input"].lower()
    return {
        "karar": "onaylandı" if evet_iceriyor else "reddedildi",
        "guvensiz_mi": not evet_iceriyor,
    }

# Test
print(karar_node({"user_input": "evet, kabul ediyorum"}))
# -> {'karar': 'onaylandı', 'guvensiz_mi': False}
```

</details>

---

**Önceki ders:** [TypedDict ←](./typeddict) | **Sonraki ders:** [Fonksiyonlar & Decorator →](./functions-decorator)
