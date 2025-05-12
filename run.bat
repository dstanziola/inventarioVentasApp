@echo off
chcp 65001
echo Iniciando Gestor de Inventario...
echo.

:: Verificar si existe el entorno virtual
if not exist "venv" (
    echo Creando entorno virtual...
    python -m venv venv
    call venv\Scripts\activate
    echo Instalando dependencias...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate
)

:: Configurar PYTHONPATH
set PYTHONPATH=%PYTHONPATH%;%CD%

:: Ejecutar la aplicación
echo Iniciando aplicación...
python main.py
if errorlevel 1 (
    echo Error al ejecutar la aplicación
    echo Presione una tecla para salir...
    pause > nul
    exit /b 1
)

echo.
echo Presione una tecla para salir...
pause > nul