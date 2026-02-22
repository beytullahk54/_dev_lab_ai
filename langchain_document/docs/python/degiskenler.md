# Ders 7: Değişkenler & Tipler

> **Laravel karşılığı:** Python'da `$` yok, tip bildirimi zorunlu değil ama önerilir. `None` = PHP'nin `null`'u, `True/False` = PHP'nin `true/false`'u (büyük harfle!).

---

## 🔥 Temel Değişkenler

```python
# PHP'de: $isim = "Ahmet"; $yas = 30;
# Python'da: ($ yok, ; yok)

isim = "Ahmet"       # str
yas = 30             # int
maas = 5500.50       # float
aktif = True         # bool (büyük T!) — PHP: true (küçük t)
bos = None           # None — PHP: null

# Aynı anda birden fazla atama
x, y, z = 1, 2, 3
print(x, y, z)  # -> 1 2 3

# Swap (değer değiştirme) — PHP'de temp değişken gerekir
a, b = 10, 20
a, b = b, a
print(a, b)  # -> 20 10
```

---

## 📦 String İşlemleri

```python
# F-String — PHP'deki "Merhaba {$isim}" gibi
isim = "Ahmet"
print(f"Merhaba, {isim}!")           # -> Merhaba, Ahmet!
print(f"Yas: {yas + 1}")             # -> Yas: 31 (hesaplama yapabilir)
print(f"Maas: {maas:.2f} TL")       # -> Maas: 5500.50 TL (format)

# Multiline string — PHP'deki heredoc gibi
sistem_prompt = """
Sen yardımcı bir AI asistanısın.
Her zaman Türkçe cevap ver.
Kısa ve öz ol.
""".strip()  # Başındaki/sonundaki boşlukları temizle

print(sistem_prompt)

# String metodları
metin = "  Merhaba, LangGraph!  "
print(metin.strip())          # -> Merhaba, LangGraph! (boşluk temizle)
print(metin.lower())          # -> merhaba, langgraph!
print(metin.upper())          # -> MERHABA, LANGGRAPH!
print(metin.replace(",", "")) # -> Merhaba LangGraph!
print("lang" in metin)        # -> True (PHP: str_contains())
print(metin.split(","))       # -> ['  Merhaba', ' LangGraph!  ']
```

---

## 🔢 Sayı İşlemleri

```python
# Normal bölme — PHP gibi
print(10 / 3)    # -> 3.3333...

# Tam sayı bölme — PHP: intdiv(10, 3)
print(10 // 3)   # -> 3

# Mod — PHP: 10 % 3
print(10 % 3)    # -> 1

# Üs alma — PHP: pow(2, 10)
print(2 ** 10)   # -> 1024

# Büyük sayılar için _ kullanabilirsin (okunabilirlik)
bir_milyon = 1_000_000
print(bir_milyon)  # -> 1000000

# Round, abs, min, max
print(round(3.7))          # -> 4
print(abs(-15))            # -> 15
print(min(3, 1, 4, 1, 5))  # -> 1
print(max(3, 1, 4, 1, 5))  # -> 5
```

---

## 📋 List — PHP Array (Sıralı)

```python
# PHP: $liste = ["a", "b", "c"];
liste = ["elma", "armut", "kiraz"]

# Erişim
print(liste[0])    # -> elma (0'dan başlar)
print(liste[-1])   # -> kiraz (sondan)

# Slice (dilim) — PHP: array_slice
print(liste[1:3])  # -> ['armut', 'kiraz'] (1 dahil, 3 hariç)
print(liste[:2])   # -> ['elma', 'armut'] (baştan 2)
print(liste[-2:])  # -> ['armut', 'kiraz'] (sondan 2)

# Ekleme, silme
liste.append("mango")          # Sona ekle — PHP: array_push
liste.insert(0, "üzüm")       # Başa ekle
liste.remove("armut")         # Değere göre sil
cikarilan = liste.pop()        # Sondan çıkar ve döndür
cikarilan = liste.pop(0)       # İndeksten çıkar

# Sıralama
sayilar = [3, 1, 4, 1, 5, 9]
print(sorted(sayilar))         # -> [1, 1, 3, 4, 5, 9] (orijinal bozulmaz)
sayilar.sort()                 # Orijinali sıralar (in-place)
sayilar.sort(reverse=True)     # Tersten sırala

# LangGraph mesaj geçmişi örneği:
mesajlar = []
mesajlar.append({"rol": "user", "icerik": "Merhaba"})
mesajlar.append({"rol": "assistant", "icerik": "Merhaba!"})
print(f"Toplam mesaj: {len(mesajlar)}")  # -> 2
```

