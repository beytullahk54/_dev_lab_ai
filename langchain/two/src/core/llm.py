from langchain_ollama import ChatOllama

# --- MODEL TANIMI ---
llm = ChatOllama(
    model="gemma3:4b",
    temperature=0,  # Router işlemleri için tutarlılık önemli
    num_predict=1024
)

llm_qwen1 = ChatOllama(
    model="gemma3:4b",
    temperature=0,
    num_predict=1024
)
