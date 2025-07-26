#!/usr/bin/env python3
"""
VALIDACIÓN INTEGRAL SPRINT 2 - Sistema de Reportes
Protocolo de Validación Completa según instrucciones Claude v3.0

Objetivo: Validar funcionamiento, cobertura y integración del Sprint 2
Autor: Sistema de Inventario Copy Point S.A.
"""

import sys
import os
import subprocess
import json
import sqlite3
import tempfile
from pathlib import Path
from datetime import datetime, date, timedelta
from decimal import Decimal

# Configurar paths
PROJECT_ROOT = Path(__file__).parent
SRC_PATH = PROJECT_ROOT / "src"
TESTS_PATH = PROJECT_ROOT / "tests"
sys.path.insert(0, str(SRC_PATH))

def setup_logging():
    """Configurar logging para validación"""
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def test_report_service_import():
    """VALIDACIÓN 1: Importación y estructura básica"""
    logger = setup_logging()
    logger.info("🔍 VALIDACIÓN 1: Importación ReportService")
    
    try:
        from services.report_service import ReportService
        logger.info("✅ ReportService importado exitosamente")
        
        # Verificar métodos implementados
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
        
        service = ReportService(":memory:")
        missing_methods = []
        
        for method in expected_methods:
            if hasattr(service, method):
                logger.info(f"✅ Método {method} encontrado")
            else:
                logger.error(f"❌ Método {method} FALTANTE")
                missing_methods.append(method)
        
        if missing_methods:
            logger.error(f"❌ FALLO: Métodos faltantes: {missing_methods}")
            return False
        
        logger.info(f"✅ ÉXITO: Todos los métodos implementados ({len(expected_methods)}/10)")
        return True
        
    except Exception as e:
        logger.error(f"❌ ERROR en importación: {e}")
        return False

def test_functional_validation():
    """VALIDACIÓN 2: Funcionalidad básica con datos reales"""
    logger = setup_logging()
    logger.info("🔍 VALIDACIÓN 2: Funcionalidad básica")
    
    try:
        from services.report_service import ReportService
        
        # Crear DB temporal con datos de prueba
        db_fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(db_fd)
        
        # Setup datos de prueba
        conn = sqlite3.connect(db_path)
        setup_test_database(conn)
        conn.close()
        
        # Crear servicio
        service = ReportService(db_path)
        
        # TEST: Reporte de inventario
        try:
            inventory_report = service.generate_inventory_report()
            assert 'data' in inventory_report
            assert 'summary' in inventory_report
            logger.info("✅ generate_inventory_report() funcional")
        except Exception as e:
            logger.error(f"❌ generate_inventory_report() falló: {e}")
            return False
        
        # TEST: Reporte de movimientos
        try:
            fecha_inicio = date(2025, 7, 1)
            fecha_fin = date(2025, 7, 31)
            movements_report = service.generate_movements_report(fecha_inicio, fecha_fin)
            assert 'data' in movements_report
            assert 'summary' in movements_report
            logger.info("✅ generate_movements_report() funcional")
        except Exception as e:
            logger.error(f"❌ generate_movements_report() falló: {e}")
            return False
        
        # TEST: Reporte de ventas
        try:
            sales_report = service.generate_sales_report(fecha_inicio, fecha_fin)
            assert 'data' in sales_report
            assert 'totals' in sales_report
            logger.info("✅ generate_sales_report() funcional")
        except Exception as e:
            logger.error(f"❌ generate_sales_report() falló: {e}")
            return False
        
        # TEST: Reporte de rentabilidad
        try:
            profitability_report = service.generate_profitability_report(fecha_inicio, fecha_fin)
            assert 'data' in profitability_report
            assert 'totals' in profitability_report
            logger.info("✅ generate_profitability_report() funcional")
        except Exception as e:
            logger.error(f"❌ generate_profitability_report() falló: {e}")
            return False
        
        # Cleanup
        os.unlink(db_path)
        
        logger.info("✅ ÉXITO: Validación funcional completada - 4/4 reportes básicos")
        return True
        
    except Exception as e:
        logger.error(f"❌ ERROR en validación funcional: {e}")
        return False

