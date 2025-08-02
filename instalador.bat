@echo off
REM ------------------------------
REM setup.bat — Ejecuta install.ps1
REM ------------------------------

REM 1) Determinar ruta donde está este .bat
SET "SCRIPT_DIR=%~dp0"

REM 2) Verificar que existan install.ps1 y requirements.txt
IF NOT EXIST "%SCRIPT_DIR%install.ps1" (
    ECHO ERROR: No se encontró install.ps1 en %SCRIPT_DIR%
    PAUSE
    EXIT /B 1
)
IF NOT EXIST "%SCRIPT_DIR%requirements.txt" (
    ECHO ERROR: No se encontró requirements.txt en %SCRIPT_DIR%
    PAUSE
    EXIT /B 1
)

REM 3) Invocar PowerShell para ejecutar el script con política de ejecución temporalmente relajada
ECHO Ejecutando instalación...
powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%install.ps1"
IF %ERRORLEVEL% NEQ 0 (
    ECHO.
    ECHO *** La instalación falló con código de error %ERRORLEVEL% ***
    PAUSE
    EXIT /B %ERRORLEVEL%
)

REM 4) Fin correcto
ECHO.
ECHO Instalación completada con éxito.
PAUSE
