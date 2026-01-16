from langchain_ollama import ChatOllama

# --- MODEL TANIMI ---
# Bilgisayarında Ollama açık olmalı ve 'ollama pull qwen3:8b' yapmış olmalısın.
llm = ChatOllama(
    model="qwen3:4b",
    temperature=0,  # Router işlemleri için tutarlılık önemli
    num_predict=1024
)

llm_qwen1 = ChatOllama(
    model="gemma3:1b",
    temperature=0,
    num_predict=1024
)
