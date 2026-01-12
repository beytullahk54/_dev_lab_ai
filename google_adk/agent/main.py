from my_agent.agent import root_agent

def main():
    print("Ajan başlatıldı (Çıkmak için 'exit' yazın).")
    
    # Oturum (session) yönetimi gerekebilir, ancak basit kullanımda
    # doğrudan ajana sorgu göndermeyi deneyeceğiz.
    
    while True:
        user_input = input("Siz: ")
        if user_input.lower() in ["exit", "q", "quit"]:
            break
            
        try:
            # ADK Agent'ın query metodu genellikle bir response döner.
            # Dönen objenin yapısına göre text'i alacağız.
            response = root_agent.query(user_input)
            
            # Eğer response bir obje ise ve content özelliği varsa:
            if hasattr(response, 'content'):
                print(f"Ajan: {response.content}")
            else:
                print(f"Ajan: {response}")
                
        except Exception as e:
            print(f"Hata oluştu: {e}")

if __name__ == "__main__":
    main()
