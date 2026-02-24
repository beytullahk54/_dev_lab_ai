"""
Dosya oluşturma aracı (tool) - Langchain agent tarafından kullanılacak
"""
import os
from typing import Optional


class FileCreatorTool:
    """Dosya oluşturma aracı - basitleştirilmiş versiyon"""
    
    def _run(self, filename: str, content: str, directory: str = "output") -> str:
        """Dosya oluşturma işlemini gerçekleştirir"""
        try:
            # Klasör yoksa oluştur
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            # Tam dosya yolu
            filepath = os.path.join(directory, filename)
            
            # Dosyayı oluştur ve içeriği yaz
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"✅ Dosya başarıyla oluşturuldu: {filepath}"
        
        except Exception as e:
            return f"❌ Dosya oluşturulurken hata oluştu: {str(e)}"
