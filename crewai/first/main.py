import os
import sys
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool

# Load environment variables
load_dotenv()
env_path = os.path.join(os.path.dirname(__file__), '../../.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

# Determine Root Agent Model based on API Key availability
gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if gemini_key:
    root_model = 'gemini/gemini-2.5-flash-lite'
    print(f"✅ Gemini API Key found. Using {root_model} for Root Agent.")
else:
    root_model = 'ollama/gemma3:4b'
    print("⚠️ Gemini/Google API Key NOT found. Falling back to ollama/gemma3:4b for Root Agent.")

# --- Tools ---
class CalculatorTools:
    @tool("Calculate Expression")
    def calculate(expression: str) -> str:
        """Verilen matematiksel ifadeyi hesaplar. Örn: '25 * 45'.
        Sadece rakamlar ve +, -, *, /, (, ) operatörleri kullanılabilir."""
        try:
            # Güvenlik önlemi (Basit kontrol)
            allowed_chars = "0123456789+-*/(). "
            if not all(c in allowed_chars for c in expression):
                return "Hata: Sadece rakamlar ve +, -, *, /, (, ) operatörleri kullanılabilir."
            return str(eval(expression))
        except Exception as e:
            return f"Hesaplama hatası: {e}"

        except Exception as e:
            return f"Hesaplama hatası: {e}"

class LegalTools:
    @tool("Read Law Article")
    def read_article(article_name: str) -> str:
        """Hukuk maddelerini kaynaklardan okur. Şu an test için sadece 'Madde 1' mevcuttur."""
        # Basit bir deneme maddesi
        if "madde 1" in article_name.lower() or "1. madde" in article_name.lower():
            return (
                "Yazılım Geliştirme Kanunu Madde 1: \n"
                "Her yazılımcı, yazdığı kodun okunabilir ve sürdürülebilir olmasından sorumludur. "
                "Spaghetti kod yazmak, ' teknik borç' kapsamında suç sayılır."
            )
        return "Aradığınız madde veritabanında bulunamadı."

# --- Agents ---

# 1. Math Agent
math_agent = Agent(
    role='Math Agent',
    goal='Sadece sayısal ve matematiksel soruları çözmek.',
    backstory=(
        'Sen matematik uzmanısın. '
        'SADECE ve SADECE kullanıcı net bir matematik işlemi (toplama, çıkarma vb.) sorduğunda "Calculate Expression" aracını kullan. '
        'Eğer kullanıcı "Merhaba", "Nasılsın" gibi şeyler derse, matematik dışı konulara girme. '
        'Cevabına "[Math Agent]: " ile başla.'
    ),
    verbose=True,
    allow_delegation=False,
    tools=[CalculatorTools.calculate],
    llm='ollama/gemma3:4b'
)

# 2. Coding Agent
coding_agent = Agent(
    role='Coding Agent',
    goal='Kod yazma, refactoring ve pratik uygulama üretmek.',
    backstory=(
        'Kod yazma, refactoring ve pratik uygulama uzmanısın. '
        'Verilen problemlere yönelik çalışan, production-ready kod blokları ve örnekleri üretirsin. '
        'Cevabının başına "[Coding Agent]: " ekle.'
    ),
    verbose=True,
    allow_delegation=False,
    llm='ollama/gemma3:4b'
)

# 3. Programming Info Agent
programing_information_agent = Agent(
    role='Info Agent',
    goal='Yazılım kavramları ve teorik bilgi vermek.',
    backstory=(
        'Yazılım teknolojileri, diller (Laravel, Vue vb.) hakkında ayrıntılı bilgi verirsin. '
        'Kod yazmaktan çok kavramları anlatırsın. '
        'Cevabının başına "[Info Agent]: " ekle.'
    ),
    verbose=True,
    allow_delegation=False,
    llm='ollama/gemma3:4b'
)

# 4. General Agent
general_agent = Agent(
    role='General Agent',
    goal='Genel bilgi ve sohbet.',
    backstory=(
        'Sen samimi bir sohbet arkadaşısın. '
        'Kullanıcı ile havadan sudan konuş, hal hatır sor. '
        'Cevabının başına "[General Agent]: " ekle.'
    ),
    verbose=True,
    allow_delegation=False,
    llm='ollama/gemma3:4b'
)

# 5. Law Agent
law_agent = Agent(
    role='Law Agent',
    goal='Hukuki soruları cevaplamak ve kanun maddelerini yorumlamak.',
    backstory=(
        'Sen uzman bir hukuk danışmanısın. Şu an test aşamasındasın ve "Yazılım Geliştirme Kanunu" konusunda uzmansın. '
        'Sana bir soru sorulduğunda veya bir madde istendiğinde MUTLAKA "Read Law Article" aracını kullanarak bilgiyi doğrula. '
        'Hukuk dışı konulara girme. '
        'Cevabının başına "[Law Agent]: " ekle.'
    ),
    verbose=True,
    allow_delegation=False,
    tools=[LegalTools.read_article],
    llm=root_model
)

# Root/Manager Agent
# CrewAI'da hiyerarşik yapı kullanıldığında Manager Agent görevleri dağıtır.
root_manager = Agent(
    role='Root Agent',
    goal='Kullanıcı isteklerini yönetmek ve doğru ajana iletmek.',
    backstory=(
        'Sen ana asistansın. Görevin kullanıcı ile sohbet etmek ve GEREKTİĞİNDE uzman çağırmaktır. '
        'ÇOK ÖNEMLİ KURALLAR: '
        '1. Eğer kullanıcı "Merhaba", "Selam", "Nasılsın" derse: Kendin cevap ver veya "Delegate work to coworker" aracını kullanarak "General Agent"a yönlendir. '
        '2. Başka bir ajana iş verirken ASLA ajanın adını doğrudan eylem (Action) olarak yazma. '
        '3. MUTLAKA "Delegate work to coworker" veya "Ask question to coworker" araçlarını kullan. '
        '4. "coworker" parametresine ilgili ajanın tam adını (örn: "Math Agent", "General Agent", "Law Agent") yaz.'
    ),
    verbose=True,
    allow_delegation=True,
    # Kullanıcının belirttiği model. Eğer API anahtarı yoksa çalışmayabilir, 
    # bu durumda 'ollama/gemma3:4b' veya 'openai/gpt-4' gibi bir model ile değiştirin.
    llm=root_model
)

# --- Main Execution ---
def run_crew(user_input):
    # Bu görev hiyerarşik süreçte manager tarafından uygun ajana atanacak 
    # veya manager kendisi halledecek.
    task = Task(
        description=f"""
        Kullanıcıdan gelen mesaj: '{user_input}'
        
        Bu mesajı analiz et.
        - Eğer bir selamlama veya genel sohbet ise, samimi bir şekilde cevap ver.
        - Eğer matematiksel bir işlem ise, hesaplat.
        - Eğer kodlama ile ilgiliyse, kod yazdır.
        - Eğer hukuk veya kanun ile ilgiliyse, hukuk ajanına danış.
        - Eğer teknik bilgi sorusuysa, bilgi verdir.
        
        Sonuç olarak kullanıcıya dönülecek yanıtı oluştur.
        """,
        expected_output="Kullanıcıya verilecek son cevap metni.",
        agent=None # Hiyerarşik süreçte boş bırakılır, manager atar.
    )

    crew = Crew(
        agents=[math_agent, coding_agent, programing_information_agent, general_agent, law_agent],
        tasks=[task],
        process=Process.hierarchical,
        manager_agent=root_manager,
        verbose=True
    )

    return crew.kickoff()

if __name__ == "__main__":
    print("\n--- CrewAI Tabanlı Asistan ---")
    print("Çıkmak için 'q' veya 'exit' yazın.\n")
    
    while True:
        try:
            user_input = input("Sen: ")
            if user_input.lower() in ['q', 'exit', 'quit']:
                print("Çıkış yapılıyor...")
                break
            
            if not user_input.strip():
                continue

            result = run_crew(user_input)
            print(f"\nAsistan: {result}\n")
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\nİşlem iptal edildi.")
            break
        except Exception as e:
            print(f"\nHata oluştu: {e}")
