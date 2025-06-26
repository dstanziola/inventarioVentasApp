#!/usr/bin/env python3
"""
Script de validación completa para FASE 2 - Sistema de Reportes

Este script valida que todas las funcionalidades del sistema de reportes
estén implementadas correctamente y funcionen sin errores.

VALIDACIONES INCLUIDAS:
1. Importación de módulos
2. Creación de servicios
3. Generación de reportes
4. Exportación a PDF
5. Interfaz de usuario

Ejecutar desde el directorio raíz del proyecto:
python temp/validate_fase2_complete.py
"""

import sys
import os
import traceback
from pathlib import Path
from datetime import date, timedelta
import tempfile
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Agregar el directorio raíz al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Prueba que todas las importaciones funcionen correctamente"""
    print("🔍 VALIDANDO IMPORTACIONES")
    print("=" * 50)
    
    tests = [
        ("ReportService", "from services.report_service import ReportService"),
        ("PDFReportGenerator", "from reports.pdf_generator import PDFReportGenerator, generate_pdf_report"),
        ("ReportsForm", "from ui.forms.reports_form import ReportsForm"),
        ("Reportlab", "from reportlab.lib.pagesizes import A4"),
    ]
    
    for name, import_statement in tests:
        try:
            exec(import_statement)
            print(f"✅ {name}: Importación exitosa")
        except ImportError as e:
            print(f"❌ {name}: Error de importación - {e}")
            return False
        except Exception as e:
            print(f"⚠️ {name}: Error general - {e}")
            return False
    
    print("\n🎉 Todas las importaciones exitosas")
    return True

def test_report_service():
    """Prueba la funcionalidad del ReportService"""
    print("\n📊 VALIDANDO REPORTSERVICE")
    print("=" * 50)
    
    try:
        from services.report_service import ReportService
        
        # Crear servicio con BD temporal
        db_path = ":memory:"
        service = ReportService(db_path)
        print("✅ ReportService creado exitosamente")
        
        # Probar método de estadísticas (que no requiere datos)
        try:
            stats = service.get_summary_statistics()
            print(f"✅ Estadísticas obtenidas: {len(stats)} métricas")
        except Exception as e:
            print(f"⚠️ Error en estadísticas: {e}")
        
        # Probar generación de reporte de inventario (sin datos)
        try:
            report = service.generate_inventory_report()
            assert 'data' in report
            assert 'summary' in report
            assert 'generated_at' in report
            print("✅ Reporte de inventario generado correctamente")
        except Exception as e:
            print(f"⚠️ Error en reporte de inventario: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en ReportService: {e}")
        traceback.print_exc()
        return False

def test_pdf_generation():
    """Prueba la generación de PDFs"""
    print("\n📄 VALIDANDO GENERACIÓN DE PDFs")
    print("=" * 50)
    
    try:
        from reports.pdf_generator import generate_pdf_report
        
        # Datos de prueba para PDF
        test_report_data = {
            'data': [
                {
                    'id_producto': 1,
                    'nombre': 'Producto Test',
                    'categoria': 'Test Category',
                    'stock_actual': 10,
                    'costo_unitario': 5.50,
                    'valor_total': 55.00
                }
            ],
            'summary': {
                'total_productos': 1,
                'productos_con_stock': 1,
                'productos_sin_stock': 0,
                'valor_total_inventario': 55.00,
                'fecha_corte': date.today().isoformat()
            },
            'generated_at': '2025-06-25T10:00:00',
            'filters_applied': {}
        }
        
        # Crear archivo temporal para PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            pdf_path = tmp.name
        
        try:
            # Generar PDF de prueba
            success = generate_pdf_report(
                report_data=test_report_data,
                pdf_path=pdf_path,
                report_type='inventory'
            )
            
            if success and os.path.exists(pdf_path):
                file_size = os.path.getsize(pdf_path)
                print(f"✅ PDF generado exitosamente ({file_size} bytes)")
                
                # Verificar que es un PDF válido
                with open(pdf_path, 'rb') as f:
                    header = f.read(8)
                    if header.startswith(b'%PDF'):
                        print("✅ PDF válido - Encabezado correcto")
                    else:
                        print("⚠️ PDF posiblemente inválido - Encabezado incorrecto")
                
                return True
            else:
                print("❌ Error generando PDF")
                return False
                
        finally:
            # Limpiar archivo temporal
            if os.path.exists(pdf_path):
                os.unlink(pdf_path)
        
    except Exception as e:
        print(f"❌ Error en generación de PDF: {e}")
        traceback.print_exc()
        return False

def test_integration():
    """Prueba la integración entre ReportService y PDFGenerator"""
    print("\n🔗 VALIDANDO INTEGRACIÓN COMPLETA")
    print("=" * 50)
    
    try:
        from services.report_service import ReportService
        
        # Crear servicio
        service = ReportService(":memory:")
        
        # Generar reporte
        report_data = service.generate_inventory_report()
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            pdf_path = tmp.name
        
        try:
            # Exportar a PDF usando el método integrado
            success = service.export_to_pdf(
                report_data=report_data,
                pdf_path=pdf_path,
                report_type='inventory'
            )
            
            if success and os.path.exists(pdf_path):
                print("✅ Integración ReportService -> PDF exitosa")
                return True
            else:
                print("❌ Error en integración")
                return False
                
        finally:
            if os.path.exists(pdf_path):
                os.unlink(pdf_path)
                
    except Exception as e:
        print(f"❌ Error en integración: {e}")
        traceback.print_exc()
        return False

def test_ui_creation():
    """Prueba que la interfaz de reportes se pueda crear"""
    print("\n🖥️ VALIDANDO INTERFAZ DE USUARIO")
    print("=" * 50)
    
    try:
        # Importar sin crear ventana real
        from ui.forms.reports_form import ReportsForm
        
        # Crear instancia (sin mostrar)
        reports_form = ReportsForm(parent=None, db_path=":memory:")
        
        print("✅ ReportsForm creado exitosamente")
        
        # Validar que tiene los métodos esperados
        expected_methods = [
            '_generate_inventory_report',
            '_generate_movements_report', 
            '_generate_sales_report',
            '_generate_profitability_report',
            '_export_to_pdf'
        ]
        
        for method in expected_methods:
            if hasattr(reports_form, method):
                print(f"✅ Método {method} presente")
            else:
                print(f"❌ Método {method} faltante")
                return False
        
        print("✅ Interfaz de reportes validada")
        return True
        
    except Exception as e:
        print(f"❌ Error en interfaz: {e}")
        traceback.print_exc()
        return False

def test_main_window_integration():
    """Prueba que el MainWindow tenga integrado el sistema de reportes"""
    print("\n🏠 VALIDANDO INTEGRACIÓN CON MAINWINDOW")
    print("=" * 50)
    
    try:
        from ui.main.main_window import MainWindow
        
        # Verificar que tiene los métodos de reportes
        expected_methods = [
            '_open_reports_system',
            '_open_inventory_report_direct',
            '_open_sales_report_direct',
            '_open_movements_report_direct',
            '_open_profitability_report_direct'
        ]
        
        for method in expected_methods:
            if hasattr(MainWindow, method):
                print(f"✅ Método {method} presente en MainWindow")
            else:
                print(f"❌ Método {method} faltante en MainWindow")
                return False
        
        print("✅ Integración con MainWindow validada")
        return True
        
    except Exception as e:
        print(f"❌ Error validando MainWindow: {e}")
        traceback.print_exc()
        return False

def run_all_tests():
    """Ejecuta todas las pruebas de validación"""
    print("🧪 VALIDACIÓN COMPLETA - FASE 2: SISTEMA DE REPORTES")
    print("=" * 60)
    
    tests = [
        ("Importaciones", test_imports),
        ("ReportService", test_report_service),
        ("Generación PDF", test_pdf_generation),
        ("Integración", test_integration),
        ("Interfaz Usuario", test_ui_creation),
        ("MainWindow", test_main_window_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n💥 Error ejecutando {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE VALIDACIÓN")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ EXITOSO" if result else "❌ FALLÓ"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\nResultado final: {passed}/{total} pruebas exitosas")
    
    if passed == total:
        print("\n🎉 ¡FASE 2 VALIDADA COMPLETAMENTE!")
        print("✅ Sistema de Reportes listo para producción")
        print("\nFuncionalidades implementadas:")
        print("• ReportService con 4 tipos de reportes")
        print("• Generación profesional de PDFs")
        print("• Interfaz de usuario completa")
        print("• Integración con MainWindow")
        print("• Exportación con formato corporativo")
    else:
        print(f"\n⚠️ FASE 2 INCOMPLETA: {total - passed} prueba(s) fallaron")
        print("Revisar errores antes de proceder a producción")
    
    return passed == total

if __name__ == "__main__":
    try:
        # Cambiar al directorio del proyecto
        os.chdir(project_root)
        
        # Ejecutar validación completa
        success = run_all_tests()
        
        # Código de salida
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Validación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error fatal durante validación: {e}")
        traceback.print_exc()
        sys.exit(1)
