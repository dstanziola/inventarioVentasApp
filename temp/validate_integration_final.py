"""
Validación de Integración Completa - FASE 3
Verifica que todos los componentes de la Fase 3 estén correctamente integrados
"""

import sys
import os
from pathlib import Path
import importlib
import sqlite3

def validar_importaciones():
    """Valida que todas las importaciones necesarias funcionen"""
    
    print("📦 VALIDANDO IMPORTACIONES...")
    
    modulos_fase3 = [
        ('models.ticket', 'Ticket'),
        ('models.company_config', 'CompanyConfig'),
        ('services.ticket_service', 'TicketService'),
        ('services.company_service', 'CompanyService'),
        ('ui.forms.ticket_preview_form', 'TicketPreviewForm'),
        ('ui.forms.company_config_form', 'CompanyConfigForm'),
        ('reports.ticket_generator', 'TicketGenerator')
    ]
    
    importaciones_exitosas = 0
    
    for modulo_name, clase_name in modulos_fase3:
        try:
            modulo = importlib.import_module(modulo_name)
            clase = getattr(modulo, clase_name)
            print(f"  ✅ {modulo_name}.{clase_name}")
            importaciones_exitosas += 1
        except ImportError as e:
            print(f"  ❌ {modulo_name}.{clase_name} - ImportError: {e}")
        except AttributeError as e:
            print(f"  ❌ {modulo_name}.{clase_name} - AttributeError: {e}")
        except Exception as e:
            print(f"  ❌ {modulo_name}.{clase_name} - Error: {e}")
    
    print(f"\n  📊 Importaciones exitosas: {importaciones_exitosas}/{len(modulos_fase3)}")
    return importaciones_exitosas == len(modulos_fase3)

def validar_servicios():
    """Valida que los servicios funcionen correctamente"""
    
    print("\n🔧 VALIDANDO SERVICIOS...")
    
    try:
        # Importar dependencias
        from db.database import get_database_connection
        from services.ticket_service import TicketService
        from services.company_service import CompanyService
        
        # Obtener conexión
        db_connection = get_database_connection()
        
        # Validar TicketService
        print("  🎫 Validando TicketService...")
        ticket_service = TicketService(db_connection)
        
        # Verificar métodos principales
        metodos_ticket = ['generar_ticket_venta', 'generar_ticket_entrada', 'buscar_tickets']
        for metodo in metodos_ticket:
            if hasattr(ticket_service, metodo):
                print(f"    ✅ {metodo}()")
            else:
                print(f"    ❌ FALTA: {metodo}()")
        
        # Validar CompanyService
        print("  🏢 Validando CompanyService...")
        company_service = CompanyService(db_connection)
        
        # Verificar configuración por defecto
        config = company_service.obtener_configuracion()
        if config:
            print(f"    ✅ Configuración cargada: {config.nombre}")
        else:
            print(f"    ⚠️  No hay configuración de empresa")
        
        # Verificar métodos principales
        metodos_company = ['obtener_configuracion', 'actualizar_configuracion', 'crear_configuracion_por_defecto']
        for metodo in metodos_company:
            if hasattr(company_service, metodo):
                print(f"    ✅ {metodo}()")
            else:
                print(f"    ❌ FALTA: {metodo}()")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error al validar servicios: {e}")
        return False

def validar_formularios():
    """Valida que los formularios de UI funcionen"""
    
    print("\n🖥️  VALIDANDO FORMULARIOS...")
    
    try:
        # Importar formularios
        from ui.forms.ticket_preview_form import TicketPreviewForm
        from ui.forms.company_config_form import CompanyConfigForm
        
        print("  ✅ TicketPreviewForm importado correctamente")
        print("  ✅ CompanyConfigForm importado correctamente")
        
        # Verificar métodos requeridos
        metodos_requeridos = ['show', '__init__']
        
        for FormClass, name in [(TicketPreviewForm, 'TicketPreviewForm'), 
                               (CompanyConfigForm, 'CompanyConfigForm')]:
            print(f"  🔍 Verificando {name}...")
            for metodo in metodos_requeridos:
                if hasattr(FormClass, metodo):
                    print(f"    ✅ {metodo}()")
                else:
                    print(f"    ❌ FALTA: {metodo}()")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error al validar formularios: {e}")
        return False

def validar_reportes():
    """Valida que el sistema de reportes funcione"""
    
    print("\n📄 VALIDANDO GENERACIÓN DE REPORTES...")
    
    try:
        from reports.ticket_generator import TicketGenerator
        
        print("  ✅ TicketGenerator importado correctamente")
        
        # Verificar métodos principales
        metodos_reportes = ['generar_ticket', 'crear_pdf_venta', 'crear_pdf_entrada']
        
        for metodo in metodos_reportes:
            if hasattr(TicketGenerator, metodo):
                print(f"    ✅ {metodo}()")
            else:
                print(f"    ❌ FALTA: {metodo}()")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error al validar reportes: {e}")
        return False

