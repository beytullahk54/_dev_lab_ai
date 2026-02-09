import pymysql
import json
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Veritabanı bağlantısı
conn = pymysql.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    port=int(os.getenv("DB_PORT", 3308)),
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

sql = """
SELECT 
    m.support_message_issue_id,
    GROUP_CONCAT(
        CONCAT(u.name, ': ', m.support_message_content) 
        ORDER BY m.support_message_issue_id ASC ,
        m.support_message_id ASC 
        SEPARATOR ' | '
    ) AS formatted_messages
FROM 
    support_message m
JOIN 
    user u ON m.support_message_user_id = u.id
GROUP BY 
    m.support_message_issue_id;
"""

# Cursor oluştur
cursor = conn.cursor()

# Tablodan tüm verileri çek
cursor.execute(sql)
data = cursor.fetchall()

for row in data:
    if 'formatted_messages' in row and row['formatted_messages']:
        # Esma: ve Onur: ile başlayan kısımları Destek: olarak değiştir
        row['formatted_messages'] = row['formatted_messages'].replace('Esma Doğruel:', 'Destek:')
        row['formatted_messages'] = row['formatted_messages'].replace('Onur AYTAÇ:', 'Destek:')

# JSON dosyasına kaydet
with open("ornek.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Qdrant'a veri ekle
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "agents"))

from core.qdrant import setup_database, create_points

# Koleksiyon adı
collection_name = "test_collection_2"

# Verileri Qdrant formatına dönüştür (id, text)
# Uzun metinleri chunk'lara böl (max 512 karakter per chunk - çok güvenli limit)
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50  # Chunk'lar arası örtüşme

def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Metni belirtilen boyutta parçalara böler"""
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap  # Örtüşme ile devam et
        
        # Son chunk'u kontrol et
        if end >= text_length:
            break
    
    return chunks

texts = []
point_id = 1

for idx, row in enumerate(data, start=1):
    if row.get('formatted_messages'):
        text = row['formatted_messages']
        original_length = len(text)
        
        # Eğer metin uzunsa chunk'lara böl
        if original_length > CHUNK_SIZE:
            chunks = chunk_text(text)
            print(f"📦 Kayıt {idx}: {original_length} karakter -> {len(chunks)} chunk'a bölündü")
            
            for chunk_idx, chunk in enumerate(chunks, start=1):
                # Her chunk için metadata ekle
                texts.append((
                    point_id,
                    f"[Kayıt {idx} - Bölüm {chunk_idx}/{len(chunks)}] {chunk}"
                ))
                point_id += 1
        else:
            # Kısa metinler direkt eklensin
            texts.append((point_id, text))
            point_id += 1

print(f"\n📊 Toplam: {len(data)} kayıt -> {len(texts)} embedding noktası")

# Qdrant'a batch'ler halinde ekle (bağlantı kopmasını önler)
BATCH_SIZE = 50

if texts:
    total_batches = (len(texts) + BATCH_SIZE - 1) // BATCH_SIZE
    print(f"\n🔄 {total_batches} batch halinde Qdrant'a ekleniyor...")
    
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i:i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        
        try:
            create_points(collection_name, batch)
            print(f"  ✓ Batch {batch_num}/{total_batches}: {len(batch)} kayıt eklendi")
        except Exception as e:
            print(f"  ✗ Batch {batch_num}/{total_batches} hatası: {e}")
            continue
    
    print(f"\n✅ Toplam {len(texts)} mesaj Qdrant'a eklendi (koleksiyon: {collection_name})")
else:
    print("⚠ Qdrant'a eklenecek veri bulunamadı")


#print(f"\n✓ {len(data)} kayıt bulundu\n")
#print(json.dumps(data, ensure_ascii=False, indent=2))

# Bağlantıyı kapat
cursor.close()
conn.close()

print(f"✓ {len(data)} kayıt ornek.json dosyasına kaydedildi")
