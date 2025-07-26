#!/usr/bin/env python3
"""
Ejecutor para el script de solución de cache ProductService
Session ID: 2025-07-22-productservice-method-error
"""

import sys
import subprocess
import os
from pathlib import Path

def main():
    """Ejecutar el script de solución y capturar resultados."""
    print("🚀 EJECUTANDO SOLUCIÓN DE CACHE - ProductService search_products")
    print("=" * 60)
    
    # Ubicar script de solución
    project_root = Path(__file__).parent
    fix_script = project_root / "fix_search_products_cache.py"
    
    if not fix_script.exists():
        print("❌ ERROR: Script de solución no encontrado")
        return False
    
    try:
        # Ejecutar script de solución
        print("🔧 Ejecutando fix_search_products_cache.py...")
        
        result = subprocess.run([
            sys.executable, str(fix_script)
        ], capture_output=True, text=True, cwd=project_root)
        
        # Mostrar output completo
        print("\n📊 RESULTADO DE LA EJECUCIÓN:")
        print("=" * 40)
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        
        print(f"\n📈 CÓDIGO DE SALIDA: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ SCRIPT EJECUTADO EXITOSAMENTE")
            return True
        else:
            print("❌ SCRIPT FALLÓ")
            return False
            
    except Exception as e:
        print(f"❌ ERROR EJECUTANDO SCRIPT: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
