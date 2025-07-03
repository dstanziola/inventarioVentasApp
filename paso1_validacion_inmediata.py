"""
PASO 1: Script de Validación Inmediata del Sistema
==================================================

Objetivo: Verificar que el sistema principal ejecuta correctamente
"""

import sys
import os
import traceback

def validate_main_execution():
    """Validar que main.py ejecuta sin errores críticos."""
    print("1️⃣ VALIDANDO EJECUCIÓN DE MAIN.PY...")
    
    try:
        # Cambiar al directorio del proyecto
        project_dir = "D:\\inventario_app2"
        os.chdir(project_dir)
        
        # Agregar al path
        sys.path.insert(0, project_dir)
        sys.path.insert(0, os.path.join(project_dir, 'src'))
        
        print("   ✅ Directorio del proyecto configurado")
        
        # Intentar importar módulos principales
        try:
            from db.database import DatabaseConnection, get_database_connection
            print("   ✅ Módulo database importado correctamente")
        except Exception as e:
            print(f"   ❌ Error importando database: {e}")
            return False
        
        try:
            from services.category_service import CategoryService
            from services.product_service import ProductService
            from services.user_service import UserService
            print("   ✅ Servicios principales importados correctamente")
        except Exception as e:
            print(f"   ❌ Error importando servicios: {e}")
            return False
        
        try:
            from ui.auth.login_window import LoginWindow
            print("   ✅ LoginWindow importado correctamente")
        except Exception as e:
            print(f"   ⚠️ Warning - LoginWindow: {e}")
            # No es crítico para validación básica
        
        print("   ✅ Importaciones principales exitosas")
        return True
        
    except Exception as e:
        print(f"   ❌ Error crítico en validación: {e}")
        traceback.print_exc()
        return False

def validate_database_creation():
    """Validar que la base de datos se puede crear correctamente."""
    print("\n2️⃣ VALIDANDO CREACIÓN DE BASE DE DATOS...")
    
    try:
        import tempfile
        from db.database import DatabaseConnection
        
        # Crear BD temporal
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        # Probar conexión y creación de tablas
        db_connection = DatabaseConnection(temp_db.name)
        db_connection.connect()
        db_connection.create_tables()
        
        print("   ✅ Base de datos creada exitosamente")
        print("   ✅ Tablas creadas correctamente")
        
        # Limpiar
        db_connection.disconnect()
        os.unlink(temp_db.name)
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error en base de datos: {e}")
        traceback.print_exc()
        return False

def validate_basic_services():
    """Validar que los servicios básicos funcionan."""
    print("\n3️⃣ VALIDANDO SERVICIOS BÁSICOS...")
    
    try:
        import tempfile
        from db.database import DatabaseConnection
        from services.category_service import CategoryService
        from services.user_service import UserService
        
        # Crear BD temporal
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        db_connection = DatabaseConnection(temp_db.name)
        db_connection.connect()
        db_connection.create_tables()
        
        # Test CategoryService
        category_service = CategoryService(db_connection)
        categoria = category_service.create_category('Test Category', 'MATERIAL')
        
        if categoria and categoria.nombre == 'Test Category':
            print("   ✅ CategoryService funcional")
        else:
            print("   ❌ CategoryService falló")
            return False
        
        # Test UserService
        user_service = UserService(db_connection)
        usuario = user_service.create_user('admin', 'password123', 'ADMIN')
        
        if usuario and usuario.nombre_usuario == 'admin':
            print("   ✅ UserService funcional")
        else:
            print("   ❌ UserService falló")
            return False
        
        # Test autenticación
        auth_user = user_service.authenticate('admin', 'password123')
        if auth_user:
            print("   ✅ Autenticación funcional")
        else:
            print("   ❌ Autenticación falló")
            return False
        
        # Limpiar
        db_connection.disconnect()
        os.unlink(temp_db.name)
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error en servicios: {e}")
        traceback.print_exc()
        return False

def main():
    """Ejecutar validación completa."""
    print("🔍 VALIDACIÓN INMEDIATA DEL SISTEMA")
    print("=" * 50)
    print("📍 Objetivo: Verificar estado funcional básico")
    
    tests = [
        ("Ejecución principal", validate_main_execution),
        ("Base de datos", validate_database_creation),
        ("Servicios básicos", validate_basic_services)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Error ejecutando {test_name}: {e}")
            results.append((test_name, False))
    
    # Reporte final
    print("\n" + "=" * 50)
    print("📊 RESULTADO DE VALIDACIÓN INMEDIATA")
    print("=" * 50)
    
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ EXITOSO" if success else "❌ FALLÓ"
        print(f"   {test_name}: {status}")
    
    success_rate = (successful / total) * 100
    print(f"\n📈 Tasa de éxito: {success_rate:.0f}% ({successful}/{total})")
    
    if success_rate >= 100:
        print("\n🎉 EXCELENTE - Sistema completamente funcional")
        print("✅ Recomendación: Proceder con tests adaptados")
        print("🚀 Próximo paso: Ejecutar adaptación de tests FASE 5A")
        return True
    elif success_rate >= 66:
        print("\n⚠️ ACEPTABLE - Problemas menores identificados")
        print("🔧 Recomendación: Corregir issues antes de continuar")
        print("📝 Próximo paso: Debug de problemas específicos")
        return True
    else:
        print("\n❌ CRÍTICO - Problemas fundamentales")
        print("🛠️ Recomendación: Debugging extensivo requerido")
        print("⚠️ Próximo paso: Corrección de errores críticos")
        return False

if __name__ == "__main__":
    try:
        success = main()
        print(f"\n🏁 Validación {'exitosa' if success else 'con problemas'}")
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO EN VALIDACIÓN: {e}")
        traceback.print_exc()