---

## 🗂️ Dict — PHP Associative Array

```python
# PHP: $kullanici = ["ad" => "Ahmet", "yas" => 30];
kullanici = {
    "ad": "Ahmet",
    "yas": 30,
    "email": "ahmet@test.com",
}

# Erişim
print(kullanici["ad"])                         # -> Ahmet
print(kullanici.get("telefon", "Yok"))         # -> Yok (PHP: $arr['key'] ?? 'Yok')

# Güncelleme
kullanici["yas"] = 31
kullanici["sehir"] = "İstanbul"  # Yeni key ekle

# Silme
del kullanici["email"]          # PHP: unset($kullanici['email'])

# Döngü
for key, value in kullanici.items():
    print(f"{key}: {value}")

print(list(kullanici.keys()))    # -> ['ad', 'yas', 'sehir']
print(list(kullanici.values())) # -> ['Ahmet', 31, 'İstanbul']

# Birleştirme — PHP: array_merge
varsayilan = {"model": "gpt-4", "temperature": 0.7}
ozellestirilmis = {"temperature": 0.3, "max_tokens": 500}
birlesik = {**varsayilan, **ozellestirilmis}  # ** spread operator
print(birlesik)
# -> {'model': 'gpt-4', 'temperature': 0.3, 'max_tokens': 500}
```

---

## 🔀 Kontrol Akışı

```python
# IF - ELIF - ELSE (PHP'deki gibi ama : ve girinti var)
yas = 25

if yas < 18:
    print("Çocuk")
elif yas < 65:
    print("Yetişkin")  # -> Bu çalışır
else:
    print("Yaşlı")

# Tek satır ternary — PHP: $yas >= 18 ? "Yetişkin" : "Çocuk"
durum = "Yetişkin" if yas >= 18 else "Çocuk"
print(durum)  # -> Yetişkin

# FOR döngüsü — PHP: foreach
# Listeyi gez
meyveler = ["elma", "armut", "kiraz"]
for meyve in meyveler:
    print(meyve)

# Range ile — PHP: for ($i = 0; $i < 5; $i++)
for i in range(5):
    print(i)  # -> 0, 1, 2, 3, 4

for i in range(1, 6):
    print(i)  # -> 1, 2, 3, 4, 5

# Index ile gez — PHP: foreach($arr as $i => $val)
for index, meyve in enumerate(meyveler):
    print(f"{index}: {meyve}")

# Dict gez
ayarlar = {"model": "gpt-4", "temp": 0.7}
for key, value in ayarlar.items():
    print(f"{key} = {value}")

# WHILE — PHP gibi
sayac = 0
while sayac < 3:
    print(f"Deneme {sayac + 1}")
    sayac += 1
```

---

## 🎯 LangGraph İçin Önemli Pattern'ler

