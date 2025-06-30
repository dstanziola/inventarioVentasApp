#!/usr/bin/env python3
"""
Script de Verificación Rápida del Sistema de Inventario

Ejecuta verificaciones básicas para determinar si el sistema está listo para usar.

Fecha: 30/06/2025
Uso: python quick_check.py
"""

import os
import sys
import sqlite3
from pathlib import Path

def print_status(message, status):
    """Imprimir estado con formato."""
    symbol = "✅" if status else "❌"
    print(f"{symbol} {message}")
    return status

def check_structure():
    """Verificar estructura básica del proyecto."""
    print("\n=== ESTRUCTURA DEL PROYECTO ===")
    
    project_root = Path(__file__).parent
    
    # Directorios críticos
    critical_dirs = ['src', 'src/db', 'src/models', 'src/services', 'src/ui']
    all_dirs_exist = True
    
    for dir_path in critical_dirs:
        full_path = project_root / dir_path
        exists = full_path.exists()
        print_status(f"Directorio {dir_path}", exists)
        all_dirs_exist = all_dirs_exist and exists
    
    # Archivos críticos
    critical_files = ['main.py', 'config.py', 'styles.py']
    all_files_exist = True
    
    for file_path in critical_files:
        full_path = project_root / file_path
        exists = full_path.exists() and full_path.stat().st_size > 0
        size = full_path.stat().st_size if full_path.exists() else 0
        print_status(f"Archivo {file_path} ({size} bytes)", exists and size > 0)
        all_files_exist = all_files_exist and exists and size > 0
    
    return all_dirs_exist and all_files_exist

def check_database():
    """Verificar estado de la base de datos."""
    print("\n=== BASE DE DATOS ===")
    
    db_path = Path(__file__).parent / 'inventario.db'
    
    if not db_path.exists():
        print_status("Base de datos existe", False)
        return False
    
    print_status(f"Base de datos existe ({db_path.stat().st_size} bytes)", True)
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Verificar tablas principales
        expected_tables = ['usuarios', 'categorias', 'productos', 'ventas']
        all_tables_exist = True
        
        for table in expected_tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            exists = cursor.fetchone() is not None
            if exists:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print_status(f"Tabla {table} ({count} registros)", True)
            else:
                print_status(f"Tabla {table}", False)
                all_tables_exist = False
        
        conn.close()
        return all_tables_exist
        
    except Exception as e:
        print_status(f"Error conectando a BD: {e}", False)
        return False

def check_imports():
    """Verificar imports críticos."""
    print("\n=== IMPORTS DEL SISTEMA ===")
    
    # Agregar src al path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root / 'src'))
    
    critical_imports = [
        'db.database',
        'models',
        'services',
        'ui.main.main_window'
    ]
    
    all_imports_ok = True
    
    for module_name in critical_imports:
        try:
            __import__(module_name)
            print_status(f"Import {module_name}", True)
        except Exception as e:
            print_status(f"Import {module_name}: {e}", False)
            all_imports_ok = False
    
    return all_imports_ok

def check_dependencies():
    """Verificar dependencias básicas."""
    print("\n=== DEPENDENCIAS ===")
    
    basic_deps = ['tkinter', 'sqlite3']
    optional_deps = ['reportlab', 'qrcode', 'PIL']
    
    basic_ok = True
    for dep in basic_deps:
        try:
            __import__(dep)
            print_status(f"Dependencia básica {dep}", True)
        except ImportError:
            print_status(f"Dependencia básica {dep}", False)
            basic_ok = False
    
    optional_ok = True
    for dep in optional_deps:
        try:
            if dep == 'PIL':
                import PIL
            else:
                __import__(dep)
            print_status(f"Dependencia opcional {dep}", True)
        except ImportError:
            print_status(f"Dependencia opcional {dep}", False)
            optional_ok = False
    
    return basic_ok, optional_ok

def main():
    """Función principal de verificación."""
    print("🔍 VERIFICACIÓN RÁPIDA DEL SISTEMA DE INVENTARIO")
    print("=" * 60)
    
    # Ejecutar verificaciones
    structure_ok = check_structure()
    database_ok = check_database()
    imports_ok = check_imports()
    basic_deps_ok, optional_deps_ok = check_dependencies()
    
    # Resumen final
    print("\n=== RESUMEN ===")
    
    critical_checks = [
        ("Estructura del proyecto", structure_ok),
        ("Base de datos", database_ok),
        ("Imports del sistema", imports_ok),
        ("Dependencias básicas", basic_deps_ok)
    ]
    
    optional_checks = [
        ("Dependencias opcionales", optional_deps_ok)
    ]
    
    critical_passed = sum(1 for _, status in critical_checks if status)
    total_critical = len(critical_checks)
    
    print(f"\nVerificaciones críticas: {critical_passed}/{total_critical}")
    for name, status in critical_checks:
        print_status(name, status)
    
    print(f"\nVerificaciones opcionales:")
    for name, status in optional_checks:
        print_status(name, status)
    
    # Determinar estado general
    if critical_passed == total_critical:
        print("\n🎉 ¡SISTEMA LISTO PARA USAR!")
        print("✅ Todas las verificaciones críticas pasaron")
        print("✅ Puede ejecutar: python main.py")
        
        if not optional_deps_ok:
            print("⚠️  Algunas dependencias opcionales faltan (reportes y códigos de barras)")
            print("💡 Instalar con: pip install reportlab qrcode[pil]")
        
        return True
    else:
        print("\n❌ SISTEMA NO ESTÁ LISTO")
        failed_checks = [name for name, status in critical_checks if not status]
        print(f"❌ Verificaciones fallidas: {', '.join(failed_checks)}")
        print("💡 Ejecutar: python initialize_system.py")
        return False

if __name__ == "__main__":
    main()
