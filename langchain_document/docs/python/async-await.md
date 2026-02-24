# Ders 4: Async / Await

> **Laravel karşılığı:** Laravel Queue ile bir işi arka plana atarsın, cevabı beklemezsin. Python'da `async/await` ise **beklersin** ama aynı anda birden fazla işi sürdürürsün — Laravel'deki `Http::async()->get()` + `Promise` gibi.

---

## 🤔 Neden Async?

LLM API'leri (OpenAI, Anthropic) network çağrısıdır. Async ile bu çağrı yapılırken CPU boş kalmaz, başka işler çalışır.

```
Sync (normal):    [İstek 1] --- bekliyorum --- [cevap 1] [İstek 2] --- bekliyorum --- [cevap 2]
Async:            [İstek 1] [İstek 2]           [cevap 1] [cevap 2]
                  ↑ İkisi aynı anda gönderildi!
```

---

## 🔥 Temel Kullanım

```python
import asyncio

# async fonksiyon tanımı
async def selam_ver(ad: str) -> str:
    await asyncio.sleep(1)  # 1 saniye bekle (LLM çağrısı simülasyonu)
    return f"Merhaba, {ad}!"

# async fonksiyonu çalıştır
async def main():
    sonuc = await selam_ver("Ahmet")
    print(sonuc)  # -> Merhaba, Ahmet!

# asyncio.run() ile başlat — PHP'deki index.php gibi giriş noktası
asyncio.run(main())
```

---

## ⚡ Paralel Çalıştırma — asyncio.gather()

```python
import asyncio

async def llm_cagir(soru: str, model: str) -> str:
    """LLM çağrısı simülasyonu — farklı modeller farklı süre alır"""
    await asyncio.sleep(2)  # Network gecikmesi simülasyonu
    return f"[{model}] Cevap: {soru}"

async def main():
    # Sıralı — toplamda 4 saniye sürer
    # cevap1 = await llm_cagir("Soru 1", "gpt-4")
    # cevap2 = await llm_cagir("Soru 2", "claude")

    # Paralel — sadece 2 saniye sürer! (en yavaş kadar)
    cevap1, cevap2 = await asyncio.gather(
        llm_cagir("Python nedir?", "gpt-4"),
        llm_cagir("LangGraph nedir?", "claude"),
    )

    print(cevap1)  # -> [gpt-4] Cevap: Python nedir?
    print(cevap2)  # -> [claude] Cevap: LangGraph nedir?

asyncio.run(main())
```

---

## 🔥 LangGraph'ta Async Node

LangGraph node'ları async olabilir ve olmalı — çünkü LLM çağrıları async:

```python
import asyncio
from typing import TypedDict, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage

class AgentState(TypedDict):
    messages: List[dict]
    user_input: str
    response: str

# Async node — 'async def' ile tanımlanır
async def llm_node(state: AgentState) -> dict:
    """LLM'e sorar ve cevabı state'e yazar"""

    llm = ChatOpenAI(model="gpt-4", temperature=0.7)

    # await ile LLM çağrısı — cevap gelene kadar bekle
    response = await llm.ainvoke([
        HumanMessage(content=state["user_input"])
    ])

    return {"response": response.content}

# Test (API key olmadan simülasyon)
async def test_node():
    state: AgentState = {
        "messages": [],
        "user_input": "Python öğrenmek istiyorum",
        "response": "",
    }

    # Gerçekte LLM çağrısı yapılır
    # result = await llm_node(state)
    print("Async node çalışıyor...")

asyncio.run(test_node())
```

---

## 🧩 Async Context Manager — `async with`

```python
import asyncio
import aiohttp  # pip install aiohttp

async def api_cagir(url: str) -> dict:
    """HTTP isteği — requests yerine aiohttp kullan (async için)"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# Birden fazla API çağrısı paralel
async def coklu_api():
    urls = [
        "https://api.github.com/repos/langchain-ai/langgraph",
        "https://api.github.com/repos/langchain-ai/langchain",
    ]

    sonuclar = await asyncio.gather(
        *[api_cagir(url) for url in urls]
    )

    for sonuc in sonuclar:
        print(f"Repo: {sonuc.get('name', 'N/A')}, Stars: {sonuc.get('stargazers_count', 0)}")

# asyncio.run(coklu_api())  # İnternet bağlantısı gerekir
```

---

## 🔄 Async Generator — Streaming

LLM cevabı stream olarak almak için:

