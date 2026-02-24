"""
FastAPI Endpoint - Groq AI Dosya Oluşturucu Agent
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from agent import FileCreatorAgent
from schema_agent import SchemaGeneratorAgent
import os

# FastAPI uygulaması
app = FastAPI(
    title="Groq AI Agent API",
    description="Langchain ve Groq API kullanarak dosya oluşturan ve şema üreten AI agent",
    version="2.0.0"
)

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request modeli
class FileRequest(BaseModel):
    prompt: str
    directory: Optional[str] = "output"

# Response modeli
class FileResponse(BaseModel):
    success: bool
    message: str
    filename: Optional[str] = None
    filepath: Optional[str] = None

# Agent instances (singleton)
agent_instance = None
schema_agent_instance = None

def get_agent():
    """File creator agent instance'ını al (lazy loading)"""
    global agent_instance
    if agent_instance is None:
        try:
            agent_instance = FileCreatorAgent()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Agent başlatılamadı: {str(e)}")
    return agent_instance

def get_schema_agent():
    """Schema generator agent instance'ını al (lazy loading)"""
    global schema_agent_instance
    if schema_agent_instance is None:
        try:
            schema_agent_instance = SchemaGeneratorAgent()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Schema agent başlatılamadı: {str(e)}")
    return schema_agent_instance


@app.get("/")
async def root():
    """API ana endpoint"""
    return {
        "message": "🤖 Groq AI Agent API",
        "version": "2.0.0",
        "endpoints": {
            "GET /create-file": "Dosya oluştur",
            "GET /generate-schema": "Tablo şeması oluştur",
            "POST /chat": "Chat",
            "GET /health": "Sağlık kontrolü",
            "GET /docs": "API dokümantasyonu"
        }
    }


@app.get("/health")
async def health_check():
    """Sağlık kontrolü endpoint"""
    try:
        # API key kontrolü
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return {
                "status": "unhealthy",
                "message": "GROQ_API_KEY bulunamadı"
            }
        
        return {
            "status": "healthy",
            "message": "API çalışıyor",
            "groq_api_configured": True
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": str(e)
        }


@app.get("/create-file", response_model=FileResponse)
async def create_file(prompt: str, directory: str = "output"):
    """
    Dosya oluşturma endpoint (GET metodu)
    
    Args:
        prompt: str - Dosya oluşturma talimatı (query parameter)
        directory: str - Dosyanın kaydedileceği klasör (opsiyonel, varsayılan: "output")
        
    Returns:
        FileResponse - Başarı durumu ve dosya bilgileri
        
    Example:
        GET /create-file?prompt=Bir TODO listesi oluştur&directory=output
        GET /create-file?prompt=Python notlarımı kaydet
    """
    try:
        # Agent'ı al
        agent = get_agent()
        
        # Dosyayı oluştur
        result = agent.run(prompt)
        
        # Sonucu parse et
        if "✅" in result:
            # Başarılı
            # Dosya yolunu çıkar
            if "oluşturuldu:" in result:
                filepath = result.split("oluşturuldu:")[-1].strip()
                filename = os.path.basename(filepath)
            else:
                filepath = None
                filename = None
            
            return FileResponse(
                success=True,
                message=result,
                filename=filename,
                filepath=filepath
            )
        else:
            # Hata
            return FileResponse(
                success=False,
                message=result
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dosya oluşturulurken hata: {str(e)}")


@app.post("/chat")
async def chat(request: FileRequest):
    """
    Basit chat endpoint - dosya oluşturmadan sadece yanıt ver
    
    Args:
        request: FileRequest - prompt
        
    Returns:
        dict - Agent yanıtı
    """
    try:
        agent = get_agent()
        result = agent.run(request.prompt)
        
        return {
            "prompt": request.prompt,
            "response": result
        }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat hatası: {str(e)}")


@app.get("/generate-schema")
async def generate_schema(description: str):
    """
    Tablo şeması oluşturma endpoint
    
    Args:
        description: str - Tablo açıklaması (örn: "Ürün tablosu", "Kullanıcı yönetimi")
        
    Returns:
        dict - Şema bilgileri ve kod örnekleri
        
    Example:
        GET /generate-schema?description=Ürün tablosu
        GET /generate-schema?description=Kullanıcı yönetimi için tablo
        GET /generate-schema?description=Sipariş takip tablosu
    """
    try:
        # Schema agent'ı al
        agent = get_schema_agent()
        
        # Şema oluştur
        result = agent.generate_schema(description)
        
        return result
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Şema oluşturulurken hata: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
