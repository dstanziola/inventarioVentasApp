"""
Script simple para validar tests críticos FASE 5A
================================================

Ejecuta tests críticos uno por uno y reporta resultados.
"""

import os
import sys
import subprocess
import time

def main():
    print("\n" + "="*60)
    print("🧪 VALIDACIÓN TESTS CRÍTICOS FASE 5A")
    print("="*60)
    
    # Cambiar al directorio del proyecto
    os.chdir("D:\\inventario_app2")
    print(f"📁 Directorio: {os.getcwd()}")
    
    # Tests a ejecutar
    tests = [
        "tests/test_category_form_basic.py",
        "tests/test_client_form_basic.py", 
        "tests/test_fase5a_coverage_analysis.py"
    ]
    
    results = {}
    
    for test_file in tests:
        print(f"\n🔍 VERIFICANDO: {test_file}")
        
        # Verificar que existe
        if not os.path.exists(test_file):
            print(f"❌ No encontrado: {test_file}")
            results[test_file] = "NOT_FOUND"
            continue
        
        print(f"✅ Archivo encontrado")
        
        # Intentar ejecutar
        try:
            start_time = time.time()
            result = subprocess.run([sys.executable, test_file], 
                                  capture_output=True, text=True, 
                                  timeout=120)
            duration = time.time() - start_time
            
            if result.returncode == 0:
                print(f"✅ EXITOSO ({duration:.1f}s)")
                results[test_file] = "SUCCESS"
                
                # Buscar líneas de resumen en output
                lines = result.stdout.split('\n')
                summary_lines = [line for line in lines if any(word in line for word in 
                               ['✅', '📊', 'RESUMEN', 'Tests exitosos', 'Tasa de éxito'])]
                
                for line in summary_lines[:3]:  # Solo las primeras 3 líneas relevantes
                    if line.strip():
                        print(f"   📊 {line.strip()}")
                        
            else:
                print(f"❌ FALLÓ ({duration:.1f}s)")
                results[test_file] = "FAILED"
                
                # Mostrar algunos errores
                if result.stderr:
                    error_lines = result.stderr.split('\n')[:3]
                    for line in error_lines:
                        if line.strip():
                            print(f"   ⚠️ {line.strip()}")
                            
        except subprocess.TimeoutExpired:
            print("⏰ TIMEOUT (>120s)")
            results[test_file] = "TIMEOUT"
        except Exception as e:
            print(f"💥 ERROR: {e}")
            results[test_file] = "ERROR"
    
    # Resumen final
    print(f"\n" + "="*60)
    print("📊 RESUMEN FINAL")
    print("="*60)
    
    total = len(results)
    successful = list(results.values()).count("SUCCESS")
    failed = list(results.values()).count("FAILED")
    errors = len(results) - successful - failed
    
    print(f"📈 Tests procesados: {total}")
    print(f"✅ Exitosos: {successful}")
    print(f"❌ Fallidos: {failed}")
    print(f"⚠️ Errores: {errors}")
    
    if total > 0:
        success_rate = (successful / total) * 100
        print(f"📊 Tasa de éxito: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("\n🎉 VALIDACIÓN EXITOSA")
            print("🚀 Sistema preparado para análisis completo de cobertura")
        else:
            print("\n⚠️ VALIDACIÓN PARCIAL") 
            print("🔧 Revisar componentes fallidos")
    
    print(f"\n🎯 Siguiente paso: Análisis detallado de cobertura con pytest")
    return successful >= (total * 0.8)  # 80% éxito mínimo

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
