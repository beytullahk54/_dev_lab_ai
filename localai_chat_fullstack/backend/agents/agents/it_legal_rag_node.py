from ..core.state import AgentState
from ..core.llm import llm

# --- 3. BİLİŞİM HUKUKU VERİ TABANI (RAG SİMÜLASYONU) ---
IT_LEGAL_DOCS = [
    "Madde 1: KVKK Madde 12 - Veri sorumlusu, kişisel verilerin güvenliğini sağlamak için gerekli teknik tedbirleri almak zorundadır.",
    "Madde 2: TCK Madde 243 - Bilişim sistemine yetkisiz giriş yapmanın cezası 1 yıla kadar hapistir.",
    "Madde 3: 5651 Sayılı Kanun - Yer sağlayıcılar, kullanıcı içeriklerini önceden denetlemekle yükümlü değildir."
]

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
