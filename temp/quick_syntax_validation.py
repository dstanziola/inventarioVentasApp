"""
Validación rápida de sintaxis - ejecutar directamente.
"""
import os
import ast

def validate_syntax(file_path):
    """Validar sintaxis Python usando AST."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Intentar parsear con AST
        ast.parse(content)
        print(f"✅ {os.path.basename(file_path)}: Sintaxis correcta")
        return True
        
    except SyntaxError as e:
        print(f"❌ {os.path.basename(file_path)}: Error de sintaxis en línea {e.lineno}: {e.msg}")
        return False
    except Exception as e:
        print(f"❌ {os.path.basename(file_path)}: Error: {e}")
        return False

# Validar archivos
files_to_validate = [
    "D:/inventario_app2/services/label_service.py",
    "D:/inventario_app2/tests/unit/services/test_label_service.py"
]

print("=== VALIDACIÓN DE SINTAXIS ===")
all_valid = True

for file_path in files_to_validate:
    if os.path.exists(file_path):
        valid = validate_syntax(file_path)
        all_valid = all_valid and valid
    else:
        print(f"❌ Archivo no encontrado: {file_path}")
        all_valid = False

print(f"\n{'✅ TODOS LOS ARCHIVOS VÁLIDOS' if all_valid else '❌ HAY ERRORES DE SINTAXIS'}")
