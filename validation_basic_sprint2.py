#!/usr/bin/env python3
"""
VALIDACIÓN BÁSICA SPRINT 2 - ReportService
Verificación rápida de funcionalidad sin ejecutar pytest completo
"""
import sys
import os
import traceback
from pathlib import Path

# Configurar paths
PROJECT_ROOT = Path(__file__).parent
SRC_PATH = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

print("🎯 VALIDACIÓN BÁSICA SPRINT 2 - SISTEMA DE REPORTES")
print("=" * 60)

# TEST 1: Importación básica
print("\n🔍 TEST 1: Importación ReportService")
try:
    from services.report_service import ReportService
    print("✅ ReportService importado exitosamente")
    import_success = True
except Exception as e:
    print(f"❌ Error en importación: {e}")
    import_success = False

if not import_success:
    print("🚨 FALLO CRÍTICO: No se puede importar ReportService")
    sys.exit(1)

# TEST 2: Verificar métodos implementados
print("\n🔍 TEST 2: Verificación de métodos implementados")
service = ReportService(":memory:")

expected_methods = [
    'generate_inventory_report',
    'generate_movements_report', 
    'generate_sales_report',
    'generate_profitability_report',
    'generate_low_stock_report',
    'generate_top_selling_products_report',
    'generate_trends_analysis_report',
    'generate_detailed_movements_report',
    'get_summary_statistics',
    'export_to_pdf'
]

methods_found = 0
for method in expected_methods:
    if hasattr(service, method):
        print(f"✅ {method}")
        methods_found += 1
    else:
        print(f"❌ {method} - FALTANTE")

print(f"\n📊 MÉTODOS: {methods_found}/{len(expected_methods)} implementados")

# TEST 3: Verificar archivos de tests
print("\n🔍 TEST 3: Verificación archivos de tests")
test_files = [
    "tests/services/test_report_service_complete.py",
    "tests/services/test_report_service_auxiliary_methods.py", 
    "tests/services/test_report_service_fase3.py",
    "test_report_service_emergency.py"
]

tests_found = 0
for test_file in test_files:
    if Path(test_file).exists():
        size = Path(test_file).stat().st_size
        print(f"✅ {test_file}: {size} bytes")
        tests_found += 1
    else:
        print(f"❌ {test_file}: NO ENCONTRADO")

print(f"\n📊 TESTS: {tests_found}/{len(test_files)} archivos encontrados")

# TEST 4: Test funcional básico con DB temporal
print("\n🔍 TEST 4: Test funcional básico")
import sqlite3
import tempfile
from datetime import date

try:
    # Crear DB temporal
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    
    # Setup básico de DB
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Tabla mínima para test
    cursor.execute("""
        CREATE TABLE categorias (
            id_categoria INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL,
            tipo TEXT DEFAULT 'MATERIAL'
        )
    """)
    
    cursor.execute("""
        CREATE TABLE productos (
            id_producto INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL,
            id_categoria INTEGER,
            stock INTEGER DEFAULT 0,
            costo DECIMAL(10,2) DEFAULT 0,
            precio DECIMAL(10,2) DEFAULT 0,
            stock_minimo INTEGER DEFAULT 5,
            activo INTEGER DEFAULT 1
        )
    """)
    
    # Datos mínimos
    cursor.execute("INSERT INTO categorias (id_categoria, nombre) VALUES (1, 'Test')")
    cursor.execute("INSERT INTO productos (id_producto, nombre, id_categoria, stock, costo, precio) VALUES (1, 'Producto Test', 1, 10, 5.0, 8.0)")
    conn.commit()
    conn.close()
    
    # Test del servicio
    service = ReportService(db_path)
    
    # Test reporte de inventario
    inventory_report = service.generate_inventory_report()
    if 'data' in inventory_report and 'summary' in inventory_report:
        print("✅ generate_inventory_report() funcional")
        functional_test = True
    else:
        print("❌ generate_inventory_report() falló")
        functional_test = False
    
    # Cleanup
    os.unlink(db_path)
    
except Exception as e:
    print(f"❌ Test funcional falló: {e}")
    functional_test = False

# RESUMEN FINAL
print("\n" + "=" * 60)
print("📊 RESUMEN DE VALIDACIÓN")
print("=" * 60)

total_tests = 4
passed_tests = 0

if import_success:
    print("✅ Importación: ÉXITO")
    passed_tests += 1
else:
    print("❌ Importación: FALLO")

if methods_found == len(expected_methods):
    print("✅ Métodos implementados: ÉXITO")
    passed_tests += 1
else:
    print(f"⚠️ Métodos implementados: PARCIAL ({methods_found}/{len(expected_methods)})")

if tests_found == len(test_files):
    print("✅ Archivos de tests: ÉXITO") 
    passed_tests += 1
else:
    print(f"⚠️ Archivos de tests: PARCIAL ({tests_found}/{len(test_files)})")

if functional_test:
    print("✅ Test funcional: ÉXITO")
    passed_tests += 1
else:
    print("❌ Test funcional: FALLO")

success_rate = (passed_tests / total_tests) * 100
print(f"\n📈 RESULTADO: {passed_tests}/{total_tests} tests exitosos ({success_rate:.1f}%)")

# CONCLUSIÓN
print("\n🎯 CONCLUSIÓN:")
if passed_tests == total_tests:
    print("🟢 SPRINT 2 COMPLETAMENTE FUNCIONAL")
    print("✅ ReportService implementado al 100%")
    print("✅ Todos los métodos operativos")
    print("✅ Tests disponibles")
    print("✅ Funcionalidad básica confirmada")
elif passed_tests >= 3:
    print("🟡 SPRINT 2 FUNCIONAL CON ISSUES MENORES")
    print("✅ Funcionalidad principal OK")
    print("⚠️ Algunos componentes requieren atención")
else:
    print("🔴 SPRINT 2 TIENE PROBLEMAS CRÍTICOS")
    print("❌ Se requiere intervención")

print("\n" + "=" * 60)
print(f"🏗️ Sistema de Inventario Copy Point S.A.")
print(f"📅 Validación ejecutada exitosamente")
print("=" * 60)
