#!/usr/bin/env python3
"""
Script para ejecutar validación TDD y mostrar resultados.
"""

import subprocess
import sys
import os

def main():
    # Cambiar al directorio del proyecto
    os.chdir('D:\\inventario_app2')
    
    print("🧪 Ejecutando Test TDD de Validación...")
    print("="*50)
    
    # Ejecutar el test TDD
    result = subprocess.run([
        sys.executable, 'tests/test_critical_fixes_validation.py'
    ], capture_output=True, text=True)
    
    print("SALIDA:")
    print(result.stdout)
    
    if result.stderr:
        print("\nERRORES:")
        print(result.stderr)
    
    print(f"\nCÓDIGO DE RETORNO: {result.returncode}")
    
    return result.returncode

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
