# Sınıf Geçme Ajanı

Bu örnekte **3 ders ajanının** ve **1 karar ajanının** birlikte çalıştığı bir sistemi sıfırdan inşa ediyoruz.

Kural basit:
> Matematik, Fizik ve Kimya derslerinin **her birinden en az 55** almak zorundasın.

---

## Mimari

```
         ┌──────────────────────────────────┐
         │            AgentState            │
         │  ogrenci_adi, mat, fiz, kim      │
         │  mat_sonuc, fiz_sonuc, kim_sonuc │
         │  final_karar, aciklama           │
         └──────────────────────────────────┘
                          │
              ┌───────────▼───────────┐
              │    matematik_agent    │
              │  Not >= 55 → "geçti" │
              └───────────┬───────────┘
                          │
              ┌───────────▼───────────┐
              │      fizik_agent      │
              │  Not >= 55 → "geçti" │
              └───────────┬───────────┘
                          │
              ┌───────────▼───────────┐
              │      kimya_agent      │
              │  Not >= 55 → "geçti" │
              └───────────┬───────────┘
                          │
              ┌───────────▼───────────┐
              │   karar_agent         │
              │  3 ders de geçti mi?  │
              └───────────┬───────────┘
                          │
           ┌──────────────┴──────────────┐
           │                             │
    ┌──────▼──────┐              ┌───────▼──────┐
    │  gecti_node │              │ kaldi_node   │
    │  Tebrikler! │              │ Eksik dersler│
    └──────┬──────┘              └───────┬──────┘
           │                             │
           └──────────────┬──────────────┘
                        [END]
```

---

## 1. AgentState Tanımı

```python
# state.py
from typing import TypedDict

class SinifState(TypedDict):
    ogrenci_adi: str   # Öğrencinin adı

    # Notlar (girdi)
    mat: int           # Matematik notu
    fiz: int           # Fizik notu
    kim: int           # Kimya notu

    # Ders sonuçları (her ajan doldurur)
    mat_sonuc: str     # "geçti" veya "kaldı"
    fiz_sonuc: str
    kim_sonuc: str

    # Final
    final_karar: str   # "geçti" veya "kaldı"
    aciklama: str      # Detaylı açıklama
```

---

## 2. Ders Ajanları

Her ders ajanı aynı mantıkla çalışır: notu oku, 55'e kıyasla, sonucu state'e yaz.

### Matematik Ajanı

```python
# agents/matematik_agent.py

def matematik_agent(state: SinifState) -> dict:
    not_degeri = state["mat"]
    sinir = 55

    if not_degeri >= sinir:
        sonuc = "geçti"
        mesaj = f"✅ Matematik: {not_degeri} — Geçti"
    else:
        sonuc = "kaldı"
        mesaj = f"❌ Matematik: {not_degeri} — Kaldı ({sinir - not_degeri} puan eksik)"

    print(mesaj)
    return {"mat_sonuc": sonuc}
```

### Fizik Ajanı

```python
# agents/fizik_agent.py

def fizik_agent(state: SinifState) -> dict:
    not_degeri = state["fiz"]
    sinir = 55

    if not_degeri >= sinir:
        sonuc = "geçti"
        mesaj = f"✅ Fizik: {not_degeri} — Geçti"
    else:
        sonuc = "kaldı"
        mesaj = f"❌ Fizik: {not_degeri} — Kaldı ({sinir - not_degeri} puan eksik)"

    print(mesaj)
    return {"fiz_sonuc": sonuc}
```

### Kimya Ajanı

```python
# agents/kimya_agent.py

def kimya_agent(state: SinifState) -> dict:
    not_degeri = state["kim"]
    sinir = 55

    if not_degeri >= sinir:
        sonuc = "geçti"
        mesaj = f"✅ Kimya: {not_degeri} — Geçti"
    else:
        sonuc = "kaldı"
        mesaj = f"❌ Kimya: {not_degeri} — Kaldı ({sinir - not_degeri} puan eksik)"

    print(mesaj)
    return {"kim_sonuc": sonuc}
```

::: tip DRY Prensibi
Üç ajanın kodu neredeyse aynı. Ortak bir fonksiyona sarmak istersen:

