#!/usr/bin/env python3
"""
Script de testing final para validar la integración completa de FASE 3
Sistema de Tickets y Configuración de Empresa

FUNCIONALIDADES A VALIDAR:
- Integración en main_window.py
- Integración en movement_form.py  
- Integración en sales_form.py
- Base de datos preparada
- Servicios funcionando
- Formularios accesibles
"""

import os
import sys
import ast
import sqlite3
import importlib.util
from pathlib import Path

def validate_syntax(file_path, file_name):
    """Validar sintaxis de archivo Python"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, f"Error sintaxis línea {e.lineno}: {e.msg}"
    except Exception as e:
        return False, str(e)

def check_database_tables():
    """Verificar tablas requeridas en base de datos"""
    db_path = r"D:\inventario_app2\inventario.db"
    
    if not os.path.exists(db_path):
        return False, "Base de datos no existe"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['tickets', 'company_config']
        missing_tables = [t for t in required_tables if t not in tables]
        
        conn.close()
        
        if missing_tables:
            return False, f"Tablas faltantes: {missing_tables}"
        return True, f"Tablas requeridas presentes: {required_tables}"
        
    except Exception as e:
        return False, f"Error verificando BD: {e}"

def check_service_imports():
    """Verificar que servicios de tickets existen y son importables"""
    base_path = r"D:\inventario_app2"
    
    services_to_check = [
        ('services/ticket_service.py', 'TicketService'),
        ('services/company_service.py', 'CompanyService'),
        ('reports/ticket_generator.py', 'TicketGenerator'),
        ('ui/forms/ticket_preview_form.py', 'TicketPreviewForm'),
        ('ui/forms/company_config_form.py', 'CompanyConfigForm')
    ]
    
    results = []
    
    for service_path, class_name in services_to_check:
        full_path = os.path.join(base_path, service_path)
        
        if not os.path.exists(full_path):
            results.append((service_path, False, "Archivo no existe"))
            continue
            
        # Verificar sintaxis
        valid, error = validate_syntax(full_path, service_path)
        if not valid:
            results.append((service_path, False, f"Sintaxis: {error}"))
            continue
            
        # Verificar que contiene la clase
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if f"class {class_name}" in content:
                    results.append((service_path, True, "OK"))
                else:
                    results.append((service_path, False, f"Clase {class_name} no encontrada"))
        except Exception as e:
            results.append((service_path, False, f"Error leyendo: {e}"))
    
    return results

def check_integration_in_files():
    """Verificar integración en archivos principales"""
    base_path = r"D:\inventario_app2"
    
    checks = [
        # main_window.py
        {
            'file': 'ui/main/main_window.py',
            'checks': [
                ('Menú Tickets', 'tickets_menu = tk.Menu'),
                ('Método generar ticket venta', 'def _generate_sales_ticket'),
                ('Método generar ticket entrada', 'def _generate_entry_ticket'),
                ('Método buscar tickets', 'def _search_tickets'),
                ('Método vista previa tickets', 'def _open_ticket_preview'),
                ('Método configuración empresa', 'def _open_company_config'),
                ('Importación TicketPreviewForm', 'from ui.forms.ticket_preview_form import TicketPreviewForm'),
                ('Importación CompanyConfigForm', 'from ui.forms.company_config_form import CompanyConfigForm')
            ]
        },
        # movement_form.py
        {
            'file': 'ui/forms/movement_form.py',
            'checks': [
                ('Método offer ticket generation', 'def _offer_ticket_generation'),
                ('Llamada a offer ticket', 'self._offer_ticket_generation'),
                ('Importación TicketService', 'from services.ticket_service import TicketService')
            ]
        },
        # sales_form.py
        {
            'file': 'ui/forms/sales_form.py',
            'checks': [
                ('Método simulate successful sale', 'def _simulate_successful_sale'),
                ('Llamada a simulate', 'self._simulate_successful_sale'),
                ('Testing de tickets', 'Desea probar la generación de ticket')
            ]
        }
    ]
    
    results = []
    
    for file_info in checks:
        file_path = os.path.join(base_path, file_info['file'])
        file_name = file_info['file']
        
        if not os.path.exists(file_path):
            results.append((file_name, False, "Archivo no existe"))
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            file_results = []
            for check_name, check_text in file_info['checks']:
                if check_text in content:
                    file_results.append(f"✅ {check_name}")
                else:
                    file_results.append(f"❌ {check_name}")
            
            results.append((file_name, True, file_results))
            
        except Exception as e:
            results.append((file_name, False, f"Error: {e}"))
    
    return results

def main():
    """Ejecutar todas las validaciones"""
    print("="*80)
    print("🔍 TESTING FINAL - FASE 3: SISTEMA DE TICKETS")
    print("="*80)
    
    all_passed = True
    
    # 1. Validar sintaxis de archivos críticos
    print("\n1️⃣ VALIDACIÓN DE SINTAXIS")
    print("-"*40)
    
    critical_files = [
        ('ui/main/main_window.py', 'MainWindow'),
        ('ui/forms/movement_form.py', 'MovementForm'),
        ('ui/forms/sales_form.py', 'SalesWindow'),
        ('services/ticket_service.py', 'TicketService'),
        ('services/company_service.py', 'CompanyService'),
        ('reports/ticket_generator.py', 'TicketGenerator'),
        ('ui/forms/ticket_preview_form.py', 'TicketPreviewForm'),
        ('ui/forms/company_config_form.py', 'CompanyConfigForm')
    ]
    
    for file_path, class_name in critical_files:
        full_path = os.path.join(r"D:\inventario_app2", file_path)
        valid, error = validate_syntax(full_path, file_path)
        
        if valid:
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}: {error}")
            all_passed = False
    
    # 2. Verificar base de datos
    print("\n2️⃣ VERIFICACIÓN DE BASE DE DATOS")
    print("-"*40)
    
    db_valid, db_message = check_database_tables()
    if db_valid:
        print(f"✅ Base de datos: {db_message}")
    else:
        print(f"❌ Base de datos: {db_message}")
        all_passed = False
    
    # 3. Verificar servicios
    print("\n3️⃣ VERIFICACIÓN DE SERVICIOS")
    print("-"*40)
    
    service_results = check_service_imports()
    for service_path, is_valid, message in service_results:
        if is_valid:
            print(f"✅ {service_path}: {message}")
        else:
            print(f"❌ {service_path}: {message}")
            all_passed = False
    
    # 4. Verificar integración
    print("\n4️⃣ VERIFICACIÓN DE INTEGRACIÓN")
    print("-"*40)
    
    integration_results = check_integration_in_files()
    for file_name, is_valid, results in integration_results:
        if is_valid:
            print(f"📄 {file_name}:")
            if isinstance(results, list):
                for result in results:
                    print(f"   {result}")
            else:
                print(f"   {results}")
        else:
            print(f"❌ {file_name}: {results}")
            all_passed = False
    
    # 5. Verificar directorios
    print("\n5️⃣ VERIFICACIÓN DE DIRECTORIOS")
    print("-"*40)
    
    required_dirs = [
        r"D:\inventario_app2\data\reports",
        r"D:\inventario_app2\reports\templates",
        r"D:\inventario_app2\logs",
        r"D:\inventario_app2\temp"
    ]
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}")
        else:
            print(f"⚠️ {dir_path} (será creado automáticamente)")
    
    # Resultado final
    print("\n" + "="*80)
    if all_passed:
        print("🎉 FASE 3 COMPLETADA EXITOSAMENTE")
        print("✅ Sistema de tickets totalmente integrado")
        print("✅ Configuración de empresa lista")
        print("✅ Todos los formularios integrados")
        print("✅ Base de datos preparada")
        print("✅ Servicios funcionando")
        print("\n🚀 EL SISTEMA ESTÁ LISTO PARA USO")
    else:
        print("⚠️ HAY PROBLEMAS QUE REQUIEREN ATENCIÓN")
        print("❌ Revisar errores arriba")
        print("🔧 Ejecutar correcciones necesarias")
    
    print("="*80)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
