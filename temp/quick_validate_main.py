import ast

# Validar sintaxis del archivo main_window.py
file_path = r"D:\inventario_app2\ui\main\main_window.py"

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        source_code = f.read()
    
    # Intentar parsear el código
    ast.parse(source_code)
    print("✅ Sintaxis válida en main_window.py")
    print("✅ Archivo validado correctamente")
    
except SyntaxError as e:
    print("❌ Error de sintaxis:")
    print(f"Línea {e.lineno}: {e.text}")
    print(f"Error: {e.msg}")
    
except Exception as e:
    print(f"❌ Error al validar: {e}")
