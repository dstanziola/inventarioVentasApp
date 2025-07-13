@echo off
:: Verificacion instantanea de correcciones - Una sola linea
:: Uso: check_fixes.bat

echo ⚡ VERIFICACION INSTANTANEA DE CORRECCIONES
echo.

:: Verificar Python y entorno
if exist "venv\Scripts\python.exe" (
    set PYTHON_CMD=venv\Scripts\python.exe
) else (
    set PYTHON_CMD=python
)

:: Ejecutar verificacion simple
%PYTHON_CMD% -c "
import sys, os
sys.path.insert(0, 'src')
errors = 0
try:
    from models.venta import Venta
    v = Venta(responsable='test')
    if hasattr(v, 'get') and v.get('responsable') == 'test':
        print('✅ Venta.get() - OK')
    else:
        print('❌ Venta.get() - FALLO')
        errors += 1
except Exception as e:
    print(f'❌ Venta import - FALLO: {e}')
    errors += 1

try:
    from services.sales_service import SalesService
    if hasattr(SalesService, 'obtener_detalles_venta'):
        print('✅ SalesService.obtener_detalles_venta - OK')
    else:
        print('❌ SalesService.obtener_detalles_venta - FALLO')
        errors += 1
except Exception as e:
    print(f'❌ SalesService import - FALLO: {e}')
    errors += 1

if errors == 0:
    print('\n🎉 CORRECCIONES FUNCIONAN - Listo para tests completos')
else:
    print(f'\n🚨 {errors} ERRORES DETECTADOS - Revisar implementacion')
    
sys.exit(errors)
"

if errorlevel 1 (
    echo.
    echo 💡 Para diagnostico completo ejecute: validate_corrections.bat
)

echo.
pause
