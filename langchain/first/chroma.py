""" pip install chromadb """

import chromadb
from chromadb.utils import embedding_functions
# chroma_client = chromadb.Client() : Ramde çalışır
# Verileri diske kaydetmek için PersistentClient kullanın
chroma_client = chromadb.PersistentClient(path="./chroma_db")

turkce_embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="paraphrase-multilingual-MiniLM-L12-v2"
)
# Koleksiyon varsa getir, yoksa oluştur (hata almamak için)
collection = chroma_client.get_or_create_collection(name="my_collection",embedding_function=turkce_embedding_func)

collection.add(
    ids=["id3", "id4","id5","id6","id7","id8"],
    documents=[
        "Fatih Sultan Mehmet İstanbul'u fethetmiştir.",
        "Ankara Türkiye'nin başkentidir.",
        "Döner çok lezzetli bir yemektir."
    ]
)

results = collection.query(
    query_texts=["Conquest of Istanbul"], # Chroma will embed this for you
    #where_document={"$contains":"istanbul"},
    n_results=15 # how many results to return
)
print(results)