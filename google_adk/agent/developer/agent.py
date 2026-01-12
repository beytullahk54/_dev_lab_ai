import os
from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent

# Load environment variables from the root .env file or local .env
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))


def calculate(expression: str) -> str:
    """Verilen matematiksel ifadeyi hesaplar. Örn: '25 * 45'"""
    try:
        # Güvenlik için sadece basit matematiksel karakterlere izin verilebilir
        # ancak şimdilik demo amaçlı eval kullanıyoruz.
        allowed_chars = "0123456789+-*/(). "
        if not all(c in allowed_chars for c in expression):
            return "Hata: Sadece rakamlar ve +, -, *, /, (, ) operatörleri kullanılabilir."
        return str(eval(expression))
    except Exception as e:
        return f"Hesaplama hatası: {e}"

math_agent = Agent(
    model='ollama/gemma3:4b',
    name='math_agent',
    description='Sadece sayısal ve matematiksel soruları çözen uzman.',
    instruction='Sen matematik uzmanısın. '
                'SADECE ve SADECE kullanıcı net bir matematik işlemi (toplama, çıkarma vb.) sorduğunda "calculate" aracını kullan. '
                'Eğer kullanıcı "Merhaba", "Nasılsın" gibi şeyler derse, ASLA araç kullanma. Sadece "Ben matematik ajanıyım, işleminiz nedir?" diye sor. '
                'Cevabına "[Math Agent]: " ile başla.',
    tools=[calculate],
)

coding_agent = Agent(
    model='ollama/gemma3:4b',
    name='coding_agent',
    description='Kod yazma, refactoring ve pratik uygulama uzmanı.',
    instruction='Verilen problemlere yönelik çalışan, production-ready kod blokları ve örnekleri üretin. Cevabının başına "[Coding Agent]: " ekle.',
)

programing_information_agent = Agent(
    model='ollama/gemma3:4b',
    name='programing_information_agent',
    description='Yazılım kavramları ve teorik bilgi uzmanı.',
    instruction='Yazılım teknolojileri, diller (Laravel, Vue vb.) hakkında bilgi ver. Kod yazma, kavram anlat. Cevabının başına "[Info Agent]: " ekle.',
)

general_agent = Agent(
    model='ollama/gemma3:4b',
    name='general_agent',
    description='Genel bilgi ve sohbet uzmanı.',
    instruction='Sen samimi bir sohbet arkadaşısın. Kullanıcı ile havadan sudan konuş, hal hatır sor. [General Agent]:',
)

root_agent = Agent(
    model='gemini-2.5-flash-lite', # ADK'da en güncel ve hızlı router modeli
    name='root_agent',
    description='Ana asistan.',
    instruction='Sen ana asistansın. Görevin kullanıcı ile sohbet etmek ve GEREKTİĞİNDE uzman çağırmaktır. '
                'ÇOK ÖNEMLİ KURAL: '
                'Eğer kullanıcı "Merhaba", "Selam", "Nasılsın" derse: '
                '   - ASLA `transfer_to_agent` KULLANMA. '
                '   - ASLA başka bir ajanı çağırma. '
                '   - Sadece kendin "Merhaba, size nasıl yardım edebilirim?" diye cevap yaz. '
                'Sadece ve sadece kullanıcı "Hesapla", "Kod yaz" gibi teknik bir istekte bulunursa ajan çağır.',
    sub_agents=[general_agent, math_agent, coding_agent, programing_information_agent],
)