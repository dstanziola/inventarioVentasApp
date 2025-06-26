"""
Script temporal para ejecutar tests unitarios de modelos.
Valida que los tests pasen correctamente siguiendo TDD.

Autor: Sistema TDD - FASE 3
Fecha: 2025-06-25
"""

import subprocess
import sys
import os

def main():
    # Cambiar al directorio del proyecto
    project_dir = r"D:\inventario_app2"
    os.chdir(project_dir)
    
    print("=== EJECUTANDO TESTS UNITARIOS DE MODELOS ===")
    print(f"Directorio de trabajo: {os.getcwd()}")
    print()
    
    # Verificar que Python puede importar los módulos
    print("1. Verificando imports...")
    try:
        sys.path.append(project_dir)
        from models.ticket import Ticket, TicketNumberGenerator
        from models.company_config import CompanyConfig
        print("✓ Modelos importados correctamente")
    except ImportError as e:
        print(f"✗ Error al importar modelos: {e}")
        return False
    
    # Ejecutar tests con pytest
    print("\n2. Ejecutando tests con pytest...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/unit/models/test_ticket.py",
            "tests/unit/models/test_company_config.py",
            "-v",
            "--tb=short",
            "--no-header"
        ], capture_output=True, text=True, timeout=60)
        
        print("RESULTADO DE TESTS:")
        print(result.stdout)
        
        if result.stderr:
            print("\nERRORES/WARNINGS:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("\n✓ TODOS LOS TESTS PASARON EXITOSAMENTE")
            return True
        else:
            print(f"\n✗ TESTS FALLARON (código de retorno: {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ Tests tomaron demasiado tiempo (timeout)")
        return False
    except Exception as e:
        print(f"✗ Error ejecutando tests: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
