# Ders 5: Class Yapısı

> **Laravel karşılığı:** Python class = Laravel'deki **Eloquent Model** veya **Service Class**. `__init__` = Laravel'deki `__construct()`, `self` = Laravel'deki `$this`.

---

## 🔥 Temel Class

```python
# PHP:
# class Kullanici {
#     public function __construct(private string $ad, private int $yas) {}
#     public function selamla(): string { return "Merhaba, " . $this->ad; }
# }

# Python:
class Kullanici:
    def __init__(self, ad: str, yas: int):  # __construct gibi
        self.ad = ad      # $this->ad gibi
        self.yas = yas

    def selamla(self) -> str:    # Her method'a self gerekli!
        return f"Merhaba, {self.ad}"

    def __repr__(self) -> str:   # PHP'deki __toString() gibi
        return f"Kullanici(ad={self.ad}, yas={self.yas})"

# Kullanım
kullanici = Kullanici("Ahmet", 30)
print(kullanici.selamla())   # -> Merhaba, Ahmet
print(kullanici)             # -> Kullanici(ad=Ahmet, yas=30)
```

---

## 🧩 Class Özellikleri

```python
class AgentBase:
    # Class variable — tüm instance'lar paylaşır (PHP: public static $count)
    toplam_agent_sayisi: int = 0

    def __init__(self, ad: str, model: str = "gpt-4"):
        # Instance variable — her instance'a özel (PHP: $this->ad)
        self.ad = ad
        self.model = model
        self.aktif = True
        self._gizli = "bunu dışarı verme"  # _ ile "private" convention

        # Class variable'ı güncelle
        AgentBase.toplam_agent_sayisi += 1

    # Instance method — self ile çalışır
    def bilgi_ver(self) -> str:
        return f"Agent: {self.ad}, Model: {self.model}"

    # Class method — cls ile çalışır (PHP: public static function)
    @classmethod
    def toplam_goster(cls) -> str:
        return f"Toplam agent: {cls.toplam_agent_sayisi}"

    # Static method — ne self ne cls (PHP: pure static function)
    @staticmethod
    def gecerli_modeller() -> list:
        return ["gpt-4", "gpt-3.5-turbo", "claude-3"]

# Test
a1 = AgentBase("HukukAgent")
a2 = AgentBase("MatematikAgent", model="claude-3")

print(a1.bilgi_ver())          # -> Agent: HukukAgent, Model: gpt-4
print(AgentBase.toplam_goster())  # -> Toplam agent: 2
print(AgentBase.gecerli_modeller())  # -> ['gpt-4', 'gpt-3.5-turbo', 'claude-3']
```

---

## 🏗️ Kalıtım (Inheritance)

```python
# PHP: class LawAgent extends AgentBase

class AgentBase:
    def __init__(self, ad: str, model: str):
        self.ad = ad
        self.model = model

    def calistir(self, soru: str) -> str:
        raise NotImplementedError("Alt sınıf implement etmeli!")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(ad={self.ad})"


class HukukAgent(AgentBase):  # AgentBase'den miras al
    def __init__(self, model: str = "gpt-4"):
        super().__init__("HukukAgent", model)  # PHP: parent::__construct()
        self.uzmanlik_alanlari = ["ceza", "medeni", "idare"]

    def calistir(self, soru: str) -> str:
        # Override — parent'ın metodunu ezmek
        return f"[Hukuk] {soru} sorusunu inceliyorum..."


class MatematikAgent(AgentBase):
    def __init__(self, model: str = "gpt-4"):
        super().__init__("MatematikAgent", model)

    def calistir(self, soru: str) -> str:
        return f"[Matematik] {soru} hesaplıyorum..."


# Polimorfizm
agentler: list[AgentBase] = [
    HukukAgent(),
    MatematikAgent(model="claude-3"),
]

for agent in agentler:
    print(agent)                      # __repr__ çalışır
    print(agent.calistir("5+5=?"))    # Her agent kendi calistir()ını çalıştırır
```

---

## 🔥 LangGraph'ta Agent Class Yapısı

Büyük projelerde agent'ları class olarak organize edersin:

