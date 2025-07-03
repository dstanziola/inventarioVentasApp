"""
Script para ejecutar test de validación de modelos corregido.
FASE 5A - Gap Analysis - Test Crítico #1
"""

import sys
import os
import subprocess

def ejecutar_test():
    """Ejecutar el test de validación de modelos."""
    print("="*70)
    print("🧪 EJECUTANDO TEST DE VALIDACIÓN DE MODELOS")
    print("="*70)
    
    # Cambiar al directorio del proyecto
    os.chdir("D:/inventario_app2")
    
    # Ejecutar el test
    try:
        result = subprocess.run(
            [sys.executable, "tests/test_models_validation.py"],
            capture_output=True,
            text=True,
            timeout=120  # 2 minutos timeout
        )
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        
        print(f"\nRETURN CODE: {result.returncode}")
        
        if result.returncode == 0:
            print("\n✅ TEST COMPLETADO EXITOSAMENTE")
        else:
            print("\n❌ TEST FALLÓ")
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ TEST TIMEOUT - Se excedió el tiempo límite")
        return False
    except Exception as e:
        print(f"❌ ERROR EJECUTANDO TEST: {e}")
        return False

if __name__ == "__main__":
    success = ejecutar_test()
    sys.exit(0 if success else 1)
