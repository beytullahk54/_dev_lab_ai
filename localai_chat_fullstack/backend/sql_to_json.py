import mariadb
import json
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Veritabanı bağlantısı
conn = mariadb.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    port=3306
)

cursor = conn.cursor(dictionary=True)

sql = """
SELECT 
    m.support_message_issue_id,
    GROUP_CONCAT(
        CONCAT(u.name, ': ', m.support_message_content) 
        ORDER BY m.support_message_issue_id ASC 
        SEPARATOR ' | '
    ) AS formatted_messages
FROM 
    support_message m
JOIN 
    user u ON m.support_message_user_id = u.id
GROUP BY 
    m.support_message_issue_id;
"""

# Tablodan tüm verileri çek
cursor.execute(sql)
data = cursor.fetchall()

# JSON dosyasına kaydet
with open("ornek.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)


print(f"\n✓ {len(data)} kayıt bulundu\n")
print(json.dumps(data, ensure_ascii=False, indent=2))

# Bağlantıyı kapat
cursor.close()
conn.close()

print(f"✓ {len(data)} kayıt ornek.json dosyasına kaydedildi")
