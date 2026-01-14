import os
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama  # OpenAI yerine Ollama kullanıyoruz

# --- 1. STATE (HAFIZA) ---
class AgentState(TypedDict):
    user_query: str
    final_answer: str
    intent: str

# --- 2. MODEL TANIMI (QWEN3:8B) ---
# Bilgisayarında Ollama açık olmalı ve 'ollama pull qwen3:8b' yapmış olmalısın.
llm = ChatOllama(
    model="gemma3:1b",
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
    if "math" in category: category = "math"
    elif "legal" in category: category = "legal"
    else: category = "greeting"
    
    print(f"🔀 Karar: {category.upper()}")
    return {"intent": category}

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
workflow.add_node("math_expert", math_expert_node)
workflow.add_node("legal_expert", legal_expert_node)
workflow.add_node("greeting_expert", greeting_node)

workflow.set_entry_point("main_agent")

workflow.add_conditional_edges(
    "main_agent",
    route_decision,
    {
        "math": "math_expert",
        "legal": "legal_expert",
        "greeting": "greeting_expert"
    }
)

workflow.add_edge("math_expert", END)
workflow.add_edge("legal_expert", END)
workflow.add_edge("greeting_expert", END)

app = workflow.compile()

# --- 5. ÇALIŞTIRMA ---
if __name__ == "__main__":
    soru = "Mirastaki saklı pay oranları nedir?"
    result = app.invoke({"user_query": soru, "intent": "", "final_answer": ""})
    print(f"\n📩 Qwen3 Yanıtı:\n{result['final_answer']}")