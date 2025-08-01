# 1) Instalar Python si no existe
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Descargando e instalando Python 3.x..."
    Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.6/python-3.11.6-amd64.exe" -OutFile "$env:TEMP\python-installer.exe"
    Start-Process "$env:TEMP\python-installer.exe" -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1 Include_pip=1' -Wait
}

# 2) Crear carpeta de instalación
$installDir = "C:\Program Files\InventarioApp"
if (-not (Test-Path $installDir)) { New-Item -ItemType Directory -Path $installDir | Out-Null }

# 3) Copiar archivos del proyecto
Copy-Item -Path ".\*" -Destination $installDir -Recurse -Force

# 4) Instalar dependencias
Write-Host "Instalando dependencias..."
python -m pip install --upgrade pip
python -m pip install --no-cache-dir -r "$installDir\requirements.txt"

# 5) Crear acceso directo en Escritorio
$WScriptShell = New-Object -ComObject WScript.Shell
$shortcut = $WScriptShell.CreateShortcut("$env:USERPROFILE\Desktop\InventarioApp.lnk")
$shortcut.TargetPath = "python"
$shortcut.Arguments   = "`"$installDir\main.py`""
$shortcut.IconLocation = "$installDir\src\ui\main\icon.ico,0"  # si tienes un .ico
$shortcut.Save()

Write-Host "Instalación completada. Ejecuta InventarioApp desde el acceso directo."
