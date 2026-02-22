# Ders 3: Fonksiyonlar & Decorator

> **Laravel karşılığı:** Decorator = Laravel **Middleware**. Bir fonksiyonu çağırmadan önce/sonra bir şeyler yapar. `@app.route()` → Laravel'deki `Route::get()` gibi düşün.

---

## 🔥 Python Fonksiyon Temelleri

```python
# PHP:
# function topla(int $a, int $b): int {
#     return $a + $b;
# }

# Python:
def topla(a: int, b: int) -> int:
    return a + b

print(topla(3, 5))  # -> 8
```

---

## 🧩 Parametre Çeşitleri

```python
# 1. Positional arguments — sıraya göre
def selamla(ad, soyad):
    print(f"{ad} {soyad}")

selamla("Ali", "Ak")  # -> Ali Ak

# 2. Default değerler — PHP'deki gibi
def baglan(host: str = "localhost", port: int = 5432) -> str:
    return f"{host}:{port}"

print(baglan())                        # -> localhost:5432
print(baglan("192.168.1.1"))           # -> 192.168.1.1:5432
print(baglan(port=3306))               # -> localhost:3306

# 3. Keyword arguments — parametre adıyla çağır
def model_cagir(
    prompt: str,
    model: str = "gpt-4",
    temperature: float = 0.7,
    max_tokens: int = 1000,
) -> str:
    return f"Model: {model}, Prompt: {prompt}"

# Keyword ile çağır — sıra önemli değil
sonuc = model_cagir(
    prompt="Python nedir?",
    temperature=0.5,
    model="gpt-3.5-turbo",
)
print(sonuc)

# 4. *args — değişken sayıda argüman (PHP'deki ...$args)
def hepsini_yazdir(*args):
    for item in args:
        print(item)

hepsini_yazdir("a", "b", "c")  # -> a, b, c

# 5. **kwargs — keyword argümanlar (PHP'deki ...$kwargs)
def ayarla(**kwargs):
    for key, value in kwargs.items():
        print(f"{key} = {value}")

ayarla(tema="dark", dil="tr", model="gpt-4")
```

---

## 🎭 Decorator Nedir?

Decorator, bir fonksiyonu **sarmalar (wrap)** — öncesinde veya sonrasında kod çalıştırır.

```python
# Laravel'de Middleware — request gelmeden önce token kontrol eder:
# Route::middleware('auth:api')->get('/user', ...);

# Python'da Decorator — fonksiyon çalışmadan önce log basar:

import time

def sure_olc(fonksiyon):
    """Bu decorator, fonksiyonun kaç ms sürdüğünü ölçer"""
    def wrapper(*args, **kwargs):
        baslangic = time.time()
        sonuc = fonksiyon(*args, **kwargs)       # asıl fonksiyonu çalıştır
        bitis = time.time()
        sure = (bitis - baslangic) * 1000
        print(f"⏱️ {fonksiyon.__name__} → {sure:.2f}ms")
        return sonuc
    return wrapper

# Kullanım — @ işareti ile uygula
@sure_olc
def agir_islem(n: int) -> int:
    """Ağır bir hesaplama simülasyonu"""
    toplam = 0
    for i in range(n):
        toplam += i
    return toplam

sonuc = agir_islem(1_000_000)
# -> ⏱️ agir_islem → 45.23ms
print(sonuc)
```

---

## 🔥 LangGraph'ta Decorator Kullanımı

LangGraph'ta node'ları `@graph.node` veya tool'ları `@tool` decorator ile tanımlarsın:

```python
from langchain_core.tools import tool
from typing import TypedDict
from langgraph.graph import StateGraph, END

# @tool decorator — bu fonksiyon bir LangGraph tool'u olur
@tool
def hava_durumu_sor(sehir: str) -> str:
    """Verilen şehir için hava durumunu döndürür."""
    # Gerçekte API çağrısı yapılır
    return f"{sehir} için hava: Güneşli, 22°C"

@tool
def hesap_makinesi(ifade: str) -> str:
    """Matematiksel işlem yapar."""
    try:
        sonuc = eval(ifade)  # Üretimde eval kullanma!
        return str(sonuc)
    except Exception as e:
        return f"Hata: {e}"

# Toolları kullan
print(hava_durumu_sor.invoke({"sehir": "İstanbul"}))
# -> İstanbul için hava: Güneşli, 22°C

print(hesap_makinesi.invoke({"ifade": "15 * 4 + 20"}))
# -> 80
```

---

## 🧩 functools.wraps — Decorator Yazmak

Kendi decorator'larını yazarken `functools.wraps` kullan — PHP'de `$this->next($request)` gibi "zinciri bozmadan geç":

