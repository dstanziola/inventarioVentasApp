
# Test básico de validación
import py_compile

filepath = r"D:\inventario_app2\ui\forms\label_generator_form.py"

try:
    py_compile.compile(filepath, doraise=True)
    print("Sintaxis válida")
except Exception as e:
    print(f"Error: {e}")
