"""
Migración: Añadir columna activo a tabla categorias
Fecha: 2025-07-03
Motivo: Resolver inconsistencia en tests y mantener consistencia arquitectónica

PROBLEMA IDENTIFICADO:
- Tests esperan columna 'activo' en tabla categorias
- Tabla categorias no tiene columna 'activo'
- Otros modelos (Cliente, Producto, Usuario) sí tienen campo 'activo'

SOLUCIÓN:
- Añadir columna 'activo' a tabla categorias
- Actualizar modelo Categoria con atributo 'activo'
- Mantener consistencia arquitectónica del sistema
"""

import sqlite3
from typing import Optional


def migrate_add_activo_to_categorias(db_path: str) -> bool:
    """
    Migración para añadir columna activo a tabla categorias.
    
    Args:
        db_path: Ruta a la base de datos
        
    Returns:
        True si la migración fue exitosa
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(categorias)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        if 'activo' in column_names:
            print("✅ Columna 'activo' ya existe en tabla categorias")
            return True
        
        # Añadir columna activo con valor por defecto 1 (activo)
        cursor.execute("""
            ALTER TABLE categorias 
            ADD COLUMN activo BOOLEAN DEFAULT 1
        """)
        
        # Actualizar todas las categorías existentes a activo=1
        cursor.execute("UPDATE categorias SET activo = 1 WHERE activo IS NULL")
        
        conn.commit()
        print("✅ Columna 'activo' añadida exitosamente a tabla categorias")
        
        # Verificar la migración
        cursor.execute("PRAGMA table_info(categorias)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        if 'activo' in column_names:
            print("✅ Migración verificada - columna 'activo' existe")
            return True
        else:
            print("❌ Error: columna 'activo' no se añadió correctamente")
            return False
            
    except Exception as e:
        print(f"❌ Error en migración: {e}")
        return False
    finally:
        if conn:
            conn.close()


def rollback_add_activo_to_categorias(db_path: str) -> bool:
    """
    Rollback de la migración (no es posible en SQLite sin reconstruir tabla).
    
    Args:
        db_path: Ruta a la base de datos
        
    Returns:
        False - SQLite no permite DROP COLUMN
    """
    print("⚠️ SQLite no permite DROP COLUMN")
    print("💡 Para rollback, se requiere reconstruir la tabla")
    return False


if __name__ == "__main__":
    # Test de migración
    print("🔄 Ejecutando migración: añadir columna activo a categorias")
    
    # Usar base de datos de desarrollo
    db_path = "D:\\inventario_app2\\inventario.db"
    
    if migrate_add_activo_to_categorias(db_path):
        print("✅ Migración completada exitosamente")
    else:
        print("❌ Migración falló")
