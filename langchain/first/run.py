import os
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama  # OpenAI yerine Ollama kullanıyoruz

# --- 3. BİLİŞİM HUKUKU VERİ TABANI (RAG SİMÜLASYONU) ---
IT_LEGAL_DOCS = [
    "Madde 1: KVKK Madde 12 - Veri sorumlusu, kişisel verilerin güvenliğini sağlamak için gerekli teknik tedbirleri almak zorundadır.",
    "Madde 2: TCK Madde 243 - Bilişim sistemine yetkisiz giriş yapmanın cezası 1 yıla kadar hapistir.",
    "Madde 3: 5651 Sayılı Kanun - Yer sağlayıcılar, kullanıcı içeriklerini önceden denetlemekle yükümlü değildir."
]

# --- 1. STATE (HAFIZA) ---
class AgentState(TypedDict):
    user_query: str
    final_answer: str
    intent: str

# --- 2. MODEL TANIMI (QWEN3:8B) ---
# Bilgisayarında Ollama açık olmalı ve 'ollama pull qwen3:8b' yapmış olmalısın.
llm = ChatOllama(
    model="qwen3:4b",
    temperature=0,  # Router işlemleri için tutarlılık önemli
    num_predict=1024
)

# --- 3. NODE'LAR (AJANLAR) ---

def main_router_agent(state: AgentState):
    """RESEPSİYONİST: Soruyu Qwen3 ile analiz eder."""
    print(f"\n🤖 Qwen3 Router: İstek analiz ediliyor... ('{state['user_query']}')")
    
    system_prompt = """
    Sen bir yönlendirme asistanısın. Gelen soruyu analiz et ve şu 3 kategoriden birini seç:
    - "math": Matematiksel işlemler ve sayısal problemler.
    - 'it_legal': Bilişim hukuku, KVKK, siber suçlar, internet yasaları.
    - "legal": Hukuk, kanunlar ve sözleşmeler.
    - "greeting": Merhaba, nasılsın gibi günlük sohbetler.
    
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
    else: category = "greeting"
    
    print(f"🔀 Karar: {category.upper()}")
    return {"intent": category}

def it_legal_rag_node(state: AgentState):
    """RAG AJANI: Verilen 3 maddeye göre cevap verir."""
    print("🖥️  Bilişim Hukuku RAG Ajanı çalışıyor...")
    
    # Retrieval (Bilgi Getirme) aşaması: 3 maddeyi context olarak birleştiriyoruz
    context = "\n".join(IT_LEGAL_DOCS)
    
    prompt = f"""
    Sen bir Bilişim Hukuku uzmanısın. SADECE aşağıdaki maddelere dayanarak cevap ver:
    {context}
    
    Soru: {state['user_query']}
    """
    
    response = llm.invoke(prompt)
    return {"final_answer": response.content}

def math_expert_node(state: AgentState):
    print("🧮 Qwen3 Matematik Uzmanı çalışıyor...")
    response = llm.invoke(f"Bir matematik profesörü olarak çöz: {state['user_query']}")
    return {"final_answer": response.content}

def legal_expert_node(state: AgentState):
    print("⚖️  Qwen3 Hukuk Uzmanı çalışıyor...")
    response = llm.invoke(f"Bir avukat olarak Türk Hukukuna göre cevapla: {state['user_query']}")
    return {"final_answer": response.content}

def greeting_node(state: AgentState):
    print("👋 Qwen3 Karşılama Ekibi çalışıyor...")
    response = llm.invoke(f"Nazikçe selamla: {state['user_query']}")
    return {"final_answer": response.content}

# --- 4. GRAFİK VE YÖNLENDİRME MANTIĞI ---

def route_decision(state: AgentState) -> Literal["math", "legal", "greeting"]:
    return state["intent"]

workflow = StateGraph(AgentState)

workflow.add_node("main_agent", main_router_agent)
workflow.add_node("it_legal_expert", it_legal_rag_node) # Yeni RAG Node
workflow.add_node("math_expert", math_expert_node)
workflow.add_node("legal_expert", legal_expert_node)
workflow.add_node("greeting_expert", greeting_node)

workflow.set_entry_point("main_agent")

workflow.add_conditional_edges(
    "main_agent",
    route_decision,
    {
        "math": "math_expert",
        "it_legal": "it_legal_expert",
        "legal": "legal_expert",
        "greeting": "greeting_expert"
    }
)

workflow.add_edge("it_legal_expert", END)
workflow.add_edge("math_expert", END)
workflow.add_edge("legal_expert", END)
workflow.add_edge("greeting_expert", END)

app = workflow.compile()

# --- 5. ÇALIŞTIRMA ---
def start_chat():
    print("\n" + "="*50)
    print("🚀 Qwen3 Multi-Agent Sistemi Başlatıldı (2026)")
    print("🤖 Departmanlar: Matematik, Genel Hukuk, Bilişim Hukuku")
    print("💡 Çıkmak için 'exit' veya 'quit' yazabilirsin.")
    print("="*50)

    while True:
        user_input = input("\n👤 Siz: ")
        
        if user_input.lower() in ["exit", "quit", "çıkış"]:
            print("👋 Görüşmek üzere!")
            break

        # Ajanları çalıştır
        print("⏳ İşleniyor...")
        result = app.invoke({"user_query": user_input, "intent": "", "final_answer": ""})
        
        # Sonucu Estetik Bastır
        print(f"\n📂 [Departman: {result['intent'].upper()}]")
        print(f"🤖 Asistan: {result['final_answer']}")
        print("-" * 30)

if __name__ == "__main__":
    start_chat()