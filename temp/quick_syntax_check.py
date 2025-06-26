"""
Validación rápida de sintaxis para archivos de tests.
"""

import py_compile
import os

def validar_archivo(path):
    try:
        py_compile.compile(path, doraise=True)
        return True, "OK"
    except Exception as e:
        return False, str(e)

# Validar archivos de tests
archivos = [
    "tests/unit/models/test_ticket.py",
    "tests/unit/models/test_company_config.py",
    "models/ticket.py", 
    "models/company_config.py"
]

print("=== VALIDACIÓN DE SINTAXIS ===")

for archivo in archivos:
    if os.path.exists(archivo):
        valido, mensaje = validar_archivo(archivo)
        status = "✓" if valido else "✗"
        print(f"{status} {archivo}: {mensaje}")
    else:
        print(f"✗ {archivo}: No existe")

print("\n=== TESTS DE IMPORTS ===")

try:
    from models.ticket import Ticket, TicketNumberGenerator
    print("✓ Ticket importado correctamente")
    
    from models.company_config import CompanyConfig
    print("✓ CompanyConfig importado correctamente")
    
    # Test básico
    ticket = Ticket.crear_ticket_venta("V000001", 1, "admin")
    config = CompanyConfig()
    
    print("✓ Instancias creadas correctamente")
    print("✓ VALIDACIÓN COMPLETA - TODO OK")
    
except Exception as e:
    print(f"✗ Error: {e}")
