@echo off
REM ============================================
REM CONSTRUCCIÓN AUTOMÁTICA PYINSTALLER CON LOGO
REM Sistema de Inventario Copy Point S.A.
REM ============================================

echo 🚀 CONSTRUCCIÓN PYINSTALLER OPTIMIZADO CON LOGO PERSONALIZADO
echo ============================================
echo   App: CopyPoint-Inventario v1.0.4
echo   Logos: 3 archivos PNG disponibles
echo   Destino: Paquete portable para distribución
echo ============================================

echo.
echo [PASO 1] 🔧 Activando entorno virtual...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo    ✅ Entorno virtual activado
) else (
    echo    ❌ ERROR: Entorno virtual no encontrado
    echo    ℹ️  Verificar que existe: venv\Scripts\activate.bat
    pause
    exit /b 1
)

echo.
echo [PASO 2] 📋 Verificando dependencias críticas...
python -c "import PyInstaller; print('   ✅ PyInstaller:', PyInstaller.__version__)" 2>nul || (
    echo    📦 Instalando PyInstaller...
    pip install --upgrade pyinstaller
)

python -c "import PIL; print('   ✅ Pillow disponible para conversión ICO')" 2>nul || (
    echo    📦 Instalando Pillow...
    pip install --upgrade Pillow
)

echo.
echo [PASO 3] 🎨 Verificando logos disponibles...
if exist "logo 320x320.png" (
    echo    ✅ logo 320x320.png - Óptimo para ICO
) else (
    echo    ⚠️  logo 320x320.png no encontrado
)

if exist "logo 2000x2000.png" (
    echo    ✅ logo 2000x2000.png - Alta resolución
) else (
    echo    ⚠️  logo 2000x2000.png no encontrado
)

if exist "logo 940x788 transp.png" (
    echo    ✅ logo 940x788 transp.png - Con transparencia
) else (
    echo    ⚠️  logo 940x788 transp.png no encontrado
)

echo.
echo [PASO 4] ⚡ EJECUTANDO CONSTRUCCIÓN AUTOMÁTICA...
echo ============================================
echo ⏱️  Tiempo estimado: 5-10 minutos
echo 🎯 Proceso completo automático en curso...
echo ============================================

python build_config\build_portable_complete.py

if errorlevel 1 (
    echo.
    echo ❌ ERROR en la construcción
    echo Revisar mensajes anteriores para detalles
    pause
    exit /b 1
) else (
    echo.
    echo ============================================
    echo 🎉 CONSTRUCCIÓN COMPLETADA EXITOSAMENTE
    echo ============================================
    echo.
    echo 📦 Archivos generados en dist\:
    echo    • CopyPoint-Inventario.exe (ejecutable con logo)
    echo    • CopyPoint-Inventario-Portable\ (paquete completo)
    echo    • CopyPoint-Inventario-Portable_v1.0.4.zip (📎 LISTO PARA PENDRIVE)
    echo    • build_report.json (reporte técnico)
    echo    • GUIA_RAPIDA.md (instrucciones distribución)
    echo.
    echo 🎯 EL PAQUETE ESTÁ LISTO PARA DISTRIBUCIÓN
    echo    • Logo corporativo integrado en ejecutable
    echo    • Accesos directos con iconos personalizados
    echo    • Scripts de instalación automáticos
    echo    • Sistema de actualizaciones incluido
    echo    • Compatible Windows 10/11 sin dependencias
    echo.
    echo 📋 Próximos pasos:
    echo    1. Probar el paquete en sistema limpio
    echo    2. Copiar archivo ZIP a pendrive para distribución
    echo    3. Proporcionar GUIA_RAPIDA.md a usuarios finales
    echo.
    start dist
    echo 📁 Abriendo carpeta dist con resultados...
)

echo.
pause
