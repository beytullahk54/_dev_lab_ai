# Tüm Sistemi Çalıştırma

Projeyi farklı şekillerde çalıştırabilirsin: terminal chat döngüsü, API servisi veya tek seferlik invoke.

## Terminal Chat Döngüsü

`run.py`'daki `start_chat()` fonksiyonu:

```python
def start_chat():
    print("\n" + "="*50)
    print("🚀 Multi-Agent Sistemi Başlatıldı")
    print("💡 Çıkmak için 'exit' yaz")
    print("="*50)

    while True:
        user_input = input("\n👤 Siz: ")

        if user_input.lower() in ["exit", "quit", "çıkış"]:
            print("👋 Görüşmek üzere!")
            break

        result = app.invoke({
            "user_query": user_input,
            "intent": "",
            "final_answer": ""
        })

        print(f"\n📂 [Departman: {result['intent'].upper()}]")
        print(f"🤖 Asistan: {result['final_answer']}")
        print("-" * 30)

if __name__ == "__main__":
    start_chat()
```

Çalıştırma:

```bash
python -m agents.run
```

## Tek Seferlik Invoke

```python
from agents.run import app

result = app.invoke({
    "user_query": "Yazılım sözleşmesi nedir?",
    "intent": "",
    "final_answer": ""
})

print(result["intent"])       # it_legal
print(result["final_answer"]) # Detaylı yanıt...
```

## Streaming ile Çalıştırma

Yanıtı adım adım al — büyük yanıtlar için idealdir:

```python
for event in app.stream({
    "user_query": "Türev nedir?",
    "intent": "",
    "final_answer": ""
}):
    for node_name, node_output in event.items():
        if "final_answer" in node_output:
            print(f"[{node_name}]: {node_output['final_answer']}")
```

## Toplu İşlem

Birden fazla soruyu sırayla işle:

```python
questions = [
    "Merhaba!",
    "2 + 2 kaçtır?",
    "KVKK nedir?",
    "Kira artış oranı ne kadar olabilir?"
]

for q in questions:
    result = app.invoke({"user_query": q, "intent": "", "final_answer": ""})
    print(f"[{result['intent']:10}] {q[:40]}")
    print(f"           → {result['final_answer'][:80]}...\n")
```

## Olası Hatalar ve Çözümleri

### Ollama Bağlantı Hatası

```
ConnectionRefusedError: [Errno 61] Connection refused
```

Çözüm:
```bash
ollama serve
```

### Model Bulunamadı

```
Error: model 'qwen3:8b' not found
```

Çözüm:
```bash
ollama pull qwen3:8b
```

### Bilinmeyen Intent

Router beklenmedik bir değer döndürürse:
```
ValueError: 'unknown_intent' is not a valid node name
```

Çözüm: `route_decision`'a fallback ekle (bkz. [Yönlendirme Mantığı](/project/routing)).

## Performans İpuçları

- Router için **küçük model** kullan (`qwen2.5:1.5b`) — daha hızlı
- Uzman ajanlar için **büyük model** kullan — daha kaliteli
- RAG araması `k=3` yeterlidir, daha fazlası bağlamı karıştırır
- Ollama'da `num_predict` ile token limitini ayarla

## Sonraki Adım

[Conditional Edges (İleri Seviye) →](/advanced/conditional-edges)
