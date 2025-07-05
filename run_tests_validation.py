#!/usr/bin/env python3
"""
Script para ejecutar tests de validación de refactorización modo teclado.

Ejecuta los tests específicos para validar que la refactorización
a modo teclado funciona correctamente.
"""

import subprocess
import sys
import os
from datetime import datetime

def run_test(test_path, description):
    """Ejecutar un test específico y mostrar resultados."""
    print(f"\n{'='*60}")
    print(f"EJECUTANDO: {description}")
    print(f"Archivo: {test_path}")
    print('='*60)
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            test_path, 
            '-v', '--tb=short', '--no-header'
        ], capture_output=True, text=True, timeout=120)
        
        print(f"Return code: {result.returncode}")
        
        if result.stdout:
            print("\nSALIDA:")
            print(result.stdout)
        
        if result.stderr and result.stderr.strip():
            print("\nERRORES/WARNINGS:")
            print(result.stderr)
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("ERROR: Test timeout después de 120 segundos")
        return False
    except Exception as e:
        print(f"ERROR ejecutando test: {e}")
        return False

def main():
    """Función principal."""
    print("VALIDACIÓN DE REFACTORIZACIÓN MODO TECLADO")
    print("Sistema de Inventario Copy Point S.A.")
    print(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("\nValidando implementación sin dependencias de hardware...")
    
    # Cambiar al directorio del proyecto
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print(f"Directorio: {os.getcwd()}")
    
    # Lista de tests a ejecutar
    tests = [
        ("tests/ui/widgets/test_barcode_entry.py", 
         "Widget BarcodeEntry - Modo Teclado"),
        ("tests/ui/forms/test_movement_form_barcode_integration.py", 
         "MovementForm - Integración Códigos de Barras"),
        ("tests/ui/forms/test_sales_form_barcode_integration.py", 
         "SalesForm - Integración Códigos de Barras"),
        ("tests/test_barcode_service_keyboard_mode.py", 
         "BarcodeService - Modo Teclado"),
    ]
    
    # Ejecutar tests
    passed = 0
    failed = 0
    
    for test_path, description in tests:
        if os.path.exists(test_path):
            success = run_test(test_path, description)
            if success:
                passed += 1
                print(f"✅ {description}: ÉXITO")
            else:
                failed += 1
                print(f"❌ {description}: FALLÓ")
        else:
            print(f"⚠️ Test no encontrado: {test_path}")
            failed += 1
    
    # Resumen final
    print(f"\n{'='*60}")
    print("RESUMEN DE VALIDACIÓN")
    print('='*60)
    print(f"Tests exitosos: {passed}")
    print(f"Tests fallidos: {failed}")
    print(f"Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 REFACTORIZACIÓN VALIDADA EXITOSAMENTE")
        print("✅ Todos los tests pasaron")
        print("✅ Modo teclado implementado correctamente")
        print("✅ Sin dependencias de hardware")
        return True
    else:
        print(f"\n⚠️ REFACTORIZACIÓN REQUIERE ATENCIÓN")
        print(f"❌ {failed} tests fallaron")
        print("🔧 Revisar implementación antes de commit")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
