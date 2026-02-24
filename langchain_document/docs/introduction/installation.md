# Kurulum

## Gereksinimler

- Python 3.10+
- Node.js 18+ (VitePress için)
- Ollama (yerel LLM çalıştırmak için)

## Python Paketleri

```bash
pip install langgraph langchain langchain-core langchain-ollama langchain-community
```

Vektör veritabanı için:

```bash
pip install chromadb  # veya faiss-cpu
```

Tüm bağımlılıkları `requirements.txt` ile yüklemek için:

```txt
# requirements.txt
langgraph>=0.2.0
langchain>=0.3.0
langchain-core>=0.3.0
langchain-ollama>=0.2.0
langchain-community>=0.3.0
chromadb>=0.5.0
```

```bash
pip install -r requirements.txt
```

## Proje Yapısı

Projenizin dizin yapısı:

```
backend/
└── agents/
    ├── __init__.py
    ├── run.py                    # ← Graf tanımı ve çalıştırma
    ├── core/
    │   ├── state.py              # ← AgentState tanımı
    │   ├── llm.py                # ← LLM bağlantısı
    │   └── embedding_engine.py   # ← Embedding fonksiyonu
    └── agents/
        ├── main_router_agent.py  # ← Ana yönlendirici
        ├── math_expert_node.py
        ├── legal_expert_node.py
        ├── it_legal_rag_node.py
        ├── greeting_node.py
        ├── vector_rag_node.py
        └── support_rag_node.py
```

## Ollama ile Yerel LLM

```bash
# Ollama kur (macOS)
brew install ollama

# Modeli indir
ollama pull qwen3:8b

# Servisi başlat
ollama serve
```

Ollama varsayılan olarak `http://localhost:11434` adresinde çalışır.

## Paket Versiyonlarını Doğrula

```python
import langchain
import langgraph

print(langchain.__version__)   # 0.3.x
print(langgraph.__version__)   # 0.2.x
```

## Sonraki Adım

[State (Durum) Yönetimi →](/core/state)
