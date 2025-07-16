#!/usr/bin/env python3
"""
Script para buscar la función create_movement_window en movement_form.py
"""

def find_function():
    """Buscar la función create_movement_window"""
    with open(r'D:\inventario_app2\src\ui\forms\movement_form.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"Total de líneas en el archivo: {len(lines)}")
    
    # Buscar líneas que contienen create_movement_window
    matches = []
    for i, line in enumerate(lines):
        if 'create_movement_window' in line:
            matches.append((i + 1, line.strip()))
    
    print("\nLíneas que contienen 'create_movement_window':")
    for line_num, content in matches:
        print(f"Línea {line_num}: {content}")
    
    # Buscar funciones def en las últimas 100 líneas
    print("\nFunciones en las últimas 100 líneas:")
    for i in range(max(0, len(lines) - 100), len(lines)):
        line = lines[i].strip()
        if line.startswith('def '):
            print(f"Línea {i + 1}: {line}")
    
    # Si el usuario dice que está en línea 2776, verificar esa área
    if len(lines) >= 2776:
        print(f"\nContenido alrededor de la línea 2776:")
        for i in range(2770, min(len(lines), 2785)):
            print(f"Línea {i + 1}: {lines[i].rstrip()}")
    else:
        print(f"\nEl archivo solo tiene {len(lines)} líneas")

if __name__ == "__main__":
    find_function()
