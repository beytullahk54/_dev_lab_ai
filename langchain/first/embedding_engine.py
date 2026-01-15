import ollama
from qdrant_client import QdrantClient
from typing import List, Optional

# --- Yapılandırma ---
MODEL_NAME = "mxbai-embed-large"  # Türkçe performansı yüksek Ollama modeli
QDRANT_URL = "localhost"
QDRANT_PORT = 6333

# Qdrant İstemcisi (Modül düzeyinde bir kez başlatılır)
client = QdrantClient(QDRANT_URL, port=QDRANT_PORT)

def text_to_vector(text: str) -> List[float]:
    """
    Girilen metni Ollama kullanarak vektöre (embedding) dönüştürür.
    """
    try:
        response = ollama.embeddings(model=MODEL_NAME, prompt=text)
        return response['embedding']
    except Exception as e:
        print(f"Embedding hatası: {e}")
        return []