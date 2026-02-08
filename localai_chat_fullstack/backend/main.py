from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn
import asyncio
import json
from agents.run import app as agent_workflow

# FastAPI uygulaması
app = FastAPI(title="Simple LLM API", version="1.0.0")

# CORS ayarları (frontend ile iletişim için)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Geliştirme için tüm originlere izin ver
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ollama ile LLM kullanımı
LLM_LOADED = False
MODEL_NAME = "gemma3:4b"  # Ollama'da yüklü model adı

try:
    import ollama
    print(f"Ollama bağlantısı kontrol ediliyor...")
    print(f"Model: {MODEL_NAME}")
    
    # Ollama'nın çalıştığını kontrol et - basit bir test isteği gönder
    try:
        models_response = ollama.list()
        # models_response bir dict, içinde 'models' key'i var ve bu bir liste
        if 'models' in models_response:
            model_names = [m.get('name', m.get('model', '')) for m in models_response['models']]
            print(f"Mevcut modeller: {model_names}")
            
            # Model adını kontrol et (tam eşleşme veya :latest ile)
            if MODEL_NAME in model_names or f"{MODEL_NAME}:latest" in model_names:
                LLM_LOADED = True
                print(f"✅ Model '{MODEL_NAME}' hazır!")
            else:
                print(f"⚠️  Model '{MODEL_NAME}' bulunamadı.")
                print(f"📥 Yüklemek için: ollama pull {MODEL_NAME}")
        else:
            print("⚠️  Ollama çalışıyor ama model listesi alınamadı")
            
    except Exception as list_error:
        print(f"⚠️  Model listesi alınamadı: {list_error}")
        # Yine de modeli kullanmayı dene
        LLM_LOADED = True
        print(f"Model '{MODEL_NAME}' kullanılmaya çalışılacak...")
        
except Exception as e:
    print(f"❌ Ollama bağlantısı başarısız: {e}")
    print("Demo modunda çalışıyor...")
    print("Ollama'yı başlatmak için: ollama serve")

# Request modeli
class QuestionRequest(BaseModel):
    question: str
    max_length: int = 100

# Response modeli
class AnswerResponse(BaseModel):
    question: str
    answer: str
    model_loaded: bool

@app.get("/")
async def root():
    """API durumunu kontrol et"""
    return {
        "status": "running",
        "message": "LLM API çalışıyor",
        "model": MODEL_NAME if LLM_LOADED else "demo",
        "model_loaded": LLM_LOADED
    }

@app.post("/ask/stream")
async def ask_question_stream(request: QuestionRequest):
    """
    LLM'e soru sor ve cevabı chunk chunk gönder (streaming)
    
    Args:
        request: Soru ve maksimum cevap uzunluğu
    
    Returns:
        Server-Sent Events formatında streaming cevap
    """
    async def generate_response():
        try:
            if LLM_LOADED:
                # Agent workflow'u çalıştır (streaming değil, tek seferde sonuç döner)
                # invoke() senkron olduğu için thread pool'da çalıştırıyoruz
                result = await asyncio.to_thread(
                    agent_workflow.invoke, 
                    {"user_query": request.question, "intent": "", "final_answer": ""}
                )
                
                # Sonucu al
                answer = result.get('final_answer', 'Cevap bulunamadı.')
                
                # Cevabı kelime kelime stream et (gerçek streaming simülasyonu)
                words = answer.split()
                for i, word in enumerate(words):
                    chunk_data = {
                        "chunk": word + " ",
                        "done": i == len(words) - 1
                    }
                    yield f"data: {json.dumps(chunk_data)}\n\n"
                    await asyncio.sleep(0.05)  # Streaming efekti için küçük gecikme
                    
            else:
                # Demo cevap
                answer = f"{request.question}\n\nBu bir demo cevaptır. Ollama bağlantısı yok."
                
                # Cevabı kelime kelime gönder
                words = answer.split()
                for i, word in enumerate(words):
                    chunk_data = {
                        "chunk": word + " ",
                        "done": i == len(words) - 1
                    }
                    yield f"data: {json.dumps(chunk_data)}\n\n"
                    await asyncio.sleep(0.05)
            
            # Son chunk - işlem tamamlandı
            yield f"data: {json.dumps({'chunk': '', 'done': True})}\n\n"
            
        except Exception as e:
            error_data = {"error": str(e), "done": True}
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(
        generate_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@app.get("/health")
async def health_check():
    """Sağlık kontrolü"""
    return {
        "status": "healthy",
        "model_loaded": LLM_LOADED
    }

if __name__ == "__main__":
    # Sunucuyu başlat
    print("\n" + "="*60)
    print("🚀 LLM API Sunucusu Başlatılıyor...")
    print("="*60)
    print(f"📊 Model Durumu: {'Yüklü ✅' if LLM_LOADED else 'Demo Modu 🔧'}")
    print(f"🌐 URL: http://localhost:8000")
    print(f"📚 Docs: http://localhost:8000/docs")
    print("="*60 + "\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
