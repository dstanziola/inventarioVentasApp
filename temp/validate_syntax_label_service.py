"""
Script temporal para validar sintaxis de archivos Python.
"""

import subprocess
import sys
import os

def validate_python_file(file_path):
    """Validar sintaxis de un archivo Python."""
    try:
        result = subprocess.run([
            sys.executable, '-m', 'py_compile', file_path
        ], capture_output=True, text=True)
        
        print(f"=== VALIDACIÓN SINTAXIS: {os.path.basename(file_path)} ===")
        print(f"Código de retorno: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ Sintaxis correcta - Archivo compilado exitosamente")
            return True
        else:
            print("❌ Errores de sintaxis encontrados:")
            if result.stderr:
                print("STDERR:", result.stderr)
            if result.stdout:
                print("STDOUT:", result.stdout)
            return False
            
    except Exception as e:
        print(f"❌ Error validando archivo: {e}")
        return False

if __name__ == "__main__":
    # Validar LabelService
    label_service_path = "D:/inventario_app2/services/label_service.py"
    validate_python_file(label_service_path)
    
    # Validar test_label_service
    test_path = "D:/inventario_app2/tests/unit/services/test_label_service.py"
    validate_python_file(test_path)