```python
def ders_degerlendirici(ders_adi: str, not_alani: str, sonuc_alani: str):
    def agent(state: SinifState) -> dict:
        not_degeri = state[not_alani]
        sonuc = "geçti" if not_degeri >= 55 else "kaldı"
        return {sonuc_alani: sonuc}
    return agent

matematik_agent = ders_degerlendirici("Matematik", "mat", "mat_sonuc")
fizik_agent     = ders_degerlendirici("Fizik", "fiz", "fiz_sonuc")
kimya_agent     = ders_degerlendirici("Kimya", "kim", "kim_sonuc")
```
:::

---

## 3. Karar Ajanı

```python
# agents/karar_agent.py

def karar_agent(state: SinifState) -> dict:
    sonuclar = {
        "Matematik": state["mat_sonuc"],
        "Fizik":     state["fiz_sonuc"],
        "Kimya":     state["kim_sonuc"],
    }

    kalan_dersler = [ders for ders, s in sonuclar.items() if s == "kaldı"]

    if not kalan_dersler:
        karar = "geçti"
        aciklama = (
            f"🎉 Tebrikler {state['ogrenci_adi']}! "
            f"Tüm derslerden geçmeyi başardın."
        )
    else:
        karar = "kaldı"
        aciklama = (
            f"😞 {state['ogrenci_adi']}, maalesef sınıfı geçemedin.\n"
            f"Kaldığın dersler: {', '.join(kalan_dersler)}\n"
            f"Bu derslerde 55'in altında not aldın."
        )

    return {
        "final_karar": karar,
        "aciklama": aciklama
    }
```

---

## 4. Sonuç Ajanları

```python
# agents/sonuc_agentlari.py

def gecti_node(state: SinifState) -> dict:
    print("\n" + "="*40)
    print("🏆 SINIF GEÇİLDİ!")
    print(f"   {state['aciklama']}")
    print(f"   Mat:{state['mat']}  Fiz:{state['fiz']}  Kim:{state['kim']}")
    print("="*40)
    return {}

def kaldi_node(state: SinifState) -> dict:
    print("\n" + "="*40)
    print("📚 SINIF GEÇİLEMEDİ")
    print(f"   {state['aciklama']}")
    print(f"   Mat:{state['mat']}  Fiz:{state['fiz']}  Kim:{state['kim']}")
    print("="*40)
    return {}
```

---

## 5. Yönlendirme Fonksiyonu

Karar ajanının state'e yazdığı `final_karar` değerine göre doğru sonuç node'una gider:

```python
from typing import Literal

def sinif_karar_rota(state: SinifState) -> Literal["geçti", "kaldı"]:
    return state["final_karar"]
```

---

## 6. Graf Kurulumu (run.py)

```python
# run.py
from langgraph.graph import StateGraph, END
from typing import Literal

from .state import SinifState
from .agents.matematik_agent import matematik_agent
from .agents.fizik_agent import fizik_agent
from .agents.kimya_agent import kimya_agent
from .agents.karar_agent import karar_agent
from .agents.sonuc_agentlari import gecti_node, kaldi_node

# Yönlendirici
def sinif_karar_rota(state: SinifState) -> Literal["geçti", "kaldı"]:
    return state["final_karar"]

# Graf
workflow = StateGraph(SinifState)

# Node'ları ekle
workflow.add_node("matematik",  matematik_agent)
workflow.add_node("fizik",      fizik_agent)
workflow.add_node("kimya",      kimya_agent)
workflow.add_node("karar",      karar_agent)
workflow.add_node("gecti_node", gecti_node)
workflow.add_node("kaldi_node", kaldi_node)

# Başlangıç → Matematik
workflow.set_entry_point("matematik")

# Sıralı akış: mat → fiz → kim → karar
workflow.add_edge("matematik", "fizik")
workflow.add_edge("fizik",     "kimya")
workflow.add_edge("kimya",     "karar")

# Karar → Koşullu dal
workflow.add_conditional_edges(
    "karar",
    sinif_karar_rota,
    {
        "geçti": "gecti_node",
        "kaldı": "kaldi_node",
    }
)

workflow.add_edge("gecti_node", END)
workflow.add_edge("kaldi_node", END)

app = workflow.compile()
```

---

## 7. Çalıştırma ve Test

### Temel Kullanım

