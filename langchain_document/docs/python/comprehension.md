# Ders 6: List & Dict Comprehension

> **Laravel karşılığı:** Laravel Collection'daki `->map()`, `->filter()`, `->pluck()` metodları. Python'da tek satırda aynı şeyi yaparsın.

---

## 🔥 List Comprehension

```python
# Laravel: collect([1,2,3,4,5])->map(fn($x) => $x * 2)->values()
# Python:
sayilar = [1, 2, 3, 4, 5]
iki_katlari = [x * 2 for x in sayilar]
print(iki_katlari)  # -> [2, 4, 6, 8, 10]

# Sadece çiftleri al — filter gibi
# Laravel: ->filter(fn($x) => $x % 2 === 0)
ciftler = [x for x in sayilar if x % 2 == 0]
print(ciftler)  # -> [2, 4]

# Map + Filter birlikte
# Çift sayıların karesini al
kareler = [x ** 2 for x in sayilar if x % 2 == 0]
print(kareler)  # -> [4, 16]

# String listesi dönüşümü
isimler = ["ahmet", "mehmet", "ali"]
buyuk_isimler = [isim.upper() for isim in isimler]
print(buyuk_isimler)  # -> ['AHMET', 'MEHMET', 'ALI']
```

---

## 🧩 Dict Comprehension

```python
# Laravel: collect($array)->mapWithKeys(fn($v, $k) => [$k => $v * 2])

fiyatlar = {"elma": 5, "armut": 8, "kiraz": 15}

# Tüm fiyatları %20 artır
yeni_fiyatlar = {urun: fiyat * 1.20 for urun, fiyat in fiyatlar.items()}
print(yeni_fiyatlar)
# -> {'elma': 6.0, 'armut': 9.6, 'kiraz': 18.0}

# Sadece pahalıları al (10 TL üzeri)
pahali_urunler = {
    urun: fiyat
    for urun, fiyat in fiyatlar.items()
    if fiyat > 10
}
print(pahali_urunler)  # -> {'kiraz': 15}

# List'ten dict oluştur
isimler = ["Ahmet", "Mehmet", "Ali"]
id_map = {isim: len(isim) for isim in isimler}  # isim → harf sayısı
print(id_map)  # -> {'Ahmet': 5, 'Mehmet': 6, 'Ali': 3}
```

---

## 🔥 LangGraph'ta Comprehension Kullanımı

LangGraph'ta mesaj geçmişini işlemek için çok kullanılır:

```python
from typing import TypedDict, List

class Mesaj(TypedDict):
    rol: str       # "user" veya "assistant"
    icerik: str
    token_sayisi: int

# Örnek mesaj listesi
mesajlar: List[Mesaj] = [
    {"rol": "user", "icerik": "Merhaba!", "token_sayisi": 10},
    {"rol": "assistant", "icerik": "Merhaba! Nasıl yardımcı olabilirim?", "token_sayisi": 30},
    {"rol": "user", "icerik": "Python nedir?", "token_sayisi": 15},
    {"rol": "assistant", "icerik": "Python güçlü bir dildir.", "token_sayisi": 25},
    {"rol": "user", "icerik": "Teşekkürler!", "token_sayisi": 8},
]

# 1. Sadece user mesajlarını al
# Laravel: ->filter(fn($m) => $m['rol'] === 'user')
user_mesajlari = [m for m in mesajlar if m["rol"] == "user"]
print(f"Kullanıcı mesaj sayısı: {len(user_mesajlari)}")  # -> 3

# 2. Tüm içerikleri çek
# Laravel: ->pluck('icerik')
icerikleri = [m["icerik"] for m in mesajlar]
print(icerikleri)

# 3. Total token sayısı
toplam_token = sum(m["token_sayisi"] for m in mesajlar)  # Generator expression
print(f"Toplam token: {toplam_token}")  # -> 88

# 4. LLM formatına dönüştür (LangChain için)
# LangChain şu formatı bekler: [{"role": "user", "content": "..."}]
llm_formati = [
    {"role": m["rol"], "content": m["icerik"]}
    for m in mesajlar
]
print(llm_formati[0])  # -> {'role': 'user', 'content': 'Merhaba!'}

# 5. Son N mesajı al ve formatla (context window yönetimi)
son_3_mesaj = [
    {"role": m["rol"], "content": m["icerik"]}
    for m in mesajlar[-3:]    # Slice ile son 3 eleman
]
print(f"Son 3 mesaj: {len(son_3_mesaj)}")  # -> 3
```

