from core.state import AgentState
from core.llm import llm

def greeting_node(state: AgentState):
    print("👋 Qwen3 Karşılama Ekibi çalışıyor...")
    response = llm.invoke(f"Nazikçe selamla: {state['user_query']}")
    return {"final_answer": response.content}
