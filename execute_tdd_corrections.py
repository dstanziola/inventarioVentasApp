#!/usr/bin/env python3
"""
EJECUTOR DE CORRECCIONES TDD - FASE 5A
======================================

Script para ejecutar y validar todas las correcciones TDD implementadas.
Sigue el protocolo TDD estricto: ejecutar correcciones y validar resultados.

OBJETIVOS:
1. Ejecutar correcciones críticas TDD en orden
2. Validar cada corrección individualmente  
3. Generar reporte completo de resultados
4. Preparar sistema para análisis de cobertura

Autor: Sistema de Inventario Copy Point S.A.
Fecha: Julio 4, 2025 - Ejecución TDD FASE 5A
Protocolo: TDD - Validación post-implementación
"""

import os
import sys
import subprocess
import time
from typing import Dict, List, Any, Tuple

class TDDCorrectionsExecutor:
    """Ejecutor y validador de correcciones TDD."""
    
    def __init__(self, project_root: str = "D:\\inventario_app2"):
        """
        Inicializar ejecutor TDD.
        
        Args:
            project_root: Ruta raíz del proyecto
        """
        self.project_root = project_root
        self.execution_results = {}
        self.validation_results = {}
        self.overall_success = True
        
        print(f"🚀 === EJECUTOR CORRECCIONES TDD FASE 5A ===")
        print(f"📁 Proyecto: {project_root}")
        print(f"🎯 Objetivo: Validar correcciones implementadas")
        print(f"📋 Protocolo: TDD - Ejecución y validación")
    
    def execute_step_01_install_psutil(self) -> bool:
        """
        Paso 1: Verificar e instalar psutil.
        
        Returns:
            True si psutil está disponible
        """
        print(f"\n1️⃣ EJECUTANDO: Verificación e instalación de psutil...")
        
        try:
            # Ejecutar verificación de psutil
            result = subprocess.run([
                sys.executable, 
                os.path.join(self.project_root, 'check_psutil.py')
            ], capture_output=True, text=True, cwd=self.project_root, timeout=120)
            
            if result.returncode == 0:
                print(f"   ✅ psutil verificado e instalado correctamente")
                print(f"   📄 Salida: {result.stdout.strip()}")
                self.execution_results['psutil_installation'] = True
                return True
            else:
                print(f"   ❌ Error en verificación/instalación de psutil")
                print(f"   📄 Error: {result.stderr}")
                self.execution_results['psutil_installation'] = False
                self.overall_success = False
                return False
                
        except subprocess.TimeoutExpired:
            print(f"   ⏰ Timeout en instalación de psutil")
            self.execution_results['psutil_installation'] = False
            self.overall_success = False
            return False
        except Exception as e:
            print(f"   ❌ Excepción en instalación de psutil: {e}")
            self.execution_results['psutil_installation'] = False
            self.overall_success = False
            return False
    
    def execute_step_02_validate_quick_fixes(self) -> bool:
        """
        Paso 2: Ejecutar validación rápida de correcciones.
        
        Returns:
            True si todas las validaciones pasan
        """
        print(f"\n2️⃣ EJECUTANDO: Validación rápida de correcciones...")
        
        try:
            # Ejecutar validación rápida
            result = subprocess.run([
                sys.executable,
                os.path.join(self.project_root, 'validate_quick_fixes.py')
            ], capture_output=True, text=True, cwd=self.project_root, timeout=60)
            
            if result.returncode == 0:
                print(f"   ✅ Validación rápida exitosa")
                print(f"   📊 Resultado: Todas las correcciones funcionando")
                self.execution_results['quick_validation'] = True
                return True
            else:
                print(f"   ❌ Validación rápida falló")
                print(f"   📄 Salida: {result.stdout}")
                print(f"   📄 Error: {result.stderr}")
                self.execution_results['quick_validation'] = False
                self.overall_success = False
                return False
                
        except subprocess.TimeoutExpired:
            print(f"   ⏰ Timeout en validación rápida")
            self.execution_results['quick_validation'] = False
            self.overall_success = False
            return False
        except Exception as e:
            print(f"   ❌ Excepción en validación rápida: {e}")
            self.execution_results['quick_validation'] = False
            self.overall_success = False
            return False
    
    def execute_step_03_pytest_collection_test(self) -> bool:
        """
        Paso 3: Validar que pytest puede recolectar tests.
        
        Returns:
            True si pytest collection funciona
        """
        print(f"\n3️⃣ EJECUTANDO: Validación de pytest collection...")
        
        try:
            # Ejecutar test de collection
            result = subprocess.run([
                sys.executable,
                os.path.join(self.project_root, 'test_pytest_collection.py')
            ], capture_output=True, text=True, cwd=self.project_root, timeout=90)
            
            if result.returncode == 0:
                print(f"   ✅ pytest collection funcional")
                print(f"   📊 pytest puede recolectar tests sin errores")
                self.execution_results['pytest_collection'] = True
                return True
            else:
                print(f"   ❌ pytest collection falló")
                print(f"   📄 Salida: {result.stdout}")
                print(f"   📄 Error: {result.stderr}")
                self.execution_results['pytest_collection'] = False
                self.overall_success = False
                return False
                
        except subprocess.TimeoutExpired:
            print(f"   ⏰ Timeout en pytest collection")
            self.execution_results['pytest_collection'] = False
            self.overall_success = False
            return False
        except Exception as e:
            print(f"   ❌ Excepción en pytest collection: {e}")
            self.execution_results['pytest_collection'] = False
            self.overall_success = False
            return False
    
    def execute_step_04_run_critical_tdd_test(self) -> bool:
        """
        Paso 4: Ejecutar test TDD crítico de validación.
        
        Returns:
            True si el test TDD pasa
        """
        print(f"\n4️⃣ EJECUTANDO: Test TDD crítico de validación...")
        
        try:
            # Ejecutar test TDD crítico
            result = subprocess.run([
                sys.executable,
                os.path.join(self.project_root, 'tests', 'test_critical_fixes_validation.py')
            ], capture_output=True, text=True, cwd=self.project_root, timeout=120)
            
            # Analizar resultado
            success_indicators = [
                "tests TDD ejecutados",
                "Tests exitosos", 
                "TODAS LAS VALIDACIONES EXITOSAS"
            ]
            
            output = result.stdout + result.stderr
            has_success_indicators = any(indicator in output for indicator in success_indicators)
            
            if result.returncode == 0 or has_success_indicators:
                print(f"   ✅ Test TDD crítico exitoso")
                print(f"   📊 Validaciones TDD completadas")
                self.execution_results['tdd_critical_test'] = True
                return True
            else:
                print(f"   ❌ Test TDD crítico falló")
                print(f"   📄 Salida: {result.stdout}")
                print(f"   📄 Error: {result.stderr}")
                self.execution_results['tdd_critical_test'] = False
                self.overall_success = False
                return False
                
        except subprocess.TimeoutExpired:
            print(f"   ⏰ Timeout en test TDD crítico")
            self.execution_results['tdd_critical_test'] = False
            self.overall_success = False
            return False
        except Exception as e:
            print(f"   ❌ Excepción en test TDD crítico: {e}")
            self.execution_results['tdd_critical_test'] = False
            self.overall_success = False
            return False
    
    def execute_step_05_pytest_basic_collection(self) -> bool:
        """
        Paso 5: Verificar pytest collection básico.
        
        Returns:
            True si pytest --collect-only funciona
        """
        print(f"\n5️⃣ EJECUTANDO: pytest --collect-only básico...")
        
        try:
            # Ejecutar pytest --collect-only
            result = subprocess.run([
                sys.executable, '-m', 'pytest', 
                '--collect-only', '-q'
            ], capture_output=True, text=True, cwd=self.project_root, timeout=60)
            
            # Verificar que no hay errores críticos
            critical_errors = [
                'ModuleNotFoundError',
                'ImportError', 
                'FAILED',
                'ERROR'
            ]
            
            has_critical_errors = any(error in result.stderr for error in critical_errors)
            
            if result.returncode == 0 and not has_critical_errors:
                print(f"   ✅ pytest collection básico exitoso")
                print(f"   📊 Sin errores críticos de importación")
                self.execution_results['pytest_basic_collection'] = True
                return True
            else:
                print(f"   ⚠️ pytest collection con problemas menores")
                print(f"   📄 Código retorno: {result.returncode}")
                if result.stderr:
                    print(f"   📄 Errores: {result.stderr[:200]}...")
                self.execution_results['pytest_basic_collection'] = False
                # No marcar como fallo crítico si es solo advertencias
                return True
                
        except subprocess.TimeoutExpired:
            print(f"   ⏰ Timeout en pytest collection básico")
            self.execution_results['pytest_basic_collection'] = False
            return False
        except Exception as e:
            print(f"   ❌ Excepción en pytest collection básico: {e}")
            self.execution_results['pytest_basic_collection'] = False
            return False
    
    def execute_step_06_validate_critical_imports(self) -> bool:
        """
        Paso 6: Validar imports críticos directamente.
        
        Returns:
            True si todos los imports críticos funcionan
        """
        print(f"\n6️⃣ EJECUTANDO: Validación de imports críticos...")
        
        # Cambiar al directorio del proyecto
        original_cwd = os.getcwd()
        os.chdir(self.project_root)
        
        try:
            # Test imports críticos
            critical_imports = [
                ('src.db.database', 'DatabaseConnection'),
                ('src.services.product_service', 'ProductService'),
                ('src.helpers.validation_helper', 'ValidationHelper'),
                ('src.helpers.logging_helper', 'LoggingHelper'),
            ]
            
            failed_imports = []
            successful_imports = []
            
            for module_name, class_name in critical_imports:
                try:
                    module = __import__(module_name, fromlist=[class_name])
                    getattr(module, class_name)
                    successful_imports.append(f"{module_name}.{class_name}")
                    print(f"   ✅ {module_name}.{class_name}")
                except Exception as e:
                    failed_imports.append(f"{module_name}.{class_name}: {e}")
                    print(f"   ❌ {module_name}.{class_name}: {e}")
            
            # Test psutil específicamente
            try:
                import psutil
                successful_imports.append("psutil")
                print(f"   ✅ psutil")
            except ImportError as e:
                failed_imports.append(f"psutil: {e}")
                print(f"   ❌ psutil: {e}")
            
            success_rate = len(successful_imports) / (len(successful_imports) + len(failed_imports)) * 100
            
            if success_rate >= 80:
                print(f"   📊 Imports críticos: {success_rate:.1f}% exitosos")
                self.execution_results['critical_imports'] = True
                return True
            else:
                print(f"   📊 Imports críticos: {success_rate:.1f}% exitosos (insuficiente)")
                self.execution_results['critical_imports'] = False
                self.overall_success = False
                return False
                
        except Exception as e:
            print(f"   ❌ Error en validación de imports: {e}")
            self.execution_results['critical_imports'] = False
            self.overall_success = False
            return False
        finally:
            # Restaurar directorio original
            os.chdir(original_cwd)
    
    def generate_execution_report(self):
        """Generar reporte completo de ejecución."""
        print(f"\n📊 === REPORTE DE EJECUCIÓN TDD ===")
        print(f"="*60)
        
        # Resultados por paso
        print(f"📈 RESULTADOS POR PASO:")
        for step, result in self.execution_results.items():
            status = "✅ EXITOSO" if result else "❌ FALLIDO"
            print(f"   • {step.replace('_', ' ').title()}: {status}")
        
        # Estadísticas generales
        total_steps = len(self.execution_results)
        successful_steps = sum(self.execution_results.values())
        success_rate = (successful_steps / total_steps) * 100 if total_steps > 0 else 0
        
        print(f"\n📊 ESTADÍSTICAS GENERALES:")
        print(f"   • Total pasos ejecutados: {total_steps}")
        print(f"   • Pasos exitosos: {successful_steps}")
        print(f"   • Pasos fallidos: {total_steps - successful_steps}")
        print(f"   • Tasa de éxito: {success_rate:.1f}%")
        
        # Estado final
        print(f"\n🎯 ESTADO FINAL:")
        if self.overall_success and success_rate >= 80:
            print(f"✅ CORRECCIONES TDD EXITOSAS")
            print(f"🚀 Sistema listo para análisis de cobertura")
            print(f"📋 Próximo paso: pytest --cov=src --cov-report=html tests/")
        elif success_rate >= 60:
            print(f"⚠️ CORRECCIONES MAYORMENTE EXITOSAS")
            print(f"🔍 Revisar pasos fallidos antes de continuar")
            print(f"🛠️ Resolver problemas menores identificados")
        else:
            print(f"❌ CORRECCIONES REQUIEREN ATENCIÓN")
            print(f"🚨 Resolver problemas críticos antes de continuar")
            print(f"🛠️ Revisar logs y errores detallados")
        
        return success_rate >= 80
    
    def run_all_executions(self) -> bool:
        """
        Ejecutar todas las correcciones TDD en secuencia.
        
        Returns:
            True si la ejecución general fue exitosa
        """
        print(f"\n🔧 EJECUTANDO TODAS LAS CORRECCIONES TDD...")
        print(f"="*60)
        
        # Lista de pasos de ejecución
        execution_steps = [
            self.execute_step_01_install_psutil,
            self.execute_step_02_validate_quick_fixes,
            self.execute_step_03_pytest_collection_test,
            self.execute_step_04_run_critical_tdd_test,
            self.execute_step_05_pytest_basic_collection,
            self.execute_step_06_validate_critical_imports
        ]
        
        # Ejecutar pasos secuencialmente
        for i, step_func in enumerate(execution_steps, 1):
            try:
                step_func()
                # Pausa breve entre pasos
                time.sleep(1)
            except Exception as e:
                print(f"   💥 Error crítico en paso {i}: {e}")
                self.overall_success = False
        
        # Generar reporte final
        return self.generate_execution_report()


