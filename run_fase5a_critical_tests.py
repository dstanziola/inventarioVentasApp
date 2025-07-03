"""
Script para ejecutar tests críticos FASE 5A - Formularios UI
=============================================================

Este script ejecuta los tests recién creados para CategoryForm y ClientForm
que son críticos para el deployment del sistema.

TESTS INCLUIDOS:
- test_category_form_basic.py (15 tests)
- test_client_form_basic.py (20 tests)

Ejecutar desde: D:\inventario_app2\
Comando: python run_fase5a_critical_tests.py

Autor: Sistema de Inventario Copy Point S.A.
Fecha: Julio 3, 2025 - FASE 5A
"""

import subprocess
import sys
import os
from pathlib import Path
import time

def print_header():
    """Imprimir encabezado del script."""
    print("\n" + "="*70)
    print("🧪 TESTS CRÍTICOS FASE 5A - FORMULARIOS UI")
    print("="*70)
    print("📅 Fecha: Julio 3, 2025")
    print("🎯 Objetivo: Validar CategoryForm y ClientForm")
    print("📊 Tests esperados: 35 tests totales")
    print("="*70 + "\n")

def check_environment():
    """Verificar que estamos en el directorio correcto."""
    current_dir = Path.cwd()
    expected_files = [
        'tests/test_category_form_basic.py',
        'tests/test_client_form_basic.py',
        'src/ui/forms/category_form.py',
        'src/ui/forms/client_form.py'
    ]
    
    print("🔍 VERIFICANDO ENTORNO...")
    print(f"📁 Directorio actual: {current_dir}")
    
    missing_files = []
    for file in expected_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ ARCHIVOS FALTANTES:")
        for file in missing_files:
            print(f"   • {file}")
        return False
    
    print("✅ Todos los archivos necesarios encontrados")
    return True

def run_test_file(test_file):
    """Ejecutar un archivo de test específico."""
    print(f"\n📋 EJECUTANDO: {test_file}")
    print("-" * 50)
    
    start_time = time.time()
    
    try:
        # Ejecutar el test
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=180  # 3 minutos timeout
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Analizar resultado
        if result.returncode == 0:
            print(f"✅ {test_file}: EXITOSO ({duration:.1f}s)")
            status = "SUCCESS"
        else:
            print(f"❌ {test_file}: FALLÓ ({duration:.1f}s)")
            status = "FAILED"
        
        # Extraer información relevante del output
        if result.stdout:
            lines = result.stdout.split('\n')
            
            # Buscar líneas de resumen
            for line in lines:
                if any(keyword in line for keyword in ['RESUMEN', 'Exitosos:', 'Tasa éxito:', 'tests ran']):
                    print(f"   📊 {line.strip()}")
            
            # Buscar errores específicos si falló
            if status == "FAILED":
                print("\n   🔍 DETALLES DEL ERROR:")
                error_lines = []
                for line in lines[-20:]:  # Últimas 20 líneas
                    if any(keyword in line.lower() for keyword in ['error', 'fail', 'exception', 'traceback']):
                        error_lines.append(line.strip())
                
                for error_line in error_lines[:5]:  # Máximo 5 líneas de error
                    print(f"   • {error_line}")
        
        if result.stderr and status == "FAILED":
            print(f"   ⚠️ Error stderr: {result.stderr[:200]}...")
        
        return status, duration
        
    except subprocess.TimeoutExpired:
        print(f"⏰ {test_file}: TIMEOUT")
        return "TIMEOUT", 180
    except Exception as e:
        print(f"💥 {test_file}: ERROR - {e}")
        return "ERROR", 0

def generate_summary(results):
    """Generar resumen final de ejecución."""
    print(f"\n" + "="*70)
    print("📊 RESUMEN FINAL - TESTS CRÍTICOS FASE 5A")
    print("="*70)
    
    total_tests = len(results)
    successful_tests = sum(1 for status, _ in results.values() if status == "SUCCESS")
    total_duration = sum(duration for _, duration in results.values())
    
    print(f"📈 Tests ejecutados: {total_tests}")
    print(f"✅ Exitosos: {successful_tests}")
    print(f"❌ Fallidos: {total_tests - successful_tests}")
    print(f"⏱️ Tiempo total: {total_duration:.1f}s")
    print(f"📊 Tasa de éxito: {(successful_tests/total_tests)*100:.1f}%")
    
    print(f"\n📋 DETALLE POR TEST:")
    for test_file, (status, duration) in results.items():
        status_icon = "✅" if status == "SUCCESS" else "❌"
        print(f"   {status_icon} {test_file}: {status} ({duration:.1f}s)")
    
    if successful_tests == total_tests:
        print(f"\n🎉 TODOS LOS TESTS EXITOSOS")
        print("✅ FORMULARIOS UI VALIDADOS PARA DEPLOYMENT")
        print("🚀 LISTOS PARA CONTINUAR FASE 5A")
    else:
        print(f"\n⚠️ HAY {total_tests - successful_tests} TESTS FALLIDOS")
        print("🔧 REVISAR ERRORES ANTES DE CONTINUAR")
        print("📝 CONSIDERAR AJUSTES EN CÓDIGO O TESTS")
    
    return successful_tests == total_tests

def main():
    """Función principal del script."""
    print_header()
    
    # Verificar entorno
    if not check_environment():
        print("\n❌ ENTORNO NO VÁLIDO - ABORTAR EJECUCIÓN")
        return False
    
    # Lista de tests críticos a ejecutar
    critical_tests = [
        'tests/test_category_form_basic.py',
        'tests/test_client_form_basic.py'
    ]
    
    print(f"\n🎯 EJECUTANDO {len(critical_tests)} TESTS CRÍTICOS...")
    
    # Ejecutar cada test
    results = {}
    for test_file in critical_tests:
        status, duration = run_test_file(test_file)
        results[test_file] = (status, duration)
    
    # Generar resumen
    all_successful = generate_summary(results)
    
    # Mensaje final
    if all_successful:
        print(f"\n🎊 ¡FASE 5A TESTS CRÍTICOS COMPLETADOS EXITOSAMENTE!")
        print("📝 Próximos pasos:")
        print("   1. Ejecutar coverage analysis completo")
        print("   2. Identificar tests faltantes restantes")
        print("   3. Completar tests de performance")
        print("   4. Preparar para deployment")
    else:
        print(f"\n🚨 ALGUNOS TESTS FALLARON - ACCIÓN REQUERIDA")
        print("📝 Acciones recomendadas:")
        print("   1. Revisar errores específicos arriba")
        print("   2. Verificar configuración de entorno")
        print("   3. Corregir código si es necesario")
        print("   4. Re-ejecutar tests fallidos")
    
    return all_successful

if __name__ == '__main__':
    try:
        success = main()
        exit_code = 0 if success else 1
        print(f"\n🏁 Script terminado con código: {exit_code}")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n⚠️ Ejecución interrumpida por usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        sys.exit(1)
