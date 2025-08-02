# -*- mode: python ; coding: utf-8 -*-
"""
Configuración PyInstaller para COPY-INV Sistema de Inventario con Logo
Archivo: build_config/pyinstaller_config.py
Fecha: 2025-08-02
Versión: 1.0.0
"""

import os
import sys
from pathlib import Path
from PIL import Image

# Configuración base del proyecto
PROJECT_ROOT = Path(__file__).parent.parent
APP_NAME = "CopyPoint-Inventario"
VERSION = "1.0.4"

# Configuración de logos
LOGO_320 = PROJECT_ROOT / "logo 320x320.png"
LOGO_2000 = PROJECT_ROOT / "logo 2000x2000.png"
LOGO_TRANSP = PROJECT_ROOT / "logo 940x788 transp.png"
ICON_PATH = PROJECT_ROOT / "copypoint_logo.ico"

class LogoConverter:
    """Conversor de logos PNG a ICO para PyInstaller."""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        
    def create_ico_from_png(self):
        """Crear archivo .ico desde PNG para PyInstaller."""
        print("Convirtiendo logo a formato ICO...")
        
        # Verificar que PIL está disponible
        try:
            from PIL import Image
        except ImportError:
            print("Instalando Pillow para conversión de imágenes...")
            import subprocess
            subprocess.run([sys.executable, "-m", "pip", "install", "Pillow"], check=True)
            from PIL import Image
        
        # Usar logo de 320x320 como base para ICO
        if LOGO_320.exists():
            source_logo = LOGO_320
            print(f"Usando logo fuente: {source_logo.name}")
        elif LOGO_TRANSP.exists():
            source_logo = LOGO_TRANSP
            print(f"Usando logo transparente: {source_logo.name}")
        elif LOGO_2000.exists():
            source_logo = LOGO_2000
            print(f"Usando logo alta resolución: {source_logo.name}")
        else:
            print("No se encontró ningún archivo de logo")
            return None
            
        try:
            # Abrir imagen PNG
            img = Image.open(source_logo)
            
            # Convertir a RGBA si no lo está
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Crear múltiples tamaños para ICO (16, 32, 48, 64, 128, 256)
            sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
            icons = []
            
            for size in sizes:
                # Redimensionar manteniendo aspect ratio
                icon = img.copy()
                icon.thumbnail(size, Image.Resampling.LANCZOS)
                
                # Crear imagen nueva con fondo transparente del tamaño exacto
                new_icon = Image.new('RGBA', size, (0, 0, 0, 0))
                
                # Centrar la imagen redimensionada
                x = (size[0] - icon.size[0]) // 2
                y = (size[1] - icon.size[1]) // 2
                new_icon.paste(icon, (x, y), icon)
                
                icons.append(new_icon)
            
            # Guardar como ICO
            icons[0].save(
                ICON_PATH,
                format='ICO',
                sizes=[icon.size for icon in icons],
                append_images=icons[1:]
            )
            
            print(f"Archivo ICO creado: {ICON_PATH.name}")
            return ICON_PATH
            
        except Exception as e:
            print(f"Error creando ICO: {e}")
            return None

# Configuración PyInstaller
PYINSTALLER_CONFIG = {
    # Archivos principales
    'main_script': str(PROJECT_ROOT / "main.py"),
    'icon': str(ICON_PATH) if ICON_PATH.exists() else None,
    
    # Opciones de compilación
    'onefile': True,           # Un solo ejecutable
    'windowed': True,          # Sin ventana de consola
    'console': False,          # No mostrar consola
    'debug': False,            # Sin debug info
    
    # Directorios de datos a incluir
    'datas': [
        (str(PROJECT_ROOT / "config"), "config"),
        (str(PROJECT_ROOT / "data"), "data") if (PROJECT_ROOT / "data").exists() else None,
        (str(PROJECT_ROOT / "docs"), "docs") if (PROJECT_ROOT / "docs").exists() else None,
        (str(PROJECT_ROOT / "styles.py"), ".") if (PROJECT_ROOT / "styles.py").exists() else None,
        (str(LOGO_320), "assets") if LOGO_320.exists() else None,
        (str(LOGO_2000), "assets") if LOGO_2000.exists() else None,
        (str(LOGO_TRANSP), "assets") if LOGO_TRANSP.exists() else None,
        (str(ICON_PATH), "assets") if ICON_PATH.exists() else None,
    ],
    
    # Módulos hidden imports (PyQt6, SQLite, etc.)
    'hiddenimports': [
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtWidgets',
        'PyQt6.QtGui',
        'PyQt6.QtSql',
        'sqlite3',
        'reportlab',
        'openpyxl',
        'pandas',
        'bcrypt',
        'configparser',
        'logging',
        'json',
        'datetime',
        'decimal',
        'pathlib',
        'Pillow',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'barcode',
        'qrcode',
        'tkcalendar',
    ],
    
    # Módulos a excluir (reducir tamaño)
    'excludes': [
        'tkinter',           # No usar Tkinter si ya tienes PyQt6
        'matplotlib',        # Excluir si no se usa para gráficos
        'notebook',
        'IPython',
        'jupyter',
        'test',
        'tests',
        'unittest',
        'doctest',
        'pydoc',
        'xml',
        'urllib3',
        'requests',
        'email',
        'html',
        'http',
        'setuptools',
        'distutils',
    ],
    
    # Configuración adicional
    'name': APP_NAME,
    'distpath': str(PROJECT_ROOT / "dist"),
    'workpath': str(PROJECT_ROOT / "build"),
    'specpath': str(PROJECT_ROOT),
    
    # UPX compression (opcional, reduce tamaño)
    'upx': True,
    'upx_exclude': ['vcruntime140.dll', 'msvcp140.dll'],
    
    # Información de versión Windows
    'version_info': {
        'version': VERSION,
        'description': 'Sistema de Inventario Copy Point S.A.',
        'company': 'Copy Point S.A.',
        'product': 'COPY-INV',
        'copyright': f'Copyright (c) 2025 Copy Point S.A.',
        'internal_name': APP_NAME,
        'original_filename': f'{APP_NAME}.exe',
    }
}

