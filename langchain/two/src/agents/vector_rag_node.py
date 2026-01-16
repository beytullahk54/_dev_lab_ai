from qdrant_client import QdrantClient
from core.llm import llm_qwen1

def vektor_rag_node(state: AgentState):
    """Vektör RAG AJANI: Mesajı vektörde sorgular"""
    print("👋 Vektör Ajanı Çalışıyor...")

    client = QdrantClient(url="http://localhost:6333")
    
    sorgu_vektoru = text_to_vector(state['user_query'])
    search_result = client.query_points(
        collection_name="test_collection_2",
        query=sorgu_vektoru,
        limit=50,
        score_threshold=0.70,
        with_payload=True
    ).points

    #print(search_result)

    temiz_liste = [point.payload.get("text", "") for point in search_result]
    context = "\n".join(temiz_liste)
    #print(temiz_liste)

    prompt = f"""
    SADECE aşağıdaki maddelere dayanarak cevap ver:
    {context}
    
    Soru: {state['user_query']}
    """

    response = llm_qwen1.invoke(prompt)
    return {"final_answer": response.content}
