# Ders 8: Kütüphaneler & venv

> **Laravel karşılığı:**  
> `venv` = `vendor/` klasörü ve `composer.json`  
> `pip` = `composer`  
> `requirements.txt` = `composer.json`  
> `.env` = `.env`

---

## 🗂️ Proje Yapısı

```
langgraph-proje/
│
├── venv/                    ← vendor/ gibi — git'e commit etme!
│   └── lib/
│
├── .env                     ← API anahtarları (composer.json'daki gibi gizli)
├── .gitignore               ← venv/ ve .env buraya
├── requirements.txt         ← composer.json gibi — bağımlılıklar
│
├── src/
│   ├── agents/
│   │   ├── __init__.py      ← PHP'deki namespace tanımı gibi
│   │   ├── law_agent.py
│   │   └── general_agent.py
│   ├── state.py             ← AgentState TypedDict
│   └── graph.py             ← LangGraph graph kurulumu
│
└── main.py                  ← index.php gibi giriş noktası
```

---

## ⚙️ venv Kurulumu

```bash
# 1. Proje klasörü oluştur
mkdir langgraph-proje
cd langgraph-proje

# 2. Virtual environment oluştur — vendor/ gibi izole
python -m venv venv

# 3. Aktif et (Mac/Linux)
source venv/bin/activate

# Aktif et (Windows)
# venv\Scripts\activate

# 4. Shell değişir → (venv) görünür:
# (venv) kullanici@makine:~/langgraph-proje$

# 5. Deaktif et
deactivate
```

---

## 📦 pip — Paket Yöneticisi

```bash
# Paket kur — composer require gibi
pip install langchain-openai
pip install langgraph
pip install python-dotenv

# Birden fazla
pip install langchain langgraph openai anthropic chromadb

# Belirli sürüm
pip install langchain==0.3.0

# Kaldır
pip uninstall langchain

# Kurulu paketleri listele
pip list

# requirements.txt'e kaydet — composer.lock gibi
pip freeze > requirements.txt

# requirements.txt'den kur — composer install gibi
pip install -r requirements.txt
```

---

## 📄 requirements.txt

```txt
# requirements.txt — composer.json gibi
langchain>=0.3.0
langchain-openai>=0.2.0
langgraph>=0.2.0
langchain-community>=0.3.0
python-dotenv>=1.0.0
chromadb>=0.5.0
pydantic>=2.0.0
asyncio
```

---

## 🔐 .env Dosyası

```bash
# .env — Laravel .env ile birebir aynı mantık
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx
LANGCHAIN_API_KEY=ls__xxxxxxxxxxxx
LANGCHAIN_TRACING_V2=true

# Database
CHROMA_HOST=localhost
CHROMA_PORT=8000
```

```python
# .env'i Python'da kullan
from dotenv import load_dotenv
import os

load_dotenv()  # .env dosyasını yükle

api_key = os.getenv("OPENAI_API_KEY")
print(api_key)  # -> sk-xxxxxxxx

# Varsayılan değerle
model = os.getenv("LLM_MODEL", "gpt-4")  # .env yoksa gpt-4 kullan
```

---

## 🔥 LangGraph için Temel Kütüphaneler

### 1. LangChain Core

```python
# pip install langchain-core
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

# Mesaj tipleri — LangGraph'ta çok kullanılır
sistem = SystemMessage(content="Sen yardımcı bir AI'sın")
kullanici = HumanMessage(content="Merhaba!")
asistan = AIMessage(content="Merhaba! Nasıl yardımcı olabilirim?")

mesajlar = [sistem, kullanici, asistan]
print(mesajlar[0].content)  # -> Sen yardımcı bir AI'sın

# Prompt Template — Laravel blade gibi
prompt = ChatPromptTemplate.from_messages([
    ("system", "Sen {uzmanlık} konusunda uzmansın"),
    ("human", "{soru}"),
])

doldurulmus = prompt.format_messages(
    uzmanlık="hukuk",
    soru="İş kanunu nedir?"
)
print(doldurulmus[0].content)
```

### 2. LangGraph

```python
# pip install langgraph
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

# StateGraph — yönlendirme motoru
# END — son nokta (graph biter)
# add_messages — mesaj listesine ekleme reducer'ı
# ToolNode — tool çağrıları için hazır node
```

### 3. LLM Bağlantıları

```python
# OpenAI
# pip install langchain-openai
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.7,
    max_tokens=1000,
)

# Anthropic
# pip install langchain-anthropic
from langchain_anthropic import ChatAnthropic

claude = ChatAnthropic(model="claude-3-5-sonnet-20241022")

# Ollama (yerel model)
# pip install langchain-ollama
from langchain_ollama import ChatOllama

ollama = ChatOllama(model="qwen2.5:7b")  # Yerel, ücretsiz
```

### 4. Vector Store (RAG için)

```python
# ChromaDB
# pip install chromadb langchain-chroma
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma(
    collection_name="belgeler",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)
```