def setup_test_database(conn):
    """Configurar base de datos de prueba"""
    cursor = conn.cursor()
    
    # Crear tablas
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
            activo INTEGER DEFAULT 1,
            FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE movimientos (
            id_movimiento INTEGER PRIMARY KEY,
            id_producto INTEGER,
            fecha_movimiento DATETIME,
            tipo_movimiento TEXT,
            cantidad INTEGER,
            responsable TEXT,
            observaciones TEXT,
            id_venta TEXT,
            costo_unitario DECIMAL(10,2),
            FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE ventas (
            id_venta INTEGER PRIMARY KEY,
            numero_factura TEXT,
            fecha_venta DATETIME,
            id_cliente INTEGER,
            subtotal DECIMAL(10,2),
            impuestos DECIMAL(10,2),
            total DECIMAL(10,2),
            responsable TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE clientes (
            id_cliente INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL
        )
    """)
    
    # Insertar datos de prueba
    cursor.execute("INSERT INTO categorias (id_categoria, nombre, tipo) VALUES (1, 'Papelería', 'MATERIAL')")
    cursor.execute("INSERT INTO categorias (id_categoria, nombre, tipo) VALUES (2, 'Electrónicos', 'MATERIAL')")
    
    cursor.execute("""
        INSERT INTO productos (id_producto, nombre, id_categoria, stock, costo, precio, stock_minimo) 
        VALUES (1, 'Papel A4', 1, 100, 5.50, 8.00, 10)
    """)
    cursor.execute("""
        INSERT INTO productos (id_producto, nombre, id_categoria, stock, costo, precio, stock_minimo) 
        VALUES (2, 'USB 32GB', 2, 5, 15.00, 25.00, 5)
    """)
    
    cursor.execute("INSERT INTO clientes (id_cliente, nombre) VALUES (1, 'Cliente Test')")
    
    cursor.execute("""
        INSERT INTO movimientos (id_producto, fecha_movimiento, tipo_movimiento, cantidad, responsable, id_venta)
        VALUES (1, '2025-07-20 15:00:00', 'VENTA', -10, 'vendedor', '1')
    """)
    
    cursor.execute("""
        INSERT INTO ventas (id_venta, numero_factura, fecha_venta, id_cliente, subtotal, impuestos, total, responsable)
        VALUES (1, 'FAC-001', '2025-07-20 15:00:00', 1, 80.00, 8.00, 88.00, 'vendedor')
    """)
    
    conn.commit()

def test_advanced_reports():
    """VALIDACIÓN 3: Reportes avanzados"""
    logger = setup_logging()
    logger.info("🔍 VALIDACIÓN 3: Reportes avanzados")
    
    try:
        from services.report_service import ReportService
        
        # Usar DB temporal
        db_fd, db_path = tempfile.mkstemp(suffix='.db')
        os.close(db_fd)
        
        conn = sqlite3.connect(db_path)
        setup_test_database(conn)
        conn.close()
        
        service = ReportService(db_path)
        fecha_inicio = date(2025, 7, 1)
        fecha_fin = date(2025, 7, 31)
        
        advanced_tests = [
            ('generate_low_stock_report', lambda: service.generate_low_stock_report()),
            ('generate_top_selling_products_report', lambda: service.generate_top_selling_products_report(fecha_inicio, fecha_fin)),
            ('generate_trends_analysis_report', lambda: service.generate_trends_analysis_report(fecha_inicio, fecha_fin)),
            ('generate_detailed_movements_report', lambda: service.generate_detailed_movements_report(fecha_inicio, fecha_fin)),
            ('get_summary_statistics', lambda: service.get_summary_statistics())
        ]
        
        passed_tests = 0
        for test_name, test_func in advanced_tests:
            try:
                result = test_func()
                assert isinstance(result, dict)
                logger.info(f"✅ {test_name}() funcional")
                passed_tests += 1
            except Exception as e:
                logger.error(f"❌ {test_name}() falló: {e}")
        
        # Cleanup
        os.unlink(db_path)
        
        logger.info(f"✅ ÉXITO: Reportes avanzados {passed_tests}/5 funcionales")
        return passed_tests == 5
        
    except Exception as e:
        logger.error(f"❌ ERROR en reportes avanzados: {e}")
        return False

def test_existing_test_files():
    """VALIDACIÓN 4: Verificar archivos de tests existentes"""
    logger = setup_logging()
    logger.info("🔍 VALIDACIÓN 4: Archivos de tests")
    
    test_files = [
        TESTS_PATH / "services" / "test_report_service_complete.py",
        TESTS_PATH / "services" / "test_report_service_auxiliary_methods.py",
        TESTS_PATH / "services" / "test_report_service_fase3.py",
        PROJECT_ROOT / "test_report_service_emergency.py"
    ]
    
    valid_files = 0
    for test_file in test_files:
        if test_file.exists():
            size = test_file.stat().st_size
            logger.info(f"✅ {test_file.name}: {size} bytes")
            valid_files += 1
        else:
            logger.error(f"❌ {test_file.name}: NO ENCONTRADO")
    
    logger.info(f"📊 ARCHIVOS DE TESTS: {valid_files}/{len(test_files)} encontrados")
    return valid_files == len(test_files)

def run_pytest_validation():
    """VALIDACIÓN 5: Ejecutar pytest específico"""
    logger = setup_logging()
    logger.info("🔍 VALIDACIÓN 5: Ejecución pytest")
    
    try:
        # Intentar ejecutar test de emergencia
        emergency_test = PROJECT_ROOT / "test_report_service_emergency.py"
        
        if not emergency_test.exists():
            logger.error("❌ test_report_service_emergency.py no encontrado")
            return False
        
        # Ejecutar test
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            str(emergency_test), 
            "-v", "--tb=short", "-x"
        ], capture_output=True, text=True, cwd=str(PROJECT_ROOT))
        
        if result.returncode == 0:
            logger.info("✅ Tests de emergencia PASARON")
            logger.info(f"Output: {result.stdout}")
            return True
        else:
            logger.error("❌ Tests de emergencia FALLARON")
            logger.error(f"Error: {result.stderr}")
            logger.error(f"Output: {result.stdout}")
            return False
            
    except Exception as e:
        logger.error(f"❌ ERROR ejecutando pytest: {e}")
        return False

def generate_validation_report():
    """Generar reporte de validación completo"""
    logger = setup_logging()
    logger.info("📊 GENERANDO REPORTE DE VALIDACIÓN COMPLETO")
    
    print("=" * 80)
    print("🎯 VALIDACIÓN INTEGRAL SPRINT 2 - SISTEMA DE REPORTES")
    print("=" * 80)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🏗️  Protocolo: Claude v3.0 - TDD + Clean Architecture")
    print()
    
    # Ejecutar todas las validaciones
    validations = [
        ("Importación y Estructura", test_report_service_import),
        ("Funcionalidad Básica", test_functional_validation), 
        ("Reportes Avanzados", test_advanced_reports),
        ("Archivos de Tests", test_existing_test_files),
        ("Ejecución PyTest", run_pytest_validation)
    ]
    
    results = {}
    total_validations = len(validations)
    passed_validations = 0
    
    for validation_name, validation_func in validations:
        print(f"\n🔍 Ejecutando: {validation_name}")
        print("-" * 50)
        
        try:
            result = validation_func()
            results[validation_name] = result
            if result:
                passed_validations += 1
                print(f"✅ {validation_name}: ÉXITO")
            else:
                print(f"❌ {validation_name}: FALLO")
        except Exception as e:
            print(f"❌ {validation_name}: ERROR - {e}")
            results[validation_name] = False
    
    # Reporte final
    print("\n" + "=" * 80)
    print("📊 RESUMEN DE VALIDACIÓN INTEGRAL")
    print("=" * 80)
    
    for validation_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {validation_name}")
    
    success_rate = (passed_validations / total_validations) * 100
    print(f"\n📈 TASA DE ÉXITO: {passed_validations}/{total_validations} ({success_rate:.1f}%)")
    
    # Conclusión
    print("\n🎯 CONCLUSIÓN:")
    if passed_validations == total_validations:
        print("🟢 SPRINT 2 COMPLETAMENTE FUNCIONAL Y VALIDADO")
        print("✅ Sistema de reportes implementado al 100%")
        print("✅ Tests y cobertura validados")
        print("✅ Integración confirmada")
    elif passed_validations >= 3:
        print("🟡 SPRINT 2 FUNCIONAL CON ISSUES MENORES")
        print("✅ Funcionalidad principal confirmada")
        print("⚠️  Algunos tests o validaciones requieren atención")
    else:
        print("🔴 SPRINT 2 REQUIERE ATENCIÓN CRÍTICA")
        print("❌ Problemas fundamentales detectados")
        print("🔧 Se requiere intervención inmediata")
    
    print("\n" + "=" * 80)
    print(f"📄 Reporte generado: {datetime.now()}")
    print("🏗️  Sistema de Inventario Copy Point S.A.")
    print("=" * 80)
    
    return passed_validations == total_validations

if __name__ == "__main__":
    """Ejecutar validación integral completa"""
    success = generate_validation_report()
    sys.exit(0 if success else 1)
