#!/usr/bin/env python3
"""
LIMPIEZA RÁPIDA DE CACHE - ProductService.search_products Fix
Problema: Cache .pyc obsoleto causa AttributeError falso positivo
Solución: Eliminar cache específico y regenerar
"""

import os
import shutil
from pathlib import Path

def main():
    print("🔧 LIMPIEZA RÁPIDA DE CACHE")
    print("=" * 40)
    
    project_root = Path(__file__).parent
    
    # Directorios críticos a limpiar
    critical_dirs = [
        "src/ui/widgets/__pycache__",
        "src/services/__pycache__",
        "src/application/services/__pycache__"
    ]
    
    cleaned = 0
    
    for cache_dir in critical_dirs:
        full_path = project_root / cache_dir
        if full_path.exists():
            try:
                shutil.rmtree(full_path)
                print(f"✅ Eliminado: {cache_dir}")
                cleaned += 1
            except Exception as e:
                print(f"❌ Error: {cache_dir} - {e}")
        else:
            print(f"⏩ No existe: {cache_dir}")
    
    # Limpiar archivos .pyc sueltos
    pyc_files = [
        "src/ui/widgets/product_search_widget.pyc",
        "src/services/product_service.pyc",
        "src/application/services/auth_service.pyc"
    ]
    
    for pyc_file in pyc_files:
        full_path = project_root / pyc_file
        if full_path.exists():
            try:
                full_path.unlink()
                print(f"✅ Eliminado archivo: {pyc_file}")
                cleaned += 1
            except Exception as e:
                print(f"❌ Error archivo: {pyc_file} - {e}")
    
    print(f"\n🎯 RESULTADO: {cleaned} elementos limpiados")
    
    if cleaned > 0:
        print("\n✅ CACHE LIMPIADO EXITOSAMENTE")
        print("🚀 Reiniciar aplicación para regenerar cache")
    else:
        print("\n⚠️ No se encontraron archivos para limpiar")
    
    # Verificar que los archivos fuente están correctos
    print("\n🔍 VERIFICACIÓN FINAL:")
    
    # Verificar ProductService
    product_service = project_root / "src/services/product_service.py"
    if product_service.exists():
        content = product_service.read_text(encoding='utf-8')
        if "def search_products(" in content:
            print("✅ ProductService.search_products() verificado")
        else:
            print("❌ search_products() NO ENCONTRADO")
    
    # Verificar AuthService  
    auth_service = project_root / "src/application/services/auth_service.py"
    if auth_service.exists():
        content = auth_service.read_text(encoding='utf-8')
        if "self._session_manager.is_authenticated" in content and "self._session_manager.is_authenticated()" not in content:
            print("✅ AuthService.is_authenticated corrección verificada")
        else:
            print("❌ AuthService.is_authenticated NO CORREGIDO")
    
    print("\n🎉 LIMPIEZA COMPLETADA")
    return True

if __name__ == "__main__":
    main()
