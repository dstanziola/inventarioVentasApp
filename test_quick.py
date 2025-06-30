"""
Test simple para verificar que el problema está resuelto.
"""

# Test directo de la corrección
print("Verificando corrección del problema de inicialización...")

try:
    # Paso 1: Verificar que BarcodeService se puede inicializar sin argumentos
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    from services.barcode_service import BarcodeService
    barcode_service = BarcodeService()
    print("✅ BarcodeService se inicializa correctamente")
    
    # Paso 2: Verificar que ProductService se puede inicializar con db_connection
    from services.product_service import ProductService
    from unittest.mock import Mock
    
    mock_db = Mock()
    product_service = ProductService(mock_db)
    print("✅ ProductService se inicializa correctamente")
    
    # Paso 3: Verificar que se puede configurar ProductService en BarcodeService
    barcode_service.set_product_service(product_service)
    print("✅ ProductService configurado en BarcodeService")
    
    # Paso 4: Verificar que todos los servicios pueden inicializarse juntos
    from services.sales_service import SalesService
    from services.client_service import ClientService
    
    sales_service = SalesService(mock_db)
    client_service = ClientService(mock_db)
    print("✅ Todos los servicios inicializados correctamente")
    
    print("\n🎉 CORRECCIÓN EXITOSA")
    print("El problema ha sido resuelto. El formulario de ventas debería abrirse sin errores.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("La corrección no funcionó completamente.")
