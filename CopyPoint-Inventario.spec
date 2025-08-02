# -*- mode: python ; coding: utf-8 -*-
"""
Archivo .spec generado automáticamente para CopyPoint-Inventario
No editar manualmente - usar pyinstaller_config.py
"""

import os
from pathlib import Path

block_cipher = None
project_root = Path(r"D:\inventario_app2")

a = Analysis(
    ['D:\inventario_app2\main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=[('D:\\inventario_app2\\config', 'config'), ('D:\\inventario_app2\\data', 'data'), ('D:\\inventario_app2\\docs', 'docs'), ('D:\\inventario_app2\\styles.py', '.'), ('D:\\inventario_app2\\logo 320x320.png', 'assets'), ('D:\\inventario_app2\\logo 2000x2000.png', 'assets'), ('D:\\inventario_app2\\logo 940x788 transp.png', 'assets')],
    hiddenimports=['PyQt6', 'PyQt6.QtCore', 'PyQt6.QtWidgets', 'PyQt6.QtGui', 'PyQt6.QtSql', 'sqlite3', 'reportlab', 'openpyxl', 'pandas', 'bcrypt', 'configparser', 'logging', 'json', 'datetime', 'decimal', 'pathlib', 'Pillow', 'PIL', 'PIL.Image', 'PIL.ImageTk', 'barcode', 'qrcode', 'tkcalendar'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'notebook', 'IPython', 'jupyter', 'test', 'tests', 'unittest', 'doctest', 'pydoc', 'xml', 'urllib3', 'requests', 'email', 'html', 'http', 'setuptools', 'distutils'],
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
    name='CopyPoint-Inventario',
    debug=false,
    bootloader_ignore_signals=False,
    strip=False,
    upx=true,
    upx_exclude=['vcruntime140.dll', 'msvcp140.dll'],
    runtime_tmpdir=None,
    console=false,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='D:\inventario_app2\copypoint_logo.ico',
    version='version_info.txt',
)
