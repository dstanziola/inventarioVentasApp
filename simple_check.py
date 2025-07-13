#!/usr/bin/env python3
"""
Verificación básica y rápida de correcciones implementadas.

Script simple que no requiere pytest, solo Python estándar.
Valida que las correcciones básicas funcionan.

Uso: python simple_check.py
"""

import sys
import os
from pathlib import Path


def simple_check():
    """Verificación simple de correcciones."""
    print("🔍 VERIFICACIÓN SIMPLE DE CORRECCIONES")
    print("=" * 50)
    
    # Detectar directorio src
    current_dir = Path.cwd()
    src_dir = None
    
    if (current_dir / 'src').exists():
        src_dir = current_dir / 'src'
    elif (current_dir.parent / 'src').exists():
        src_dir = current_dir.parent / 'src'
    else:
        print("❌ ERROR: No se encuentra directorio 'src'")
        print("   Ejecute desde el directorio raíz del proyecto")
        return False
    
    print(f"📁 Directorio src: {src_dir}")
    
    # Agregar src al path
    sys.path.insert(0, str(src_dir))
    
    errors = 0
    
    # Test 1: Verificar imports básicos
    print("\n1️⃣ Verificando imports básicos...")
    try:
        from models.venta import Venta
        print("   ✅ models.venta importado correctamente")
    except Exception as e:
        print(f"   ❌ Error importando models.venta: {e}")
        errors += 1
    
    try:
        from services.sales_service import SalesService
        print("   ✅ services.sales_service importado correctamente")
    except Exception as e:
        print(f"   ❌ Error importando services.sales_service: {e}")
        errors += 1
    
    # Test 2: Verificar método get() en Venta
    print("\n2️⃣ Verificando método Venta.get()...")
    try:
        venta = Venta(responsable="test_user", id_cliente=123)
        
        # Verificar que método existe
        if not hasattr(venta, 'get'):
            print("   ❌ ERROR: Venta no tiene método get()")
            errors += 1
        else:
            print("   ✅ Método get() existe")
            
            # Verificar funcionamiento básico
            responsable = venta.get('responsable')
            if responsable == "test_user":
                print("   ✅ get() retorna valores correctos")
            else:
                print(f"   ❌ ERROR: get() retornó '{responsable}', esperado 'test_user'")
                errors += 1
            
            # Verificar default value
            missing = venta.get('missing_attr', 'default')
            if missing == 'default':
                print("   ✅ get() maneja valores por defecto correctamente")
            else:
                print(f"   ❌ ERROR: get() con default retornó '{missing}', esperado 'default'")
                errors += 1
                
    except Exception as e:
        print(f"   ❌ ERROR: Fallo al probar Venta.get(): {e}")
        errors += 1
    
    # Test 3: Verificar método obtener_detalles_venta en SalesService
    print("\n3️⃣ Verificando SalesService.obtener_detalles_venta()...")
    try:
        # Verificar que método existe (sin ejecutarlo)
        if hasattr(SalesService, 'obtener_detalles_venta'):
            print("   ✅ Método obtener_detalles_venta existe")
        else:
            print("   ❌ ERROR: SalesService no tiene método obtener_detalles_venta")
            errors += 1
            
    except Exception as e:
        print(f"   ❌ ERROR: Fallo al verificar SalesService: {e}")
        errors += 1
    
    # Test 4: Verificar estructura de archivos críticos
    print("\n4️⃣ Verificando archivos críticos...")
    critical_files = [
        'models/venta.py',
        'services/sales_service.py',
        'ui/forms/sales_form.py'
    ]
    
    for file_path in critical_files:
        full_path = src_dir / file_path
        if full_path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - NO ENCONTRADO")
            errors += 1
    
    # Resumen final
    print("\n" + "=" * 50)
    if errors == 0:
        print("🎉 VERIFICACIÓN EXITOSA")
        print("   Todas las correcciones básicas funcionan correctamente")
        print("   Sistema listo para pruebas más exhaustivas")
        return True
    else:
        print(f"🚨 VERIFICACIÓN FALLIDA - {errors} errores encontrados")
        print("   Revisar e implementar correcciones faltantes")
        print("   Ejecutar scripts completos para más detalles")
        return False


if __name__ == '__main__':
    print("VERIFICACIÓN SIMPLE - CORRECCIONES SALES_FORM.PY")
    print("Verificación rápida sin dependencias externas")
    print()
    
    try:
        success = simple_check()
        
        print("\n📋 PRÓXIMOS PASOS:")
        if success:
            print("   1. Ejecutar validate_corrections.bat para validación completa")
            print("   2. Ejecutar tests exhaustivos con pytest")
            print("   3. Probar funcionalidad en interfaz real")
        else:
            print("   1. Revisar errores mostrados arriba")
            print("   2. Implementar correcciones faltantes")
            print("   3. Ejecutar esta verificación nuevamente")
        
        print(f"\n⏰ Verificación completada")
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Verificación cancelada por usuario")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)
