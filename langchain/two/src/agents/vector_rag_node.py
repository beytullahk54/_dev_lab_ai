from core.llm import llm
from core.state import AgentState
from core.embedding_engine import text_to_vector
from core.qdrant import query_points

def vektor_rag_node(state: AgentState):
    """Vektör RAG AJANI: Mesajı vektörde sorgular"""
    print("👋 Vektör Ajanı Çalışıyor...")
    array = query_points("test_collection_2", state['user_query']) 
    context = "\n".join(array)
    print(array)
    print(context)
    prompt = f"""
    SADECE aşağıdaki maddelere dayanarak cevap ver:
    {context}
    
    Soru: {state['user_query']}
    """

    response = llm.invoke(prompt)
    return {"final_answer": response.content}
