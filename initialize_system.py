#!/usr/bin/env python3
"""
Script de Inicialización Automática del Sistema de Inventario

Este script:
1. Crea la base de datos si no existe
2. Inicializa el schema completo
3. Carga datos por defecto
4. Verifica la integridad del sistema
5. Ejecuta tests básicos

Fecha: 30/06/2025
Uso: python initialize_system.py
"""

import os
import sys
import logging
from pathlib import Path

# Agregar src/ al path para imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

def setup_logging():
    """Configurar logging para el script de inicialización."""
    log_dir = project_root / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'initialization.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def print_header(message):
    """Imprimir mensaje con formato de cabecera."""
    print(f"\n{'='*60}")
    print(f" {message}")
    print(f"{'='*60}")

def print_step(step, message):
    """Imprimir paso con formato."""
    print(f"\n[PASO {step}] {message}")

def initialize_database(logger):
    """Inicializar la base de datos completa."""
    try:
        from db.database import initialize_database, get_database_connection
        
        db_path = project_root / 'inventario.db'
        
        if db_path.exists():
            logger.info(f"Base de datos ya existe: {db_path}")
            db_conn = get_database_connection(str(db_path))
        else:
            logger.info(f"Creando nueva base de datos: {db_path}")
            db_conn = initialize_database(str(db_path))
        
        # Verificar integridad
        if db_conn.verify_schema_integrity():
            logger.info("✅ Integridad de base de datos verificada")
            return True, db_conn
        else:
            logger.error("❌ Problemas de integridad en la base de datos")
            return False, None
            
    except Exception as e:
        logger.error(f"❌ Error inicializando base de datos: {e}")
        return False, None

def verify_file_structure(logger):
    """Verificar estructura de archivos del proyecto."""
    logger.info("Verificando estructura de archivos...")
    
    required_dirs = [
        'src', 'src/db', 'src/models', 'src/services', 'src/ui',
        'tests', 'docs', 'config', 'logs', 'data'
    ]
    
    required_files = [
        'main.py', 'config.py', 'requirements.txt', 'styles.py',
        'src/db/database.py', 'src/models/__init__.py', 'src/services/__init__.py'
    ]
    
    missing_dirs = []
    missing_files = []
    
    # Verificar directorios
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if not full_path.exists():
            missing_dirs.append(dir_path)
            full_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Creado directorio: {dir_path}")
    
    # Verificar archivos
    for file_path in required_files:
        full_path = project_root / file_path
        if not full_path.exists():
            missing_files.append(file_path)
    
    if missing_files:
        logger.warning(f"❌ Archivos faltantes: {missing_files}")
        return False
    else:
        logger.info("✅ Estructura de archivos completa")
        return True

def test_imports(logger):
    """Probar imports críticos del sistema."""
    logger.info("Probando imports del sistema...")
    
    critical_imports = [
        ('db.database', 'DatabaseConnection'),
        ('models', 'Producto'),
        ('services', 'ProductService'),
        ('ui.main.main_window', 'MainWindow')
    ]
    
    failed_imports = []
    
    for module_name, class_name in critical_imports:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            logger.info(f"✅ Import exitoso: {module_name}.{class_name}")
        except Exception as e:
            logger.error(f"❌ Error import: {module_name}.{class_name} - {e}")
            failed_imports.append(f"{module_name}.{class_name}")
    
    if failed_imports:
        logger.error(f"❌ Imports fallidos: {failed_imports}")
        return False
    else:
        logger.info("✅ Todos los imports exitosos")
        return True

def verify_dependencies(logger):
    """Verificar dependencias Python instaladas."""
    logger.info("Verificando dependencias...")
    
    critical_dependencies = [
        'tkinter', 'sqlite3', 'reportlab', 'qrcode', 'PIL'
    ]
    
    missing_deps = []
    
    for dep in critical_dependencies:
        try:
            if dep == 'PIL':
                import PIL
            else:
                __import__(dep)
            logger.info(f"✅ Dependencia OK: {dep}")
        except ImportError:
            logger.error(f"❌ Dependencia faltante: {dep}")
            missing_deps.append(dep)
    
    if missing_deps:
        logger.error(f"❌ Instalar dependencias: pip install {' '.join(missing_deps)}")
        return False
    else:
        logger.info("✅ Todas las dependencias disponibles")
        return True

def run_basic_tests(logger, db_conn):
    """Ejecutar tests básicos del sistema."""
    logger.info("Ejecutando tests básicos...")
    
    try:
        # Test 1: Verificar conexión de base de datos
        cursor = db_conn.get_connection().cursor()
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        user_count = cursor.fetchone()[0]
        logger.info(f"✅ Test DB: {user_count} usuarios en sistema")
        
        # Test 2: Verificar que existe usuario admin
        cursor.execute("SELECT nombre_usuario FROM usuarios WHERE rol = 'ADMIN' LIMIT 1")
        admin_user = cursor.fetchone()
        if admin_user:
            logger.info(f"✅ Test Admin: Usuario administrador '{admin_user[0]}' existe")
        else:
            logger.error("❌ Test Admin: No existe usuario administrador")
            return False
        
        # Test 3: Verificar tablas principales
        expected_tables = ['productos', 'categorias', 'ventas', 'movimientos']
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        for table in expected_tables:
            if table in existing_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                logger.info(f"✅ Test Tabla: {table} ({count} registros)")
            else:
                logger.error(f"❌ Test Tabla: {table} no existe")
                return False
        
        logger.info("✅ Todos los tests básicos pasaron")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en tests básicos: {e}")
        return False