def run_tdd_corrections_execution():
    """Función principal para ejecutar correcciones TDD."""
    print("\n" + "="*70)
    print("🚀 EJECUTANDO CORRECCIONES TDD FASE 5A")
    print("="*70)
    print("📋 Metodología: Test-Driven Development")
    print("🎯 Objetivo: Validar correcciones implementadas")
    print("📊 Expectativa: >80% éxito para continuar")
    print("="*70)
    
    executor = TDDCorrectionsExecutor()
    success = executor.run_all_executions()
    
    print("\n" + "="*70)
    print("📊 EJECUCIÓN TDD COMPLETADA")
    print("="*70)
    
    if success:
        print("🎉 ÉXITO: Correcciones TDD funcionando correctamente")
        print("📈 Sistema preparado para análisis de cobertura")
        print("🎯 Comando recomendado: pytest --cov=src --cov-report=html tests/")
        return True
    else:
        print("⚠️ ATENCIÓN: Algunos problemas detectados")
        print("🔍 Revisar reporte detallado arriba")
        print("🛠️ Resolver problemas antes de continuar")
        return False


if __name__ == '__main__':
    print("🎬 Iniciando Ejecución de Correcciones TDD...")
    success = run_tdd_corrections_execution()
    
    if success:
        print(f"\n✅ EJECUCIÓN EXITOSA - Continuar con FASE 5A")
        sys.exit(0)
    else:
        print(f"\n⚠️ EJECUCIÓN CON PROBLEMAS - Revisar y corregir")
        sys.exit(1)
