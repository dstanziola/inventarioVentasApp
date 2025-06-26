"""
Validación Rápida de Estado - FASE 3
Verifica rápidamente el estado de todos los componentes
"""

import os
import sys
from pathlib import Path

def verificar_archivo(ruta, descripcion):
    """Verifica si un archivo existe y su tamaño"""
    path = Path(ruta)
    if path.exists():
        size = path.stat().st_size
        print(f"✅ {descripcion}: {size:,} bytes")
        return True
    else:
        print(f"❌ {descripcion}: NO ENCONTRADO")
        return False

def verificar_base_datos():
    """Verificación rápida de base de datos"""
    db_path = Path("inventario.db")
    if db_path.exists():
        try:
            import sqlite3
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Verificar tablas de Fase 3
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tickets'")
            tickets_existe = cursor.fetchone() is not None
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='company_config'")
            company_existe = cursor.fetchone() is not None
            
            conn.close()
            
            print(f"✅ Base de datos: {db_path.stat().st_size:,} bytes")
            print(f"  {'✅' if tickets_existe else '❌'} Tabla tickets")
            print(f"  {'✅' if company_existe else '❌'} Tabla company_config")
            
            return tickets_existe and company_existe
        except Exception as e:
            print(f"❌ Error en base de datos: {e}")
            return False
    else:
        print("❌ Base de datos: NO ENCONTRADA")
        return False

def main():
    """Validación rápida"""
    
    print("⚡ VALIDACIÓN RÁPIDA - FASE 3")
    print("=" * 50)
    
    # Archivos críticos de Fase 3
    archivos_criticos = [
        ("services/ticket_service.py", "TicketService"),
        ("services/company_service.py", "CompanyService"),
        ("ui/forms/ticket_preview_form.py", "TicketPreviewForm"),
        ("ui/forms/company_config_form.py", "CompanyConfigForm"),
        ("reports/ticket_generator.py", "TicketGenerator"),
        ("models/ticket.py", "Modelo Ticket"),
        ("models/company_config.py", "Modelo CompanyConfig"),
        ("ui/main/main_window.py", "MainWindow Integrado")
    ]
    
    archivos_ok = 0
    
    print("\n📁 VERIFICANDO ARCHIVOS:")
    for ruta, desc in archivos_criticos:
        if verificar_archivo(ruta, desc):
            archivos_ok += 1
    
    print(f"\n🗄️ VERIFICANDO BASE DE DATOS:")
    db_ok = verificar_base_datos()
    
    print(f"\n📋 VERIFICANDO TESTS:")
    tests_fase3 = [
        ("tests/unit/models/test_ticket.py", "Tests Ticket"),
        ("tests/unit/models/test_company_config.py", "Tests CompanyConfig"),
        ("tests/unit/services/test_ticket_service.py", "Tests TicketService"),
        ("tests/unit/services/test_company_service.py", "Tests CompanyService")
    ]
    
    tests_ok = 0
    for ruta, desc in tests_fase3:
        if verificar_archivo(ruta, desc):
            tests_ok += 1
    
    # Resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN RÁPIDO:")
    print(f"✅ Archivos principales: {archivos_ok}/{len(archivos_criticos)}")
    print(f"✅ Tests unitarios: {tests_ok}/{len(tests_fase3)}")
    print(f"✅ Base de datos: {'OK' if db_ok else 'ERROR'}")
    
    total_componentes = len(archivos_criticos) + len(tests_fase3) + 1  # +1 para BD
    componentes_ok = archivos_ok + tests_ok + (1 if db_ok else 0)
    
    porcentaje = (componentes_ok / total_componentes) * 100
    
    print(f"\n📈 COMPLETITUD GENERAL: {porcentaje:.1f}%")
    
    if porcentaje >= 95:
        print("🎉 FASE 3 PRÁCTICAMENTE COMPLETA")
        print("🚀 Lista para testing final")
    elif porcentaje >= 80:
        print("⚡ FASE 3 CASI COMPLETA")
        print("🔧 Revisar componentes faltantes")
    else:
        print("⚠️  FASE 3 INCOMPLETA")
        print("🛠️ Requiere trabajo adicional")
    
    return porcentaje >= 95

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