def create_sample_data(logger, db_conn):
    """Crear datos de muestra para testing."""
    logger.info("Creando datos de muestra...")
    
    try:
        cursor = db_conn.get_connection().cursor()
        
        # Verificar si ya existen productos
        cursor.execute("SELECT COUNT(*) FROM productos")
        product_count = cursor.fetchone()[0]
        
        if product_count > 0:
            logger.info(f"✅ Ya existen {product_count} productos, omitiendo datos de muestra")
            return True
        
        # Productos de muestra
        sample_products = [
            ("Papel Bond Carta", 1, "Papel bond tamaño carta", 100, 10, 0.50, 0.75, 7.00),
            ("Tinta Negra HP", 1, "Cartucho de tinta negra HP", 20, 5, 25.00, 40.00, 7.00),
            ("Servicio de Impresión", 3, "Servicio de impresión por página", 0, 0, 0.05, 0.10, 7.00)
        ]
        
        for product_data in sample_products:
            cursor.execute("""
                INSERT INTO productos (nombre, id_categoria, descripcion, stock, stock_minimo, 
                                     costo, precio, tasa_impuesto, activo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, product_data)
        
        db_conn.get_connection().commit()
        logger.info(f"✅ Creados {len(sample_products)} productos de muestra")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creando datos de muestra: {e}")
        return False

def generate_initialization_report(logger, results):
    """Generar reporte de inicialización."""
    report_path = project_root / 'logs' / 'initialization_report.txt'
    
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("REPORTE DE INICIALIZACIÓN DEL SISTEMA\n")
            f.write("="*50 + "\n\n")
            f.write(f"Fecha: {Path(__file__).stat().st_mtime}\n")
            f.write(f"Proyecto: {project_root}\n\n")
            
            f.write("RESULTADOS:\n")
            for step, success in results.items():
                status = "✅ EXITOSO" if success else "❌ FALLIDO"
                f.write(f"- {step}: {status}\n")
            
            total_steps = len(results)
            successful_steps = sum(results.values())
            f.write(f"\nRESUMEN: {successful_steps}/{total_steps} pasos exitosos\n")
            
            if successful_steps == total_steps:
                f.write("\n🎉 SISTEMA LISTO PARA USAR\n")
            else:
                f.write("\n⚠️ SISTEMA REQUIERE CORRECCIONES\n")
        
        logger.info(f"✅ Reporte generado: {report_path}")
        
    except Exception as e:
        logger.error(f"❌ Error generando reporte: {e}")

def main():
    """Función principal de inicialización."""
    print_header("INICIALIZACIÓN AUTOMÁTICA DEL SISTEMA")
    print(f"Directorio del proyecto: {project_root}")
    
    logger = setup_logging()
    logger.info("=== INICIANDO INICIALIZACIÓN AUTOMÁTICA ===")
    
    results = {}
    
    # Paso 1: Verificar estructura de archivos
    print_step(1, "Verificando estructura de archivos")
    results['Estructura de archivos'] = verify_file_structure(logger)
    
    # Paso 2: Verificar dependencias
    print_step(2, "Verificando dependencias Python")
    results['Dependencias'] = verify_dependencies(logger)
    
    # Paso 3: Probar imports
    print_step(3, "Probando imports del sistema")
    results['Imports del sistema'] = test_imports(logger)
    
    # Paso 4: Inicializar base de datos
    print_step(4, "Inicializando base de datos")
    db_success, db_conn = initialize_database(logger)
    results['Base de datos'] = db_success
    
    # Paso 5: Ejecutar tests básicos
    if db_success and db_conn:
        print_step(5, "Ejecutando tests básicos")
        results['Tests básicos'] = run_basic_tests(logger, db_conn)
        
        # Paso 6: Crear datos de muestra
        print_step(6, "Creando datos de muestra")
        results['Datos de muestra'] = create_sample_data(logger, db_conn)
        
        db_conn.close()
    else:
        results['Tests básicos'] = False
        results['Datos de muestra'] = False
    
    # Generar reporte final
    print_step(7, "Generando reporte de inicialización")
    generate_initialization_report(logger, results)
    
    # Resumen final
    print_header("RESUMEN DE INICIALIZACIÓN")
    
    total_steps = len(results)
    successful_steps = sum(results.values())
    
    print(f"\nPasos completados: {successful_steps}/{total_steps}")
    
    for step, success in results.items():
        status = "✅ EXITOSO" if success else "❌ FALLIDO"
        print(f"  {step}: {status}")
    
    if successful_steps == total_steps:
        print("\n🎉 ¡SISTEMA COMPLETAMENTE INICIALIZADO!")
        print("✅ El sistema está listo para usar")
        print("✅ Ejecutar: python main.py")
    else:
        print("\n⚠️ INICIALIZACIÓN INCOMPLETA")
        print("❌ Revise los errores arriba y corríjalos")
        print("❌ Vuelva a ejecutar este script")
    
    logger.info("=== INICIALIZACIÓN COMPLETADA ===")
    return successful_steps == total_steps

if __name__ == "__main__":
    main()
