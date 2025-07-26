#!/usr/bin/env python3
"""
Script de limpieza de cache específico para ProductService search_products bug
Ejecuta la limpieza real de directorios __pycache__ problemáticos
Session ID: 2025-07-22-productservice-method-error
"""

import os
import shutil
import sys
from pathlib import Path

def cleanup_cache_directories():
    """Limpiar directorios de cache problemáticos."""
    print("🧹 LIMPIEZA DE CACHE - ProductService search_products")
    print("=" * 55)
    
    project_root = Path(__file__).parent
    
    # Directorios críticos a limpiar
    cache_dirs_to_clean = [
        project_root / "src" / "ui" / "widgets" / "__pycache__",
        project_root / "src" / "services" / "__pycache__",
        project_root / "src" / "__pycache__"
    ]
    
    success_count = 0
    
    for cache_dir in cache_dirs_to_clean:
        print(f"\n🔍 Procesando: {cache_dir}")
        
        if cache_dir.exists():
            try:
                # Listar archivos antes de eliminar
                files = list(cache_dir.glob("*.pyc"))
                print(f"   📁 {len(files)} archivos .pyc encontrados")
                
                # Verificar archivos críticos
                critical_files = []
                for file in files:
                    if "product_search_widget" in file.name:
                        critical_files.append("product_search_widget.cpython-312.pyc")
                    elif "product_service" in file.name:
                        critical_files.append("product_service.cpython-312.pyc")
                
                if critical_files:
                    print(f"   ⚠️ Archivos problemáticos: {critical_files}")
                
                # Eliminar directorio completo
                shutil.rmtree(cache_dir)
                print(f"   ✅ ELIMINADO: {cache_dir}")
                success_count += 1
                
            except Exception as e:
                print(f"   ❌ ERROR: {e}")
        else:
            print(f"   ⏩ NO EXISTE: {cache_dir}")
    
    print(f"\n📊 RESULTADO: {success_count}/{len(cache_dirs_to_clean)} directorios limpiados")
    
    if success_count > 0:
        print("\n🎉 CACHE LIMPIADO EXITOSAMENTE")
        print("📝 Los archivos .pyc se regenerarán automáticamente")
        print("🔄 Reinicie la aplicación para aplicar cambios")
        return True
    else:
        print("\n⚠️ NO SE REQUIRIÓ LIMPIEZA")
        return True

if __name__ == "__main__":
    try:
        success = cleanup_cache_directories()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ ERROR CRÍTICO: {e}")
        sys.exit(1)
