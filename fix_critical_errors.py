"""
Script principal para corregir todos los errores identificados.
Se ejecuta independientemente y corrige:
1. Esquema de base de datos (columna 'activo')
2. Método is_scanner_available en BarcodeService
3. Inicialización de servicios

Fecha: 03/07/2025
Estado: CORRECCIONES CRÍTICAS
"""

import sqlite3
import os
import sys
import logging
from typing import List, Tuple

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fix_database_schema(db_path: str) -> bool:
    """
    Corrige el esquema de la base de datos.
    
    Args:
        db_path: Ruta a la base de datos
        
    Returns:
        True si se corrigió exitosamente, False en caso contrario
    """
    if not os.path.exists(db_path):
        logger.error(f"Base de datos no encontrada: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        logger.info(f"Corrigiendo esquema de base de datos: {db_path}")
        
        # Verificar tabla categorias
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='categorias'")
        if not cursor.fetchone():
            logger.error("Tabla 'categorias' no existe")
            return False
        
        # Verificar columnas existentes
        cursor.execute("PRAGMA table_info(categorias)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        logger.info(f"Columnas existentes en categorias: {column_names}")
        
        # Agregar columna 'activo' si no existe
        if 'activo' not in column_names:
            logger.info("Agregando columna 'activo' a tabla categorias")
            cursor.execute("ALTER TABLE categorias ADD COLUMN activo BOOLEAN DEFAULT 1")
            
            # Actualizar todos los registros existentes
            cursor.execute("UPDATE categorias SET activo = 1 WHERE activo IS NULL")
            
            logger.info("Columna 'activo' agregada exitosamente")
        else:
            logger.info("Columna 'activo' ya existe")
        
        # Verificar otras tablas importantes
        tables_to_check = ['productos', 'clientes', 'usuarios']
        
        for table_name in tables_to_check:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            if cursor.fetchone():
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                column_names = [col[1] for col in columns]
                
                if 'activo' not in column_names:
                    logger.info(f"Agregando columna 'activo' a tabla {table_name}")
                    cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN activo BOOLEAN DEFAULT 1")
                    cursor.execute(f"UPDATE {table_name} SET activo = 1 WHERE activo IS NULL")
                    logger.info(f"Columna 'activo' agregada a {table_name}")
                else:
                    logger.info(f"Columna 'activo' ya existe en {table_name}")
        
        conn.commit()
        
        # Verificar integridad
        cursor.execute("PRAGMA integrity_check")
        integrity_result = cursor.fetchone()[0]
        
        if integrity_result == "ok":
            logger.info("Integridad de base de datos: OK")
        else:
            logger.warning(f"Advertencia de integridad: {integrity_result}")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Error corrigiendo base de datos: {e}")
        return False

def verify_service_files() -> bool:
    """
    Verifica que los archivos de servicios estén correctos.
    
    Returns:
        True si los archivos están correctos, False en caso contrario
    """
    try:
        # Verificar BarcodeService
        barcode_service_path = "src/services/barcode_service.py"
        if not os.path.exists(barcode_service_path):
            logger.error(f"Archivo no encontrado: {barcode_service_path}")
            return False
        
        with open(barcode_service_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'is_scanner_available' not in content:
            logger.error("Método 'is_scanner_available' no encontrado en BarcodeService")
            return False
        else:
            logger.info("✓ Método 'is_scanner_available' encontrado en BarcodeService")
        
        # Verificar CategoryService
        category_service_path = "src/services/category_service.py"
        if not os.path.exists(category_service_path):
            logger.error(f"Archivo no encontrado: {category_service_path}")
            return False
        
        with open(category_service_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'def __init__(self, db_connection)' not in content:
            logger.error("Constructor de CategoryService no correcto")
            return False
        else:
            logger.info("✓ Constructor de CategoryService correcto")
        
        return True
        
    except Exception as e:
        logger.error(f"Error verificando archivos de servicios: {e}")
        return False

def run_test_validation() -> bool:
    """
    Ejecuta una validación rápida de las correcciones.
    
    Returns:
        True si la validación pasa, False en caso contrario
    """
    try:
        # Agregar src al path
        sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
        
        # Importar y probar CategoryService
        from db.database import get_database_connection
        from services.category_service import CategoryService
        from services.barcode_service import BarcodeService
        
        logger.info("Probando inicialización de servicios...")
        
        # Probar CategoryService
        db_connection = get_database_connection()
        category_service = CategoryService(db_connection)
        logger.info("✓ CategoryService inicializado correctamente")
        
        # Probar BarcodeService
        barcode_service = BarcodeService()
        if hasattr(barcode_service, 'is_scanner_available'):
            result = barcode_service.is_scanner_available()
            logger.info(f"✓ BarcodeService.is_scanner_available() = {result}")
        else:
            logger.error("✗ BarcodeService no tiene is_scanner_available")
            return False
        
        # Probar operaciones básicas de categorías
        categorias = category_service.get_all_categories()
        logger.info(f"✓ Categorías cargadas: {len(categorias)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error en validación: {e}")
        return False

def main():
    """Función principal de corrección."""
    print("=" * 60)
    print("CORRECCIÓN DE ERRORES CRÍTICOS DEL SISTEMA")
    print("=" * 60)
    
    success_count = 0
    total_fixes = 3
    
    # Corrección 1: Esquema de base de datos
    print("\\n1. Corrigiendo esquema de base de datos...")
    if fix_database_schema("inventario.db"):
        print("   ✓ Esquema de base de datos corregido")
        success_count += 1
    else:
        print("   ✗ Error corrigiendo esquema de base de datos")
    
    # Corrección 2: Verificar archivos de servicios
    print("\\n2. Verificando archivos de servicios...")
    if verify_service_files():
        print("   ✓ Archivos de servicios verificados")
        success_count += 1
    else:
        print("   ✗ Error en archivos de servicios")
    
    # Corrección 3: Validación de correcciones
    print("\\n3. Validando correcciones...")
    if run_test_validation():
        print("   ✓ Validación exitosa")
        success_count += 1
    else:
        print("   ✗ Error en validación")
    
    # Resumen
    print("\\n" + "=" * 60)
    print(f"RESUMEN: {success_count}/{total_fixes} correcciones exitosas")
    
    if success_count == total_fixes:
        print("✅ TODAS LAS CORRECCIONES APLICADAS EXITOSAMENTE")
        print("\\nEl sistema debería funcionar correctamente ahora.")
        print("Puede ejecutar: python main.py")
    else:
        print("❌ ALGUNAS CORRECCIONES FALLARON")
        print("\\nRevise los errores anteriores antes de ejecutar el sistema.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
