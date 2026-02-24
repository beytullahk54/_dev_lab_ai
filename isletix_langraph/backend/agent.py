"""
Langchain Agent - Groq API ile Dosya Oluşturucu (Basitleştirilmiş Versiyon)
"""
import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from tools import FileCreatorTool

# .env dosyasını yükle
load_dotenv()


class FileCreatorAgent:
    """Groq API kullanarak dosya oluşturan basit agent"""
    
    def __init__(self):
        """Agent'ı başlat"""
        # Groq API key kontrolü
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("❌ GROQ_API_KEY bulunamadı! Lütfen .env dosyasını oluşturun.")
        
        # Groq LLM'i başlat
        self.llm = ChatGroq(
            temperature=0.7,
            model_name="llama-3.3-70b-versatile",  # Groq'un güncel modeli
            groq_api_key=self.api_key
        )
        
        # Dosya oluşturma aracı
        self.file_tool = FileCreatorTool()
        
        # System prompt
        self.system_prompt = """Sen dosya oluşturma konusunda uzman bir asistansın.

Görevin:
1. Kullanıcının isteğini anla
2. Uygun dosya adı ve içeriği belirle
3. JSON formatında yanıt ver

Yanıt formatı:
{
    "filename": "dosya_adi.uzanti",
    "content": "dosya içeriği buraya",
    "explanation": "kullanıcıya açıklama"
}

Kurallar:
- Dosya adını açıklayıcı ve uygun uzantıyla belirle (.txt, .md, .json, vb.)
- İçeriği net, düzenli ve anlamlı oluştur
- Türkçe karakterleri doğru kullan
- Markdown, text, JSON gibi formatları destekle

Örnek:
Kullanıcı: "Bir TODO listesi oluştur"
Yanıt:
{
    "filename": "todo.md",
    "content": "# TODO Listesi\\n\\n- [ ] Görev 1\\n- [ ] Görev 2\\n- [ ] Görev 3",
    "explanation": "TODO listesi markdown formatında oluşturuldu."
}

SADECE JSON yanıt ver, başka bir şey yazma!"""
    
    def run(self, user_input: str) -> str:
        """Agent'ı çalıştır"""
        try:
            # LLM'e sor
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=user_input)
            ]
            
            response = self.llm.invoke(messages)
            response_text = response.content.strip()
            
            # JSON parse et
            # Eğer markdown code block içindeyse temizle
            if response_text.startswith("```"):
                # ```json ile başlıyorsa temizle
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1])
            
            data = json.loads(response_text)
            
            # Dosyayı oluştur
            filename = data.get("filename", "output.txt")
            content = data.get("content", "")
            explanation = data.get("explanation", "Dosya oluşturuldu.")
            
            result = self.file_tool._run(
                filename=filename,
                content=content,
                directory="output"
            )
            
            return f"{explanation}\n{result}"
            
        except json.JSONDecodeError as e:
            return f"❌ JSON parse hatası: {str(e)}\nLLM yanıtı: {response_text}"
        except Exception as e:
            return f"❌ Hata oluştu: {str(e)}"


def main():
    """Ana fonksiyon - interaktif mod"""
    print("=" * 60)
    print("🤖 GROQ AI DOSYA OLUŞTURUCU AGENT")
    print("=" * 60)
    print("\nLangchain + Groq API ile çalışıyor")
    print("Çıkmak için 'quit' veya 'exit' yazın\n")
    
    try:
        # Agent'ı başlat
        agent = FileCreatorAgent()
        print("✅ Agent başarıyla başlatıldı!\n")
        
        # İnteraktif döngü
        while True:
            user_input = input("👤 Siz: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'çıkış']:
                print("\n👋 Görüşmek üzere!")
                break
            
            if not user_input:
                continue
            
            print("\n🤖 Agent çalışıyor...\n")
            response = agent.run(user_input)
            print(f"🤖 Agent: {response}\n")
            print("-" * 60 + "\n")
    
    except Exception as e:
        print(f"\n❌ Kritik hata: {str(e)}")
        print("\nLütfen şunları kontrol edin:")
        print("1. .env dosyasında GROQ_API_KEY tanımlı mı?")
        print("2. Gerekli paketler yüklü mü? (uv sync)")


if __name__ == "__main__":
    main()