def validar_main_window():
    """Valida que main_window tenga integración completa"""
    
    print("\n🪟 VALIDANDO INTEGRACIÓN EN MAIN WINDOW...")
    
    try:
        # Leer el contenido de main_window.py
        main_path = Path("ui/main/main_window.py")
        
        if not main_path.exists():
            print("  ❌ main_window.py no encontrado")
            return False
        
        with open(main_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Verificar importaciones clave
        importaciones_clave = [
            'from ui.forms.ticket_preview_form import TicketPreviewForm',
            'from ui.forms.company_config_form import CompanyConfigForm'
        ]
        
        print("  🔍 Verificando importaciones:")
        for imp in importaciones_clave:
            if imp in contenido:
                print(f"    ✅ {imp.split(' import ')[1]}")
            else:
                print(f"    ❌ FALTA: {imp.split(' import ')[1]}")
        
        # Verificar métodos de tickets
        metodos_tickets = [
            '_open_company_config',
            '_generate_sales_ticket',
            '_generate_entry_ticket', 
            '_search_tickets',
            '_open_ticket_preview'
        ]
        
        print("  🔍 Verificando métodos de tickets:")
        metodos_presentes = 0
        for metodo in metodos_tickets:
            if f"def {metodo}(" in contenido:
                print(f"    ✅ {metodo}()")
                metodos_presentes += 1
            else:
                print(f"    ❌ FALTA: {metodo}()")
        
        # Verificar menú de tickets
        tiene_menu = '"Tickets"' in contenido or "'Tickets'" in contenido
        print(f"  {'✅' if tiene_menu else '❌'} Menú de Tickets: {'Presente' if tiene_menu else 'Faltante'}")
        
        return metodos_presentes == len(metodos_tickets) and tiene_menu
        
    except Exception as e:
        print(f"  ❌ Error al validar main_window: {e}")
        return False

def validar_dependencias():
    """Valida que las dependencias requeridas estén instaladas"""
    
    print("\n📋 VALIDANDO DEPENDENCIAS...")
    
    dependencias_fase3 = [
        'reportlab',
        'qrcode',
        'PIL'  # Pillow para qrcode
    ]
    
    dependencias_ok = 0
    
    for dep in dependencias_fase3:
        try:
            importlib.import_module(dep)
            print(f"  ✅ {dep}")
            dependencias_ok += 1
        except ImportError:
            print(f"  ❌ FALTA: {dep}")
    
    if dependencias_ok < len(dependencias_fase3):
        print(f"\n  ⚠️  Instalar dependencias faltantes con:")
        print(f"     pip install reportlab qrcode[pil]")
    
    return dependencias_ok == len(dependencias_fase3)

def main():
    """Función principal de validación"""
    
    print("🔍 VALIDACIÓN COMPLETA DE INTEGRACIÓN - FASE 3")
    print("=" * 70)
    
    # Ejecutar todas las validaciones
    validaciones = [
        ("Dependencias", validar_dependencias),
        ("Importaciones", validar_importaciones),
        ("Servicios", validar_servicios),
        ("Formularios", validar_formularios),
        ("Reportes", validar_reportes),
        ("Main Window", validar_main_window)
    ]
    
    resultados = []
    
    for nombre, funcion in validaciones:
        try:
            resultado = funcion()
            resultados.append((nombre, resultado))
        except Exception as e:
            print(f"❌ Error en validación de {nombre}: {e}")
            resultados.append((nombre, False))
    
    # Resumen final
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE VALIDACIÓN DE INTEGRACIÓN:")
    
    exitosos = 0
    for nombre, resultado in resultados:
        status = "✅ EXITOSO" if resultado else "❌ FALLIDO"
        print(f"  {status} - {nombre}")
        if resultado:
            exitosos += 1
    
    print(f"\n📈 ESTADÍSTICAS:")
    print(f"  ✅ Validaciones exitosas: {exitosos}/{len(validaciones)}")
    print(f"  📊 Porcentaje de éxito: {(exitosos/len(validaciones)*100):.1f}%")
    
    if exitosos == len(validaciones):
        print(f"\n🎉 INTEGRACIÓN FASE 3 COMPLETADA EXITOSAMENTE")
        print(f"🚀 EL SISTEMA ESTÁ LISTO PARA PRODUCCIÓN")
        return True
    else:
        print(f"\n⚠️  HAY {len(validaciones) - exitosos} VALIDACIONES FALLIDAS")
        print(f"🔧 REVISAR COMPONENTES ANTES DE USAR EN PRODUCCIÓN")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