---

## 🧩 Nested (İç İçe) Comprehension

```python
# İç içe list düzleştirme
# Laravel: ->flatten()
parcali_liste = [[1, 2, 3], [4, 5], [6, 7, 8, 9]]
duz_liste = [item for alt_liste in parcali_liste for item in alt_liste]
print(duz_liste)  # -> [1, 2, 3, 4, 5, 6, 7, 8, 9]

# Tool sonuçlarını düzleştirme (LangGraph'ta sık kullanılır)
tool_sonuclari = [
    ["Hukuk bilgisi 1", "Hukuk bilgisi 2"],
    ["Genel bilgi 1"],
    ["Matematik sonucu 1", "Matematik sonucu 2", "Matematik sonucu 3"],
]
tum_sonuclar = [sonuc for agent_sonuclari in tool_sonuclari for sonuc in agent_sonuclari]
print(len(tum_sonuclar))  # -> 6
```

---

## 🔄 Set Comprehension — Tekrarsız Liste

```python
# Tekrar eden kelimeleri temizle
kelimeler = ["python", "java", "python", "go", "java", "rust"]
benzersiz = {kelime for kelime in kelimeler}  # { } → set
print(benzersiz)  # -> {'python', 'java', 'go', 'rust'} (sırasız)

# LangGraph'ta kullanım: aynı tool'u iki kez çağırmamak
kullanilan_toollar = {"search", "calculator", "search", "weather"}  # tekrar var
print(len(kullanilan_toollar))  # -> 3 (tekrarlar temizlendi)
```

---

## ⚡ Generator Expression — Hafızayı Koru

```python
# List comprehension tüm listeyi hafızaya alır
# Generator expression ihtiyaç oldukça hesaplar (lazy evaluation)

# PHP'deki Laravel lazy collection gibi
buyuk_veri = range(1_000_000)

# YAVAŞ — hepsini listeye yükler (1M eleman)
# toplam = sum([x * 2 for x in buyuk_veri])

# HIZLI — ihtiyaç oldukça üretir (generator)
toplam = sum(x * 2 for x in buyuk_veri)  # [ ] yerine ( )
print(toplam)  # -> 999999000000

# LangGraph'ta token sayısı hesaplama
mesajlar = [{"icerik": "abc", "token": 10}, {"icerik": "xyz", "token": 20}]
toplam_token = sum(m["token"] for m in mesajlar)
print(toplam_token)  # -> 30
```

---

## 🔥 Gerçek LangGraph Kullanımı

