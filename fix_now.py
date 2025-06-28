"""
SOLUCION RAPIDA: Limpieza de cache para resolver error de Database
Ejecutar este archivo para solucionar el problema de importación.
"""

import os
import shutil
import sys

def limpiar_cache():
    """Eliminar todos los archivos de cache Python del proyecto."""
    project_dir = r"D:\inventario_app2"
    
    print("🧹 Limpiando cache de Python...")
    print(f"📁 Directorio: {project_dir}")
    print()
    
    # Contar archivos eliminados
    cache_dirs = 0
    pyc_files = 0
    
    # Caminar por todo el directorio del proyecto
    for root, dirs, files in os.walk(project_dir):
        # Eliminar directorios __pycache__
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                print(f"✅ Eliminado directorio: {pycache_path}")
                cache_dirs += 1
            except Exception as e:
                print(f"❌ Error eliminando {pycache_path}: {e}")
            
            # Remover de la lista para evitar entrar al directorio
            dirs.remove('__pycache__')
        
        # Eliminar archivos .pyc individuales
        for file in files:
            if file.endswith('.pyc'):
                pyc_path = os.path.join(root, file)
                try:
                    os.remove(pyc_path)
                    print(f"✅ Eliminado archivo: {pyc_path}")
                    pyc_files += 1
                except Exception as e:
                    print(f"❌ Error eliminando {pyc_path}: {e}")
    
    print()
    print(f"🧹 Limpieza completada:")
    print(f"   - Directorios __pycache__ eliminados: {cache_dirs}")
    print(f"   - Archivos .pyc eliminados: {pyc_files}")
    print()
    
    # Probar la aplicación
    print("🧪 Probando la aplicación...")
    try:
        # Cambiar al directorio del proyecto
        os.chdir(project_dir)
        
        # Agregar al path
        if project_dir not in sys.path:
            sys.path.insert(0, project_dir)
        
        # Probar importar main
        import main
        print("✅ ¡ÉXITO! La aplicación se puede importar correctamente.")
        print()
        print("🚀 Para ejecutar la aplicación:")
        print(f"   cd {project_dir}")
        print("   python main.py")
        
    except Exception as e:
        print(f"❌ Error al probar: {e}")
        print()
        print("💡 Soluciones adicionales:")
        print("1. Cierre y reabra el terminal/command prompt")
        print("2. Si usa un IDE, reinícielo completamente")
        print("3. Verifique que está en el directorio correcto")
        print("4. Ejecute: pip install -r requirements.txt")

if __name__ == "__main__":
    limpiar_cache()
