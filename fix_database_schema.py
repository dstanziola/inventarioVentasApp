"""
Script para verificar y corregir el esquema de la base de datos.
Agrega la columna 'activo' si no existe en la tabla categorias.
"""

import sqlite3
import os
import logging
from typing import List, Tuple

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_table_columns(cursor: sqlite3.Cursor, table_name: str) -> List[str]:
    """
    Obtiene las columnas de una tabla.
    
    Args:
        cursor: Cursor de la base de datos
        table_name: Nombre de la tabla
        
    Returns:
        Lista de nombres de columnas
    """
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    return [column[1] for column in columns]

def column_exists(cursor: sqlite3.Cursor, table_name: str, column_name: str) -> bool:
    """
    Verifica si una columna existe en una tabla.
    
    Args:
        cursor: Cursor de la base de datos
        table_name: Nombre de la tabla
        column_name: Nombre de la columna
        
    Returns:
        True si la columna existe, False en caso contrario
    """
    columns = get_table_columns(cursor, table_name)
    return column_name in columns

def add_column_if_not_exists(cursor: sqlite3.Cursor, table_name: str, column_name: str, column_type: str, default_value: str = None):
    """
    Agrega una columna a una tabla si no existe.
    
    Args:
        cursor: Cursor de la base de datos
        table_name: Nombre de la tabla
        column_name: Nombre de la columna
        column_type: Tipo de datos de la columna
        default_value: Valor por defecto (opcional)
    """
    if not column_exists(cursor, table_name, column_name):
        alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
        if default_value:
            alter_sql += f" DEFAULT {default_value}"
        
        cursor.execute(alter_sql)
        logger.info(f"Columna '{column_name}' agregada a la tabla '{table_name}'")
    else:
        logger.info(f"La columna '{column_name}' ya existe en la tabla '{table_name}'")

def fix_database_schema(db_path: str):
    """
    Corrige el esquema de la base de datos agregando columnas faltantes.
    
    Args:
        db_path: Ruta al archivo de base de datos
    """
    if not os.path.exists(db_path):
        logger.error(f"Base de datos no encontrada: {db_path}")
        return False
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        logger.info(f"Verificando esquema de base de datos: {db_path}")
        
        # Verificar y corregir tabla categorias
        logger.info("Verificando tabla 'categorias'...")
        
        # Verificar si la tabla existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='categorias'")
        if not cursor.fetchone():
            logger.error("La tabla 'categorias' no existe")
            return False
        
        # Agregar columna 'activo' si no existe
        add_column_if_not_exists(cursor, 'categorias', 'activo', 'BOOLEAN', '1')
        
        # Verificar otras tablas y columnas críticas
        tables_to_check = [
            ('productos', 'activo', 'BOOLEAN', '1'),
            ('clientes', 'activo', 'BOOLEAN', '1'),
            ('usuarios', 'activo', 'BOOLEAN', '1'),
        ]
        
        for table_name, column_name, column_type, default_value in tables_to_check:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            if cursor.fetchone():
                logger.info(f"Verificando tabla '{table_name}'...")
                add_column_if_not_exists(cursor, table_name, column_name, column_type, default_value)
            else:
                logger.warning(f"Tabla '{table_name}' no encontrada")
        
        # Confirmar cambios
        conn.commit()
        logger.info("Esquema de base de datos corregido exitosamente")
        
        # Verificar integridad
        cursor.execute("PRAGMA integrity_check")
        integrity_result = cursor.fetchone()[0]
        
        if integrity_result == "ok":
            logger.info("Integridad de base de datos verificada: OK")
        else:
            logger.warning(f"Problemas de integridad: {integrity_result}")
        
        # Cerrar conexión
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"Error corrigiendo esquema de base de datos: {e}")
        return False

def main():
    """Función principal para ejecutar correcciones."""
    db_path = "inventario.db"
    
    print("=== CORRECCIÓN DE ESQUEMA DE BASE DE DATOS ===")
    print(f"Base de datos: {db_path}")
    
    if fix_database_schema(db_path):
        print("✓ Esquema corregido exitosamente")
    else:
        print("✗ Error corrigiendo esquema")
    
    # También corregir base de datos de prueba si existe
    test_db_path = "test_critical_fixes.db"
    if os.path.exists(test_db_path):
        print(f"\\nCorrigiendo base de datos de prueba: {test_db_path}")
        if fix_database_schema(test_db_path):
            print("✓ Base de datos de prueba corregida")
        else:
            print("✗ Error corrigiendo base de datos de prueba")

if __name__ == "__main__":
    main()
