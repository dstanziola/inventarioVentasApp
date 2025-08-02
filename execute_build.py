#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ejecutor de Construcción PyInstaller con Logo Personalizado
Creado para sesión de continuación Claude AI
Fecha: 2025-08-02
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Ejecutar construcción completa."""
    print("EJECUTANDO CONSTRUCCIÓN PYINSTALLER OPTIMIZADO")
    print("=" * 60)
    
    # Configurar paths
    project_root = Path(__file__).parent
    build_script = project_root / "build_config" / "build_portable_complete.py"
    
    print(f"Directorio del proyecto: {project_root}")
    print(f"Verificando logos disponibles...")
    
    # Verificar logos
    logos = [
        "logo 320x320.png",
        "logo 2000x2000.png", 
        "logo 940x788 transp.png"
    ]
    
    logos_encontrados = []
    for logo in logos:
        logo_path = project_root / logo
        if logo_path.exists():
            size_mb = logo_path.stat().st_size / (1024 * 1024)
            logos_encontrados.append(f"{logo} ({size_mb:.1f}MB)")
    
    print(f"   Logos encontrados: {len(logos_encontrados)}/3")
    for logo in logos_encontrados:
        print(f"      • {logo}")
    
    print(f"\n Script de construcción: {build_script.name}")
    
    if not build_script.exists():
        print(f"ERROR: Script no encontrado en {build_script}")
        return False
    
    print(f"   Script encontrado ({build_script.stat().st_size / 1024:.1f} KB)")
    
    # Verificar entorno virtual
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("   Entorno virtual activado")
    else:
        print("    ADVERTENCIA: Entorno virtual no detectado")
    
    print("\n🔨 INICIANDO CONSTRUCCIÓN...")
    print("-" * 40)
    
    try:
        # Cambiar al directorio del proyecto
        os.chdir(project_root)
        
        # Ejecutar script de construcción
        result = subprocess.run([
            sys.executable, 
            str(build_script)
        ], cwd=project_root, text=True, capture_output=True)
        
        # Mostrar salida
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("\nCONSTRUCCIÓN COMPLETADA EXITOSAMENTE")
            
            # Verificar archivos generados
            dist_dir = project_root / "dist"
            if dist_dir.exists():
                print(f"\nArchivos generados en {dist_dir}:")
                for item in dist_dir.iterdir():
                    if item.is_file():
                        size_mb = item.stat().st_size / (1024 * 1024)
                        print(f" {item.name} ({size_mb:.1f} MB)")
                    elif item.is_dir():
                        file_count = len(list(item.rglob('*')))
                        print(f" {item.name}/ ({file_count} archivos)")
            
            return True
        else:
            print(f"\n ERROR: Construcción falló con código {result.returncode}")
            return False
    
    except Exception as e:
        print(f"\n EXCEPCIÓN: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n PROCESO COMPLETADO - PAQUETE PORTABLE LISTO")
    else:
        print("\n PROCESO FALLÓ - REVISAR ERRORES ARRIBA")
    
    input("\nPresiona ENTER para continuar...")
