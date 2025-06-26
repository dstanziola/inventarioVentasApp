#!/usr/bin/env python3
"""
Script de validación para verificar la sintaxis del archivo database.py
"""

import sys
import os
import ast

def validate_database():
    """Validar sintaxis del archivo database.py"""
    
    db_file = "D:\\inventario_app2\\db\\database.py"
    
    try:
        # Verificar que el archivo existe
        if not os.path.exists(db_file):
            print(f"❌ Archivo no encontrado: {db_file}")
            return False
            
        # Leer contenido
        with open(db_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Validar sintaxis con AST
        ast.parse(content)
        
        print("✅ database.py - Sintaxis válida")
        
        # Intentar importar el módulo
        sys.path.insert(0, "D:\\inventario_app2")
        
        try:
            from db.database import DatabaseConnection
            print("✅ database.py - Importación exitosa")
            
            # Verificar que la clase principal funciona
            if hasattr(DatabaseConnection, 'create_tables'):
                print("✅ database.py - Métodos principales disponibles")
            else:
                print("❌ database.py - Falta método create_tables")
                
        except ImportError as e:
            print(f"❌ database.py - Error de importación: {e}")
            return False
            
        return True
        
    except SyntaxError as e:
        print(f"❌ database.py - Error de sintaxis: {e}")
        print(f"Línea {e.lineno}: {e.text}")
        return False
    except Exception as e:
        print(f"❌ Error al validar database.py: {e}")
        return False

if __name__ == "__main__":
    validate_database()
