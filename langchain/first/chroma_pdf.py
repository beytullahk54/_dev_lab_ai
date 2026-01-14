"""brew install tesseract
brew install poppler
pip install pytesseract pdf2image pillow"""

import chromadb
import os
import time

# Gerekli kütüphaneler (pip install pypdf pytesseract pdf2image pillow)
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    from pdf2image import convert_from_path
    import pytesseract
except ImportError:
    convert_from_path = None
    pytesseract = None

def extract_text_hybrid(pdf_path):
    """
    1. Önce pypdf ile metin okumayı dener (Hızlı).
    2. Eğer metin bulamazsa, Tesseract OCR devreye girer (Yavaş ama Görsel Okur).
    """
    if PdfReader is None:
        return "HATA: 'pypdf' kütüphanesi eksik."

    text_content = ""
    
    # Adım 1: Standart Metin Okuma
    print("   ↳ 1. Yöntem: Standart metin okuma deneniyor...")
    reader = PdfReader(pdf_path)
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text_content += extracted + "\n"
    
    # Eğer metin doluysa, OCR'a gerek yok.
    if text_content.strip():
        print("   ✅ Metin başarıyla ayıklandı.")
        return text_content

    # Adım 2: OCR (Görselden Metne)
    print("   ⚠️ Metin bulunamadı. 2. Yöntem: OCR (Görsel Okuma) devreye giriyor...")
    
    if convert_from_path is None or pytesseract is None:
        return "HATA: OCR için 'pdf2image' ve 'pytesseract' kütüphaneleri eksik."
    
    try:
        images = convert_from_path(pdf_path)
        ocr_text = ""
        for i, img in enumerate(images):
            print(f"      ↳ Sayfa {i+1} taranıyor...")
            ocr_text += pytesseract.image_to_string(img, lang='tur+eng') # Türkçe ve İngilizce desteği
        return ocr_text
    except Exception as e:
        return f"HATA: OCR işlemi sırasında hata oluştu. (Poppler kurulu mu?)\nHata: {str(e)}"

def chunk_text(text, chunk_size=1000):
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i+chunk_size])
    return chunks

def main():
    pdf_file_path = "sample.pdf" # PDF dosyanızın adı
    collection_name = "pdf_ocr_collection"
    
    print(f"🚀 İşlem Başlıyor: {pdf_file_path}")

    # 1. Dosya Kontrolü
    if not os.path.exists(pdf_file_path):
        print(f"❌ Dosya bulunamadı: {pdf_file_path}")
        return

    # 2. Metin Çıkarma (Hybrid)
    raw_text = extract_text_hybrid(pdf_file_path)
    
    if raw_text.startswith("HATA") or not raw_text.strip():
        print(f"❌ Sonuç başarısız: {raw_text}")
        return

    print(f"📄 Toplam {len(raw_text)} karakter okundu.")

    # 3. ChromaDB Hazırlık
    client = chromadb.PersistentClient(path="./chroma_db_ocr")
    collection = client.get_or_create_collection(name=collection_name)

    # 4. Parçalama ve Kaydetme
    chunks = chunk_text(raw_text)
    print(f"✂️  Metin {len(chunks)} parçaya bölündü.")
    
    ids = [f"doc_{time.time()}_{i}" for i in range(len(chunks))]
    metadatas = [{"source": pdf_file_path} for i in range(len(chunks))]

    print("💾 ChromaDB'ye kaydediliyor...")
    collection.add(
        documents=chunks,
        ids=ids,
        metadatas=metadatas
    )
    print("✅ Kayıt tamamlandı!")

    # 5. Test Sorgusu
    query = "Belgede nelerden bahsediliyor?"
    print(f"\n🔍 Test Sorgusu: '{query}'")
    results = collection.query(query_texts=[query], n_results=2)
    print("Sonuçlar:", results['documents'][0])

if __name__ == "__main__":
    main()
