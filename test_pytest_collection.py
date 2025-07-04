"""
Script simple para probar pytest collection y validar correcciones.
"""

import subprocess
import sys
import os

def test_pytest_collection():
    print("🧪 Probando pytest collection...")
    
    os.chdir('D:\\inventario_app2')
    
    # Test 1: Verificar que pytest puede ejecutarse
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest', '--version'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ pytest disponible")
        else:
            print(f"❌ pytest no disponible: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando pytest: {e}")
        return False
    
    # Test 2: Intentar collection en test crítico
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            '--collect-only', '-q',
            'tests/test_fase5a_critical_validation.py'
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ pytest puede recolectar test_fase5a_critical_validation.py")
            return True
        else:
            print(f"❌ pytest collection falló:")
            print(f"STDERR: {result.stderr}")
            print(f"STDOUT: {result.stdout}")
            return False
            
    except Exception as e:
        print(f"❌ Error en pytest collection: {e}")
        return False

if __name__ == '__main__':
    success = test_pytest_collection()
    sys.exit(0 if success else 1)
