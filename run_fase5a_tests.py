#!/usr/bin/env python3
"""
Script para ejecutar tests de FASE 5A y generar reporte de cobertura.

FASE 5A: Testing Final ≥95% Cobertura
Ejecuta: coverage_analysis, performance, security
"""

import os
import sys
import subprocess
import traceback

# Agregar directorio principal al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_single_test(test_file, test_name):
    """Ejecutar un test individual y capturar resultado."""
    print(f"\n{'='*70}")
    print(f"🧪 EJECUTANDO: {test_name}")
    print(f"📁 Archivo: {test_file}")
    print(f"{'='*70}")
    
    try:
        # Intentar ejecutar el test directamente
        test_path = os.path.join("tests", test_file)
        
        if not os.path.exists(test_path):
            print(f"❌ ERROR: Archivo {test_path} no encontrado")
            return False
        
        # Ejecutar usando el módulo directamente
        result = subprocess.run([
            sys.executable, test_path
        ], capture_output=True, text=True, timeout=300)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        
        print(f"\nCódigo de salida: {result.returncode}")
        
        # Considerar exitoso si código de salida es 0
        success = result.returncode == 0
        
        if success:
            print(f"✅ {test_name} - EXITOSO")
        else:
            print(f"❌ {test_name} - FALLÓ")
        
        return success
        
    except subprocess.TimeoutExpired:
        print(f"⏰ TIMEOUT: {test_name} excedió 5 minutos")
        return False
    except Exception as e:
        print(f"❌ ERROR EJECUTANDO {test_name}: {e}")
        traceback.print_exc()
        return False

def main():
    """Ejecutar todos los tests de FASE 5A."""
    print("🎯 SISTEMA DE INVENTARIO - EJECUCIÓN TESTS FASE 5A")
    print("📊 Objetivo: Validar cobertura ≥95% y preparar para deployment")
    print("⚡ Tests: Coverage Analysis, Performance, Security")
    
    # Cambiar al directorio del proyecto
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    print(f"📂 Directorio de trabajo: {project_dir}")
    
    # Tests a ejecutar
    tests_to_run = [
        ("test_fase5a_coverage_analysis.py", "Coverage Analysis"),
        ("test_fase5a_performance.py", "Performance Testing"),
        ("test_fase5a_security.py", "Security Testing")
    ]
    
    results = {}
    
    # Ejecutar cada test
    for test_file, test_name in tests_to_run:
        success = run_single_test(test_file, test_name)
        results[test_name] = success
    
    # Reporte final
    print(f"\n{'='*70}")
    print("📊 REPORTE FINAL FASE 5A")
    print(f"{'='*70}")
    
    total_tests = len(results)
    successful_tests = sum(1 for success in results.values() if success)
    failed_tests = total_tests - successful_tests
    
    print(f"📈 Total tests ejecutados: {total_tests}")
    print(f"✅ Tests exitosos: {successful_tests}")
    print(f"❌ Tests fallidos: {failed_tests}")
    
    success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
    print(f"📊 Tasa de éxito: {success_rate:.1f}%")
    
    # Detalle por test
    print(f"\n📋 DETALLE POR TEST:")
    for test_name, success in results.items():
        status = "✅ EXITOSO" if success else "❌ FALLÓ"
        print(f"   • {test_name}: {status}")
    
    # Recomendaciones
    print(f"\n🎯 EVALUACIÓN FINAL:")
    if success_rate >= 95:
        print("🎉 EXCELENTE - Sistema listo para FASE 5B deployment")
        print("✅ Recomendación: Proceder con deployment y documentación")
        print("🚀 Próximo paso: Ejecutar deployment scripts")
    elif success_rate >= 80:
        print("⚠️ ACEPTABLE - Resolver issues menores antes de deployment")
        print("🔧 Recomendación: Revisar tests fallidos y corregir")
        print("📝 Próximo paso: Corregir problemas identificados")
    else:
        print("❌ INSUFICIENTE - Requiere correcciones antes de deployment")
        print("🛠️ Recomendación: Revisar y corregir problemas críticos")
        print("⚠️ Próximo paso: Debugging y corrección de issues")
    
    return success_rate >= 95

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Ejecución interrumpida por usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        traceback.print_exc()
        sys.exit(1)
