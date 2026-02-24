"""
Tablo şeması oluşturma aracı - Langchain agent tarafından kullanılacak
"""
import os


class SchemaGeneratorTool:
    """Tablo şeması oluşturma aracı"""
    
    def _run(self, schema_data: dict) -> dict:
        """
        Şema verilerini formatlar ve döndürür
        
        Args:
            schema_data: dict - field, header, sortable bilgilerini içeren liste
            
        Returns:
            dict - Formatlanmış şema
        """
        try:
            return {
                "success": True,
                "schema": schema_data,
                "count": len(schema_data) if isinstance(schema_data, list) else 0
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
