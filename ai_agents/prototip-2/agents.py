"""
agents.py
---------
LangGraph tabanl? iki agent ve bir router (y?nlendirici) tan?mlan?r.

Mimari:
  [Kullan?c? mesaj?]
       |
  [router_node]  <- Groq LLM mesaj? analiz eder, hangi agent'? ?a??raca??na karar verir
       |
  +---------+----------+
  |                    |
[kayit_ac_node]  [kullanici_say_node]
  |                    |
[SQLite yaz]    [SQLite oku]
  |                    |
  +--------+-----------+
           |
      [cevap string]

Neden LangGraph?
- Her "node" izole bir i? birimidir; yeni agent eklemek sadece yeni node + edge eklemektir.
- State (durum) graf boyunca ta??n?r; mesaj ge?mi?i veya ek bilgi kolayca eklenebilir.
- Groq ile LangChain entegrasyonu sayesinde LLM ?a?r?lar? standart bir aray?zle yap?l?r.
"""

import os
from typing import TypedDict

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

import database as db

load_dotenv()

# ---------- LLM (lazy) ----------
_llm: "ChatGroq | None" = None

def get_llm() -> "ChatGroq":
    """LLM nesnesini ilk çağrıda oluşturur (lazy init).
    Böylece .env okunduktan sonra key doğrulanır."""
    global _llm
    if _llm is None:
        _llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model="llama-3.1-8b-instant",
            temperature=0,
        )
    return _llm

# ---------- Graf State ----------
class AgentState(TypedDict):
    """
    Graf boyunca ta??nan durum nesnesi.
    - user_message : kullan?c?dan gelen ham metin
    - intent       : router'?n belirledi?i niyet ("kayit_ac" | "kullanici_say" | "bilinmiyor")
    - response     : son kullan?c?ya d?nd?r?lecek metin
    """
    user_message: str
    intent: str
    response: str


# ---------- Node 1: Router ----------
def router_node(state: AgentState) -> AgentState:
    """
    Groq LLM'e kullan?c? mesaj?n? g?nderir.
    LLM sadece '?intent_etiketi?' format?nda cevap verir.
    Bu sayede downstream nodelar karar almak zorunda kalmaz.
    """
    system_prompt = (
        "Sen bir y?nlendirici (router) yapay zekasısın. "
        "Kullanıcı mesajını analiz et ve yalnızca aşağıdaki etiketlerden BİRİNİ yaz:\n"
        "- kayit_ac   → yeni kullanıcı kaydı açılmak isteniyorsa\n"
        "- kullanici_say → kaç kullanıcı olduğu soruluyorsa\n"
        "- bilinmiyor → başka bir şeyse\n"
        "Sadece etiketi yaz, başka hiçbir şey yazma."
    )
    result = get_llm().invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=state["user_message"]),
    ])
    intent = result.content.strip().lower()
    if intent not in ("kayit_ac", "kullanici_say"):
        intent = "bilinmiyor"
    return {**state, "intent": intent}


# ---------- Node 2: Kayıt Aç Agent ----------
def kayit_ac_node(state: AgentState) -> AgentState:
    """
    Kullan?c? mesaj?ndan isim ?ekip SQLite'a kaydeder.
    Groq LLM mesajdan sadece ismi ?ekme g?revini ?stlenir.
    """
    system_prompt = (
        "Kullanıcı mesajından kaydedilecek kişinin adını çıkar. "
        "Sadece ismi yaz (örn: 'Beytullah'), başka hiçbir şey yazma."
    )
    result = get_llm().invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=state["user_message"]),
    ])
    name = result.content.strip()
    outcome = db.insert_user(name)

    if outcome["status"] == "created":
        response = f"✅ '{name}' için kayıt başarıyla oluşturuldu."
    else:
        response = f"ℹ️ '{name}' adına zaten bir kayıt mevcut."

    return {**state, "response": response}


# ---------- Node 3: Kullanıcı Say Agent ----------
def kullanici_say_node(state: AgentState) -> AgentState:
    """SQLite'tan toplam kullan?c? say?s?n? okur."""
    total = db.count_users()
    response = f"📊 Sistemde toplam {total} kullanıcı kayıtlı."
    return {**state, "response": response}


# ---------- Node 4: Bilinmiyor ----------
def bilinmiyor_node(state: AgentState) -> AgentState:
    """Hi?bir agent'la e?le?meyen mesajlar i?in geri d?n?? mesaj?."""
    response = (
        "🤖 Anlayamadım. Şunu deneyebilirsin:\n"
        "• 'Beytullah için kayıt aç'\n"
        "• 'Kaç kullanıcımız var?'"
    )
    return {**state, "response": response}


# ---------- Router Fonksiyonu (edge karar?) ----------
def route_decision(state: AgentState) -> str:
    """router_node'dan sonra hangi node'a gidilece?ini belirler."""
    return state["intent"]


# ---------- Graf Tan?m? ----------
def build_graph() -> StateGraph:
    """
    Graf bir kez olu?turulur, uygulama ?mr? boyunca ayn? nesne kullan?l?r.
    Yeni bir agent eklemek i?in:
      1. Yeni bir node fonksiyonu yaz.
      2. graph.add_node(...) ile ekle.
      3. router_node'a yeni intent etiketini tan?t.
      4. conditional_edges'e yeni dal? ekle.
    """
    graph = StateGraph(AgentState)

    graph.add_node("router", router_node)
    graph.add_node("kayit_ac", kayit_ac_node)
    graph.add_node("kullanici_say", kullanici_say_node)
    graph.add_node("bilinmiyor", bilinmiyor_node)

    graph.set_entry_point("router")

    graph.add_conditional_edges(
        "router",
        route_decision,
        {
            "kayit_ac":      "kayit_ac",
            "kullanici_say": "kullanici_say",
            "bilinmiyor":    "bilinmiyor",
        },
    )

    graph.add_edge("kayit_ac",      END)
    graph.add_edge("kullanici_say", END)
    graph.add_edge("bilinmiyor",    END)

    return graph.compile()


app_graph = build_graph()


def run_agent(user_message: str) -> str:
    """D??ar?dan ?a?r?lan tek giri? noktas?."""
    initial_state: AgentState = {
        "user_message": user_message,
        "intent": "",
        "response": "",
    }
    final_state = app_graph.invoke(initial_state)
    return final_state["response"]
