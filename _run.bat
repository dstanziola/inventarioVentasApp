@echo off
chcp 65001 >nul
title Sistema de Inventario - Launcher Simple

echo Iniciando Sistema de Inventario v2.0
echo(

:: Cambiar al directorio donde está el script
cd /d "%~dp0"

echo Directorio actual: %CD%
echo(

:: Verificar si Python está disponible
where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en PATH.
    pause
    exit
)

:: Intentar activar entorno virtual si existe
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo Entorno virtual activado
) else (
    echo No se encontró entorno virtual, usando Python del sistema
)

echo(
if exist "main.py" (
    echo main.py encontrado
) else (
    echo ERROR: main.py no encontrado
    pause
    exit
)

echo Ejecutando aplicación: usuario: admin, contraseña: admin123
python main.py

if errorlevel 1 (
    echo ERROR: La aplicación terminó con errores.
) else (
    echo Aplicación finalizada correctamente.
)

pause
