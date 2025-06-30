"""
Verificación Mejorada del Sistema - Corrige problemas identificados
"""

import os
import sys
import sqlite3
import logging
from pathlib import Path

# Configurar logging básico
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def quick_system_check():
    """Verificación rápida del estado del sistema."""
    print("VERIFICACIÓN RÁPIDA DEL SISTEMA DE INVENTARIO")
    print("=" * 50)
    
    status = {
        "structure": False,
        "database": False,
        "imports": False,
        "services": False
    }
    
    # 1. Verificar estructura de directorios
    print("1. Verificando estructura de directorios...")
    required_dirs = ['src', 'src/db', 'src/services', 'src/models', 'src/ui', 'data']
    missing_dirs = []
    
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"   ❌ Directorios faltantes: {missing_dirs}")
        # Crear directorios faltantes
        for dir_path in missing_dirs:
            os.makedirs(dir_path, exist_ok=True)
            print(f"   ✓ Creado: {dir_path}")
    else:
        print("   ✓ Estructura de directorios OK")
    
    status["structure"] = True
    
    # 2. Verificar base de datos
    print("\n2. Verificando base de datos...")
    db_path = os.path.join("data", "inventario.db")
    
    if not os.path.exists(db_path):
        print("   ❌ Base de datos no existe")
        print("   ⚠️  EJECUTE: python repair_database.py")
        status["database"] = False
    else:
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Verificar tabla crítica
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='categorias';")
            if cursor.fetchone():
                print("   ✓ Base de datos existe y tiene estructura")
                
                # Verificar datos básicos
                cursor.execute("SELECT COUNT(*) FROM categorias;")
                cat_count = cursor.fetchone()[0]
                print(f"   ✓ Categorías en BD: {cat_count}")
                
                status["database"] = True
            else:
                print("   ❌ Base de datos sin estructura completa")
                print("   ⚠️  EJECUTE: python repair_database.py")
                status["database"] = False
            
            conn.close()
            
        except sqlite3.Error as e:
            print(f"   ❌ Error de base de datos: {e}")
            status["database"] = False
    
    # 3. Verificar imports (sin crear archivos de prueba)
    print("\n3. Verificando imports...")
    
    # Agregar src al path si no está
    src_path = os.path.join(os.getcwd(), 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    try:
        # Import críticos
        from db.database import get_database_connection
        print("   ✓ get_database_connection import OK")
        
        from services.category_service import CategoryService
        print("   ✓ CategoryService import OK")
        
        from services.product_service import ProductService
        print("   ✓ ProductService import OK")
        
        from models.producto import Producto
        print("   ✓ Producto model import OK")
        
        status["imports"] = True
        
    except ImportError as e:
        print(f"   ❌ Error de import: {e}")
        status["imports"] = False
    
    # 4. Verificar servicios (solo si imports OK y BD existe)
    print("\n4. Verificando servicios...")
    
    if status["imports"] and status["database"]:
        try:
            # Probar conexión sin crear archivos temporales
            db_conn = get_database_connection()
            
            if db_conn:
                print("   ✓ Conexión de base de datos OK")
                
                # Probar CategoryService
                cat_service = CategoryService(db_conn)
                categories = cat_service.get_all_categories()
                print(f"   ✓ CategoryService OK ({len(categories)} categorías)")
                
                # Probar ProductService
                prod_service = ProductService(db_conn)
                products = prod_service.get_all_products()
                print(f"   ✓ ProductService OK ({len(products)} productos)")
                
                status["services"] = True
            else:
                print("   ❌ No se pudo obtener conexión de base de datos")
                status["services"] = False
                
        except Exception as e:
            print(f"   ❌ Error en servicios: {e}")
            status["services"] = False
    else:
        print("   ⏭️  Omitido (requiere imports y BD)")
        status["services"] = False
    
    # Resumen final
    print("\n" + "=" * 50)
    print("RESUMEN DE VERIFICACIÓN")
    print("=" * 50)
    
    total_checks = len(status)
    passed_checks = sum(status.values())
    
    for check, result in status.items():
        icon = "✓" if result else "❌"
        print(f"{icon} {check.upper()}: {'OK' if result else 'FALLA'}")
    
    print(f"\nResultado: {passed_checks}/{total_checks} verificaciones exitosas")
    
    if all(status.values()):
        print("\n🎉 ¡SISTEMA COMPLETAMENTE FUNCIONAL!")
        print("Ejecute: python main.py")
        print("Usuario: admin | Contraseña: admin123")
    elif status["database"] and status["imports"]:
        print("\n⚠️  Sistema casi listo, servicios con problemas menores")
        print("Intente ejecutar: python main.py")
    else:
        print("\n❌ SISTEMA REQUIERE REPARACIÓN")
        if not status["database"]:
            print("1. Ejecute: python repair_database.py")
        print("2. Luego ejecute: python quick_check_fixed.py")
    
    print("=" * 50)
    return all(status.values())

if __name__ == "__main__":
    quick_system_check()
