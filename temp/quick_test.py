import sys
import os

# Agregar el directorio del proyecto al path
sys.path.insert(0, 'D:/inventario_app2')

print("🔍 Verificación rápida de FASE 2")
print("=" * 40)

# Test 1: Importar ReportService
try:
    from services.report_service import ReportService
    print("✅ ReportService importado")
except Exception as e:
    print(f"❌ Error importando ReportService: {e}")

# Test 2: Importar PDF Generator
try:
    from reports.pdf_generator import PDFReportGenerator
    print("✅ PDFReportGenerator importado")
except Exception as e:
    print(f"❌ Error importando PDFReportGenerator: {e}")

# Test 3: Importar ReportsForm
try:
    from ui.forms.reports_form import ReportsForm
    print("✅ ReportsForm importado")
except Exception as e:
    print(f"❌ Error importando ReportsForm: {e}")

# Test 4: Crear ReportService
try:
    service = ReportService(":memory:")
    print("✅ ReportService creado")
    
    # Test de generación de reporte básico
    report = service.generate_inventory_report()
    print(f"✅ Reporte generado con {len(report['data'])} items")
    
except Exception as e:
    print(f"❌ Error creando ReportService: {e}")

# Test 5: Verificar que reportlab esté disponible
try:
    from reportlab.lib.pagesizes import A4
    print("✅ Reportlab disponible")
except Exception as e:
    print(f"❌ Reportlab no disponible: {e}")

print("\n🎯 Verificación básica completada")
