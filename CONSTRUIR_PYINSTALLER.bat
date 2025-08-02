@echo off
REM ========================================
REM  CONSTRUCCION RAPIDA PYINSTALLER
REM  COPY-INV v1.0.4 con Logo Personalizado
REM ========================================

echo.
echo 🚀 INICIANDO CONSTRUCCION PYINSTALLER OPTIMIZADO
echo ===============================================
echo.

REM Verificar que estamos en el directorio correcto
if not exist "main.py" (
    echo ❌ ERROR: main.py no encontrado
    echo    Ejecutar desde el directorio raiz del proyecto
    echo    Directorio actual: %CD%
    pause
    exit /b 1
)

REM Verificar logos disponibles
echo 🎨 Verificando logos disponibles...
set LOGOS_FOUND=0
if exist "logo 320x320.png" (
    echo    ✅ logo 320x320.png encontrado
    set /a LOGOS_FOUND+=1
)
if exist "logo 2000x2000.png" (
    echo    ✅ logo 2000x2000.png encontrado  
    set /a LOGOS_FOUND+=1
)
if exist "logo 940x788 transp.png" (
    echo    ✅ logo 940x788 transp.png encontrado
    set /a LOGOS_FOUND+=1
)

echo    📊 Total logos encontrados: %LOGOS_FOUND%/3

if %LOGOS_FOUND% EQU 0 (
    echo    ⚠️ ADVERTENCIA: No se encontraron archivos de logo
    echo       El ejecutable usará icono por defecto
    pause
)

echo.
echo ⚙️ Verificando entorno de desarrollo...

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python no está disponible
    echo    Asegúrate de que Python esté instalado y en el PATH
    pause
    exit /b 1
) else (
    echo ✅ Python disponible
)

REM Activar entorno virtual si existe
if exist "venv\Scripts\activate.bat" (
    echo ✅ Activando entorno virtual...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️ No se encontró entorno virtual en venv\Scripts\
    echo   Continuando con Python del sistema...
)

REM Verificar PyInstaller
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo 📦 Instalando PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo ❌ ERROR: No se pudo instalar PyInstaller
        pause
        exit /b 1
    )
) else (
    echo ✅ PyInstaller disponible
)

REM Verificar Pillow
pip show Pillow >nul 2>&1
if errorlevel 1 (
    echo 📦 Instalando Pillow para conversión de imágenes...
    pip install Pillow
    if errorlevel 1 (
        echo ❌ ERROR: No se pudo instalar Pillow
        pause
        exit /b 1
    )
) else (
    echo ✅ Pillow disponible
)

echo.
echo 🔨 EJECUTANDO CONSTRUCCION COMPLETA...
echo =====================================

REM Ejecutar script de construcción
python build_config\build_portable_complete.py

if errorlevel 1 (
    echo.
    echo ❌ ERROR EN LA CONSTRUCCION
    echo ===========================
    echo La construcción falló. Posibles causas:
    echo • Dependencias faltantes
    echo • Permisos insuficientes 
    echo • Archivos en uso
    echo • Espacio en disco insuficiente
    echo.
    echo Revisar los mensajes de error arriba para más detalles.
    pause
    exit /b 1
)

echo.
echo ✅ CONSTRUCCION COMPLETADA EXITOSAMENTE
echo ======================================

REM Verificar archivos generados
if exist "dist\CopyPoint-Inventario.exe" (
    echo ✅ Ejecutable principal: dist\CopyPoint-Inventario.exe
    for %%I in ("dist\CopyPoint-Inventario.exe") do echo    📊 Tamaño: %%~zI bytes
) else (
    echo ❌ Ejecutable principal no encontrado
)

if exist "dist\CopyPoint-Inventario-Portable" (
    echo ✅ Paquete portable: dist\CopyPoint-Inventario-Portable\
) else (
    echo ❌ Paquete portable no encontrado
)

if exist "dist\CopyPoint-Inventario-Portable_v1.0.4.zip" (
    echo ✅ Archivo ZIP: dist\CopyPoint-Inventario-Portable_v1.0.4.zip
    for %%I in ("dist\CopyPoint-Inventario-Portable_v1.0.4.zip") do echo    📊 Tamaño: %%~zI bytes
    echo.
    echo 🎯 ARCHIVO LISTO PARA DISTRIBUCION: 
    echo    dist\CopyPoint-Inventario-Portable_v1.0.4.zip
) else (
    echo ❌ Archivo ZIP de distribución no encontrado
)

echo.
echo 🎉 PROCESO COMPLETADO
echo ====================
echo.
echo Próximos pasos:
echo 1. Probar el ejecutable: dist\CopyPoint-Inventario.exe
echo 2. Probar instalación: extraer ZIP y ejecutar instalar.bat
echo 3. Verificar accesos directos con logo personalizado
echo 4. Distribuir: CopyPoint-Inventario-Portable_v1.0.4.zip
echo.
echo 📞 Soporte: soporte.inventario@copypoint.com
echo 📖 Documentación: dist\CopyPoint-Inventario-Portable\README.txt
echo.

pause
