"""
Script simple de validación de sintaxis para main_window.py
"""

import py_compile
import sys

def validate_main_window():
    """Valida específicamente main_window.py"""
    try:
        print("🔍 Validando sintaxis de main_window.py...")
        py_compile.compile('ui/main/main_window.py', doraise=True)
        print("✅ main_window.py - SINTAXIS VÁLIDA")
        return True
    except py_compile.PyCompileError as e:
        print("❌ ERRORES DE SINTAXIS EN main_window.py:")
        print(str(e))
        return False
    except Exception as e:
        print(f"❌ Error al validar: {e}")
        return False

if __name__ == "__main__":
    validate_main_window()