```python
import asyncio
from typing import TypedDict, List, Optional
from dataclasses import dataclass

# dataclass — TypedDict'e alternatif, method ekleyebilirsin
# PHP'deki DTO (Data Transfer Object) gibi
@dataclass
class AgentConfig:
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 1000
    sistem_prompt: str = "Sen yardımcı bir AI asistanısın."


class BaseAgent:
    """Tüm agent'ların temel sınıfı — Laravel'deki BaseController gibi"""

    def __init__(self, ad: str, config: Optional[AgentConfig] = None):
        self.ad = ad
        self.config = config or AgentConfig()
        self.calisti_mi = False

    async def calistir(self, state: dict) -> dict:
        """Alt sınıflar bunu implement etmeli — abstract method gibi"""
        raise NotImplementedError(f"{self.ad} için calistir() implement edilmeli!")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(ad={self.ad}, model={self.config.model})"


class HukukAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            ad="HukukAgent",
            config=AgentConfig(
                temperature=0.3,   # Hukuk için düşük temperature (deterministik)
                sistem_prompt="Sen uzman bir hukuk danışmanısın."
            )
        )

    async def calistir(self, state: dict) -> dict:
        """State'i al, LLM'e sor, state'i güncelle"""
        soru = state.get("user_input", "")

        # Gerçekte: await llm.ainvoke([HumanMessage(content=soru)])
        await asyncio.sleep(0.1)  # Simülasyon

        self.calisti_mi = True
        return {
            "response": f"[{self.ad}] '{soru}' sorusu için hukuki değerlendirme yapıldı.",
            "next_agent": "END"
        }


class GenelAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            ad="GenelAgent",
            config=AgentConfig(temperature=0.8)
        )

    async def calistir(self, state: dict) -> dict:
        soru = state.get("user_input", "")
        await asyncio.sleep(0.1)

        return {
            "response": f"[{self.ad}] Genel cevap: '{soru}'",
            "next_agent": "END"
        }


# Agent Registry — Laravel'deki Service Container gibi
class AgentRegistry:
    def __init__(self):
        self._agentler: dict[str, BaseAgent] = {}

    def kaydet(self, agent: BaseAgent) -> None:
        self._agentler[agent.ad] = agent
        print(f"✅ {agent} kaydedildi")

    def al(self, ad: str) -> Optional[BaseAgent]:
        return self._agentler.get(ad)

    def hepsini_listele(self) -> List[str]:
        return list(self._agentler.keys())


async def main():
    # Registry oluştur ve agent'ları kaydet
    registry = AgentRegistry()
    registry.kaydet(HukukAgent())
    registry.kaydet(GenelAgent())

    print(f"Kayıtlı agent'lar: {registry.hepsini_listele()}")

    # Bir agent'ı çalıştır
    hukuk = registry.al("HukukAgent")
    if hukuk:
        state = {"user_input": "İş kanunu nedir?"}
        sonuc = await hukuk.calistir(state)
        print(sonuc["response"])


asyncio.run(main())
```

---

## 🧩 Property Decorator

```python
class Agent:
    def __init__(self, ad: str):
        self._ad = ad          # _ad → gizli attribute
        self._aktif = False

    # PHP: public function getAd(): string
    @property
    def ad(self) -> str:
        return self._ad.upper()  # Her zaman büyük harfle döner

    # PHP: public function setAd(string $ad): void
    @ad.setter
    def ad(self, yeni_ad: str) -> None:
        if len(yeni_ad) < 3:
            raise ValueError("Agent adı en az 3 karakter olmalı!")
        self._ad = yeni_ad

    @property
    def aktif(self) -> bool:
        return self._aktif

    @aktif.setter
    def aktif(self, deger: bool) -> None:
        print(f"Agent {'aktif' if deger else 'pasif'} edildi")
        self._aktif = deger

agent = Agent("law")
print(agent.ad)        # -> LAW (büyük harf property)
agent.aktif = True     # -> Agent aktif edildi
print(agent.aktif)     # -> True
# agent.ad = "ab"      # ValueError! 3 karakterden az
```

---

## ⚠️ Sık Yapılan Hatalar

**Hata:** `TypeError: selamla() missing 1 required positional argument: 'self'`

```python
class Agent:
    def selamla(self):       # self zorunlu!
        return "Merhaba"

agent = Agent()

# YANLIŞ
# Agent.selamla()   # TypeError! self verilmedi

# DOĞRU
agent.selamla()    # Python otomatik self geçer
```

> 🔴 **Laravel analogisi:** PHP'de `$this` yazmayı unutmak gibi — `return name` yerine `return $this->name` yazman gerekiyor.

---

## 🎯 Görev

Bir `MemoryAgent` class'ı yaz:

- Konuşma geçmişini `list` olarak tutsun
- `mesaj_ekle(rol: str, icerik: str)` metodu olsun
- `gecmis_al()` son 10 mesajı dönsün
- `temizle()` geçmişi sıfırlasın
- `__len__` total mesaj sayısını dönsün

<details>
<summary>💡 Çözümü göster</summary>

```python
from typing import TypedDict

class Mesaj(TypedDict):
    rol: str
    icerik: str

class MemoryAgent:
    def __init__(self, max_gecmis: int = 100):
        self._gecmis: list[Mesaj] = []
        self.max_gecmis = max_gecmis

    def mesaj_ekle(self, rol: str, icerik: str) -> None:
        mesaj: Mesaj = {"rol": rol, "icerik": icerik}
        self._gecmis.append(mesaj)

        # Maksimum geçmişi aş → eskiyi sil
        if len(self._gecmis) > self.max_gecmis:
            self._gecmis.pop(0)

    def gecmis_al(self, son_n: int = 10) -> list[Mesaj]:
        return self._gecmis[-son_n:]

    def temizle(self) -> None:
        self._gecmis.clear()
        print("🗑️ Geçmiş temizlendi")

    def __len__(self) -> int:
        return len(self._gecmis)

    def __repr__(self) -> str:
        return f"MemoryAgent({len(self)} mesaj)"


# Test
memory = MemoryAgent()
memory.mesaj_ekle("user", "Merhaba!")
memory.mesaj_ekle("assistant", "Merhaba! Nasıl yardımcı olabilirim?")
memory.mesaj_ekle("user", "Python nedir?")

print(f"Toplam mesaj: {len(memory)}")  # -> 3
print(memory.gecmis_al(2))            # -> Son 2 mesaj
print(memory)                          # -> MemoryAgent(3 mesaj)
```

</details>

---

**Önceki ders:** [Async / Await ←](./async-await) | **Sonraki ders:** [List & Dict Comprehension →](./comprehension)
