"""
Script de validación de sintaxis para tests de modelos.
Verifica que los archivos de tests tengan sintaxis correcta.

Autor: Sistema TDD - FASE 3  
Fecha: 2025-06-25
"""

import sys
import os
import py_compile
import traceback

def validar_sintaxis_archivo(archivo_path):
    """Validar sintaxis de un archivo Python."""
    try:
        py_compile.compile(archivo_path, doraise=True)
        return True, None
    except py_compile.PyCompileError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def main():
    print("=== VALIDACIÓN DE SINTAXIS DE TESTS UNITARIOS ===")
    
    # Archivos a validar
    archivos_tests = [
        r"D:\inventario_app2\tests\unit\models\test_ticket.py",
        r"D:\inventario_app2\tests\unit\models\test_company_config.py",
        r"D:\inventario_app2\models\ticket.py",
        r"D:\inventario_app2\models\company_config.py"
    ]
    
    todos_validos = True
    
    for archivo in archivos_tests:
        print(f"\nValidando: {os.path.basename(archivo)}")
        
        if not os.path.exists(archivo):
            print(f"  ✗ Archivo no existe: {archivo}")
            todos_validos = False
            continue
        
        valido, error = validar_sintaxis_archivo(archivo)
        
        if valido:
            print(f"  ✓ Sintaxis correcta")
        else:
            print(f"  ✗ Error de sintaxis: {error}")
            todos_validos = False
    
    # Verificar imports básicos
    print("\n=== VERIFICACIÓN DE IMPORTS ===")
    
    try:
        sys.path.append(r"D:\inventario_app2")
        
        print("Importando modelo Ticket...")
        from models.ticket import Ticket, TicketNumberGenerator
        print("✓ Ticket importado correctamente")
        
        print("Importando modelo CompanyConfig...")
        from models.company_config import CompanyConfig
        print("✓ CompanyConfig importado correctamente")
        
        # Test básico de instanciación
        print("\nCreando instancias de prueba...")
        
        ticket = Ticket.crear_ticket_venta("V000001", 1, "admin")
        print("✓ Ticket creado correctamente")
        
        config = CompanyConfig.crear_configuracion_defecto()
        print("✓ CompanyConfig creado correctamente")
        
    except Exception as e:
        print(f"✗ Error en imports: {e}")
        traceback.print_exc()
        todos_validos = False
    
    print(f"\n=== RESULTADO FINAL ===")
    if todos_validos:
        print("✓ TODOS LOS ARCHIVOS SON VÁLIDOS")
        print("✓ Los modelos se pueden importar y instanciar correctamente")
        print("✓ LISTO PARA EJECUTAR TESTS UNITARIOS")
    else:
        print("✗ HAY ERRORES QUE DEBEN CORREGIRSE")
    
    return todos_validos

if __name__ == "__main__":
    success = main()
    print(f"\nCódigo de salida: {0 if success else 1}")
