import os
from ..core.llm import llm, llm_qwen1
from ..core.state import AgentState
from ..core.embedding_engine import text_to_vector
from ..core.qdrant import query_points

def support_rag_node(state: AgentState):
    """Support RAG AJANI: Destek sorularını önceki cevaplara göre müşteriyi bilgilendirir."""
    print("👋 Support Ajanı Çalışıyor...")
    array = query_points("test_collection_2", state['user_query']) 
    
    if not array:
        print("⚠️ Vektörde veri bulunamadı.")
        return {"final_answer": "Üzgünüm, veritabanımda bu konuyla ilgili bilgi bulamadım."}

    context = os.linesep.join(array)
    prompt = f"""
    Sen bir yazılım destek ajanısın.
    Aşağıdaki kurallara uyarsın
    1) Sen sana soru soran müşteriye önceki cevaplardan derleme yaparak çözümü verirsin.
    2) Cevaplarında müşteri ismi vermezsin.
    3) Firma özelinde bilgi vermezsin
    4) Müşterinin sorusuyla ilgili çözüm önerisinde bulunursun 
    5) Maximum 5 6 paragraftan oluşan cümleler oluşturursun
    6) Sadece aşağıda verilen içeriğe bağlı kalırsın. Soru Konu alanındaki soruyu buna göre yanıtlarsın
    
    İçerik
    ---
    {context}

    Soru/Konu: {state['user_query']}
    """

    response = llm_qwen1.invoke(prompt)
    return {"final_answer": response.content}
