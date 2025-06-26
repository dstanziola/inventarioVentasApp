#!/usr/bin/env python3
"""
Script para validar la sintaxis del archivo main_window.py modificado
"""

import subprocess
import sys
import os

def validate_syntax():
    """Valida la sintaxis del archivo main_window.py"""
    
    file_path = r"D:\inventario_app2\ui\main\main_window.py"
    
    print("Validando sintaxis de main_window.py...")
    print(f"Archivo: {file_path}")
    
    if not os.path.exists(file_path):
        print("❌ El archivo no existe")
        return False
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "py_compile", file_path
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Sintaxis válida en main_window.py")
            print("✅ Archivo validado correctamente")
            return True
        else:
            print("❌ Error de sintaxis:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error al validar: {e}")
        return False

if __name__ == "__main__":
    validate_syntax()
