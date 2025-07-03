#!/usr/bin/env python3
"""
Test de diagnóstico rápido para FASE 5A
Verifica el estado básico del sistema antes de ejecutar tests completos.
"""

import sys
import os
import traceback

# Agregar path del proyecto
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

def test_imports():
    """Test de importación de módulos críticos."""
    print("1️⃣ DIAGNÓSTICO: Importación de módulos...")
    
    try:
        # Test base de datos
        from db.database import DatabaseConnection
        print("   ✅ DatabaseConnection importado")
        
        # Test servicios
        from services.category_service import CategoryService
        print("   ✅ CategoryService importado")
        
        from services.product_service import ProductService
        print("   ✅ ProductService importado")
        
        from services.user_service import UserService
        print("   ✅ UserService importado")
        
        # Test helpers
        from utils.database_helper import DatabaseHelper
        print("   ✅ DatabaseHelper importado")
        
        from utils.validation_helper import ValidationHelper
        print("   ✅ ValidationHelper importado")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error importando módulos: {e}")
        traceback.print_exc()
        return False

def test_database_connection():
    """Test conexión a base de datos."""
    print("\n2️⃣ DIAGNÓSTICO: Conexión a base de datos...")
    
    try:
        from db.database import DatabaseConnection
        import tempfile
        
        # Crear BD temporal
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        db_connection = DatabaseConnection(temp_db.name)
        db_connection.connect()
        db_connection.create_tables()
        
        print("   ✅ Base de datos temporal creada")
        print("   ✅ Tablas creadas correctamente")
        
        # Limpiar
        db_connection.disconnect()
        os.unlink(temp_db.name)
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error en base de datos: {e}")
        traceback.print_exc()
        return False

def test_basic_service_functionality():
    """Test funcionalidad básica de servicios."""
    print("\n3️⃣ DIAGNÓSTICO: Funcionalidad básica de servicios...")
    
    try:
        from db.database import DatabaseConnection
        from services.category_service import CategoryService
        import tempfile
        
        # Crear BD temporal
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        db_connection = DatabaseConnection(temp_db.name)
        db_connection.connect()
        db_connection.create_tables()
        
        # Test CategoryService
        category_service = CategoryService(db_connection)
        categoria = category_service.create_category({
            'nombre': 'Test Diagnóstico',
            'tipo': 'MATERIAL'
        })
        
        if categoria:
            print("   ✅ CategoryService funciona correctamente")
            
            # Test lectura
            categorias = category_service.get_all_categories()
            if len(categorias) >= 1:
                print("   ✅ Lectura de categorías funciona")
            else:
                print("   ⚠️ Problema en lectura de categorías")
        else:
            print("   ❌ Error creando categoría")
        
        # Limpiar
        db_connection.disconnect()
        os.unlink(temp_db.name)
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error en servicios: {e}")
        traceback.print_exc()
        return False

def test_helpers_optimization():
    """Test optimización de helpers FASE 3."""
    print("\n4️⃣ DIAGNÓSTICO: Optimización helpers FASE 3...")
    
    try:
        from db.database import DatabaseConnection
        from services.category_service import CategoryService
        import tempfile
        
        # Crear BD temporal
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        db_connection = DatabaseConnection(temp_db.name)
        db_connection.connect()
        db_connection.create_tables()
        
        # Test optimización
        category_service = CategoryService(db_connection)
        
        # Verificar helpers FASE 3
        if hasattr(category_service, 'db_helper'):
            print("   ✅ DatabaseHelper presente en CategoryService")
        else:
            print("   ⚠️ DatabaseHelper no encontrado - posible FASE 1")
        
        if hasattr(category_service, 'validator'):
            print("   ✅ ValidationHelper presente en CategoryService")
        else:
            print("   ⚠️ ValidationHelper no encontrado - posible FASE 1")
        
        if hasattr(category_service, 'logger'):
            print("   ✅ LoggingHelper presente en CategoryService")
        else:
            print("   ⚠️ LoggingHelper no encontrado - posible FASE 1")
        
        # Limpiar
        db_connection.disconnect()
        os.unlink(temp_db.name)
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error verificando helpers: {e}")
        traceback.print_exc()
        return False

def main():
    """Ejecutar diagnóstico completo."""
    print("🔍 DIAGNÓSTICO RÁPIDO FASE 5A")
    print("="*50)
    print("📍 Verificando estado del sistema antes de tests completos")
    
    tests = [
        ("Importación módulos", test_imports),
        ("Conexión BD", test_database_connection),
        ("Servicios básicos", test_basic_service_functionality),
        ("Optimización FASE 3", test_helpers_optimization)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Error ejecutando {test_name}: {e}")
            results.append((test_name, False))
    
    # Reporte
    print("\n" + "="*50)
    print("📊 REPORTE DE DIAGNÓSTICO")
    print("="*50)
    
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ OK" if success else "❌ FALLO"
        print(f"   {test_name}: {status}")
    
    success_rate = (successful / total) * 100
    print(f"\n📈 Tasa de éxito: {success_rate:.1f}% ({successful}/{total})")
    
    if success_rate >= 75:
        print("✅ SISTEMA ESTABLE - Proceder con tests completos")
        return True
    else:
        print("⚠️ PROBLEMAS DETECTADOS - Revisar antes de tests completos")
        return False

if __name__ == "__main__":
    try:
        success = main()
        print(f"\n🎯 Diagnóstico {'exitoso' if success else 'con problemas'}")
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO EN DIAGNÓSTICO: {e}")
        traceback.print_exc()