```python
import asyncio
from typing import AsyncGenerator

async def llm_stream(prompt: str) -> AsyncGenerator[str, None]:
    """LLM'den kelime kelime cevap al — streaming"""
    kelimeler = ["Python", " çok", " güçlü", " bir", " dil!"]
    for kelime in kelimeler:
        await asyncio.sleep(0.3)  # Stream gecikmesi simülasyonu
        yield kelime

async def streaming_ornek():
    async for parca in llm_stream("Python nedir?"):
        print(parca, end="", flush=True)  # Anlık yazdır
    print()  # Yeni satır

asyncio.run(streaming_ornek())
# -> Python çok güçlü bir dil! (kelime kelime gelir)
```

---

## 🔥 LangGraph Async Graph

```python
import asyncio
from typing import TypedDict
from langgraph.graph import StateGraph, END

class State(TypedDict):
    user_input: str
    step1_result: str
    step2_result: str

async def node_1(state: State) -> dict:
    await asyncio.sleep(0.1)  # LLM çağrısı simülasyonu
    return {"step1_result": f"İşlendi: {state['user_input']}"}

async def node_2(state: State) -> dict:
    await asyncio.sleep(0.1)
    return {"step2_result": f"Zenginleştirildi: {state['step1_result']}"}

# Graph kur
graph = StateGraph(State)
graph.add_node("node1", node_1)
graph.add_node("node2", node_2)
graph.set_entry_point("node1")
graph.add_edge("node1", "node2")
graph.add_edge("node2", END)

app = graph.compile()

# Async çalıştır
async def main():
    result = await app.ainvoke({   # ainvoke = async invoke
        "user_input": "Merhaba",
        "step1_result": "",
        "step2_result": "",
    })
    print(result["step2_result"])
    # -> Zenginleştirildi: İşlendi: Merhaba

asyncio.run(main())
```

---

## ⚠️ Sık Yapılan Hatalar

**Hata:** `RuntimeWarning: coroutine 'xyz' was never awaited`

```python
async def selam() -> str:
    return "Merhaba"

# YANLIŞ — await unutulmuş
# sonuc = selam()      # Coroutine object, string değil!

# DOĞRU
async def main():
    sonuc = await selam()   # await ile çağır
    print(sonuc)

asyncio.run(main())
```

> 🔴 **Laravel analogisi:** `dispatch(new MyJob())` yerine `new MyJob()` yazıp unutmak gibi — iş hiç çalışmaz.

**Hata:** `SyntaxError: 'await' outside async function`

```python
# YANLIŞ — normal fonksiyon içinde await kullanılamaz
def normal_fonksiyon():
    sonuc = await baska_async()  # SyntaxError!

# DOĞRU — async def kullan
async def async_fonksiyon():
    sonuc = await baska_async()  # OK
```

---

## 🎯 Görev

Aşağıdaki async LangGraph node'unu tamamla:

```python
import asyncio
from typing import TypedDict, List

class ChatState(TypedDict):
    user_input: str
    agent_responses: List[str]   # Birden fazla agent cevabı

# Bu fonksiyon 3 farklı "agent"ı (simulate) paralel çalıştırmalı
# ve cevaplarını agent_responses listesine eklemeli
async def paralel_agent_node(state: ChatState) -> dict:
    ???
```

<details>
<summary>💡 Çözümü göster</summary>

```python
import asyncio
from typing import TypedDict, List

class ChatState(TypedDict):
    user_input: str
    agent_responses: List[str]

async def agent_calistir(agent_adi: str, soru: str) -> str:
    """Tek bir agent'ı simüle et"""
    await asyncio.sleep(0.5)  # Her agent yarım saniye sürer
    return f"[{agent_adi}]: '{soru}' sorusuna cevabım hazır."

async def paralel_agent_node(state: ChatState) -> dict:
    # 3 agent'ı paralel çalıştır
    cevaplar = await asyncio.gather(
        agent_calistir("HukukAgent", state["user_input"]),
        agent_calistir("MatematikAgent", state["user_input"]),
        agent_calistir("GenelAgent", state["user_input"]),
    )

    return {"agent_responses": list(cevaplar)}

# Test
async def main():
    sonuc = await paralel_agent_node({
        "user_input": "Yardım lazım",
        "agent_responses": [],
    })
    for cevap in sonuc["agent_responses"]:
        print(cevap)

asyncio.run(main())
```

</details>

---

**Önceki ders:** [Fonksiyonlar & Decorator ←](./functions-decorator) | **Sonraki ders:** [Class Yapısı →](./class-yapisi)
