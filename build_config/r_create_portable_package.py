#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Creador de Paquete Portable para COPY-INV con Acceso Directo Personalizado
Archivo: build_config/create_portable_package.py
Fecha: 2025-08-02
Versión: 1.0.0

Este script crea un paquete portable completo que incluye:
- Ejecutable principal con logo
- Acceso directo personalizado con icono
- Sistema de actualizaciones
- Base de datos inicial
- Configuraciones por defecto
- Scripts de instalación avanzados
"""

import os
import sys
import shutil
import zipfile
import json
from pathlib import Path
from datetime import datetime

# Configuración del paquete
PROJECT_ROOT = Path(__file__).parent.parent
APP_NAME = "CopyPoint-Inventario"
VERSION = "1.0.4"
PACKAGE_NAME = f"{APP_NAME}-Portable"

# Configuración de logos
LOGO_320 = PROJECT_ROOT / "logo 320x320.png"
LOGO_2000 = PROJECT_ROOT / "logo 2000x2000.png"
LOGO_TRANSP = PROJECT_ROOT / "logo 940x788 transp.png"
ICON_PATH = PROJECT_ROOT / "copypoint_logo.ico"

class PortablePackageCreator:
    """Creador de paquete portable para distribución con logo personalizado."""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.dist_dir = self.project_root / "dist"
        self.package_dir = self.dist_dir / PACKAGE_NAME
        self.exe_path = self.dist_dir / f"{APP_NAME}.exe"
        
    def create_package(self):
        """Crear paquete portable completo."""
        print(f"Creando paquete portable {PACKAGE_NAME} v{VERSION}")
        
        # Verificar que existe el ejecutable
        if not self.exe_path.exists():
            raise FileNotFoundError(f"Ejecutable no encontrado: {self.exe_path}")
        
        # Crear estructura de directorios
        self._create_directory_structure()
        
        # Copiar archivos principales
        self._copy_main_files()
        
        # Copiar logos y assets
        self._copy_logo_assets()
        
        # Crear sistema de actualizaciones
        self._create_updater_system()
        
        # Crear base de datos inicial
        self._create_initial_database()
        
        # Crear scripts de instalación avanzados
        self._create_installation_scripts()
        
        # Crear documentación
        self._create_documentation()
        
        # Crear archivo de versión
        self._create_version_file()
        
        # Crear paquete ZIP para distribución
        self._create_zip_package()
        
        print(f"Paquete portable creado exitosamente en: {self.package_dir}")
        
    def _create_directory_structure(self):
        """Crear estructura de directorios del paquete."""
        print("Creando estructura de directorios...")
        
        # Limpiar directorio si existe
        if self.package_dir.exists():
            shutil.rmtree(self.package_dir)
        
        # Crear directorios principales
        directories = [
            self.package_dir,
            self.package_dir / "app",
            self.package_dir / "assets",
            self.package_dir / "data",
            self.package_dir / "config",
            self.package_dir / "logs",
            self.package_dir / "backups",
            self.package_dir / "updates",
            self.package_dir / "docs",
            self.package_dir / "temp",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            
    def _copy_main_files(self):
        """Copiar archivos principales del proyecto."""
        print("Copiando archivos principales...")
        
        # Copiar ejecutable principal
        shutil.copy2(self.exe_path, self.package_dir / "app" / f"{APP_NAME}.exe")
        
        # Copiar archivos de configuración si existen
        config_files = [
            "config.py",
            "config_db.py",
            "styles.py",
            ".env",
        ]
        
        for config_file in config_files:
            source_path = self.project_root / config_file
            if source_path.exists():
                shutil.copy2(source_path, self.package_dir / "config" / config_file)
        
        # Copiar directorio config si existe
        config_dir = self.project_root / "config"
        if config_dir.exists():
            shutil.copytree(config_dir, self.package_dir / "config" / "app_config", dirs_exist_ok=True)
            
    def _copy_logo_assets(self):
        """Copiar logos y assets visuales."""
        print("Copiando logos y assets...")
        
        assets_dir = self.package_dir / "assets"
        
        # Copiar todos los logos disponibles
        logo_files = [
            ("logo 320x320.png", "logo_medium.png"),
            ("logo 2000x2000.png", "logo_high.png"),
            ("logo 940x788 transp.png", "logo_transparent.png"),
            ("copypoint_logo.ico", "app_icon.ico"),
        ]
        
        for source_name, dest_name in logo_files:
            source_path = self.project_root / source_name
            if source_path.exists():
                dest_path = assets_dir / dest_name
                shutil.copy2(source_path, dest_path)
                print(f"Copiado: {source_name} → {dest_name}")
        
        # Crear logo para acceso directo (usar el mejor disponible)
        shortcut_icon = self._prepare_shortcut_icon()
        if shortcut_icon:
            shutil.copy2(shortcut_icon, assets_dir / "shortcut_icon.ico")
            print(f"Icono de acceso directo preparado")
            
    def _prepare_shortcut_icon(self):
        """Preparar icono optimizado para acceso directo."""
        # Si ya existe el ICO, usarlo
        if ICON_PATH.exists():
            return ICON_PATH
        
        # Si no, intentar convertir desde PNG
        try:
            from PIL import Image
            
            # Usar logo de mejor calidad disponible
            if LOGO_320.exists():
                source_logo = LOGO_320
            elif LOGO_2000.exists():
                source_logo = LOGO_2000
            elif LOGO_TRANSP.exists():
                source_logo = LOGO_TRANSP
            else:
                return None
                
            print(f"Convirtiendo {source_logo.name} a ICO para acceso directo...")
            
            img = Image.open(source_logo)
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Crear ICO optimizado para acceso directo (32x32, 48x48, 256x256)
            sizes = [(32, 32), (48, 48), (256, 256)]
            icons = []
            
            for size in sizes:
                icon = img.copy()
                icon.thumbnail(size, Image.Resampling.LANCZOS)
                
                new_icon = Image.new('RGBA', size, (0, 0, 0, 0))
                x = (size[0] - icon.size[0]) // 2
                y = (size[1] - icon.size[1]) // 2
                new_icon.paste(icon, (x, y), icon)
                icons.append(new_icon)
            
            shortcut_ico_path = self.project_root / "shortcut_icon.ico"
            icons[0].save(
                shortcut_ico_path,
                format='ICO',
                sizes=[icon.size for icon in icons],
                append_images=icons[1:]
            )
            
            return shortcut_ico_path
            
        except Exception as e:
            print(f"No se pudo crear ICO para acceso directo: {e}")
            return None
            
    def _create_updater_system(self):
        """Crear sistema de actualizaciones automáticas."""
        print("Creando sistema de actualizaciones...")
        
        updater_script = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Actualizaciones para {APP_NAME}
Generado automáticamente el {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

import os
import sys
import json
import urllib.request
import zipfile
import shutil
from pathlib import Path
try:
    from tkinter import messagebox, Toplevel, Label, Button, Progressbar
    import tkinter as tk
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

class UpdaterSystem:
    """Sistema de actualizaciones automáticas."""
    
    def __init__(self):
        self.app_dir = Path(__file__).parent / "app"
        self.updates_dir = Path(__file__).parent / "updates"
        self.current_version = "{VERSION}"
        self.update_server = "https://updates.copypoint.com/inventario"  # Configurar servidor
        
    def check_for_updates(self, show_no_updates=True):
        """Verificar si hay actualizaciones disponibles."""
        if not TKINTER_AVAILABLE and show_no_updates:
            print("Sistema de actualizaciones disponible - ejecutar desde aplicación principal")
            return False
            
        try:
            # Obtener información de versión del servidor
            version_url = f"{{self.update_server}}/version.json"
            
            with urllib.request.urlopen(version_url, timeout=10) as response:
                version_info = json.loads(response.read().decode())
            
            latest_version = version_info.get("version", self.current_version)
            download_url = version_info.get("download_url", "")
            
            if self._is_newer_version(latest_version, self.current_version):
                return self._prompt_update(latest_version, download_url)
            elif show_no_updates and TKINTER_AVAILABLE:
                messagebox.showinfo("Actualizaciones", 
                                   f"Ya tienes la versión más reciente (v{{self.current_version}})")
                return False
                
        except Exception as e:
            if show_no_updates and TKINTER_AVAILABLE:
                messagebox.showerror("Error de Actualización", 
                                   f"No se pudo verificar actualizaciones: {{e}}")
            else:
                print(f"Error verificando actualizaciones: {{e}}")
            return False
    
    def _is_newer_version(self, latest, current):
        """Comparar versiones."""
        latest_parts = [int(x) for x in latest.split('.')]
        current_parts = [int(x) for x in current.split('.')]
        
        return latest_parts > current_parts
    
    def _prompt_update(self, version, download_url):
        """Preguntar al usuario si desea actualizar."""
        if not TKINTER_AVAILABLE:
            return False
            
        result = messagebox.askyesno(
            "Actualización Disponible",
            f"Hay una nueva versión disponible: v{{version}}\\n"
            f"Versión actual: v{{self.current_version}}\\n\\n"
            f"¿Deseas descargar e instalar la actualización ahora?"
        )
        
        if result:
            return self._download_and_install(version, download_url)
        return False
    
    def _download_and_install(self, version, download_url):
        """Descargar e instalar actualización."""
        try:
            # Crear ventana de progreso
            progress_window = self._create_progress_window()
            
            # Descargar actualización
            update_file = self.updates_dir / f"update_v{{version}}.zip"
            self._download_file(download_url, update_file, progress_window)
            
            # Instalar actualización
            self._install_update(update_file, progress_window)
            
            progress_window.destroy()
            
            if TKINTER_AVAILABLE:
                messagebox.showinfo("Actualización Completada", 
                                   f"Actualización a v{{version}} instalada correctamente.\\n"
                                   f"La aplicación se reiniciará.")
            
            # Reiniciar aplicación
            self._restart_application()
            return True
            
        except Exception as e:
            if 'progress_window' in locals():
                progress_window.destroy()
            if TKINTER_AVAILABLE:
                messagebox.showerror("Error de Actualización", 
                                   f"Error durante la actualización: {{e}}")
            else:
                print(f"Error durante actualización: {{e}}")
            return False
    
    def _create_progress_window(self):
        """Crear ventana de progreso."""
        if not TKINTER_AVAILABLE:
            return None
            
        window = Toplevel()
        window.title("Actualizando COPY-INV...")
        window.geometry("400x150")
        window.resizable(False, False)
        
        # Centrar ventana
        window.update_idletasks()
        x = (window.winfo_screenwidth() // 2) - (400 // 2)
        y = (window.winfo_screenheight() // 2) - (150 // 2)
        window.geometry(f"400x150+{{x}}+{{y}}")
        
        Label(window, text="Descargando actualización...", font=("Arial", 12)).pack(pady=20)
        
        progress = Progressbar(window, length=300, mode='indeterminate')
        progress.pack(pady=10)
        progress.start()
        
        window.update()
        return window
    
    def _download_file(self, url, destination, progress_window):
        """Descargar archivo con progreso."""
        self.updates_dir.mkdir(exist_ok=True)
        urllib.request.urlretrieve(url, destination)
        if progress_window:
            progress_window.update()
    
    def _install_update(self, update_file, progress_window):
        """Instalar actualización desde archivo ZIP."""
        # Extraer actualización
        with zipfile.ZipFile(update_file, 'r') as zip_ref:
            zip_ref.extractall(self.updates_dir / "temp")
        
        # Hacer backup de la versión actual
        backup_dir = Path(__file__).parent / "backups" / f"v{{self.current_version}}_{{datetime.now().strftime('%Y%m%d_%H%M%S')}}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        shutil.copytree(self.app_dir, backup_dir / "app")
        
        # Reemplazar archivos
        temp_dir = self.updates_dir / "temp"
        for item in temp_dir.iterdir():
            if item.is_file():
                shutil.copy2(item, self.app_dir / item.name)
            elif item.is_dir():
                shutil.copytree(item, self.app_dir / item.name, dirs_exist_ok=True)
        
        # Limpiar archivos temporales
        shutil.rmtree(temp_dir)
        update_file.unlink()
        
        if progress_window:
            progress_window.update()
    
    def _restart_application(self):
        """Reiniciar la aplicación."""
        app_exe = self.app_dir / "{APP_NAME}.exe"
        if app_exe.exists():
            os.startfile(str(app_exe))
        sys.exit(0)

if __name__ == "__main__":
    updater = UpdaterSystem()
    updater.check_for_updates()
'''
        
        updater_path = self.package_dir / "updater.py"
        with open(updater_path, 'w', encoding='utf-8') as f:
            f.write(updater_script)
            
    def _create_initial_database(self):
        """Crear base de datos inicial."""
        print("🗄️ Creando base de datos inicial...")
        
        # Si existe una base de datos en el proyecto, copiarla
        source_db = self.project_root / "inventario.db"
        if source_db.exists():
            shutil.copy2(source_db, self.package_dir / "data" / "inventario.db")
            print("Base de datos copiada desde proyecto")
        else:
            # Crear base de datos vacía (se inicializará en primer uso)
            db_path = self.package_dir / "data" / "inventario.db"
            db_path.touch()
            print("Base de datos vacía creada (se inicializará en primer uso)")
            
    def _create_installation_scripts(self):
        """Crear scripts de instalación avanzados con acceso directo personalizado."""
        print("Creando scripts de instalación...")
        
        # Script de instalación Windows con acceso directo personalizado
        install_script = f'''@echo off
REM Script de Instalación {APP_NAME} v{VERSION}
REM Generado automáticamente el {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

echo ============================================
echo  INSTALACION {APP_NAME} v{VERSION}
echo ============================================

echo.
echo [1/6] Verificando sistema...
ver | findstr /i "10\\." > nul
if errorlevel 1 (
    ver | findstr /i "11\\." > nul
    if errorlevel 1 (
        echo ADVERTENCIA: Este software ha sido probado en Windows 10/11
        echo Su sistema puede no ser compatible
        pause
    )
)

echo.
echo [2/6] Verificando permisos de administrador...
openfiles >nul 2>&1
if errorlevel 1 (
    echo ADVERTENCIA: Se recomienda ejecutar como administrador
    echo para crear accesos directos correctamente
    pause
)

echo.
echo [3/6] Creando estructura de directorios...
if not exist "logs\\." mkdir logs
if not exist "temp\\." mkdir temp
if not exist "backups\\." mkdir backups
if not exist "data\\." mkdir data

echo.
echo [4/6] Creando acceso directo en el escritorio...
set DESKTOP=%USERPROFILE%\\Desktop
set TARGET=%~dp0app\\{APP_NAME}.exe
set SHORTCUT=%DESKTOP%\\COPY-INV Sistema de Inventario.lnk
set ICON_PATH=%~dp0assets\\shortcut_icon.ico

REM Verificar si existe el icono
if not exist "%ICON_PATH%" (
    set ICON_PATH=%~dp0assets\\app_icon.ico
)
if not exist "%ICON_PATH%" (
    set ICON_PATH=%TARGET%
)

REM Crear acceso directo con PowerShell
powershell -Command "^
$WshShell = New-Object -comObject WScript.Shell; ^
$Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); ^
$Shortcut.TargetPath = '%TARGET%'; ^
$Shortcut.WorkingDirectory = '%~dp0'; ^
$Shortcut.IconLocation = '%ICON_PATH%'; ^
$Shortcut.Description = 'Sistema de Inventario Copy Point S.A. - COPY-INV v{VERSION}'; ^
$Shortcut.WindowStyle = 1; ^
$Shortcut.Save()"

if exist "%SHORTCUT%" (
    echo    Acceso directo creado en el escritorio
) else (
    echo    No se pudo crear acceso directo - verificar permisos
)

echo.
echo [5/6] Creando acceso directo en menú inicio...
set STARTMENU=%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs
set STARTMENU_SHORTCUT=%STARTMENU%\\COPY-INV Sistema de Inventario.lnk

powershell -Command "^
$WshShell = New-Object -comObject WScript.Shell; ^
$Shortcut = $WshShell.CreateShortcut('%STARTMENU_SHORTCUT%'); ^
$Shortcut.TargetPath = '%TARGET%'; ^
$Shortcut.WorkingDirectory = '%~dp0'; ^
$Shortcut.IconLocation = '%ICON_PATH%'; ^
$Shortcut.Description = 'Sistema de Inventario Copy Point S.A. - COPY-INV v{VERSION}'; ^
$Shortcut.WindowStyle = 1; ^
$Shortcut.Save()"

if exist "%STARTMENU_SHORTCUT%" (
    echo    Acceso directo creado en menú inicio
) else (
    echo    No se pudo crear acceso directo en menú inicio
)

echo.
echo [6/6] Configurando base de datos...
if not exist "data\\inventario.db" (
    echo Inicializando base de datos por primera vez...
    REM La base de datos se inicializará automáticamente en primer uso
)

echo.
echo ============================================
echo  INSTALACION COMPLETADA
echo ============================================
echo.
echo  Accesos directos creados:
echo    • Escritorio: COPY-INV Sistema de Inventario.lnk
echo    • Menú Inicio: COPY-INV Sistema de Inventario.lnk
echo.
echo  Para ejecutar la aplicación:
echo    • Doble clic en el acceso directo del escritorio
echo    • Buscar "COPY-INV" en el menú inicio
echo    • Ejecutar directamente: app\\{APP_NAME}.exe
echo.
echo 👤 Datos de usuario de prueba:
echo    Usuario: admin
echo    Password: admin123
echo.
echo  IMPORTANTE: Cambiar credenciales por defecto
echo              después del primer acceso
echo.
echo  Soporte técnico: soporte.inventario@copypoint.com
echo.
pause
'''
        
        install_path = self.package_dir / "instalar.bat"
        with open(install_path, 'w', encoding='utf-8') as f:
            f.write(install_script)
        
        # Script de desinstalación mejorado
        uninstall_script = f'''@echo off
REM Script de Desinstalación {APP_NAME} v{VERSION}

echo ============================================
echo  DESINSTALACION {APP_NAME}
echo ============================================

echo.
echo Esta acción eliminará:
echo  • Accesos directos del escritorio y menú inicio
echo  • Procesos relacionados con la aplicación
echo  • Creará respaldo de la base de datos
echo.
echo Los datos de la aplicación se mantendrán en esta carpeta
echo para que puedas hacer respaldo manual si es necesario.
echo.

set /p CONFIRM="¿Estás seguro de que deseas continuar? (S/N): "
if /i "%CONFIRM%" neq "S" (
    echo Desinstalación cancelada
    pause
    exit /b 0
)

echo.
echo [1/4] Cerrando procesos relacionados...
taskkill /f /im "{APP_NAME}.exe" 2>nul
if errorlevel 1 (
    echo    No hay procesos ejecutándose
) else (
    echo    Procesos cerrados
)

echo.
echo [2/4] Eliminando accesos directos...
set DESKTOP_SHORTCUT=%USERPROFILE%\\Desktop\\COPY-INV Sistema de Inventario.lnk
set STARTMENU_SHORTCUT=%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\COPY-INV Sistema de Inventario.lnk

if exist "%DESKTOP_SHORTCUT%" (
    del "%DESKTOP_SHORTCUT%"
    echo    Acceso directo del escritorio eliminado
) else (
    echo    No se encontró acceso directo en el escritorio
)

if exist "%STARTMENU_SHORTCUT%" (
    del "%STARTMENU_SHORTCUT%"
    echo    Acceso directo del menú inicio eliminado
) else (
    echo    No se encontró acceso directo en menú inicio
)

echo.
echo [3/4] Creando respaldo de datos...
set BACKUP_DIR=%USERPROFILE%\\Documents\\COPY-INV_Backup_%DATE:~6,4%%DATE:~3,2%%DATE:~0,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%
set BACKUP_DIR=%BACKUP_DIR: =0%

if exist "data\\inventario.db" (
    mkdir "%BACKUP_DIR%" 2>nul
    copy "data\\inventario.db" "%BACKUP_DIR%\\inventario_backup.db" >nul
    copy "config\\*.py" "%BACKUP_DIR%\\" 2>nul
    echo    Respaldo creado en: %BACKUP_DIR%
) else (
    echo    No se encontró base de datos para respaldar
)

echo.
echo [4/4] Limpiando archivos temporales...
if exist "temp\\*" (
    del /q "temp\\*" 2>nul
    echo    Archivos temporales eliminados
)
if exist "logs\\*.log" (
    echo    Archivos de log mantenidos para troubleshooting
)

echo.
echo ============================================
echo  DESINSTALACION COMPLETADA
echo ============================================
echo.
echo  Accesos directos eliminados
echo  Procesos cerrados
echo  Datos respaldados en: %BACKUP_DIR%
echo.
echo  Los archivos de la aplicación permanecen en esta carpeta
echo   Puedes eliminar manualmente toda la carpeta si lo deseas
echo.
echo  Para reinstalar: ejecutar nuevamente instalar.bat
echo.
pause
'''
        
        uninstall_path = self.package_dir / "desinstalar.bat"
        with open(uninstall_path, 'w', encoding='utf-8') as f:
            f.write(uninstall_script)
            
    def _create_documentation(self):
        """Crear documentación completa para el usuario."""
        print("Creando documentación...")
        
        readme_content = f'''# {APP_NAME} v{VERSION} - Portable Edition

##  Instalación Rápida

1. **Extraer** este archivo ZIP en la ubicación deseada (ej: C:\\COPY-INV\\)
2. **Ejecutar** `instalar.bat` (preferiblemente como administrador)
3. **Usar** el acceso directo creado en el escritorio

## 👤 Primer Uso

### Credenciales por Defecto
- **Usuario:** admin
- **Password:** admin123

**IMPORTANTE:** Cambiar estas credenciales inmediatamente después del primer acceso.

### Pasos Iniciales Recomendados
1. **Cambiar password** del administrador (Administración > Usuarios)
2. **Configurar datos** de la empresa (Configuración > Empresa)
3. **Crear categorías** de productos (Inventario > Categorías)
4. **Configurar impuestos** según normativa local (Configuración > Impuestos)
5. **Crear usuarios vendedor** con permisos específicos (Administración > Usuarios)

## Estructura de Archivos

```
{PACKAGE_NAME}/
├── app/                    # Aplicación principal
│   └── {APP_NAME}.exe     # Ejecutable principal
├── assets/                 # Logos e iconos
│   ├── logo_medium.png    # Logo 320x320
│   ├── logo_high.png      # Logo 2000x2000
│   ├── logo_transparent.png # Logo con transparencia
│   ├── app_icon.ico       # Icono de aplicación
│   └── shortcut_icon.ico  # Icono para accesos directos
├── data/                   # Base de datos
│   └── inventario.db      # Base de datos SQLite
├── config/                 # Configuraciones
├── logs/                   # Archivos de log del sistema
├── backups/               # Respaldos automáticos
├── updates/               # Sistema de actualizaciones
├── docs/                  # Documentación adicional
├── temp/                  # Archivos temporales
├── instalar.bat          # Script de instalación
├── desinstalar.bat       # Script de desinstalación
├── updater.py            # Sistema de actualizaciones
└── README.txt            # Este archivo
```

## ✨ Características Principales

### Sistema Completo de Inventario
- **Gestión de productos y servicios** con categorización inteligente
- **Control de stock** en tiempo real con alertas automáticas
- **Movimientos de inventario** con trazabilidad completa
- **Códigos de barras** integrados para identificación rápida
- **Inventario físico** con herramientas de conteo y ajustes

### Sistema de Ventas Integrado
- **Punto de venta** intuitivo para procesamiento rápido
- **Facturación automática** con cálculo de impuestos
- **Gestión de clientes** con historial de compras
- **Múltiples métodos de pago** (efectivo, tarjeta, crédito)
- **Devoluciones** con proceso simplificado

### Reportes Empresariales
- **Reportes de ventas** por período, producto y vendedor
- **Control de inventario** con stock actual y valorización
- **Análisis financiero** de rentabilidad y tendencias
- **Exportación** a PDF, Excel y CSV
- **Dashboard** con métricas en tiempo real

### Administración y Seguridad
- **Usuarios y roles** con permisos granulares (Admin/Vendedor)
- **Autenticación segura** con encriptación de passwords
- **Auditoría completa** de todas las transacciones
- **Respaldos automáticos** diarios
- **Configuración empresarial** flexible

### Ventajas de la Versión Portable
- **Sin dependencias:** No requiere Python ni librerías adicionales
- **Plug-and-play:** Funciona inmediatamente después de extraer
- **Compatible:** Windows 10/11 sin instalaciones previas
- **Actualizaciones:** Sistema automático integrado
- **Respaldos:** Incluidos y configurados automáticamente

## Flujo de Trabajo Básico

### 1. Configuración Inicial
```
Primer inicio → Cambiar credenciales → Configurar empresa
→ Crear categorías → Configurar impuestos → Crear usuarios
```

### 2. Gestión de Productos
```
Inventario > Productos > Nuevo Producto
→ Completar información → Asignar categoría
→ Establecer precios → Definir stock mínimo/máximo
```

### 3. Movimientos de Inventario
```
Inventario > Movimientos > Nueva Entrada
→ Seleccionar productos → Ingresar cantidad
→ Confirmar movimiento → Verificar stock actualizado
```

### 4. Procesamiento de Ventas
```
Ventas > Nueva Venta → Agregar productos
→ Seleccionar cliente → Procesar pago
→ Imprimir factura → Verificar stock actualizado
```

### 5. Generación de Reportes
```
Reportes > [Tipo de Reporte] → Seleccionar período
→ Configurar filtros → Generar reporte
→ Exportar en formato deseado
```

## Configuración Avanzada

### Personalización de la Empresa
- **Datos fiscales:** RUC, nombre, dirección, teléfono
- **Logo empresarial:** Subir logo personalizado para facturas
- **Configuración monetaria:** Símbolo de moneda, decimales
- **Numeración:** Secuencias personalizadas para facturas

### Configuración de Impuestos
- **ITBMS:** Configurar tasa según normativa panameña
- **Exenciones:** Productos exentos de impuestos
- **Múltiples tasas:** Diferentes tasas según categoría

### Usuarios y Permisos
- **Administrador:** Acceso completo al sistema
- **Vendedor:** Ventas, consultas de inventario, reportes básicos
- **Personalizado:** Crear roles con permisos específicos

## Sistema de Actualizaciones

### Automáticas
- **Verificación:** Al iniciar la aplicación
- **Descarga:** Automática en segundo plano
- **Instalación:** Con confirmación del usuario
- **Respaldo:** Automático antes de actualizar
- **Rollback:** Posible en caso de problemas

### Manuales
- **Ejecutar:** `updater.py` desde la carpeta principal
- **Verificar:** Menu Ayuda > Buscar Actualizaciones
- **Configurar:** Servidor de actualizaciones personalizado

## Sistema de Respaldos

### Automáticos
- **Frecuencia:** Diario a las 2:00 AM
- **Ubicación:** Carpeta `backups/` con timestamp
- **Retención:** 30 días automático
- **Formato:** Base de datos comprimida + configuraciones

### Manuales
```bash
# Crear respaldo inmediato
1. Copiar archivo: data/inventario.db
2. Guardar en ubicación segura externa
3. Incluir carpeta config/ si hay personalizaciones
```

### Restauración
```bash
# Restaurar desde respaldo
1. Cerrar aplicación completamente
2. Reemplazar data/inventario.db con respaldo
3. Reiniciar aplicación
4. Verificar integridad de datos
```

## Troubleshooting Común

### Problema: La aplicación no inicia
**Posibles causas y soluciones:**
- **Windows no compatible:** Verificar Windows 10/11 de 64 bits
- **Antivirus bloquea:** Agregar excepción para toda la carpeta
- **Permisos insuficientes:** Ejecutar como administrador
- **Archivos corruptos:** Extraer nuevamente el ZIP original

### Problema: Error de base de datos
**Soluciones paso a paso:**
1. **Verificar integridad:** Logs en carpeta `logs/`
2. **Restaurar respaldo:** Usar respaldo más reciente de `backups/`
3. **Inicializar nueva:** Eliminar `data/inventario.db` (se crea nueva)
4. **Contactar soporte:** Si el problema persiste

### Problema: Acceso directo no funciona
**Soluciones:**
1. **Recrear acceso directo:** Ejecutar nuevamente `instalar.bat`
2. **Permisos de escritorio:** Verificar permisos de escritura
3. **Ejecutar directamente:** Usar `app/{APP_NAME}.exe`
4. **Icono faltante:** Verificar que existe `assets/shortcut_icon.ico`

### Problema: Actualizaciones fallan
**Soluciones:**
1. **Conexión a internet:** Verificar conectividad
2. **Firewall/Antivirus:** Temporalmente desactivar
3. **Permisos de escritura:** Ejecutar como administrador
4. **Actualización manual:** Descargar nueva versión completa

### Problema: Lentitud en la aplicación
**Optimizaciones:**
1. **Antivirus:** Excluir carpeta de escaneo en tiempo real
2. **Disco duro:** Verificar espacio libre (mínimo 1GB)
3. **Memoria RAM:** Cerrar aplicaciones innecesarias
4. **Base de datos:** Revisar tamaño en `data/inventario.db`

## Soporte Técnico

### Contactos
- **Email:** soporte.inventario@copypoint.com
- **Teléfono:** +507 XXX-XXXX
- **Horario:** Lunes a Viernes, 8:00 AM - 5:00 PM

### Información para Soporte
Cuando contactes soporte, incluye:
- **Versión:** {VERSION}
- **Sistema operativo:** Windows 10/11
- **Descripción del problema:** Detallada
- **Archivos de log:** Ubicados en `logs/`
- **Pasos para reproducir:** Si aplica

### Recursos Adicionales
- **Manual completo:** `docs/manual_usuario.pdf` (si disponible)
- **Videos tutoriales:** Enlaces en la aplicación
- **FAQ:** Preguntas frecuentes en Help > FAQ
- **Comunidad:** Foro de usuarios (si disponible)

## Información Legal

**Copyright (c) 2025 Copy Point S.A.**  
Todos los derechos reservados.

Este software es propiedad de Copy Point S.A. y está protegido por 
leyes de derechos de autor. Su uso está restringido al personal 
autorizado de la empresa.

**Términos de Uso:**
- Uso autorizado únicamente para personal de Copy Point S.A.
- Prohibida la distribución no autorizada
- Prohibida la ingeniería inversa
- Prohibido el uso comercial por terceros

**Privacidad:**
- Los datos se almacenan localmente en su equipo
- No se envía información a servidores externos
- Sistema de actualizaciones requiere conexión a internet
- Logs del sistema no contienen información personal

## Historial de Versiones

### v{VERSION} (Actual)
- Sistema completo de inventario implementado
- Gestión de ventas y facturación
- Reportes empresariales avanzados
- Sistema de usuarios y permisos
- Respaldos automáticos configurados
- Sistema de actualizaciones integrado
- Versión portable optimizada

### Próximas Versiones
- Integración con lectores de código de barras
- Reportes adicionales y dashboard mejorado
- API REST para integraciones
- Aplicación móvil complementaria
- Sincronización multi-sucursal

---

**{APP_NAME} v{VERSION} - Portable Edition**  
*Sistema de Inventario Copy Point S.A.*  
*Generado automáticamente el {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*

Para soporte técnico: soporte.inventario@copypoint.com
'''
        
        readme_path = self.package_dir / "README.txt"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
            
    def _create_version_file(self):
        """Crear archivo de información de versión."""
        print("Creando archivo de versión...")
        
        version_info = {
            "app_info": {
                "name": APP_NAME,
                "version": VERSION,
                "description": "Sistema de Inventario Copy Point S.A.",
                "company": "Copy Point S.A.",
                "build_date": datetime.now().isoformat(),
                "build_type": "Portable Edition"
            },
            "system_requirements": {
                "os": "Windows 10/11 (64-bit)",
                "architecture": "x64",
                "memory": "4GB RAM",
                "disk": "2GB free space",
                "additional": "No dependencies required"
            },
            "features": [
                "Complete inventory management system",
                "Sales and invoicing with tax calculation",
                "Enterprise reporting and analytics",
                "User management and role-based security",
                "Automatic backup system",
                "Integrated update system",
                "Portable deployment - no installation required",
                "Custom logo and branding support",
                "Desktop shortcuts with custom icons"
            ],
            "assets": {
                "logo_files": [
                    "assets/logo_medium.png",
                    "assets/logo_high.png", 
                    "assets/logo_transparent.png"
                ],
                "icon_files": [
                    "assets/app_icon.ico",
                    "assets/shortcut_icon.ico"
                ]
            },
            "installation": {
                "method": "Extract ZIP and run instalar.bat",
                "shortcuts_created": [
                    "Desktop: COPY-INV Sistema de Inventario.lnk",
                    "Start Menu: COPY-INV Sistema de Inventario.lnk"
                ],
                "default_credentials": {
                    "username": "admin",
                    "password": "admin123",
                    "warning": "Change immediately after first login"
                }
            },
            "support": {
                "email": "soporte.inventario@copypoint.com",
                "documentation": "README.txt",
                "logs_location": "logs/",
                "backup_location": "backups/"
            }
        }
        
        version_path = self.package_dir / "version.json"
        with open(version_path, 'w', encoding='utf-8') as f:
            json.dump(version_info, f, indent=2, ensure_ascii=False)
            
    def _create_zip_package(self):
        """Crear paquete ZIP para distribución."""
        print("Creando paquete ZIP para distribución...")
        
        zip_path = self.dist_dir / f"{PACKAGE_NAME}_v{VERSION}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
            for file_path in self.package_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(self.package_dir.parent)
                    zipf.write(file_path, arcname)
        
        # Información del paquete
        size_mb = zip_path.stat().st_size / (1024 * 1024)
        print(f"Paquete ZIP creado: {zip_path.name} ({size_mb:.1f} MB)")
        
        return zip_path

def main():
    """Función principal."""
    try:
        creator = PortablePackageCreator()
        creator.create_package()
        
        print("\\nPROCESO COMPLETADO EXITOSAMENTE")
        print(f"\\nArchivos generados:")
        print(f"   • Paquete portable: dist/{PACKAGE_NAME}/")
        print(f"   • Archivo ZIP: dist/{PACKAGE_NAME}_v{VERSION}.zip")
        print(f"\\nListo para distribución en pendrive")
        print(f"\\nPara instalar:")
        print(f"   1. Extraer ZIP en ubicación deseada")
        print(f"   2. Ejecutar instalar.bat como administrador")
        print(f"   3. Usar acceso directo del escritorio")
        
    except Exception as e:
        print(f"\\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
