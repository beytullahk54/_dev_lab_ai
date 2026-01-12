import streamlit as st
import sys
import os

# Mevcut dizini path'e ekle ki main.py'den import yapabilelim
sys.path.append(os.path.dirname(__file__))

from main import run_crew

st.set_page_config(page_title="CrewAI Asistanı", page_icon="🤖")

st.title("🤖 CrewAI Multi-Agent Asistan")
st.markdown("Bu asistan; **Matematik**, **Kodlama**, **Yazılım Bilgisi** ve **Genel Sohbet** konularında uzmanlaşmış ajanlardan oluşur.")

# Oturum durumunu (chat geçmişi) başlat
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Merhaba! Ben size nasıl yardımcı olabilirim?"}]

# Geçmiş mesajları ekrana bas
for msg in st.session_state.messages:
    if msg["role"] == "user":
        # Kullanıcı mesajı
        st.chat_message("user").write(msg["content"])
    else:
        # Asistan mesajı
        st.chat_message("assistant").write(msg["content"])

# Yeni giriş alanı
if prompt := st.chat_input("Mesajınızı buraya yazın..."):
    # Kullanıcı mesajını ekle ve göster
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # Asistanın cevabını bekle
    with st.spinner("Asistanlar çalışıyor, lütfen bekleyin..."):
        try:
            # CrewAI fonksiyonunu çalıştır
            response = run_crew(prompt)
            # Response objesi string formatına çevrilir
            response_text = str(response)
        except Exception as e:
            response_text = f"❌ Bir hata oluştu: {e}"
            
    # Asistan cevabını ekle ve göster
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    st.chat_message("assistant").write(response_text)
