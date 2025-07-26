#!/usr/bin/env python3
"""
LIMPIEZA EMERGENCIA - Cache Corruption MovementEntryForm + Events
Resolver errores reportados:
1. "Campo obligatorio 'code' faltante en producto" 
2. "No se pudo obtener información del usuario actual"

Session ID: 2025-07-25-emergency-cache-cleanup
"""

import os
import shutil
from pathlib import Path

def main():
    print("🚨 LIMPIEZA EMERGENCIA DE CACHE")
    print("=" * 50)
    
    project_root = Path(__file__).parent
    
    # Directorios críticos a limpiar
    critical_cache_dirs = [
        "src/ui/shared/__pycache__",          # events.py
        "src/ui/forms/__pycache__",           # movement_entry_form.py
        "src/ui/widgets/__pycache__",         # product_search_widget.py
        "src/services/__pycache__",           # product_service.py
        "src/application/services/__pycache__" # auth_service.py
    ]
    
    cleaned_count = 0
    
    for cache_dir in critical_cache_dirs:
        full_path = project_root / cache_dir
        if full_path.exists():
            try:
                shutil.rmtree(full_path)
                print(f"✅ Eliminado: {cache_dir}")
                cleaned_count += 1
            except Exception as e:
                print(f"❌ Error: {cache_dir} - {e}")
        else:
            print(f"⏩ No existe: {cache_dir}")
    
    print(f"\n🎯 LIMPIEZA COMPLETADA: {cleaned_count} directorios")
    print("\n🚀 PRÓXIMOS PASOS:")
    print("1. Reiniciar la aplicación")
    print("2. Python regenerará cache limpio")
    print("3. Probar subformulario MovementEntry")
    print("4. Los errores deben estar resueltos")
    
    return cleaned_count > 0

if __name__ == "__main__":
    main()
