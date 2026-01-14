""" pip install chromadb """

import chromadb
# chroma_client = chromadb.Client() : Ramde çalışır
# Verileri diske kaydetmek için PersistentClient kullanın
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Koleksiyon varsa getir, yoksa oluştur (hata almamak için)
collection = chroma_client.get_or_create_collection(name="my_collection")

"""collection.add(
    ids=["id1", "id2"],
    documents=[
        "This is a document about pineapple",
        "This is a document about oranges"
    ]
)"""

results = collection.query(
    query_texts=["This is a query document about hawaii"], # Chroma will embed this for you
    n_results=2 # how many results to return
)
print(results)