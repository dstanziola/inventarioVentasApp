"""
Script de prueba para verificar las correcciones de db_connection.
Testa que todos los servicios puedan ser instanciados correctamente.
"""

import sys
import os

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_service_imports():
    """Probar que los servicios se puedan importar e instanciar."""
    results = {}
    
    try:
        # Test 1: Import de database
        from db.database import get_database_connection
        db_conn = get_database_connection()
        results['database'] = "OK - Conexión establecida"
        
        # Test 2: Import de CategoryService
        from services.category_service import CategoryService
        category_service = CategoryService(db_conn)
        results['category_service'] = "OK - Instanciado correctamente"
        
        # Test 3: Import de ProductService  
        from services.product_service import ProductService
        product_service = ProductService(db_conn)
        results['product_service'] = "OK - Instanciado correctamente"
        
        # Test 4: Import de LabelService (con db_connection)
        from services.label_service import LabelService
        label_service = LabelService(db_conn)
        results['label_service'] = "OK - Instanciado con db_connection"
        
        # Test 5: Import de LabelService (sin db_connection)
        label_service_no_db = LabelService()
        results['label_service_no_db'] = "OK - Instanciado sin db_connection"
        
        # Test 6: Import de BarcodeService
        from services.barcode_service import BarcodeService
        barcode_service = BarcodeService(db_conn)
        results['barcode_service'] = "OK - Instanciado correctamente"
        
        # Test 7: Simular creación de ProductWindow (solo imports)
        try:
            from ui.forms.product_form import ProductWindow
            results['product_form_import'] = "OK - Import exitoso"
        except Exception as e:
            results['product_form_import'] = f"ERROR: {e}"
        
        # Test 8: Simular creación de SalesWindow (solo imports)
        try:
            from ui.forms.sales_form import SalesWindow
            results['sales_form_import'] = "OK - Import exitoso"
        except Exception as e:
            results['sales_form_import'] = f"ERROR: {e}"
            
    except Exception as e:
        results['error_general'] = f"ERROR GENERAL: {e}"
    
    return results

if __name__ == "__main__":
    print("=== TESTING CORRECCIONES DE DB_CONNECTION ===")
    print()
    
    results = test_service_imports()
    
    for test_name, result in results.items():
        status = "PASS" if "OK" in result else "FAIL"
        print(f"{status:4} | {test_name:25} | {result}")
    
    print()
    print("=== FIN DEL TEST ===")
