from ..core.state import AgentState
from ..core.llm import llm_qwen1

def math_expert_node(state: AgentState):
    print("🧮 Qwen3 Matematik Uzmanı çalışıyor...")
    response = llm_qwen1.invoke(f"Bir matematik profesörü olarak çöz: {state['user_query']}")
    return {"final_answer": response.content}
