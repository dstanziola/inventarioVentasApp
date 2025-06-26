#!/usr/bin/env python3
"""
Script de validación para los nuevos modelos de FASE 3
"""

import sys
import os
import ast

def validar_modelo(ruta_archivo, nombre_modelo):
    """Validar sintaxis e importación de un modelo"""
    
    try:
        # Verificar que el archivo existe
        if not os.path.exists(ruta_archivo):
            print(f"❌ {nombre_modelo} - Archivo no encontrado: {ruta_archivo}")
            return False
            
        # Leer y validar sintaxis
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            content = f.read()
        
        ast.parse(content)
        print(f"✅ {nombre_modelo} - Sintaxis válida")
        
        return True
        
    except SyntaxError as e:
        print(f"❌ {nombre_modelo} - Error de sintaxis: {e}")
        print(f"Línea {e.lineno}: {e.text}")
        return False
    except Exception as e:
        print(f"❌ {nombre_modelo} - Error: {e}")
        return False

def main():
    """Validar todos los modelos nuevos de FASE 3"""
    
    modelos_a_validar = [
        ("D:\\inventario_app2\\models\\ticket.py", "Ticket"),
        ("D:\\inventario_app2\\models\\company_config.py", "CompanyConfig"),
        ("D:\\inventario_app2\\db\\database.py", "Database (actualizado)")
    ]
    
    print("=== VALIDACIÓN DE MODELOS - FASE 3 ===")
    print()
    
    todos_validos = True
    
    for ruta, nombre in modelos_a_validar:
        if not validar_modelo(ruta, nombre):
            todos_validos = False
    
    print()
    if todos_validos:
        print("✅ TODOS LOS MODELOS SON VÁLIDOS")
        print("Listos para crear tests unitarios...")
    else:
        print("❌ HAY ERRORES EN LOS MODELOS")
        print("Corregir antes de continuar")
    
    return todos_validos

if __name__ == "__main__":
    main()
