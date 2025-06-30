"""
Script de verificación para la corrección de product_form.py
Valida que CategoryService se inicialice correctamente con la conexión de base de datos.
"""

import sys
import os
import traceback

# Agregar src al path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_root, 'src'))

def test_category_service_initialization():
    """Test de inicialización de CategoryService."""
    print("=== VERIFICANDO INICIALIZACIÓN DE CATEGORYSERVICE ===")
    
    try:
        # Test 1: Importar CategoryService
        print("1. Importando CategoryService...")
        from services.category_service import CategoryService
        print("   ✓ CategoryService importado correctamente")
        
        # Test 2: Verificar que requiere db_connection
        print("2. Verificando que requiere db_connection...")
        try:
            service = CategoryService()
            print("   ✗ ERROR: CategoryService se creó sin argumentos (no debería pasar)")
            return False
        except TypeError as e:
            if "missing 1 required positional argument" in str(e) and "db_connection" in str(e):
                print("   ✓ CategoryService requiere db_connection correctamente")
            else:
                print(f"   ✗ Error inesperado: {e}")
                return False
        
        # Test 3: Importar DatabaseConnection
        print("3. Importando DatabaseConnection...")
        from db.database import DatabaseConnection, get_database_connection
        print("   ✓ DatabaseConnection importado correctamente")
        
        # Test 4: Crear conexión de prueba
        print("4. Creando conexión de base de datos...")
        db_connection = get_database_connection("test_connection.db")
        print(f"   ✓ Conexión creada: {type(db_connection)}")
        
        # Test 5: Inicializar CategoryService con conexión
        print("5. Inicializando CategoryService con conexión...")
        category_service = CategoryService(db_connection)
        print("   ✓ CategoryService inicializado correctamente")
        
        # Test 6: Verificar que el servicio tiene la conexión
        print("6. Verificando conexión en el servicio...")
        if hasattr(category_service, 'db') and category_service.db is not None:
            print("   ✓ CategoryService tiene conexión de base de datos")
        else:
            print("   ✗ CategoryService no tiene conexión de base de datos")
            return False
        
        # Limpiar archivo de prueba
        if os.path.exists("test_connection.db"):
            os.remove("test_connection.db")
        
        print("\n🎉 TODAS LAS VERIFICACIONES PASARON - CategoryService corregido")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR EN VERIFICACIÓN: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_product_form_imports():
    """Test de importaciones de product_form.py"""
    print("\n=== VERIFICANDO IMPORTS DE PRODUCT_FORM ===")
    
    try:
        # Test imports del formulario
        print("1. Importando módulos de product_form...")
        
        from db.database import get_database_connection
        print("   ✓ get_database_connection importado")
        
        from services.product_service import ProductService
        print("   ✓ ProductService importado")
        
        from services.category_service import CategoryService
        print("   ✓ CategoryService importado")
        
        from models.producto import Producto
        print("   ✓ Producto importado")
        
        # Test imports opcionales
        try:
            from services.label_service import LabelService
            from services.barcode_service import BarcodeService
            from utils.barcode_utils import validate_barcode, BarcodeUtils, generate_product_code
            print("   ✓ Módulos de códigos de barras disponibles")
            barcode_support = True
        except ImportError as e:
            print(f"   ⚠ Módulos de códigos de barras no disponibles: {e}")
            barcode_support = False
        
        print(f"\n✓ IMPORTS VERIFICADOS - Soporte códigos: {barcode_support}")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR EN IMPORTS: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_product_form_initialization():
    """Test de inicialización de ProductWindow (sin UI)."""
    print("\n=== VERIFICANDO INICIALIZACIÓN DE PRODUCT_FORM ===")
    
    try:
        import tkinter as tk
        from unittest.mock import patch, Mock
        
        # Crear root window mock
        root = tk.Tk()
        root.withdraw()
        
        # Mock de messagebox para evitar ventanas emergentes
        with patch('tkinter.messagebox.showerror') as mock_error:
            print("1. Importando ProductWindow...")
            from ui.forms.product_form import ProductWindow
            print("   ✓ ProductWindow importado correctamente")
            
            print("2. Creando instancia de ProductWindow...")
            
            # Intentar crear ProductWindow
            try:
                product_window = ProductWindow(root)
                print("   ✓ ProductWindow creado correctamente")
                
                # Verificar que los servicios se inicializaron
                if hasattr(product_window, 'category_service') and product_window.category_service is not None:
                    print("   ✓ CategoryService inicializado en ProductWindow")
                else:
                    print("   ✗ CategoryService no inicializado en ProductWindow")
                    return False
                
                if hasattr(product_window, 'product_service') and product_window.product_service is not None:
                    print("   ✓ ProductService inicializado en ProductWindow")
                else:
                    print("   ✗ ProductService no inicializado en ProductWindow")
                    return False
                
                # Cerrar ventana
                if hasattr(product_window, 'root'):
                    product_window.root.destroy()
                
                print("\n🎉 PRODUCT_FORM FUNCIONA CORRECTAMENTE")
                return True
                
            except Exception as e:
                print(f"   ✗ Error creando ProductWindow: {e}")
                print(f"   Traceback: {traceback.format_exc()}")
                return False
            
        root.destroy()
        
    except Exception as e:
        print(f"\n❌ ERROR EN INICIALIZACIÓN: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

def main():
    """Función principal de verificación."""
    print("VERIFICACIÓN DE CORRECCIÓN - PRODUCT_FORM.PY")
    print("=" * 50)
    
    success = True
    
    # Test 1: CategoryService
    if not test_category_service_initialization():
        success = False
    
    # Test 2: Imports
    if not test_product_form_imports():
        success = False
    
    # Test 3: ProductWindow
    if not test_product_form_initialization():
        success = False
    
    # Resultado final
    print("\n" + "=" * 50)
    if success:
        print("🎉 VERIFICACIÓN EXITOSA - PROBLEMA CORREGIDO")
        print("\nEl formulario de productos debería funcionar correctamente.")
        print("Puede intentar abrir el formulario de productos ahora.")
    else:
        print("❌ VERIFICACIÓN FALLIDA - REVISAR PROBLEMAS")
        print("\nQuedan problemas por resolver.")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
