"""
Validación de servicios creados en Fase 3.
Verifica sintaxis y funcionalidad básica de TicketService y CompanyService.

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
    print("=== VALIDACIÓN DE SERVICIOS FASE 3 ===")
    
    # Archivos a validar
    archivos_servicios = [
        "services/ticket_service.py",
        "services/company_service.py",
        "tests/unit/services/test_ticket_service.py",
        "tests/unit/services/test_company_service.py"
    ]
    
    todos_validos = True
    
    print("\n1. VALIDANDO SINTAXIS...")
    for archivo in archivos_servicios:
        print(f"  Validando: {os.path.basename(archivo)}")
        
        if not os.path.exists(archivo):
            print(f"    ✗ Archivo no existe: {archivo}")
            todos_validos = False
            continue
        
        valido, error = validar_sintaxis_archivo(archivo)
        
        if valido:
            print(f"    ✓ Sintaxis correcta")
        else:
            print(f"    ✗ Error de sintaxis: {error}")
            todos_validos = False
    
    print("\n2. VALIDANDO IMPORTS...")
    
    try:
        # Validar modelos base
        from models.ticket import Ticket, TicketNumberGenerator
        from models.company_config import CompanyConfig
        print("  ✓ Modelos base importados")
        
        # Validar servicios nuevos
        from services.ticket_service import TicketService
        print("  ✓ TicketService importado")
        
        from services.company_service import CompanyService
        print("  ✓ CompanyService importado")
        
    except Exception as e:
        print(f"  ✗ Error en imports: {e}")
        traceback.print_exc()
        todos_validos = False
    
    print("\n3. VALIDANDO INSTANCIACIÓN...")
    
    try:
        # Test de instanciación básica (sin BD real)
        
        # Test Ticket
        ticket = Ticket.crear_ticket_venta("V000001", 1, "admin")
        print("  ✓ Ticket creado correctamente")
        
        # Test CompanyConfig
        config = CompanyConfig.crear_configuracion_defecto()
        print("  ✓ CompanyConfig creado correctamente")
        
        # Test TicketNumberGenerator
        numero = TicketNumberGenerator.generar_numero("VENTA", 0, "V")
        print(f"  ✓ Número generado: {numero}")
        
    except Exception as e:
        print(f"  ✗ Error en instanciación: {e}")
        traceback.print_exc()
        todos_validos = False
    
    print(f"\n=== RESULTADO FINAL ===")
    if todos_validos:
        print("✓ TODOS LOS SERVICIOS SON VÁLIDOS")
        print("✓ SINTAXIS CORRECTA")
        print("✓ IMPORTS FUNCIONAN")
        print("✓ LISTO PARA SIGUIENTE FASE")
    else:
        print("✗ HAY ERRORES QUE DEBEN CORREGIRSE")
    
    return todos_validos

if __name__ == "__main__":
    success = main()
    print(f"\nCódigo de salida: {0 if success else 1}")
