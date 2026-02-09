from ..core.state import AgentState
from ..core.llm import llm
from langchain_core.messages import HumanMessage, SystemMessage

def main_router_agent(state: AgentState):
    """RESEPSİYONİST: Soruyu Qwen3 ile analiz eder."""
    print(f"\n🤖 Qwen3 Router: İstek analiz ediliyor... ('{state['user_query']}')")
    
    system_prompt = """
    Sen bir yönlendirme asistanısın. Gelen soruyu analiz et ve şu 3 kategoriden birini seç:
    - "math": Matematiksel işlemler ve sayısal problemler.
    - "support" : Yazılımsal destek talepleri ve sorunlar için buraya yönlendir
    - 'it_legal': Bilişim hukuku, KVKK, siber suçlar, internet yasaları.
    - "legal": Hukuk, kanunlar ve sözleşmeler.
    - "greeting": Merhaba, nasılsın gibi günlük sohbetler.
    - "vektor" : Şehir bilgileri için buraya yönlendir
    
    Sadece kategoriyi tek kelime olarak cevapla (örn: math).
    """
    
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=state['user_query'])
    ])
    
    category = response.content.strip().lower()
    # Bazı yerel modeller fazla açıklama yapabilir, sadece anahtar kelimeyi ayıklayalım:
    if "it_legal" in category: category = "it_legal"
    elif "math" in category: category = "math"
    elif "legal" in category: category = "legal"
    elif "vektor" in category: category = "vektor"
    elif "support" in category: category = "support"
    else: category = "greeting"
    
    print(f"🔀 Karar: {category.upper()}")
    return {"intent": category}
