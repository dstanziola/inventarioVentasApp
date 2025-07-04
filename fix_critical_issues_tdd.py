"""
CORRECCIONES CRÍTICAS TDD - FASE 5A
===================================

Script de correcciones críticas implementado siguiendo metodología TDD estricta.
Las correcciones se aplican DESPUÉS de escribir el test de validación.

OBJETIVOS:
1. Instalar psutil para tests de performance  
2. Corregir imports DatabaseConnectionConnection → DatabaseConnection
3. Validar que todas las correcciones funcionen correctamente
4. Mantener integridad del sistema

Autor: Sistema de Inventario Copy Point S.A.
Fecha: Julio 4, 2025 - TDD Correcciones Críticas
Protocolo: TDD estricto - Correcciones basadas en tests fallidos
"""

import os
import sys
import subprocess
import tempfile
import shutil
from typing import List, Tuple, Dict, Any, Optional
import re

class CriticalFixesTDD:
    """Aplicador de correcciones críticas siguiendo metodología TDD."""
    
    def __init__(self, project_root: str = "D:\\inventario_app2"):
        """
        Inicializar corrector TDD.
        
        Args:
            project_root: Ruta raíz del proyecto
        """
        self.project_root = project_root
        self.fixes_applied = []
        self.errors_found = []
        
        print(f"🔧 === CORRECCIONES CRÍTICAS TDD ===")
        print(f"📁 Proyecto: {project_root}")
        print(f"🎯 Metodología: Test-Driven Development")
    
    def fix_01_install_psutil_dependency(self) -> bool:
        """
        Corrección 1: Instalar psutil para tests de performance.
        
        Returns:
            True si la instalación fue exitosa
        """
        print(f"\n1️⃣ CORRECCIÓN TDD: Instalando psutil...")
        
        try:
            # Intentar importar primero para ver si ya está instalado
            import psutil
            print(f"   ✅ psutil ya está instalado")
            return True
            
        except ImportError:
            print(f"   📦 psutil no encontrado, instalando...")
            
            try:
                # Instalar psutil usando pip
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', 'psutil'
                ], capture_output=True, text=True, check=True)
                
                print(f"   ✅ psutil instalado exitosamente")
                self.fixes_applied.append("Instalación de psutil")
                
                # Verificar instalación
                import psutil
                print(f"   ✅ Verificación: psutil importa correctamente")
                
                return True
                
            except subprocess.CalledProcessError as e:
                error_msg = f"Error instalando psutil: {e.stderr}"
                print(f"   ❌ {error_msg}")
                self.errors_found.append(error_msg)
                return False
            except ImportError as e:
                error_msg = f"Error verificando instalación de psutil: {e}"
                print(f"   ❌ {error_msg}")
                self.errors_found.append(error_msg)
                return False
    
    def fix_02_correct_database_connection_imports(self) -> bool:
        """
        Corrección 2: Corregir imports DatabaseConnectionConnection → DatabaseConnection.
        
        Returns:
            True si todas las correcciones fueron exitosas
        """
        print(f"\n2️⃣ CORRECCIÓN TDD: Corrigiendo imports DatabaseConnection...")
        
        # Archivos que pueden tener el error
        test_files_to_check = [
            'tests/test_fase2_validation.py',
            'tests/test_sales_service_optimization.py', 
            'tests/test_fase3_optimization.py',
            'tests/test_database_connection_evaluation.py'
        ]
        
        files_corrected = 0
        
        for file_path in test_files_to_check:
            full_path = os.path.join(self.project_root, file_path)
            
            if not os.path.exists(full_path):
                print(f"   ⚠️ Archivo no encontrado: {file_path}")
                continue
            
            try:
                # Leer archivo
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verificar si contiene el error
                if 'DatabaseConnectionConnection' in content:
                    print(f"   🔍 Corrigiendo imports en: {file_path}")
                    
                    # Crear backup
                    backup_path = full_path + '.backup'
                    shutil.copy2(full_path, backup_path)
                    
                    # Aplicar corrección
                    corrected_content = content.replace(
                        'DatabaseConnectionConnection', 
                        'DatabaseConnection'
                    )
                    
                    # Escribir archivo corregido
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(corrected_content)
                    
                    print(f"   ✅ Corregido: {file_path}")
                    files_corrected += 1
                    
                else:
                    print(f"   ✅ No requiere corrección: {file_path}")
                    
            except Exception as e:
                error_msg = f"Error procesando {file_path}: {e}"
                print(f"   ❌ {error_msg}")
                self.errors_found.append(error_msg)
        
        if files_corrected > 0:
            self.fixes_applied.append(f"Corrección imports DatabaseConnection ({files_corrected} archivos)")
            print(f"   📊 Total archivos corregidos: {files_corrected}")
        
        return True
    
    def fix_03_validate_all_critical_imports(self) -> bool:
        """
        Corrección 3: Validar que todos los imports críticos funcionen.
        
        Returns:
            True si todas las validaciones pasaron
        """
        print(f"\n3️⃣ CORRECCIÓN TDD: Validando imports críticos...")
        
        critical_imports = [
            ('src.db.database', 'DatabaseConnection'),
            ('src.services.product_service', 'ProductService'),
            ('src.services.category_service', 'CategoryService'),
            ('src.services.client_service', 'ClientService'),
            ('src.services.sales_service', 'SalesService'),
        ]
        
        all_valid = True
        
        for module_name, class_name in critical_imports:
            try:
                # Cambiar al directorio del proyecto para imports
                old_cwd = os.getcwd()
                os.chdir(self.project_root)
                
                # Intentar importar
                module = __import__(module_name, fromlist=[class_name])
                service_class = getattr(module, class_name)
                
                print(f"   ✅ {module_name}.{class_name}")
                
                # Restaurar directorio
                os.chdir(old_cwd)
                
            except Exception as e:
                print(f"   ❌ {module_name}.{class_name}: {e}")
                self.errors_found.append(f"Import fallido: {module_name}.{class_name}")
                all_valid = False
                
                # Restaurar directorio en caso de error
                os.chdir(old_cwd)
        
        if all_valid:
            self.fixes_applied.append("Validación imports críticos exitosa")
        
        return all_valid
    
    def fix_04_test_database_connection_functionality(self) -> bool:
        """
        Corrección 4: Probar funcionalidad de DatabaseConnection.
        
        Returns:
            True si la funcionalidad es correcta
        """
        print(f"\n4️⃣ CORRECCIÓN TDD: Probando funcionalidad DatabaseConnection...")
        
        try:
            # Cambiar al directorio del proyecto
            old_cwd = os.getcwd()
            os.chdir(self.project_root)
            
            # Importar DatabaseConnection
            from src.db.database import DatabaseConnection
            
            # Crear BD temporal
            temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
            temp_db.close()
            
            try:
                # Test instanciación
                db_conn = DatabaseConnection(temp_db.name)
                print(f"   ✅ Instanciación exitosa")
                
                # Test conexión
                connection = db_conn.get_connection()
                self.assertIsNotNone(connection)
                print(f"   ✅ Conexión exitosa")
                
                # Test creación de tablas
                db_conn.create_tables()
                print(f"   ✅ Creación de tablas exitosa")
                
                # Test integridad
                integrity = db_conn.verify_schema_integrity()
                if integrity:
                    print(f"   ✅ Integridad de schema validada")
                else:
                    print(f"   ⚠️ Problema con integridad de schema")
                
                # Cerrar conexión
                db_conn.close()
                print(f"   ✅ Cierre de conexión exitoso")
                
                self.fixes_applied.append("Funcionalidad DatabaseConnection validada")
                
                return True
                
            finally:
                # Limpiar archivo temporal
                if os.path.exists(temp_db.name):
                    os.unlink(temp_db.name)
                
                # Restaurar directorio
                os.chdir(old_cwd)
                
        except Exception as e:
            error_msg = f"Error probando DatabaseConnection: {e}"
            print(f"   ❌ {error_msg}")
            self.errors_found.append(error_msg)
            os.chdir(old_cwd)
            return False
    
    def assertIsNotNone(self, value):
        """Helper para validación."""
        if value is None:
            raise AssertionError("Value is None")
    
    def fix_05_validate_pytest_can_collect_tests(self) -> bool:
        """
        Corrección 5: Validar que pytest puede recolectar tests sin errores.
        
        Returns:
            True si pytest puede recolectar tests correctamente
        """
        print(f"\n5️⃣ CORRECCIÓN TDD: Validando recolección de tests por pytest...")
        
        try:
            # Cambiar al directorio del proyecto
            old_cwd = os.getcwd()
            os.chdir(self.project_root)
            
            # Ejecutar pytest --collect-only en tests críticos
            result = subprocess.run([
                sys.executable, '-m', 'pytest', 
                '--collect-only', '-q',
                'tests/test_fase2_validation.py'
            ], capture_output=True, text=True)
            
            # Restaurar directorio
            os.chdir(old_cwd)
            
            if result.returncode == 0:
                print(f"   ✅ pytest puede recolectar tests correctamente")
                self.fixes_applied.append("Validación pytest collection exitosa")
                return True
            else:
                error_msg = f"pytest collection falló: {result.stderr}"
                print(f"   ❌ {error_msg}")
                self.errors_found.append(error_msg)
                return False
                
        except Exception as e:
            error_msg = f"Error ejecutando pytest: {e}"
            print(f"   ❌ {error_msg}")
            self.errors_found.append(error_msg)
            os.chdir(old_cwd)
            return False
    
    def run_all_critical_fixes(self) -> bool:
        """
        Ejecutar todas las correcciones críticas en orden.
        
        Returns:
            True si todas las correcciones fueron exitosas
        """
        print(f"\n🔧 EJECUTANDO TODAS LAS CORRECCIONES TDD...")
        print(f"="*60)
        
        # Lista de correcciones en orden
        fixes = [
            self.fix_01_install_psutil_dependency,
            self.fix_02_correct_database_connection_imports, 
            self.fix_03_validate_all_critical_imports,
            self.fix_04_test_database_connection_functionality,
            self.fix_05_validate_pytest_can_collect_tests
        ]
        
        # Ejecutar correcciones
        successful_fixes = 0
        for fix_func in fixes:
            try:
                success = fix_func()
                if success:
                    successful_fixes += 1
            except Exception as e:
                error_msg = f"Error ejecutando {fix_func.__name__}: {e}"
                print(f"❌ {error_msg}")
                self.errors_found.append(error_msg)
        
        # Generar reporte
        self.generate_fixes_report()
        
        return successful_fixes == len(fixes)
    
    def generate_fixes_report(self):
        """Generar reporte de correcciones aplicadas."""
        print(f"\n📊 === REPORTE DE CORRECCIONES TDD ===")
        print(f"="*60)
        
        print(f"✅ CORRECCIONES APLICADAS ({len(self.fixes_applied)}):")
        for fix in self.fixes_applied:
            print(f"   • {fix}")
        
        if self.errors_found:
            print(f"\n❌ ERRORES ENCONTRADOS ({len(self.errors_found)}):")
            for error in self.errors_found:
                print(f"   • {error}")
        
        success_rate = len(self.fixes_applied) / (len(self.fixes_applied) + len(self.errors_found)) * 100 if (len(self.fixes_applied) + len(self.errors_found)) > 0 else 0
        
        print(f"\n📈 TASA DE ÉXITO: {success_rate:.1f}%")
        
        if success_rate >= 100:
            print(f"🎯 RESULTADO: TODAS LAS CORRECCIONES EXITOSAS")
            print(f"✅ Sistema listo para ejecutar suite completa de tests")
        elif success_rate >= 80:
            print(f"⚠️ RESULTADO: CORRECCIONES MAYORMENTE EXITOSAS")  
            print(f"🔍 Revisar errores antes de continuar")
        else:
            print(f"❌ RESULTADO: CORRECCIONES REQUIEREN ATENCIÓN")
            print(f"🛠️ Resolver errores antes de continuar")


def run_critical_fixes():
    """Función principal para ejecutar correcciones críticas."""
    fixer = CriticalFixesTDD()
    return fixer.run_all_critical_fixes()


if __name__ == '__main__':
    print("🚀 Iniciando Correcciones Críticas TDD...")
    success = run_critical_fixes()
    
    if success:
        print(f"\n🎉 CORRECCIONES COMPLETADAS EXITOSAMENTE")
        sys.exit(0)
    else:
        print(f"\n⚠️ CORRECCIONES COMPLETADAS CON ERRORES")
        sys.exit(1)
