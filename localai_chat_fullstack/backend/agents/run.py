import os
from typing import Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage

# Core Modules
from .core.state import AgentState
from .core.llm import llm, llm_qwen1
from .core.embedding_engine import text_to_vector

# Agents
from .agents.it_legal_rag_node import it_legal_rag_node
from .agents.main_router_agent import main_router_agent
from .agents.math_expert_node import math_expert_node
from .agents.legal_expert_node import legal_expert_node
from .agents.greeting_node import greeting_node
from .agents.vector_rag_node import vektor_rag_node
from .agents.support_rag_node import support_rag_node

def route_decision(state: AgentState) -> Literal["math", "legal", "greeting","vektor"]:
    return state["intent"]

workflow = StateGraph(AgentState)

workflow.add_node("main_agent", main_router_agent)
workflow.add_node("it_legal_expert", it_legal_rag_node)
workflow.add_node("math_expert", math_expert_node)
workflow.add_node("legal_expert", legal_expert_node)
workflow.add_node("greeting_expert", greeting_node)
workflow.add_node("vektor_rag_expert", vektor_rag_node)
workflow.add_node("support_rag_expert", support_rag_node)

workflow.set_entry_point("main_agent")

workflow.add_conditional_edges(
    "main_agent",
    route_decision,
    {
        "math": "math_expert",
        "it_legal": "it_legal_expert",
        "legal": "legal_expert",
        "greeting": "greeting_expert",
        "vektor": "vektor_rag_expert",
        "support": "support_rag_expert"
    }
)

workflow.add_edge("it_legal_expert", END)
workflow.add_edge("math_expert", END)
workflow.add_edge("legal_expert", END)
workflow.add_edge("greeting_expert", END)
workflow.add_edge("vektor_rag_expert", END)
workflow.add_edge("support_rag_expert", END)

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
        print(result)
        print(f"\n📂 [Departman: {result['intent'].upper()}]")
        print(f"🤖 Asistan: {result['final_answer']}")
        print("-" * 30)

if __name__ == "__main__":
    start_chat()