```python
from typing import TypedDict, List
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    messages: List[dict]
    user_input: str
    context: List[str]
    response: str

def context_filter_node(state: AgentState) -> dict:
    """
    RAG sonuçlarını filtrele ve formatla.
    PHP'de bu kadar kısa yazamazsın!
    """
    ham_sonuclar = [
        {"metin": "Python öğrenin", "skor": 0.95, "kaynak": "A"},
        {"metin": "JavaScript da güzel", "skor": 0.60, "kaynak": "B"},
        {"metin": "LangGraph powerful", "skor": 0.88, "kaynak": "C"},
        {"metin": "Eski içerik", "skor": 0.30, "kaynak": "D"},
    ]

    # 0.7 üzerindeki sonuçları al, metinlerini çek, formatlı yaz
    filtrelenmis_context = [
        f"[{r['kaynak']}] {r['metin']}"
        for r in ham_sonuclar
        if r["skor"] >= 0.7
    ]

    # -> ['[A] Python öğrenin', '[C] LangGraph powerful']
    return {"context": filtrelenmis_context}


def prompt_hazirla_node(state: AgentState) -> dict:
    """Context'i prompt'a ekle"""
    context_str = "\n".join(state["context"])

    son_mesajlar = [
        f"{m['rol']}: {m['icerik']}"
        for m in state["messages"][-5:]  # Son 5 mesaj
    ]
    gecmis_str = "\n".join(son_mesajlar)

    prompt = f"""Bağlam:
{context_str}

Geçmiş:
{gecmis_str}

Soru: {state['user_input']}
Cevap:"""

    return {"response": prompt}

# Test
state: AgentState = {
    "messages": [
        {"rol": "user", "icerik": "Merhaba"},
        {"rol": "assistant", "icerik": "Merhaba!"},
    ],
    "user_input": "Python nasıl öğrenilir?",
    "context": [],
    "response": "",
}

state.update(context_filter_node(state))
state.update(prompt_hazirla_node(state))
print(state["response"])
```

---

## ⚠️ Sık Yapılan Hatalar

**Hata:** `SyntaxError: invalid syntax`

```python
# YANLIŞ — dict ve list karıştırma
yanlis = {x * 2 for x in [1,2,3]}  # Bu SET, dict değil!

# DOĞRU — dict için key:value gerekli
dogru_dict = {x: x * 2 for x in [1, 2, 3]}
dogru_set = {x * 2 for x in [1, 2, 3]}
dogru_list = [x * 2 for x in [1, 2, 3]]
```

**Performans hatası:** Büyük veriyi liste olarak tutmak

```python
# YANLIŞ — 1M elemanlı liste hafızayı doldurur
buyuk_liste = [x ** 2 for x in range(1_000_000)]
toplam = sum(buyuk_liste)

# DOĞRU — generator kullan
toplam = sum(x ** 2 for x in range(1_000_000))
```

---

## 🎯 Görev

Aşağıdaki senaryoyu comprehension kullanarak tek satırda çöz:

```python
# LangGraph mesaj geçmişin var:
mesajlar = [
    {"rol": "user", "icerik": "Merhaba", "token": 5},
    {"rol": "assistant", "icerik": "Merhaba! Nasılsın?", "token": 20},
    {"rol": "user", "icerik": "Hukuk sorusu", "token": 10},
    {"rol": "assistant", "icerik": "Hukuki cevap burada", "token": 35},
    {"rol": "user", "icerik": "Teşekkürler", "token": 8},
]

# 1. Sadece "user" rolündeki mesajların içeriklerini listele
# 2. LLM formatına dönüştür: [{"role": ..., "content": ...}]
# 3. Toplam token sayısını hesapla (sadece assistant mesajları)

# YOUR CODE HERE
```

<details>
<summary>💡 Çözümü göster</summary>

```python
# 1. Kullanıcı mesaj içerikleri
kullanici_icerikleri = [m["icerik"] for m in mesajlar if m["rol"] == "user"]
print(kullanici_icerikleri)
# -> ['Merhaba', 'Hukuk sorusu', 'Teşekkürler']

# 2. LLM formatına dönüştür
llm_formati = [{"role": m["rol"], "content": m["icerik"]} for m in mesajlar]
print(llm_formati[0])
# -> {'role': 'user', 'content': 'Merhaba'}

# 3. Sadece assistant token sayısı
assistant_token = sum(m["token"] for m in mesajlar if m["rol"] == "assistant")
print(f"Assistant token: {assistant_token}")
# -> 55
```

</details>

---

**Önceki ders:** [Class Yapısı ←](./class-yapisi) | **Sonraki ders:** [Değişkenler & Tipler →](./degiskenler)
