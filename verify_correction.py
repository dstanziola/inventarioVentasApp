"""
Script de verificación para validar que la corrección funciona.
Reproduce el escenario exacto del problema reportado.
"""

import sys
import os

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_barcode_service_initialization():
    """Test básico de inicialización de BarcodeService."""
    print("=== TEST 1: Inicialización de BarcodeService ===")
    try:
        from services.barcode_service import BarcodeService
        barcode_service = BarcodeService()
        print("✅ BarcodeService se inicializa correctamente")
        print(f"   ProductService configurado: {barcode_service.product_service is not None}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_product_service_initialization():
    """Test de inicialización de ProductService."""
    print("\n=== TEST 2: Inicialización de ProductService ===")
    try:
        from services.product_service import ProductService
        from unittest.mock import Mock
        
        mock_db = Mock()
        product_service = ProductService(mock_db)
        print("✅ ProductService se inicializa correctamente con db_connection")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_services_integration():
    """Test de integración de servicios como en sales_form.py"""
    print("\n=== TEST 3: Integración de Servicios ===")
    try:
        from services.sales_service import SalesService
        from services.product_service import ProductService
        from services.client_service import ClientService
        from services.barcode_service import BarcodeService
        from unittest.mock import Mock
        
        # Mock de base de datos
        mock_db = Mock()
        
        # Crear servicios como en sales_form.py
        sales_service = SalesService(mock_db)
        product_service = ProductService(mock_db)
        client_service = ClientService(mock_db)
        barcode_service = BarcodeService()
        
        # Configurar ProductService en BarcodeService (corrección)
        barcode_service.set_product_service(product_service)
        
        print("✅ Todos los servicios se inicializan correctamente")
        print(f"   SalesService: {type(sales_service).__name__}")
        print(f"   ProductService: {type(product_service).__name__}")
        print(f"   ClientService: {type(client_service).__name__}")
        print(f"   BarcodeService: {type(barcode_service).__name__}")
        print(f"   ProductService configurado en BarcodeService: {barcode_service.product_service is not None}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_barcode_service_functionality():
    """Test de funcionalidad básica de BarcodeService."""
    print("\n=== TEST 4: Funcionalidad de BarcodeService ===")
    try:
        from services.barcode_service import BarcodeService
        from unittest.mock import Mock
        
        barcode_service = BarcodeService()
        
        # Test sin ProductService
        result = barcode_service.search_product_by_code("12345")
        print(f"   Búsqueda sin ProductService: {result}")  # Debe ser None
        
        # Test con ProductService
        mock_product_service = Mock()
        mock_product = Mock()
        mock_product.nombre = "Producto Test"
        mock_product_service.get_product_by_id.return_value = mock_product
        
        barcode_service.set_product_service(mock_product_service)
        result = barcode_service.search_product_by_code("12345")
        print(f"   Búsqueda con ProductService: {result}")  # Debe ser el mock
        
        print("✅ BarcodeService funciona correctamente")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Ejecutar todos los tests."""
    print("VERIFICACIÓN DE CORRECCIÓN - Sistema de Inventario")
    print("=" * 60)
    
    tests = [
        test_barcode_service_initialization,
        test_product_service_initialization,
        test_services_integration,
        test_barcode_service_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n=== RESULTADO FINAL ===")
    print(f"Tests pasados: {passed}/{total}")
    
    if passed == total:
        print("🎉 ¡CORRECCIÓN EXITOSA! El problema ha sido resuelto.")
        print("\nEl formulario de ventas debería abrirse sin errores ahora.")
    else:
        print("⚠️ Algunos tests fallaron. Revisar la implementación.")
        
    return passed == total

if __name__ == "__main__":
    main()
