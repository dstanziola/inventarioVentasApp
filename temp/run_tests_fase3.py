"""
Ejecutor de Tests Unitarios - FASE 3
Ejecuta todos los tests relacionados con la Fase 3 del sistema de tickets
"""

import unittest
import sys
import os
from pathlib import Path

def ejecutar_tests_fase3():
    """Ejecuta todos los tests unitarios de la Fase 3"""
    
    print("🧪 EJECUTANDO TESTS UNITARIOS - FASE 3")
    print("=" * 60)
    
    # Tests a ejecutar
    tests_fase3 = [
        'tests.unit.models.test_ticket',
        'tests.unit.models.test_company_config', 
        'tests.unit.services.test_ticket_service',
        'tests.unit.services.test_company_service'
    ]
    
    resultados = []
    total_tests = 0
    total_errores = 0
    total_fallos = 0
    
    for test_module in tests_fase3:
        print(f"\n🔍 Ejecutando: {test_module}")
        
        try:
            # Cargar el módulo de test
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromName(test_module)
            
            # Ejecutar tests
            runner = unittest.TextTestRunner(verbosity=1, buffer=True)
            result = runner.run(suite)
            
            # Recopilar resultados
            tests_run = result.testsRun
            errors = len(result.errors)
            failures = len(result.failures)
            
            total_tests += tests_run
            total_errores += errors
            total_fallos += failures
            
            if errors == 0 and failures == 0:
                status = "✅ EXITOSO"
            else:
                status = "❌ FALLIDO"
            
            print(f"  {status} - {tests_run} tests, {errors} errores, {failures} fallos")
            
            resultados.append({
                'module': test_module,
                'tests': tests_run,
                'errors': errors,
                'failures': failures,
                'success': errors == 0 and failures == 0
            })
            
        except Exception as e:
            print(f"  ❌ ERROR AL CARGAR: {e}")
            resultados.append({
                'module': test_module,
                'tests': 0,
                'errors': 1,
                'failures': 0,
                'success': False,
                'exception': str(e)
            })
            total_errores += 1
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE TESTS FASE 3:")
    
    exitosos = 0
    fallidos = 0
    
    for resultado in resultados:
        module_name = resultado['module'].split('.')[-1]
        if resultado['success']:
            print(f"  ✅ {module_name}: {resultado['tests']} tests")
            exitosos += 1
        else:
            errores = resultado.get('errors', 0)
            fallos = resultado.get('failures', 0)
            print(f"  ❌ {module_name}: {errores} errores, {fallos} fallos")
            if 'exception' in resultado:
                print(f"     Excepción: {resultado['exception']}")
            fallidos += 1
    
    print(f"\n📈 ESTADÍSTICAS GLOBALES:")
    print(f"  📊 Total de tests ejecutados: {total_tests}")
    print(f"  ✅ Módulos exitosos: {exitosos}")
    print(f"  ❌ Módulos fallidos: {fallidos}")
    print(f"  🚨 Total errores: {total_errores}")
    print(f"  ⚠️  Total fallos: {total_fallos}")
    
    # Conclusión
    if total_errores == 0 and total_fallos == 0:
        print(f"\n🎉 TODOS LOS TESTS DE FASE 3 PASARON EXITOSAMENTE")
        return True
    else:
        print(f"\n⚠️  HAY {total_errores + total_fallos} TESTS FALLIDOS")
        return False

def verificar_estructura_tests():
    """Verifica que existan los archivos de tests"""
    
    print("📁 VERIFICANDO ESTRUCTURA DE TESTS...")
    
    archivos_tests = [
        'tests/unit/models/test_ticket.py',
        'tests/unit/models/test_company_config.py',
        'tests/unit/services/test_ticket_service.py', 
        'tests/unit/services/test_company_service.py'
    ]
    
    faltantes = []
    
    for archivo in archivos_tests:
        if Path(archivo).exists():
            print(f"  ✅ {archivo}")
        else:
            print(f"  ❌ FALTA: {archivo}")
            faltantes.append(archivo)
    
    if faltantes:
        print(f"\n⚠️  FALTAN {len(faltantes)} ARCHIVOS DE TESTS")
        return False
    else:
        print(f"\n✅ TODOS LOS ARCHIVOS DE TESTS PRESENTES")
        return True

def main():
    """Función principal"""
    
    # Verificar estructura primero
    if not verificar_estructura_tests():
        print("❌ No se pueden ejecutar los tests sin los archivos requeridos")
        return False
    
    # Ejecutar tests
    success = ejecutar_tests_fase3()
    
    if success:
        print("\n✅ VALIDACIÓN DE TESTS COMPLETADA")
    else:
        print("\n❌ VALIDACIÓN DE TESTS FALLIDA")
    
    return success

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
