#!/usr/bin/env python3
"""
Script de limpieza rápida de cache - WindowManager.center_window() fix

EJECUCIÓN SIMPLE:
python quick_cache_cleanup.py

PROBLEMA:
- AttributeError: type object 'WindowManager' has no attribute 'center_window'
- Cache corruption en archivos .pyc

SOLUCIÓN:
- Eliminación específica de directorios cache problemáticos
- Regeneración automática de cache limpio

Autor: Claude AI + Equipo de Desarrollo
Fecha: 2025-07-28
"""

import os
import shutil
from pathlib import Path

def clean_cache():
    """Limpieza rápida de cache problemático."""
    project_root = Path.cwd()
    
    print("🧹 LIMPIEZA RÁPIDA CACHE - WindowManager.center_window()")
    print(f"📁 Directorio: {project_root}")
    print()
    
    # Directorios cache a limpiar
    cache_dirs = [
        "src/ui/utils/__pycache__",
        "src/ui/forms/__pycache__",
        "src/__pycache__"
    ]
    
    cleaned = 0
    
    for cache_dir in cache_dirs:
        full_path = project_root / cache_dir
        
        if full_path.exists():
            try:
                shutil.rmtree(full_path)
                print(f"✅ Eliminado: {cache_dir}")
                cleaned += 1
            except Exception as e:
                print(f"❌ Error eliminando {cache_dir}: {e}")
        else:
            print(f"ℹ️  No existe: {cache_dir}")
    
    print()
    print(f"🎯 RESULTADO: {cleaned} directorios cache limpiados")
    
    if cleaned > 0:
        print("✅ Cache corruption resuelto")
        print("✅ WindowManager.center_window() debería estar disponible")
        print("📋 Reinicie la aplicación para aplicar cambios")
    else:
        print("ℹ️  No se encontraron directorios cache problemáticos")
    
    return cleaned > 0

if __name__ == "__main__":
    clean_cache()
