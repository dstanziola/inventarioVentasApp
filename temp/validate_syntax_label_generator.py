"""
Script de validación rápida de sintaxis para archivos Python.

Verifica que los archivos creados no tengan errores de sintaxis.
"""

import py_compile
import sys
import os

def validate_file(filepath):
    """Validar sintaxis de un archivo Python."""
    try:
        py_compile.compile(filepath, doraise=True)
        print(f"✅ {filepath} - Sintaxis válida")
        return True
    except py_compile.PyCompileError as e:
        print(f"❌ {filepath} - Error de sintaxis: {e}")
        return False

def main():
    files_to_validate = [
        "D:\\inventario_app2\\ui\\forms\\label_generator_form.py",
        "D:\\inventario_app2\\tests\\integration\\test_label_generator_form.py"
    ]
    
    all_valid = True
    
    for filepath in files_to_validate:
        if os.path.exists(filepath):
            if not validate_file(filepath):
                all_valid = False
        else:
            print(f"⚠️ {filepath} - Archivo no encontrado")
            all_valid = False
    
    if all_valid:
        print("\n🎉 Todos los archivos tienen sintaxis válida")
    else:
        print("\n💥 Hay errores de sintaxis que deben corregirse")
        sys.exit(1)

if __name__ == "__main__":
    main()
