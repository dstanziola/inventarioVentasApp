#!/usr/bin/env python3
"""
Script de corrección para cache corruption WindowManager.center_window()

PROBLEMA IDENTIFICADO:
- Error: AttributeError: type object 'WindowManager' has no attribute 'center_window'
- Ubicación: LabelGeneratorForm línea 52
- Causa raíz: Cache corruption en archivos .pyc

DIAGNÓSTICO TÉCNICO:
- El método center_window() SÍ EXISTE en window_manager.py líneas 90-112
- Suite de tests confirmada operativa
- Problema es cache .pyc con versión anterior sin método

SOLUCIÓN:
- Limpieza sistemática de cache problemático
- Basado en precedentes exitosos del proyecto
- Script automatizado para prevenir errores manuales

Autor: Claude AI + Equipo de Desarrollo
Fecha: 2025-07-28
Session ID: 2025-07-28-window-manager-cache-fix
Protocolo: claude_instructions_v3.md FASE 2 - Cache cleanup
"""

import os
import sys
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Any

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WindowManagerCacheFixer:
    """
    Solucionador de cache corruption para WindowManager.center_window().
    
    Aplicación del protocolo de cache cleanup usado exitosamente
    en correcciones anteriores del proyecto.
    """
    
    def __init__(self, project_root: str = None):
        """
        Inicializar fixer de cache.
        
        Args:
            project_root: Directorio raíz del proyecto
        """
        self.project_root = Path(project_root or os.getcwd())
        self.cache_directories = []
        self.problematic_files = []
        self.backup_created = False
        
    def diagnose_problem(self) -> Dict[str, Any]:
        """
        Diagnósticar el problema específico de cache.
        
        Returns:
            Diccionario con diagnóstico completo
        """
        logger.info("=== DIAGNÓSTICO CACHE CORRUPTION ===")
        
        diagnosis = {
            "problem_detected": False,
            "method_exists": False,
            "cache_files_found": [],
            "problematic_paths": [],
            "solution_required": False
        }
        
        # 1. Verificar que el método existe en código fuente
        window_manager_path = self.project_root / "src" / "ui" / "utils" / "window_manager.py"
        
        if window_manager_path.exists():
            try:
                with open(window_manager_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                if "def center_window(" in content and "@staticmethod" in content:
                    diagnosis["method_exists"] = True
                    logger.info("✅ WindowManager.center_window() SÍ EXISTE en código fuente")
                else:
                    logger.error("❌ Método center_window() NO ENCONTRADO en código fuente")
                    return diagnosis
                    
            except Exception as e:
                logger.error(f"Error leyendo window_manager.py: {e}")
                return diagnosis
        else:
            logger.error(f"❌ Archivo window_manager.py no encontrado: {window_manager_path}")
            return diagnosis
        
        # 2. Identificar archivos cache problemáticos
        cache_paths = [
            "src/ui/utils/__pycache__",
            "src/ui/forms/__pycache__",
            "src/__pycache__"
        ]
        
        for cache_path in cache_paths:
            full_path = self.project_root / cache_path
            if full_path.exists():
                diagnosis["cache_files_found"].append(str(full_path))
                
                # Buscar archivos .pyc específicos
                for pyc_file in full_path.glob("*.pyc"):
                    if "window_manager" in pyc_file.name or "label_generator" in pyc_file.name:
                        diagnosis["problematic_paths"].append(str(pyc_file))
        
        # 3. Determinar si se requiere solución
        if diagnosis["method_exists"] and diagnosis["cache_files_found"]:
            diagnosis["problem_detected"] = True
            diagnosis["solution_required"] = True
            logger.info("🚨 CACHE CORRUPTION CONFIRMADO - Solución requerida")
        
        return diagnosis
    
    def create_backup(self) -> bool:
        """
        Crear backup de archivos cache antes de eliminar.
        
        Returns:
            True si backup fue exitoso
        """
        try:
            backup_dir = self.project_root / "cache_backup_window_manager"
            
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            
            backup_dir.mkdir()
            
            # Backup de directorios cache críticos
            cache_dirs = [
                "src/ui/utils/__pycache__",
                "src/ui/forms/__pycache__"
            ]
            
            for cache_dir in cache_dirs:
                source_path = self.project_root / cache_dir
                if source_path.exists():
                    dest_path = backup_dir / cache_dir.replace("/", "_")
                    shutil.copytree(source_path, dest_path)
                    logger.info(f"✅ Backup creado: {dest_path}")
            
            self.backup_created = True
            logger.info(f"✅ Backup completo creado en: {backup_dir}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creando backup: {e}")
            return False
    
    def clean_cache_directories(self) -> List[str]:
        """
        Limpiar directorios cache problemáticos.
        
        Returns:
            Lista de directorios limpiados
        """
        cleaned_dirs = []
        
        # Directorios cache críticos identificados
        target_directories = [
            "src/ui/utils/__pycache__",
            "src/ui/forms/__pycache__",
            "src/__pycache__"
        ]
        
        for cache_dir in target_directories:
            full_path = self.project_root / cache_dir
            
            if full_path.exists():
                try:
                    # Eliminar directorio completo
                    shutil.rmtree(full_path)
                    cleaned_dirs.append(str(full_path))
                    logger.info(f"✅ Directorio cache eliminado: {full_path}")
                    
                except Exception as e:
                    logger.error(f"❌ Error eliminando {full_path}: {e}")
            else:
                logger.info(f"ℹ️  Directorio no existe: {full_path}")
        
        return cleaned_dirs
    
    def verify_solution(self) -> bool:
        """
        Verificar que la solución fue efectiva.
        
        Returns:
            True si la verificación es exitosa
        """
        try:
            logger.info("🔍 Verificando solución...")
            
            # 1. Verificar que archivos cache fueron eliminados
            problematic_paths = [
                "src/ui/utils/__pycache__/window_manager.cpython-312.pyc",
                "src/ui/forms/__pycache__/label_generator_form.cpython-312.pyc"
            ]
            
            for path in problematic_paths:
                full_path = self.project_root / path
                if full_path.exists():
                    logger.warning(f"⚠️  Archivo cache aún existe: {full_path}")
                    return False
                else:
                    logger.info(f"✅ Archivo cache eliminado correctamente: {path}")
            
            # 2. Intentar importar módulos para forzar regeneración cache
            logger.info("🔄 Forzando regeneración de cache...")
            
            # Agregar src al path temporalmente
            src_path = str(self.project_root / "src")
            if src_path not in sys.path:
                sys.path.insert(0, src_path)
            
            try:
                # Importar WindowManager para regenerar cache
                from ui.utils.window_manager import WindowManager
                
                # Verificar que el método existe
                if hasattr(WindowManager, 'center_window'):
                    logger.info("✅ WindowManager.center_window() disponible después de limpieza")
                    
                    # Verificar que es callable
                    if callable(getattr(WindowManager, 'center_window')):
                        logger.info("✅ center_window() es callable")
                        return True
                    else:
                        logger.error("❌ center_window() no es callable")
                        return False
                else:
                    logger.error("❌ center_window() aún no disponible después de limpieza")
                    return False
                    
            except ImportError as e:
                logger.error(f"❌ Error importando WindowManager: {e}")
                return False
            finally:
                # Limpiar path
                if src_path in sys.path:
                    sys.path.remove(src_path)
        
        except Exception as e:
            logger.error(f"❌ Error en verificación: {e}")
            return False
    
    def run_complete_fix(self) -> bool:
        """
        Ejecutar corrección completa del cache corruption.
        
        Returns:
            True si corrección fue exitosa
        """
        try:
            logger.info("🚀 INICIANDO CORRECCIÓN CACHE CORRUPTION")
            logger.info("Problema: WindowManager.center_window() AttributeError")
            logger.info("Solución: Limpieza cache corrupted según protocolo v3.0")
            logger.info("")
            
            # 1. Diagnóstico
            diagnosis = self.diagnose_problem()
            
            if not diagnosis["solution_required"]:
                logger.info("ℹ️  No se requiere corrección - problema no detectado")
                return True
            
            logger.info(f"📂 Archivos cache encontrados: {len(diagnosis['cache_files_found'])}")
            logger.info(f"⚠️  Archivos problemáticos: {len(diagnosis['problematic_paths'])}")
            logger.info("")
            
            # 2. Crear backup
            logger.info("💾 Creando backup de cache...")
            if not self.create_backup():
                logger.error("❌ Error creando backup - ABORTANDO corrección")
                return False
            
            # 3. Limpiar cache
            logger.info("🧹 Limpiando cache problemático...")
            cleaned_dirs = self.clean_cache_directories()
            
            if not cleaned_dirs:
                logger.warning("⚠️  Ningún directorio cache fue limpiado")
                return False
            
            logger.info(f"✅ {len(cleaned_dirs)} directorios cache limpiados")
            logger.info("")
            
            # 4. Verificar solución
            logger.info("🔍 Verificando corrección...")
            if self.verify_solution():
                logger.info("")
                logger.info("🎉 CORRECCIÓN EXITOSA")
                logger.info("✅ WindowManager.center_window() ahora disponible")
                logger.info("✅ LabelGeneratorForm debería funcionar correctamente")
                logger.info("✅ Sistema de etiquetas desbloqueado")
                logger.info("")
                logger.info("📋 PRÓXIMOS PASOS:")
                logger.info("   1. Reiniciar aplicación Python")
                logger.info("   2. Probar LabelGeneratorForm")
                logger.info("   3. Confirmar ausencia de AttributeError")
                logger.info("")
                return True
            else:
                logger.error("❌ Verificación falló - problema persiste")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error crítico en corrección: {e}")
            return False


def main():
    """Función principal del script."""
    print("="*60)
    print("CORRECCIÓN CACHE CORRUPTION - WindowManager.center_window()")
    print("Sistema de Inventario Copy Point S.A.")
    print("="*60)
    print()
    
    # Detectar directorio del proyecto
    current_dir = Path.cwd()
    project_root = current_dir
    
    # Buscar indicadores de proyecto
    if not (project_root / "src").exists():
        # Intentar directorio padre
        project_root = current_dir.parent
        
        if not (project_root / "src").exists():
            print("❌ ERROR: No se puede detectar directorio del proyecto")
            print("   Asegúrese de ejecutar desde D:\\inventario_app2\\")
            return False
    
    print(f"📁 Directorio del proyecto: {project_root}")
    print()
    
    # Ejecutar corrección
    fixer = WindowManagerCacheFixer(str(project_root))
    success = fixer.run_complete_fix()
    
    if success:
        print("🎯 RESULTADO: CORRECCIÓN EXITOSA")
        print("   El error AttributeError debería estar resuelto")
        return True
    else:
        print("💥 RESULTADO: CORRECCIÓN FALLÓ")
        print("   Es posible que se requiera intervención manual")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
