import os
from ..core.llm import llm, llm_qwen1
from ..core.state import AgentState
from ..core.embedding_engine import text_to_vector
from ..core.qdrant import query_points

def vektor_rag_node(state: AgentState):
    """Vektör RAG AJANI: Mesajı vektörde sorgular"""
    print("👋 Vektör Ajanı Çalışıyor...")
    array = query_points("test_collection_2", state['user_query']) 
    
    if not array:
        print("⚠️ Vektörde veri bulunamadı.")
        return {"final_answer": "Üzgünüm, veritabanımda bu konuyla ilgili bilgi bulamadım."}

    context = os.linesep.join(array)
    prompt = f"""
    SADECE aşağıdaki maddelere dayanarak, sorulan soruya cevap ver veya konuyu özetle:
    {context}

    Soru/Konu: {state['user_query']}
    """

    response = llm_qwen1.invoke(prompt)
    return {"final_answer": response.content}
