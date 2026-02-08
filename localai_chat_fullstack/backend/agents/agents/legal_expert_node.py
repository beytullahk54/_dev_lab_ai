from ..core.state import AgentState
from ..core.llm import llm_qwen1

def legal_expert_node(state: AgentState):
    print("⚖️  Qwen3 Hukuk Uzmanı çalışıyor...")
    response = llm_qwen1.invoke(f"Bir avukat olarak Türk Hukukuna göre cevapla: {state['user_query']}")
    return {"final_answer": response.content}