### 5. Pydantic — Veri Validasyonu

```python
# pip install pydantic
from pydantic import BaseModel, Field

# TypedDict'in güçlü versiyonu — runtime validasyon yapabilir
class AgentConfig(BaseModel):
    model: str = Field(default="gpt-4", description="LLM model adı")
    temperature: float = Field(default=0.7, ge=0, le=1)  # 0-1 arası olmalı
    max_tokens: int = Field(default=1000, gt=0)

# Kullanım
config = AgentConfig(model="claude-3", temperature=0.3)
print(config.model)          # -> claude-3
print(config.model_dump())   # -> {'model': 'claude-3', 'temperature': 0.3, 'max_tokens': 1000}

# Config yanlışsa hata fırlatır
try:
    yanlis = AgentConfig(temperature=2.0)  # 0-1 arası değil!
except Exception as e:
    print(f"Validasyon hatası: {e}")
```

---

## 🧩 `__init__.py` — Namespace Yönetimi

```python
# src/agents/__init__.py
# Bu dosya klasörü "Python package" yapar
# PHP'deki namespace tanımı gibi düşün

from .law_agent import HukukAgent
from .general_agent import GenelAgent

# Artık dışarıdan şöyle import edebilirsin:
# from src.agents import HukukAgent, GenelAgent
```

```python
# src/agents/law_agent.py
class HukukAgent:
    def __init__(self):
        self.ad = "HukukAgent"
```

```python
# main.py
from src.agents import HukukAgent   # __init__.py sayesinde

agent = HukukAgent()
```

---

## 🔥 Tam Proje Başlangıcı

```bash
# 1. Klasör ve venv
mkdir benim-agent-projem
cd benim-agent-projem
python -m venv venv
source venv/bin/activate

# 2. Paketleri kur
pip install langgraph langchain-openai langchain-anthropic python-dotenv langchain-ollama

# 3. requirements.txt oluştur
pip freeze > requirements.txt

# 4. Klasör yapısını oluştur
mkdir -p src/agents src/tools src/state
touch .env .gitignore main.py
touch src/__init__.py src/agents/__init__.py
```

```bash
# .gitignore
venv/
.env
__pycache__/
*.pyc
.DS_Store
chroma_db/
```

```python
# main.py — başlangıç noktası
import asyncio
from dotenv import load_dotenv

load_dotenv()  # .env yükle

async def main():
    print("🚀 LangGraph Agent başlatılıyor...")
    # Buraya graph.invoke() gelecek

if __name__ == "__main__":
    asyncio.run(main())
```

```bash
# Çalıştır
python main.py
```

---

## ⚠️ Sık Yapılan Hatalar

**Hata:** `ModuleNotFoundError: No module named 'langchain'`

```bash
# venv aktif değil! Önce aktif et:
source venv/bin/activate   # Mac/Linux
# veya
venv\Scripts\activate      # Windows

# Sonra kur
pip install langchain
```

> 🔴 **Laravel analogisi:** `composer install` yapmadan `require 'vendor/autoload.php'` çağırmak gibi.

**Hata:** `ImportError: cannot import name 'xyz' from 'langchain'`

```bash
# Versiyon uyumsuzluğu — requirements.txt güncelle
pip install --upgrade langchain langchain-openai langgraph
```

---

## 🎯 Görev

Boş bir LangGraph projesi kur:

1. `langgraph-odev/` klasörü oluştur
2. venv kur ve aktif et
3. `langgraph`, `langchain-openai`, `python-dotenv` kur
4. `requirements.txt` oluştur
5. `.env` dosyasına `LLM_MODEL=gpt-4` yaz
6. `main.py`'de `.env`'i oku ve `LLM_MODEL` değişkenini yazdır

<details>
<summary>💡 Çözümü göster</summary>

```bash
# Terminal komutları
mkdir langgraph-odev && cd langgraph-odev
python -m venv venv
source venv/bin/activate
pip install langgraph langchain-openai python-dotenv
pip freeze > requirements.txt
echo "LLM_MODEL=gpt-4" > .env
```

```python
# main.py
from dotenv import load_dotenv
import os

load_dotenv()

model = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
print(f"Kullanılacak model: {model}")
# -> Kullanılacak model: gpt-4
```

```bash
python main.py
```

</details>

---

**Önceki ders:** [Değişkenler & Tipler ←](./degiskenler) | **Ana Sayfa:** [Python Eğitimi →](./index)

---

## 🎯 Öğrenme Tamamlandı!

Tüm dersleri bitirdin. Şimdi LangGraph ile yapabileceklerin:

```
✅ TypedDict ile AgentState tanımla
✅ Type hints ile güvenli kod yaz
✅ @tool decorator ile tool oluştur
✅ async/await ile LLM çağrısı yap
✅ Class ile Agent sınıfları oluştur
✅ Comprehension ile mesajları filtrele
✅ venv + pip ile proje kur
```

**Sıradaki adım:** [LangGraph Temel Kavramlar →](/core/state)