```python
from typing import TypedDict, Optional

class AgentState(TypedDict):
    user_input: str
    kategori: Optional[str]
    denemeler: int

def akilli_router(state: AgentState) -> dict:
    user_input = state["user_input"].lower().strip()

    # Anahtar kelime kontrolü
    hukuk_kelimeleri = ["kanun", "madde", "hukuk", "dava", "sözleşme"]
    matematik_kelimeleri = ["hesap", "topla", "çarp", "türev", "integral"]

    # any() — PHP'de: array_filter + count > 0 gibi
    if any(kelime in user_input for kelime in hukuk_kelimeleri):
        kategori = "hukuk"
    elif any(kelime in user_input for kelime in matematik_kelimeleri):
        kategori = "matematik"
    else:
        kategori = "genel"

    # Deneme sayısını artır
    yeni_deneme = state["denemeler"] + 1

    return {
        "kategori": kategori,
        "denemeler": yeni_deneme,
    }

# Test
state: AgentState = {
    "user_input": "İş kanunu 4. maddesi nedir?",
    "kategori": None,
    "denemeler": 0,
}

sonuc = akilli_router(state)
print(sonuc)  # -> {'kategori': 'hukuk', 'denemeler': 1}
```

---

## ⚠️ Sık Yapılan Hatalar

**Hata:** `IndentationError: unexpected indent`

```python
# YANLIŞ — Python'da girintileme kritik! (PHP'de { } vardı)
if True:
print("merhaba")  # IndentationError!

# DOĞRU — 4 boşluk (veya 1 tab) ile girintile
if True:
    print("merhaba")  # OK
```

> 🔴 **Laravel analogisi:** PHP'de `if (true) { }` — süslü parantez yerine Python girinti kullanır. Girintileme **sözdiziminin kendisi**.

**Hata:** `TypeError: 'NoneType' object is not subscriptable`

```python
# YANLIŞ
state = {"user": None}
print(state["user"]["ad"])  # TypeError! None'a erişilemiyor

# DOĞRU — None kontrolü
if state["user"] is not None:
    print(state["user"]["ad"])

# Ya da walrus operator (Python 3.8+)
if kullanici := state.get("user"):
    print(kullanici.get("ad", "anonim"))
```

---

## 🎯 Görev

Aşağıdaki fonksiyonu yaz:

```python
# Bir LangGraph node'u: mesaj geçmişini analiz et
# - Toplam mesaj sayısını döndür
# - User ve assistant mesajlarını ayrı say
# - En uzun mesajın içeriğini döndür
# - Ortalama mesaj uzunluğunu döndür

mesajlar = [
    {"rol": "user", "icerik": "Merhaba!"},
    {"rol": "assistant", "icerik": "Merhaba! Size nasıl yardımcı olabilirim?"},
    {"rol": "user", "icerik": "Python hakkında bilgi verir misin?"},
    {"rol": "assistant", "icerik": "Python, 1991'de Guido van Rossum tarafından geliştirilen güçlü bir programlama dilidir."},
]

def gecmis_analiz(mesajlar: list) -> dict:
    ???
```

<details>
<summary>💡 Çözümü göster</summary>

```python
def gecmis_analiz(mesajlar: list) -> dict:
    if not mesajlar:
        return {"toplam": 0, "user": 0, "assistant": 0}

    toplam = len(mesajlar)
    user_sayisi = len([m for m in mesajlar if m["rol"] == "user"])
    assistant_sayisi = toplam - user_sayisi

    en_uzun = max(mesajlar, key=lambda m: len(m["icerik"]))

    ortalama = sum(len(m["icerik"]) for m in mesajlar) / toplam

    return {
        "toplam_mesaj": toplam,
        "user_mesaj": user_sayisi,
        "assistant_mesaj": assistant_sayisi,
        "en_uzun_mesaj": en_uzun["icerik"][:50] + "...",  # İlk 50 karakter
        "ortalama_uzunluk": round(ortalama, 2),
    }

sonuc = gecmis_analiz(mesajlar)
for key, value in sonuc.items():
    print(f"{key}: {value}")
```

</details>

---

**Önceki ders:** [List & Dict Comprehension ←](./comprehension) | **Sonraki ders:** [Kütüphaneler & venv →](./kutuphaneler)
