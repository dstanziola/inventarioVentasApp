@echo off
echo ======================================================
echo SOLUCION CRITICA: MovementEntryForm Error Fix
echo Errores a resolver:
echo 1. Campo obligatorio 'code' faltante en producto
echo 2. No se pudo obtener informacion del usuario actual
echo ======================================================
echo.

echo [INFO] Eliminando cache corrupto...

REM Eliminar directorios de cache criticos
if exist "src\ui\shared\__pycache__" (
    rmdir /s /q "src\ui\shared\__pycache__"
    echo [OK] Eliminado: src\ui\shared\__pycache__
) else (
    echo [SKIP] No existe: src\ui\shared\__pycache__
)

if exist "src\ui\forms\__pycache__" (
    rmdir /s /q "src\ui\forms\__pycache__"
    echo [OK] Eliminado: src\ui\forms\__pycache__
) else (
    echo [SKIP] No existe: src\ui\forms\__pycache__
)

if exist "src\ui\widgets\__pycache__" (
    rmdir /s /q "src\ui\widgets\__pycache__"
    echo [OK] Eliminado: src\ui\widgets\__pycache__
) else (
    echo [SKIP] No existe: src\ui\widgets\__pycache__
)

if exist "src\services\__pycache__" (
    rmdir /s /q "src\services\__pycache__"
    echo [OK] Eliminado: src\services\__pycache__
) else (
    echo [SKIP] No existe: src\services\__pycache__
)

if exist "src\application\services\__pycache__" (
    rmdir /s /q "src\application\services\__pycache__"
    echo [OK] Eliminado: src\application\services\__pycache__
) else (
    echo [SKIP] No existe: src\application\services\__pycache__
)

echo.
echo ======================================================
echo LIMPIEZA COMPLETADA
echo ======================================================
echo.
echo PROXIMOS PASOS:
echo 1. Reiniciar la aplicacion principal
echo 2. Python regenerara cache limpio automaticamente
echo 3. Probar subformulario de movimiento entrada
echo 4. Los errores deben estar resueltos
echo.
echo NOTA: Las correcciones YA ESTAN implementadas en el codigo
echo El problema era solo cache corrupto con versiones anteriores
echo.
pause
