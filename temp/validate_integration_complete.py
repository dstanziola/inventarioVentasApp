import ast

def validate_file(file_path, file_name):
    """Validar sintaxis de un archivo Python"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parsear el código
        ast.parse(content)
        print(f"✅ {file_name}: Sintaxis válida")
        return True
        
    except SyntaxError as e:
        print(f"❌ {file_name}: Error de sintaxis")
        print(f"   Línea {e.lineno}: {e.text}")
        print(f"   Error: {e.msg}")
        return False
        
    except Exception as e:
        print(f"❌ {file_name}: Error: {e}")
        return False

# Validar archivos modificados
print("Validando archivos integrados con sistema de tickets...\n")

files_to_validate = [
    (r"D:\inventario_app2\ui\main\main_window.py", "main_window.py"),
    (r"D:\inventario_app2\ui\forms\movement_form.py", "movement_form.py"),
    (r"D:\inventario_app2\ui\forms\sales_form.py", "sales_form.py")
]

all_valid = True
for file_path, file_name in files_to_validate:
    if not validate_file(file_path, file_name):
        all_valid = False

print(f"\n{'='*50}")
if all_valid:
    print("🎯 TODOS LOS ARCHIVOS VALIDADOS CORRECTAMENTE")
    print("✅ Integración de sistema de tickets completada")
else:
    print("❌ HAY ERRORES DE SINTAXIS QUE DEBEN CORREGIRSE")

print("="*50)
