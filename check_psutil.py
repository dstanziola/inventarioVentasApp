#!/usr/bin/env python3
"""
Script para verificar e instalar psutil si es necesario.
"""

import sys
import subprocess

def check_and_install_psutil():
    print("🔍 Verificando psutil...")
    
    try:
        import psutil
        print("✅ psutil está disponible")
        
        # Probar funcionalidad básica
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        print(f"   Memoria del proceso: {memory_mb:.2f} MB")
        print("✅ psutil funcional")
        return True
        
    except ImportError:
        print("❌ psutil no está disponible")
        print("📦 Instalando psutil...")
        
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', 'psutil'
            ], capture_output=True, text=True, check=True)
            
            print("✅ psutil instalado exitosamente")
            
            # Verificar instalación
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            print(f"   Memoria del proceso: {memory_mb:.2f} MB")
            print("✅ psutil verificado después de instalación")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error instalando psutil: {e.stderr}")
            return False
        except ImportError as e:
            print(f"❌ Error importando psutil después de instalación: {e}")
            return False

if __name__ == '__main__':
    success = check_and_install_psutil()
    sys.exit(0 if success else 1)