```python
from functools import wraps
from typing import Callable, Any

def log_decorator(func: Callable) -> Callable:
    @wraps(func)  # Orijinal fonksiyonun adını ve docstring'ini koru
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        print(f"📞 {func.__name__} çağrıldı")
        print(f"   Args: {args}, Kwargs: {kwargs}")

        sonuc = func(*args, **kwargs)

        print(f"✅ {func.__name__} tamamlandı → {sonuc}")
        return sonuc
    return wrapper

def hata_yakala(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"❌ Hata: {e}")
            return None
    return wrapper

# Birden fazla decorator kullanabilirsin — üstten alta doğru uygulanır
@log_decorator
@hata_yakala
def bolme_yap(a: int, b: int) -> float:
    return a / b

bolme_yap(10, 2)   # -> 📞 bolme_yap çağrıldı ... ✅ 5.0
bolme_yap(10, 0)   # -> ❌ Hata: division by zero
```

---

## 🔄 Lambda — Kısa Anonim Fonksiyon

```python
# PHP: fn($x) => $x * 2
# Python:
iki_kat = lambda x: x * 2
print(iki_kat(5))   # -> 10

# LangGraph'ta routing için sıkça kullanılır:
# graph.add_conditional_edges("router", lambda state: state["next_agent"])

# List üzerinde lambda kullanımı
sayilar = [1, 2, 3, 4, 5]
kareler = list(map(lambda x: x ** 2, sayilar))
print(kareler)  # -> [1, 4, 9, 16, 25]
```

---

## 🔥 LangGraph Routing — Conditional Edge

Bu, LangGraph'ta en sık kullanacağın pattern:

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class AgentState(TypedDict):
    user_input: str
    next_agent: str

def router_node(state: AgentState) -> dict:
    """Kullanıcı inputuna göre yönlendir"""
    user_input = state["user_input"].lower()

    if any(word in user_input for word in ["hukuk", "kanun", "madde"]):
        next_agent = "law_agent"
    elif any(word in user_input for word in ["matematik", "hesap", "topla"]):
        next_agent = "math_agent"
    else:
        next_agent = "general_agent"

    return {"next_agent": next_agent}

def hangi_agent(state: AgentState) -> str:
    """Bu fonksiyon hangi node'a gidileceğini belirler"""
    return state["next_agent"]

# Graph kurulumu
graph = StateGraph(AgentState)
graph.add_node("router", router_node)
graph.set_entry_point("router")

# Conditional edge — Laravel Router gibi
graph.add_conditional_edges(
    "router",
    hangi_agent,       # Bu fonksiyon karar verir
    {
        "law_agent": END,      # Şimdilik END'e yönlendir
        "math_agent": END,
        "general_agent": END,
    }
)

app = graph.compile()
result = app.invoke({"user_input": "Kanun 5 nedir?", "next_agent": ""})
print(result["next_agent"])  # -> law_agent
```

---

## ⚠️ Sık Yapılan Hatalar

**Hata:** `TypeError: wrapper() takes 0 positional arguments but 1 was given`

```python
# YANLIŞ — *args, **kwargs eksik
def dekorator(func):
    def wrapper():           # Argüman almıyor!
        return func()
    return wrapper

# DOĞRU
def dekorator(func):
    def wrapper(*args, **kwargs):  # Her tür argümanı kabul et
        return func(*args, **kwargs)
    return wrapper
```

> 🔴 **Laravel analogisi:** PHP'de middleware `handle(Request $request, Closure $next)` imzası yanlışsa aynı şekilde crash eder.

---

## 🎯 Görev

Aşağıdaki iki decorator'ı yaz:

1. `@retry(max_deneme=3)` — Fonksiyon hata fırlatırsa 3 kez tekrar dene
2. `@validate_state` — `AgentState`'te `user_input` boşsa hata fırlat

<details>
<summary>💡 Çözümü göster</summary>

```python
from functools import wraps
from typing import TypedDict, Callable

class AgentState(TypedDict):
    user_input: str

def retry(max_deneme: int = 3):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            for deneme in range(max_deneme):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Deneme {deneme + 1}/{max_deneme} başarısız: {e}")
                    if deneme == max_deneme - 1:
                        raise
        return wrapper
    return decorator

def validate_state(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(state: AgentState, *args, **kwargs):
        if not state.get("user_input", "").strip():
            raise ValueError("user_input boş olamaz!")
        return func(state, *args, **kwargs)
    return wrapper

# Test
@retry(max_deneme=3)
@validate_state
def llm_cagir(state: AgentState) -> str:
    return f"LLM cevabı: {state['user_input']}"

# Çalışır
print(llm_cagir({"user_input": "Merhaba"}))

# Hata fırlatır
# print(llm_cagir({"user_input": ""}))  # ValueError!
```

</details>

---

**Önceki ders:** [Type Hints ←](./type-hints) | **Sonraki ders:** [Async / Await →](./async-await)
