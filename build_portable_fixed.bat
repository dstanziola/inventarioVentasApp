@echo off
REM Script de construcción automatizado para CopyPoint-Inventario
REM Fecha: 2025-08-02

echo ============================================
echo  CONSTRUCCION CopyPoint-Inventario v1.0.4
echo ============================================

echo.
echo [1/6] Activando entorno virtual...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo ERROR: Entorno virtual no encontrado en venv\Scripts\
    echo Verificar que el entorno virtual está en la ubicación correcta
    pause
    exit /b 1
)

echo.
echo [2/6] Verificando dependencias...
pip install --upgrade pyinstaller
pip install --upgrade Pillow
if errorlevel 1 (
    echo ERROR: No se pudo instalar/actualizar dependencias
    pause
    exit /b 1
)

echo.
echo [3/6] Limpiando builds anteriores...
if exist "build" rmdir /S /Q "build"
if exist "dist" rmdir /S /Q "dist"
if exist "__pycache__" rmdir /S /Q "__pycache__"
del "*.spec" 2>nul
del "version_info.txt" 2>nul

echo.
echo [4/6] Generando archivos de configuración...
python build_config\pyinstaller_config_fixed.py
if errorlevel 1 (
    echo ERROR: No se pudieron generar archivos de configuración
    pause
    exit /b 1
)

echo.
echo [5/6] Construyendo ejecutable...
pyinstaller CopyPoint-Inventario.spec --clean --noconfirm
if errorlevel 1 (
    echo ERROR: Fallo en la construcción del ejecutable
    pause
    exit /b 1
)

echo.
echo [6/6] Creando paquete de distribución...
python build_config\create_portable_package_fixed.py
if errorlevel 1 (
    echo ERROR: No se pudo crear el paquete de distribución
    pause
    exit /b 1
)

echo.
echo ============================================
echo  CONSTRUCCION COMPLETADA EXITOSAMENTE
echo ============================================
echo.
echo Ejecutable creado en: dist\CopyPoint-Inventario.exe
echo Paquete portable en: dist\CopyPoint-Inventario-Portable\
echo.
pause
