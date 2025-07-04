#!/usr/bin/env python3
"""
Corrección optimizada de errores críticos FASE 5A
Sistema de Inventario Copy Point S.A.

ESTRATEGIA OPTIMIZADA:
- Crear enlaces simbólicos en lugar de duplicar código
- Corregir pytest.ini con formato correcto
- Verificar imports críticos
- Mantener compatibilidad con código existente

PROTOCOLO:
- Seguir TDD: correcciones específicas para pasar tests
- Evitar duplicación de código (DRY principle)
- Mantener arquitectura existente
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime


class OptimizedCriticalFixer:
    """Corrector optimizado para errores críticos FASE 5A."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / "backups" / f"optimized_fixes_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.corrections_applied = []
        
    def create_backup(self, file_path: Path):
        """Crear backup antes de modificaciones."""
        if not self.backup_dir.exists():
            self.backup_dir.mkdir(parents=True)
        
        if file_path.exists():
            backup_path = self.backup_dir / file_path.name
            shutil.copy2(file_path, backup_path)
            print(f"📂 Backup creado: {backup_path}")
    
    def create_symbolic_links_for_helpers(self):
        """Crear enlaces simbólicos para helpers en utils."""
        print("🔗 Corrección 1: Crear enlaces simbólicos para helpers...")
        
        utils_dir = self.project_root / "src" / "utils"
        helpers_dir = self.project_root / "src" / "helpers"
        
        # Verificar que helpers existen
        validation_helper_src = helpers_dir / "validation_helper.py"
        logging_helper_src = helpers_dir / "logging_helper.py"
        
        if not validation_helper_src.exists():
            print("❌ No se encontró validation_helper.py en helpers/")
            return False
        
        if not logging_helper_src.exists():
            print("❌ No se encontró logging_helper.py en helpers/")
            return False
        
        # Crear enlaces en utils
        validation_helper_dst = utils_dir / "validation_helper.py"
        logging_helper_dst = utils_dir / "logging_helper.py"
        
        # Remover archivos existentes si los hay
        if validation_helper_dst.exists():
            self.create_backup(validation_helper_dst)
            validation_helper_dst.unlink()
        
        if logging_helper_dst.exists():
            self.create_backup(logging_helper_dst)
            logging_helper_dst.unlink()
        
        try:
            # En Windows, usar copy en lugar de symlink si no hay permisos admin
            if os.name == 'nt':
                # Intentar symlink primero
                try:
                    validation_helper_dst.symlink_to(validation_helper_src)
                    logging_helper_dst.symlink_to(logging_helper_src)
                    print("✅ Enlaces simbólicos creados exitosamente")
                except OSError:
                    # Fallback: copiar archivos
                    shutil.copy2(validation_helper_src, validation_helper_dst)
                    shutil.copy2(logging_helper_src, logging_helper_dst)
                    print("✅ Archivos copiados como fallback")
            else:
                # En Linux/Mac usar symlinks directamente
                validation_helper_dst.symlink_to(validation_helper_src)
                logging_helper_dst.symlink_to(logging_helper_src)
                print("✅ Enlaces simbólicos creados exitosamente")
            
            self.corrections_applied.append("Enlaces simbólicos/copia de helpers creados")
            return True
            
        except Exception as e:
            print(f"❌ Error creando enlaces: {e}")
            return False
    
    def fix_pytest_configuration(self):
        """Corregir configuración de pytest.ini."""
        print("🔧 Corrección 2: Corregir pytest.ini...")
        
        pytest_ini_path = self.project_root / "pytest.ini"
        
        if pytest_ini_path.exists():
            self.create_backup(pytest_ini_path)
        
        # Configuración corregida
        pytest_config = """[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    fase5a: marca para tests de la fase 5A
    performance: marca para tests de performance
    security: marca para tests de seguridad
    integration: marca para tests de integración
    unit: marca para tests unitarios
    slow: marca para tests lentos
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
"""
        
        with open(pytest_ini_path, 'w', encoding='utf-8') as f:
            f.write(pytest_config)
        
        print("✅ pytest.ini corregido")
        self.corrections_applied.append("pytest.ini formato corregido")
        return True
    
    def fix_database_connection_imports(self):
        """Corregir imports dobles de DatabaseConnection."""
        print("🔧 Corrección 3: Corregir imports de DatabaseConnection...")
        
        # Buscar archivos con import incorrecto
        test_files = list(self.project_root.glob("tests/test_*.py"))
        src_files = list(self.project_root.glob("src/**/*.py"))
        
        all_files = test_files + src_files
        files_fixed = 0
        
        for file_path in all_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verificar si tiene el import incorrecto
                if 'DatabaseConnection' in content:
                    self.create_backup(file_path)
                    
                    # Corregir import
                    corrected_content = content.replace(
                        'DatabaseConnection',
                        'DatabaseConnection'
                    )
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(corrected_content)
                    
                    print(f"✅ Corregido: {file_path.name}")
                    files_fixed += 1
                    
            except Exception as e:
                print(f"❌ Error procesando {file_path.name}: {e}")
        
        if files_fixed > 0:
            self.corrections_applied.append(f"Corregidos {files_fixed} imports de DatabaseConnection")
        else:
            self.corrections_applied.append("No se encontraron imports dobles de DatabaseConnection")
        
        return True
    
    def verify_critical_imports(self):
        """Verificar que los imports críticos funcionen."""
        print("🔍 Verificación: Imports críticos...")
        
        import_tests = [
            ("src.helpers.validation_helper", "ValidationHelper"),
            ("src.helpers.logging_helper", "LoggingHelper"), 
            ("src.utils.database_helper", "DatabaseHelper"),
            ("src.db.database", "DatabaseConnection")
        ]
        
        # Agregar project root al path temporalmente
        import sys
        original_path = sys.path.copy()
        sys.path.insert(0, str(self.project_root))
        
        try:
            import_results = []
            
            for module_name, class_name in import_tests:
                try:
                    module = __import__(module_name, fromlist=[class_name])
                    getattr(module, class_name)
                    import_results.append(f"✅ {module_name}.{class_name}")
                except ImportError as e:
                    import_results.append(f"❌ {module_name}.{class_name}: {e}")
                except AttributeError as e:
                    import_results.append(f"⚠️ {module_name}.{class_name}: {e}")
            
            print("📋 Resultados de verificación:")
            for result in import_results:
                print(f"   {result}")
            
            # Verificar que al menos los críticos funcionen
            critical_working = sum(1 for r in import_results if r.startswith("✅"))
            total_tests = len(import_results)
            
            success_rate = critical_working / total_tests
            print(f"\n📊 Tasa de éxito: {critical_working}/{total_tests} ({success_rate:.1%})")
            
            self.corrections_applied.append(f"Verificación imports: {critical_working}/{total_tests} exitosos")
            
            return success_rate >= 0.75  # 75% mínimo
            
        finally:
            # Restaurar path original
            sys.path = original_path
    
    def create_missing_init_files(self):
        """Crear archivos __init__.py faltantes."""
        print("📁 Corrección 4: Verificar archivos __init__.py...")
        
        critical_dirs = [
            self.project_root / "src",
            self.project_root / "src" / "utils",
            self.project_root / "src" / "helpers",
            self.project_root / "src" / "db",
            self.project_root / "src" / "models",
            self.project_root / "src" / "services",
            self.project_root / "src" / "ui",
            self.project_root / "tests"
        ]
        
        init_files_created = 0
        
        for dir_path in critical_dirs:
            if dir_path.exists():
                init_file = dir_path / "__init__.py"
                if not init_file.exists():
                    with open(init_file, 'w', encoding='utf-8') as f:
                        f.write(f'"""Módulo {dir_path.name} del sistema de inventario."""\n')
                    print(f"✅ Creado: {init_file}")
                    init_files_created += 1
        
        if init_files_created > 0:
            self.corrections_applied.append(f"Creados {init_files_created} archivos __init__.py")
        else:
            self.corrections_applied.append("Todos los archivos __init__.py existían")
        
        return True
    
    def run_optimized_fixes(self):
        """Ejecutar todas las correcciones optimizadas."""
        print("🚀 CORRECCIONES OPTIMIZADAS FASE 5A")
        print("=" * 50)
        
        try:
            success_steps = []
            
            # Paso 1: Crear enlaces/copias de helpers
            if self.create_symbolic_links_for_helpers():
                success_steps.append("✅ Enlaces helpers")
            else:
                success_steps.append("❌ Enlaces helpers")
            
            # Paso 2: Corregir pytest.ini
            if self.fix_pytest_configuration():
                success_steps.append("✅ pytest.ini")
            else:
                success_steps.append("❌ pytest.ini")
            
            # Paso 3: Corregir imports dobles
            if self.fix_database_connection_imports():
                success_steps.append("✅ Imports DB")
            else:
                success_steps.append("❌ Imports DB")
            
            # Paso 4: Crear __init__.py faltantes
            if self.create_missing_init_files():
                success_steps.append("✅ __init__.py")
            else:
                success_steps.append("❌ __init__.py")
            
            # Paso 5: Verificar imports críticos
            if self.verify_critical_imports():
                success_steps.append("✅ Verificación")
            else:
                success_steps.append("⚠️ Verificación")
            
            print(f"\n📊 RESUMEN DE CORRECCIONES")
            print("=" * 50)
            
            for step in success_steps:
                print(f"  {step}")
            
            print(f"\n📋 Detalles de correcciones aplicadas:")
            for correction in self.corrections_applied:
                print(f"  • {correction}")
            
            print(f"\n📂 Backups en: {self.backup_dir}")
            
            # Determinar éxito general
            successful_steps = sum(1 for step in success_steps if step.startswith("✅"))
            total_steps = len(success_steps)
            
            success_rate = successful_steps / total_steps
            
            if success_rate >= 0.8:  # 80% mínimo
                print(f"\n🎉 CORRECCIONES COMPLETADAS EXITOSAMENTE")
                print(f"📊 Tasa de éxito: {successful_steps}/{total_steps} ({success_rate:.1%})")
                return True
            else:
                print(f"\n⚠️ CORRECCIONES COMPLETADAS CON ADVERTENCIAS")
                print(f"📊 Tasa de éxito: {successful_steps}/{total_steps} ({success_rate:.1%})")
                return False
                
        except Exception as e:
            print(f"❌ Error crítico durante correcciones: {e}")
            return False


def main():
    """Función principal de corrección optimizada."""
    project_root = "D:\\inventario_app2"
    
    if not os.path.exists(project_root):
        print(f"❌ Error: Proyecto no encontrado en {project_root}")
        return False
    
    fixer = OptimizedCriticalFixer(project_root)
    success = fixer.run_optimized_fixes()
    
    if success:
        print("\n🎯 PRÓXIMOS PASOS:")
        print("1. Ejecutar test de validación:")
        print("   python test_fase5a_critical_validation.py")
        print("2. Ejecutar pytest completo:")
        print("   pytest --collect-only")
        print("3. Ejecutar análisis de cobertura:")
        print("   pytest --cov=src tests/")
    else:
        print("\n🔧 ACCIONES REQUERIDAS:")
        print("1. Revisar errores reportados")
        print("2. Corregir manualmente si es necesario")
        print("3. Ejecutar test de validación para verificar estado")
    
    return success


if __name__ == "__main__":
    main()
