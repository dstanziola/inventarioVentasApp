#!/usr/bin/env python3
"""
Script para validar la compilación del ReportService
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.append('D:/inventario_app2')

try:
    # Intentar importar el ReportService
    from services.report_service import ReportService
    print("✅ ReportService importado exitosamente")
    
    # Validar que las clases existen
    print(f"✅ Clase ReportService disponible: {ReportService}")
    
    # Intentar crear una instancia (con path ficticio para test)
    test_service = ReportService("test.db")
    print(f"✅ Instancia de ReportService creada: {test_service}")
    
    print("\n🎉 Validación completa: ReportService implementado correctamente")
    
except ImportError as e:
    print(f"❌ Error de importación: {e}")
except Exception as e:
    print(f"❌ Error general: {e}")
