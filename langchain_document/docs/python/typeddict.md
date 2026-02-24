# Ders 1: TypedDict — LangGraph'ın Kalbi

> **Laravel karşılığı:** PHP'de `array` kullanırsın ama tip belirtmezsin. TypedDict, PHP'nin **typed array**'i gibi — hangi key hangi tipte olacak, önceden bildirirsin.

---

## 🤔 Neden TypedDict?

LangGraph'ta her şey bir **State** (durum) objesi içinde taşınır. Bu state, node'lar (fonksiyonlar) arasında dolaşır. TypedDict, bu state'i tanımlamak için kullanılır.

**PHP'de array:**

```php
// PHP - tip yok, güvenli değil
$state = [
    'messages' => [],
    'user_input' => 'Merhaba',
    'response' => '',
];

// Yanlış key yazdın mı? PHP sessizce null döner.
echo $state['mesagges']; // null — hata yok!
```

**Python'da TypedDict:**

```python
from typing import TypedDict

class AgentState(TypedDict):
    messages: list[str]
    user_input: str
    response: str

# Artık IDE seni uyarır, tip kontrolü çalışır
state: AgentState = {
    "messages": [],
    "user_input": "Merhaba",
    "response": "",
}
```

---

## 📦 Temel Kullanım

```python
from typing import TypedDict

# TypedDict bir class gibi tanımlanır
class KullaniciState(TypedDict):
    ad: str
    yas: int
    aktif: bool

# Kullanımı normal dict gibi
kullanici: KullaniciState = {
    "ad": "Ahmet",
    "yas": 30,
    "aktif": True,
}

# Key'e erişim
print(kullanici["ad"])    # -> Ahmet
print(kullanici["yas"])   # -> 30
```

---

## 🔥 LangGraph'ta Gerçek Kullanım

LangGraph'ta state şu şekilde tanımlanır:

```python
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

# Bu, gerçek bir LangGraph AgentState'i
class AgentState(TypedDict):
    # 'messages' geçmişi tutar — Annotated özel bir reducer ekler
    messages: Annotated[list, add_messages]
    # Kullanıcının son sorusunu tutar
    user_input: str
    # Hangi agent çalışacak?
    next_agent: str
    # Son cevap
    final_response: str

# Başlangıç state'i — PHP'de $initialState = [...] gibi
initial_state: AgentState = {
    "messages": [],
    "user_input": "Python nedir?",
    "next_agent": "general",
    "final_response": "",
}

print(initial_state["user_input"])  # -> Python nedir?
```

---

## 🧩 İç İçe TypedDict (Nested)

```python
from typing import TypedDict

class KullaniciBilgisi(TypedDict):
    ad: str
    email: str

class ChatState(TypedDict):
    kullanici: KullaniciBilgisi   # İç içe TypedDict
    mesajlar: list[str]
    oturum_id: str

state: ChatState = {
    "kullanici": {
        "ad": "Mehmet",
        "email": "mehmet@test.com"
    },
    "mesajlar": ["Merhaba", "Nasılsın?"],
    "oturum_id": "abc-123"
}

# İç içe erişim
print(state["kullanici"]["ad"])  # -> Mehmet
```

---

## ⚠️ Sık Yapılan Hatalar

**Hata:** `KeyError: 'mesages'`

```python
# YANLIŞ — yanlış key
print(state["mesages"])   # KeyError!

# DOĞRU
print(state["messages"])
```

> 🔴 **Laravel analogisi:** PHP'de `$state['mesages']` yazsan `null` döner sessizce. Python dict'te ise `KeyError` fırlar — bu aslında _daha iyi_, hatayı hemen görürsün.

**Hata:** `TypeError: str object cannot be interpreted as an integer`

```python
class State(TypedDict):
    sayi: int

state: State = {"sayi": "beş"}  # str verdik, int bekleniyor!
# TypedDict runtime'da seni DURDURMAZ! Sadece IDE uyarır.
# Gerçek tip zorlaması için: from pydantic import BaseModel kullan
```

> 💡 TypedDict tip kontrol sadece statik analizde (IDE, mypy) çalışır. Runtime'da normal dict gibi davranır.

---

## 🔄 State Güncelleme (Node İçinden)

Node'lar state'i **kopyalayarak** günceller — Laravel'deki `array_merge()` gibi:

```python
from typing import TypedDict

class AgentState(TypedDict):
    user_input: str
    response: str
    step_count: int

# Node fonksiyonu — state alır, güncellenmiş state döner
def my_node(state: AgentState) -> dict:
    # Sadece değişen key'leri döndür — LangGraph geri kalanını korur
    return {
        "response": f"Cevap: {state['user_input']}",
        "step_count": state["step_count"] + 1,
    }

# Test edelim
mevcut_state: AgentState = {
    "user_input": "Merhaba",
    "response": "",
    "step_count": 0,
}

yeni_degerler = my_node(mevcut_state)
print(yeni_degerler)
# -> {'response': 'Cevap: Merhaba', 'step_count': 1}
```

---

## 🎯 Görev

Aşağıdaki LangGraph senaryosu için `AgentState` TypedDict'ini yaz:

**Senaryo:** Bir hukuk danışmanlık botu yapıyorsun.

- Kullanıcının sorusu tutulacak
- Hangi hukuk alanı (`ceza`, `medeni`, `idare`) tespit edilecek
- Yanıt tutulacak
- Kaç kez sorgu yapıldığı sayılacak
- Konuşma geçmişi (mesaj listesi) tutulacak

<details>
<summary>💡 Çözümü göster</summary>

```python
from typing import TypedDict

class HukukAgentState(TypedDict):
    user_input: str           # Kullanıcının sorusu
    hukuk_alani: str          # "ceza" | "medeni" | "idare"
    yanit: str                # Agent'ın cevabı
    sorgu_sayisi: int         # Kaç kez sorgu yapıldı
    mesaj_gecmisi: list[str]  # Tüm konuşma

# Başlangıç değerleri
baslangic: HukukAgentState = {
    "user_input": "",
    "hukuk_alani": "",
    "yanit": "",
    "sorgu_sayisi": 0,
    "mesaj_gecmisi": [],
}
```

</details>

---

**Sonraki ders:** [Type Hints →](./type-hints)