def create_spec_file():
    """Crear archivo .spec personalizado para PyInstaller."""
    
    # Filtrar datas que existen
    existing_datas = []
    for data_entry in PYINSTALLER_CONFIG["datas"]:
        if data_entry is not None:
            source_path = Path(data_entry[0])
            if source_path.exists():
                existing_datas.append(data_entry)
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
"""
Archivo .spec generado automáticamente para {APP_NAME}
No editar manualmente - usar pyinstaller_config.py
"""

import os
from pathlib import Path

block_cipher = None
project_root = Path(r"{PROJECT_ROOT}")

a = Analysis(
    ['{PYINSTALLER_CONFIG["main_script"]}'],
    pathex=[str(project_root)],
    binaries=[],
    datas={existing_datas},
    hiddenimports={PYINSTALLER_CONFIG["hiddenimports"]},
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes={PYINSTALLER_CONFIG["excludes"]},
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{APP_NAME}',
    debug={str(PYINSTALLER_CONFIG["debug"]).lower()},
    bootloader_ignore_signals=False,
    strip=False,
    upx={str(PYINSTALLER_CONFIG["upx"]).lower()},
    upx_exclude={PYINSTALLER_CONFIG["upx_exclude"]},
    runtime_tmpdir=None,
    console={str(PYINSTALLER_CONFIG["console"]).lower()},
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{PYINSTALLER_CONFIG["icon"] or ""}',
    version='version_info.txt',
)
'''
    
    spec_file_path = PROJECT_ROOT / f"{APP_NAME}.spec"
    with open(spec_file_path, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print(f"Archivo .spec creado: {spec_file_path.name}")
    return spec_file_path

def create_version_info():
    """Crear archivo de información de versión para Windows."""
    
    version_info_content = f'''# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({VERSION.replace('.', ',')},0),
    prodvers=({VERSION.replace('.', ',')},0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Copy Point S.A.'),
        StringStruct(u'FileDescription', u'Sistema de Inventario Copy Point S.A.'),
        StringStruct(u'FileVersion', u'{VERSION}'),
        StringStruct(u'InternalName', u'{APP_NAME}'),
        StringStruct(u'LegalCopyright', u'Copyright (c) 2025 Copy Point S.A. Todos los derechos reservados.'),
        StringStruct(u'OriginalFilename', u'{APP_NAME}.exe'),
        StringStruct(u'ProductName', u'COPY-INV Sistema de Inventario'),
        StringStruct(u'ProductVersion', u'{VERSION}')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
    
    version_file_path = PROJECT_ROOT / "version_info.txt"
    with open(version_file_path, 'w', encoding='utf-8') as f:
        f.write(version_info_content)
    
    print(f"Archivo version_info.txt creado: {version_file_path.name}")
    return version_file_path

def create_build_script():
    """Crear script de construcción automatizado."""
    
    build_script_content = f'''@echo off
REM Script de construcción automatizado para {APP_NAME}
REM Fecha: 2025-08-02

echo ============================================
echo  CONSTRUCCION {APP_NAME} v{VERSION}
echo ============================================

echo.
echo [1/6] Activando entorno virtual...
if exist "venv\\Scripts\\activate.bat" (
    call venv\\Scripts\\activate.bat
) else (
    echo ERROR: Entorno virtual no encontrado en venv\\Scripts\\
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
python build_config\\pyinstaller_config.py
if errorlevel 1 (
    echo ERROR: No se pudieron generar archivos de configuración
    pause
    exit /b 1
)

echo.
echo [5/6] Construyendo ejecutable...
pyinstaller {APP_NAME}.spec --clean --noconfirm
if errorlevel 1 (
    echo ERROR: Fallo en la construcción del ejecutable
    pause
    exit /b 1
)

echo.
echo [6/6] Creando paquete de distribución...
python build_config\\create_portable_package.py
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
echo Ejecutable creado en: dist\\{APP_NAME}.exe
echo Paquete portable en: dist\\{APP_NAME}-Portable\\
echo.
pause
'''
    
    build_script_path = PROJECT_ROOT / "build_portable.bat"
    with open(build_script_path, 'w', encoding='utf-8') as f:
        f.write(build_script_content)
    
    print(f"Script de construcción creado: {build_script_path.name}")
    return build_script_path

if __name__ == "__main__":
    print(f"Configurando construcción para {APP_NAME} v{VERSION}")
    print(f"Directorio del proyecto: {PROJECT_ROOT}")
    
    # Crear convertidor de logos
    logo_converter = LogoConverter()
    
    # Convertir logo a ICO
    ico_created = logo_converter.create_ico_from_png()
    if ico_created:
        PYINSTALLER_CONFIG['icon'] = str(ico_created)
    
    # Generar archivos de configuración
    spec_file = create_spec_file()
    version_file = create_version_info()
    build_script = create_build_script()
    
    print("\nConfiguración completada. Archivos generados:")
    print(f"   - {spec_file.name}")
    print(f"   - {version_file.name}")
    print(f"   - {build_script.name}")
    if ico_created:
        print(f"   - {ico_created.name}")
    print("\nPara construir el ejecutable, ejecuta: build_portable.bat")
