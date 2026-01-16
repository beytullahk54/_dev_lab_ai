from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
from core.embedding_engine import text_to_vector

client = QdrantClient(url="http://localhost:6333")

def setup_database(collection_name):
    if client.collection_exists(collection_name):
        print("")
        #print(f"'{collection_name}' zaten var, siliniyor...")
        #client.delete_collection(collection_name)
    else:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
        )
        print(f"'{collection_name}' başarıyla oluşturuldu.")

def create_points(collection_name, texts):
    client = QdrantClient(url="http://localhost:6333")
    points = [
        PointStruct(id=idx, vector=text_to_vector(txt), payload={"text": txt})
        for idx, txt in texts
    ]
    client.upsert(collection_name=collection_name, wait=True, points=points)

def query_points(collection_name, query, limit=50, score_threshold=0.70):
    sorgu_vektoru = text_to_vector(query)
    search_result = client.query_points(
        collection_name=collection_name,
        query=sorgu_vektoru,
        limit=limit,
        score_threshold=score_threshold,
        with_payload=True
    ).points

    temiz_liste = [point.payload.get("text", "") for point in search_result]
    return temiz_liste   

#setup_database(collection_name="test_collection_2")

"""texts = [
    (1, "Türkiye'nin başkenti Ankara'dır."),
    (2, "İstanbul bir megakenttir."),
    (3, "En sevdiğim yemek makarnadır."),
    (4, "istanbul ankaraya uzaktır."),
    (5, "fatih sultan mehmet istanbulu fethetmiştir."),
    (6, "istanbul restoranları"),
    (7, "bursanın taşları"),
    (8, "ispark megakenttedir.")
]"""

#create_points(collection_name="test_collection_2", texts=texts)