#!/usr/bin/env python3
"""
Script para ejecutar tests del ReportService - FASE 2

Valida que el ReportService esté implementado correctamente
y que todos los tests pasen exitosamente.
"""

import sys
import os
import subprocess
from pathlib import Path

# Agregar el directorio raíz al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_report_service_tests():
    """Ejecuta tests específicos del ReportService"""
    
    print("🧪 EJECUTANDO TESTS DEL REPORTSERVICE - FASE 2")
    print("=" * 50)
    
    os.chdir(project_root)
    
    # Ejecutar tests específicos del ReportService
    test_files = [
        "tests/unit/reports/test_report_service.py"
    ]
    
    for test_file in test_files:
        print(f"\n📋 Ejecutando: {test_file}")
        print("-" * 30)
        
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", test_file, "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            print(f"Return code: {result.returncode}")
            
            if result.stdout:
                print("STDOUT:")
                print(result.stdout)
            
            if result.stderr:
                print("STDERR:")
                print(result.stderr)
                
            if result.returncode == 0:
                print(f"✅ {test_file} - EXITOSO")
            else:
                print(f"❌ {test_file} - FALLÓ")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {test_file} - TIMEOUT")
        except Exception as e:
            print(f"💥 {test_file} - ERROR: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 TESTS DEL REPORTSERVICE COMPLETADOS")

if __name__ == "__main__":
    run_report_service_tests()
