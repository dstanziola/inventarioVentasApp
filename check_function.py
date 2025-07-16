"""
Verificar si existe create_movement_window en movement_form.py
"""
import re

def check_file():
    try:
        with open(r'D:\inventario_app2\src\ui\forms\movement_form.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Contar líneas
        lines = content.split('\n')
        print(f"Total líneas: {len(lines)}")
        
        # Buscar create_movement_window
        if 'create_movement_window' in content:
            print("✅ ENCONTRADA: La función 'create_movement_window' SÍ existe en el archivo")
            
            # Encontrar líneas específicas
            for i, line in enumerate(lines):
                if 'create_movement_window' in line:
                    print(f"Línea {i+1}: {line.strip()}")
        else:
            print("❌ NO ENCONTRADA: La función 'create_movement_window' NO existe en el archivo")
        
        # Verificar línea 2776 específicamente
        if len(lines) >= 2776:
            line_2776 = lines[2775]  # índice 2775 = línea 2776
            print(f"\nContenido línea 2776: {line_2776.strip()}")
            
            # Mostrar contexto alrededor de línea 2776
            print("\nContexto alrededor línea 2776:")
            for i in range(2770, min(len(lines), 2785)):
                marker = ">>> " if i == 2775 else "    "
                print(f"{marker}Línea {i+1:4}: {lines[i].rstrip()}")
        else:
            print(f"\nEl archivo solo tiene {len(lines)} líneas, no llega a la 2776")
            
        print(f"\n🔍 Resultado: {'EXISTE' if 'create_movement_window' in content else 'NO EXISTE'}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_file()