```python
# Tüm derslerden geçen öğrenci
result = app.invoke({
    "ogrenci_adi": "Ahmet",
    "mat": 72,
    "fiz": 60,
    "kim": 88,
    "mat_sonuc": "",
    "fiz_sonuc": "",
    "kim_sonuc": "",
    "final_karar": "",
    "aciklama": ""
})
```

**Çıktı:**
```
✅ Matematik: 72 — Geçti
✅ Fizik: 60 — Geçti
✅ Kimya: 88 — Geçti

========================================
🏆 SINIF GEÇİLDİ!
   🎉 Tebrikler Ahmet! Tüm derslerden geçmeyi başardın.
   Mat:72  Fiz:60  Kim:88
========================================
```

---

```python
# Fizik ve Kimyadan kalan öğrenci
result = app.invoke({
    "ogrenci_adi": "Zeynep",
    "mat": 80,
    "fiz": 42,
    "kim": 30,
    ...
})
```

**Çıktı:**
```
✅ Matematik: 80 — Geçti
❌ Fizik: 42 — Kaldı (13 puan eksik)
❌ Kimya: 30 — Kaldı (25 puan eksik)

========================================
📚 SINIF GEÇİLEMEDİ
   Zeynep, maalesef sınıfı geçemedin.
   Kaldığın dersler: Fizik, Kimya
   Bu derslerde 55'in altında not aldın.
========================================
```

---

### Toplu Test

```python
ogrenciler = [
    {"ogrenci_adi": "Ahmet",   "mat": 72, "fiz": 60, "kim": 88},
    {"ogrenci_adi": "Zeynep",  "mat": 80, "fiz": 42, "kim": 30},
    {"ogrenci_adi": "Mehmet",  "mat": 55, "fiz": 55, "kim": 55},  # tam sınır
    {"ogrenci_adi": "Ayşe",    "mat": 40, "fiz": 40, "kim": 40},  # hepsi kaldı
]

bos_state = {"mat_sonuc": "", "fiz_sonuc": "", "kim_sonuc": "", "final_karar": "", "aciklama": ""}

for ogr in ogrenciler:
    result = app.invoke({**ogr, **bos_state})
    durum = "✅ GEÇTİ" if result["final_karar"] == "geçti" else "❌ KALDI"
    print(f"{ogr['ogrenci_adi']:10} → {durum}")
```

**Çıktı:**
```
Ahmet      → ✅ GEÇTİ
Zeynep     → ❌ KALDI
Mehmet     → ✅ GEÇTİ
Ayşe       → ❌ KALDI
```

---

## 8. Geliştirme Fikirleri

Bu sistemi daha da zenginleştirebilirsin:

| Fikir | Nasıl Yapılır? |
|-------|----------------|
| 4. ders eklemek | Yeni node + state alanı + `add_edge` zincire ekle |
| Not ortalaması hesapla | Karar node'unda `(mat+fiz+kim)/3` hesapla |
| Telafi sınavı hakkı | `final_karar`'a `"telafi"` ekle, yeni node/edge |
| LLM ile yorumlama | Karar node'unda LLM'e öğrenciye motivasyon mesajı yazdır |
| PDF raporu | `gecti_node` / `kaldi_node`'da PDF oluştur |

### LLM ile Kişisel Geri Bildirim

```python
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

llm = ChatOllama(model="qwen3:8b")

def gecti_node(state: SinifState) -> dict:
    response = llm.invoke([
        SystemMessage(content="Sen destekleyici bir öğretmensin."),
        HumanMessage(content=(
            f"{state['ogrenci_adi']} sınıfı geçti! "
            f"Matematik:{state['mat']}, Fizik:{state['fiz']}, Kimya:{state['kim']}. "
            f"Kısa bir tebrik ve gelecek yıl için motivasyon mesajı yaz."
        ))
    ])
    print(response.content)
    return {}
```

---

## Bu Örnekte Öğrendikleriniz

- ✅ **State'e birden fazla node'un veri yazması** — her ders ajanı kendi sonucunu kaydetti
- ✅ **Sıralı edge zinciri** — `mat → fiz → kim → karar`
- ✅ **Conditional edge** — karar node'u sonucuna göre `geçti` veya `kaldı` node'una dallama
- ✅ **Node'ları factory fonksiyonla üretmek** — DRY prensibi
- ✅ **Toplu test** — aynı grafı farklı inputlarla çalıştırma
