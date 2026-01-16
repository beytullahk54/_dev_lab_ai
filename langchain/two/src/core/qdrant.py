from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
from embedding_engine import text_to_vector

# 1. Bağlantı ve Yapılandırma
client = QdrantClient(url="http://localhost:6333")
COLLECTION_NAME = "test_collection_2"

def setup_database():
    # Modern yöntem: Koleksiyon varsa önce sil, sonra temiz bir şekilde oluştur
    if client.collection_exists(COLLECTION_NAME):
        print(f"'{COLLECTION_NAME}' zaten var, siliniyor...")
        client.delete_collection(COLLECTION_NAME)

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
    )
    print(f"'{COLLECTION_NAME}' başarıyla oluşturuldu.")

# 2. Verileri Hazırla
texts = [
    (1, "Türkiye'nin başkenti Ankara'dır."),
    (2, "İstanbul bir megakenttir."),
    (3, "En sevdiğim yemek makarnadır."),
    (4, "istanbul ankaraya uzaktır."),
    (5, "fatih sultan mehmet istanbulu fethetmiştir."),
    (6, "istanbul restoranları"),
    (7, "bursanın taşları"),
    (8, "ispark megakenttedir.")
]

# 3. Veritabanını Sıfırla ve Oluştur
setup_database()

# 4. Verileri Vektörize Et ve Yükle
print("Vektörler oluşturuluyor ve yükleniyor...")
points = [
    PointStruct(id=idx, vector=text_to_vector(txt), payload={"text": txt})
    for idx, txt in texts
]

client.upsert(collection_name=COLLECTION_NAME, wait=True, points=points)

# 5. Anlamsal Arama (Semantic Search)
sorgu_metni = " Türkiye'nin  Arabistan ve  ile yaptığı iddia edilen  askeri  "
print(f"\nSorgulanıyor: '{sorgu_metni}'")

sorgu_vektoru = text_to_vector(sorgu_metni)

# client.search yerine bunu deneyin:
search_result = client.query_points(
    collection_name=COLLECTION_NAME,
    query=sorgu_vektoru,
    limit=50,
    score_threshold=0.70,
    with_payload=True
).points

temiz_liste = [point.payload.get("text", "") for point in search_result]


# Yazdırırken küçük bir fark var (search_result.points içinden geçer):
print("-" * 30)
print("--- Arama Sonuçları ---")
for res in search_result:
    print(f"Skor: {res.score:.4f} | Metin: {res.payload['text']}")


print(temiz_liste)