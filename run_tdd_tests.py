#!/usr/bin/env python3
"""
Script para ejecutar tests TDD de refactorización Service Container.
"""

import subprocess
import sys
import os

def run_tests():
    # Cambiar al directorio del proyecto
    os.chdir('D:/inventario_app2')
    
    test_files = [
        'tests/test_category_form_container.py',
        'tests/test_client_form_container.py', 
        'tests/test_sales_form_container.py',
        'tests/test_movement_form_container.py'
    ]
    
    results = {}
    
    for test_file in test_files:
        print(f"\n=== Ejecutando {test_file} ===")
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pytest', test_file, '-v'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            results[test_file] = {
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
            print(f"Return code: {result.returncode}")
            if result.stdout:
                print("STDOUT:")
                print(result.stdout[:1000])  # Limitar salida
            if result.stderr:
                print("STDERR:")
                print(result.stderr[:500])
                
        except Exception as e:
            print(f"Error ejecutando {test_file}: {e}")
            results[test_file] = {'error': str(e)}
    
    print(f"\n=== RESUMEN DE RESULTADOS ===")
    for test_file, result in results.items():
        if 'error' in result:
            print(f"{test_file}: ERROR - {result['error']}")
        else:
            status = "PASS" if result['returncode'] == 0 else "FAIL"
            print(f"{test_file}: {status} (code: {result['returncode']})")
    
    return results

if __name__ == "__main__":
    run_tests()
