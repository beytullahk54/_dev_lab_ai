"""
Schema Generator Agent - Groq API ile Tablo Şeması Oluşturucu
"""
import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

# .env dosyasını yükle
load_dotenv()


class SchemaGeneratorAgent:
    """Groq API kullanarak tablo şeması oluşturan agent"""
    
    def __init__(self):
        """Agent'ı başlat"""
        # Groq API key kontrolü
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("❌ GROQ_API_KEY bulunamadı! Lütfen .env dosyasını oluşturun.")
        
        # Groq LLM'i başlat
        self.llm = ChatGroq(
            temperature=0.3,  # Daha deterministik sonuçlar için düşük
            model_name="llama-3.3-70b-versatile",
            groq_api_key=self.api_key
        )
        
        # System prompt
        self.system_prompt = """Sen tablo şeması oluşturma konusunda uzman bir asistansın.

Görevin:
1. Kullanıcının istediği tablo türünü anla (örn: Ürün, Kullanıcı, Sipariş, vb.)
2. O tablo için uygun field'ları belirle
3. Her field için header (başlık) ve sortable (sıralanabilir mi) bilgisi ekle
4. JSON array formatında yanıt ver

Yanıt formatı (JavaScript/TypeScript için):
[
  { "field": "id", "header": "ID", "sortable": true },
  { "field": "name", "header": "İsim", "sortable": true },
  ...
]

Kurallar:
- field: camelCase formatında (örn: firstName, createdAt)
- header: Türkçe, kullanıcı dostu başlık
- sortable: Genellikle true, ama bazı özel alanlar için false olabilir
- Her tablo için mantıklı field'lar ekle (id, createdAt, updatedAt gibi standart alanlar dahil)
- Tablo türüne göre özel field'lar ekle

Örnek tablolar ve field'ları:

ÜRÜN TABLOSU:
[
  { "field": "id", "header": "ID", "sortable": true },
  { "field": "name", "header": "Ürün Adı", "sortable": true },
  { "field": "category", "header": "Kategori", "sortable": true },
  { "field": "brand", "header": "Marka", "sortable": true },
  { "field": "stock", "header": "Stok", "sortable": true },
  { "field": "price", "header": "Fiyat", "sortable": true },
  { "field": "status", "header": "Durum", "sortable": true },
  { "field": "createdAt", "header": "Oluşturma Tarihi", "sortable": true }
]

KULLANICI TABLOSU:
[
  { "field": "id", "header": "ID", "sortable": true },
  { "field": "firstName", "header": "Ad", "sortable": true },
  { "field": "lastName", "header": "Soyad", "sortable": true },
  { "field": "email", "header": "E-posta", "sortable": true },
  { "field": "phone", "header": "Telefon", "sortable": true },
  { "field": "role", "header": "Rol", "sortable": true },
  { "field": "status", "header": "Durum", "sortable": true },
  { "field": "createdAt", "header": "Kayıt Tarihi", "sortable": true }
]

SİPARİŞ TABLOSU:
[
  { "field": "id", "header": "Sipariş No", "sortable": true },
  { "field": "customerName", "header": "Müşteri", "sortable": true },
  { "field": "products", "header": "Ürünler", "sortable": false },
  { "field": "totalAmount", "header": "Toplam Tutar", "sortable": true },
  { "field": "status", "header": "Durum", "sortable": true },
  { "field": "paymentMethod", "header": "Ödeme Yöntemi", "sortable": true },
  { "field": "orderDate", "header": "Sipariş Tarihi", "sortable": true },
  { "field": "deliveryDate", "header": "Teslimat Tarihi", "sortable": true }
]

SADECE JSON array yanıt ver, başka bir şey yazma!"""
    
    def generate_schema(self, table_description: str) -> dict:
        """
        Tablo şeması oluştur
        
        Args:
            table_description: str - Tablo açıklaması (örn: "Ürün tablosu", "Kullanıcı yönetimi için tablo")
            
        Returns:
            dict - Şema bilgileri
        """
        try:
            # LLM'e sor
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"Şu tablo için şema oluştur: {table_description}")
            ]
            
            response = self.llm.invoke(messages)
            response_text = response.content.strip()
            
            # JSON parse et
            # Eğer markdown code block içindeyse temizle
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                # ```json veya ``` satırlarını atla
                response_text = "\n".join(lines[1:-1])
            
            schema_data = json.loads(response_text)
            
            return {
                "success": True,
                "table": table_description,
                "schema": schema_data,
                "count": len(schema_data),
                "code": self._generate_code(schema_data)
            }
            
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"JSON parse hatası: {str(e)}",
                "raw_response": response_text
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_code(self, schema_data: list) -> dict:
        """Şema için kod örnekleri oluştur"""
        # JavaScript/TypeScript kodu
        js_code = f"const tableSchema = {json.dumps(schema_data, indent=2, ensure_ascii=False)}"
        
        # Vue.js composable kodu
        vue_code = f"""const tableSchema = ref({json.dumps(schema_data, indent=2, ensure_ascii=False)})"""
        
        # Python kodu
        py_code = f"table_schema = {json.dumps(schema_data, indent=4, ensure_ascii=False)}"
        
        return {
            "javascript": js_code,
            "vue": vue_code,
            "python": py_code
        }


def main():
    """Test fonksiyonu"""
    print("🔧 Schema Generator Agent Test\n")
    
    try:
        agent = SchemaGeneratorAgent()
        
        # Test
        result = agent.generate_schema("Ürün tablosu")
        
        if result["success"]:
            print(f"✅ Şema oluşturuldu!")
            print(f"📊 Tablo: {result['table']}")
            print(f"📝 Field sayısı: {result['count']}\n")
            print("JavaScript Kodu:")
            print(result["code"]["javascript"])
        else:
            print(f"❌ Hata: {result['error']}")
            
    except Exception as e:
        print(f"❌ Kritik hata: {str(e)}")


if __name__ == "__main__":
    main()
