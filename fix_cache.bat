@echo off
echo === SOLUCION RAPIDA - ERROR DE IMPORTACION DATABASE ===
echo.
echo 1. Limpiando archivos cache...
for /d /r "D:\inventario_app2" %%d in (__pycache__) do (
    if exist "%%d" (
        echo Eliminando: %%d
        rmdir /s /q "%%d"
    )
)

echo.
echo 2. Eliminando archivos .pyc individuales...
del /s /q "D:\inventario_app2\*.pyc" 2>nul

echo.
echo 3. Cache limpiado exitosamente
echo.
echo 4. Ahora intente ejecutar la aplicacion:
echo    python main.py
echo.
echo Si persiste el error, ejecute:
echo    python temp\fix_import_error.py
echo.
pause
