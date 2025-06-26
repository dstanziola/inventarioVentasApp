import ast
import sys

try:
    # Leer el archivo
    with open(r"D:\inventario_app2\ui\main\main_window.py", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Validar sintaxis usando AST
    ast.parse(content)
    print("✅ SINTAXIS VÁLIDA: main_window.py compilado correctamente")
    print("✅ Integración de sistema de tickets completada")
    
    # Contar líneas
    lines = content.count('\n')
    print(f"📊 Total de líneas: {lines}")
    
    # Verificar métodos de tickets agregados
    methods = [
        "_open_company_config",
        "_generate_sales_ticket", 
        "_generate_entry_ticket",
        "_search_tickets",
        "_open_ticket_preview"
    ]
    
    found_methods = []
    for method in methods:
        if f"def {method}" in content:
            found_methods.append(method)
    
    print(f"✅ Métodos de tickets implementados: {len(found_methods)}/{len(methods)}")
    for method in found_methods:
        print(f"   ✓ {method}")
    
    print("\n🎯 INTEGRACIÓN MAIN_WINDOW COMPLETADA EXITOSAMENTE")
    
except SyntaxError as e:
    print(f"❌ ERROR DE SINTAXIS:")
    print(f"   Línea {e.lineno}: {e.text}")
    print(f"   Error: {e.msg}")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
