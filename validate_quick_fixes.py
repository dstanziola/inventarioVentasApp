#!/usr/bin/env python3
"""
Validación rápida de correcciones críticas TDD.
"""

import sys
import os
import tempfile

# Agregar path del proyecto
sys.path.insert(0, 'D:\\inventario_app2')

def validate_critical_fixes():
    print("🧪 === VALIDACIÓN RÁPIDA CORRECCIONES TDD ===")
    print("="*50)
    
    issues_found = []
    fixes_validated = []
    
    # Test 1: Verificar DatabaseConnection
    print("\n1️⃣ Verificando DatabaseConnection...")
    try:
        from src.db.database import DatabaseConnection
        
        # Test instanciación
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        db_conn = DatabaseConnection(temp_db.name)
        connection = db_conn.get_connection()
        
        if connection:
            print("   ✅ DatabaseConnection funcional")
            fixes_validated.append("DatabaseConnection import y funcionalidad")
        
        db_conn.close()
        os.unlink(temp_db.name)
        
    except Exception as e:
        error_msg = f"DatabaseConnection error: {e}"
        print(f"   ❌ {error_msg}")
        issues_found.append(error_msg)
    
    # Test 2: Verificar psutil
    print("\n2️⃣ Verificando psutil...")
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        
        print(f"   ✅ psutil funcional (memoria: {memory_mb:.2f} MB)")
        fixes_validated.append("psutil disponible y funcional")
        
    except ImportError as e:
        error_msg = f"psutil no disponible: {e}"
        print(f"   ❌ {error_msg}")
        issues_found.append(error_msg)
    
    # Test 3: Verificar servicios críticos
    print("\n3️⃣ Verificando servicios críticos...")
    critical_services = [
        ('src.services.product_service', 'ProductService'),
        ('src.services.category_service', 'CategoryService'),
        ('src.services.sales_service', 'SalesService'),
    ]
    
    for module_name, class_name in critical_services:
        try:
            module = __import__(module_name, fromlist=[class_name])
            service_class = getattr(module, class_name)
            print(f"   ✅ {class_name}")
        except Exception as e:
            error_msg = f"{class_name} error: {e}"
            print(f"   ❌ {error_msg}")
            issues_found.append(error_msg)
    
    if not issues_found:
        fixes_validated.append("Servicios críticos importan correctamente")
    
    # Test 4: Verificar helpers
    print("\n4️⃣ Verificando helpers...")
    try:
        from src.helpers.validation_helper import ValidationHelper
        from src.helpers.logging_helper import LoggingHelper
        
        print("   ✅ ValidationHelper")
        print("   ✅ LoggingHelper")
        fixes_validated.append("Helpers disponibles")
        
    except ImportError as e:
        # Intentar desde utils como fallback
        try:
            from src.utils.validation_helper import ValidationHelper
            from src.utils.logging_helper import LoggingHelper
            
            print("   ✅ ValidationHelper (desde utils)")
            print("   ✅ LoggingHelper (desde utils)")
            fixes_validated.append("Helpers disponibles desde utils")
            
        except ImportError as e2:
            error_msg = f"Helpers no disponibles: {e}, {e2}"
            print(f"   ❌ {error_msg}")
            issues_found.append(error_msg)
    
    # Reporte final
    print("\n📊 === RESUMEN VALIDACIÓN ===")
    print("="*50)
    
    print(f"✅ CORRECCIONES VALIDADAS ({len(fixes_validated)}):")
    for fix in fixes_validated:
        print(f"   • {fix}")
    
    if issues_found:
        print(f"\n❌ PROBLEMAS ENCONTRADOS ({len(issues_found)}):")
        for issue in issues_found:
            print(f"   • {issue}")
    
    success_rate = len(fixes_validated) / (len(fixes_validated) + len(issues_found)) * 100 if (len(fixes_validated) + len(issues_found)) > 0 else 0
    print(f"\n📈 TASA DE ÉXITO: {success_rate:.1f}%")
    
    if success_rate >= 100:
        print("🎯 RESULTADO: TODAS LAS CORRECCIONES EXITOSAS")
        print("✅ Sistema listo para ejecutar tests completos")
        return True
    elif success_rate >= 75:
        print("⚠️ RESULTADO: CORRECCIONES MAYORMENTE EXITOSAS")
        print("🔍 Resolver problemas restantes")
        return False
    else:
        print("❌ RESULTADO: CORRECCIONES REQUIEREN ATENCIÓN")
        print("🛠️ Resolver problemas críticos")
        return False

if __name__ == '__main__':
    success = validate_critical_fixes()
    sys.exit(0 if success else 1)
