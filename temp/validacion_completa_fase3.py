"""
VALIDACIÓN COMPLETA FASE 3 - SCRIPT MAESTRO
Ejecuta todas las validaciones de la Fase 3 de manera secuencial
"""

import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

def ejecutar_script(script_path, descripcion):
    """Ejecuta un script de validación y captura el resultado"""
    
    print(f"\n🔍 EJECUTANDO: {descripcion}")
    print("=" * 60)
    
    try:
        # Ejecutar el script
        result = subprocess.run([
            sys.executable, script_path
        ], capture_output=True, text=True, timeout=120)
        
        # Mostrar salida
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print("⚠️  STDERR:")
            print(result.stderr)
        
        # Determinar éxito
        success = result.returncode == 0
        
        print(f"\n{'✅ COMPLETADO' if success else '❌ FALLIDO'}: {descripcion}")
        
        return {
            'script': script_path,
            'descripcion': descripcion,
            'success': success,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
        
    except subprocess.TimeoutExpired:
        print(f"❌ TIMEOUT: {descripcion} tardó más de 2 minutos")
        return {
            'script': script_path,
            'descripcion': descripcion,
            'success': False,
            'returncode': -1,
            'stdout': '',
            'stderr': 'Timeout después de 2 minutos'
        }
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return {
            'script': script_path,
            'descripcion': descripcion,
            'success': False,
            'returncode': -1,
            'stdout': '',
            'stderr': str(e)
        }

def generar_reporte_final(resultados):
    """Genera un reporte final de todas las validaciones"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    reporte_path = f"temp/reporte_validacion_fase3_{timestamp}.txt"
    
    with open(reporte_path, 'w', encoding='utf-8') as f:
        f.write("REPORTE DE VALIDACIÓN COMPLETA - FASE 3\n")
        f.write("Sistema de Gestión de Inventario - Copy Point S.A.\n")
        f.write("=" * 70 + "\n")
        f.write(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
        
        # Resumen ejecutivo
        exitosos = sum(1 for r in resultados if r['success'])
        total = len(resultados)
        porcentaje = (exitosos / total * 100) if total > 0 else 0
        
        f.write("RESUMEN EJECUTIVO:\n")
        f.write(f"✅ Validaciones exitosas: {exitosos}/{total}\n")
        f.write(f"📊 Porcentaje de éxito: {porcentaje:.1f}%\n")
        f.write(f"🎯 Estado general: {'EXITOSO' if exitosos == total else 'REQUIERE ATENCIÓN'}\n\n")
        
        # Detalle por validación
        f.write("DETALLE DE VALIDACIONES:\n")
        f.write("-" * 40 + "\n")
        
        for i, resultado in enumerate(resultados, 1):
            status = "✅ EXITOSO" if resultado['success'] else "❌ FALLIDO"
            f.write(f"{i}. {resultado['descripcion']}\n")
            f.write(f"   Estado: {status}\n")
            f.write(f"   Script: {resultado['script']}\n")
            f.write(f"   Código de retorno: {resultado['returncode']}\n")
            
            if resultado['stderr']:
                f.write(f"   Errores: {resultado['stderr'][:200]}...\n")
            
            f.write("\n")
        
        # Recomendaciones
        f.write("RECOMENDACIONES:\n")
        f.write("-" * 20 + "\n")
        
        if exitosos == total:
            f.write("🎉 ¡FASE 3 COMPLETADA EXITOSAMENTE!\n")
            f.write("✅ El sistema está listo para producción\n")
            f.write("✅ Todas las funcionalidades de tickets implementadas\n")
            f.write("✅ Tests unitarios pasando correctamente\n")
            f.write("✅ Base de datos configurada apropiadamente\n")
            f.write("✅ Integración completa verificada\n\n")
            f.write("PRÓXIMOS PASOS:\n")
            f.write("- Realizar pruebas de usuario final\n")
            f.write("- Considerar implementar códigos de barras (Fase 4)\n")
            f.write("- Documentar cambios para usuarios\n")
        else:
            f.write("⚠️  REVISAR COMPONENTES ANTES DE PRODUCCIÓN:\n")
            for resultado in resultados:
                if not resultado['success']:
                    f.write(f"- {resultado['descripcion']}\n")
            f.write("\nCONTACTO SOPORTE:\n")
            f.write("📧 tus_amigos@copypoint.online\n")
        
        f.write(f"\n{'-' * 70}\n")
        f.write("Reporte generado automáticamente por el sistema de validación\n")
    
    return reporte_path

def main():
    """Función principal que ejecuta todas las validaciones"""
    
    print("🚀 INICIANDO VALIDACIÓN COMPLETA - FASE 3")
    print("Sistema de Gestión de Inventario - Copy Point S.A.")
    print("=" * 70)
    print(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Scripts de validación a ejecutar
    validaciones = [
        ("temp/validate_database_fase3.py", "Validación de Base de Datos"),
        ("temp/run_tests_fase3.py", "Ejecución de Tests Unitarios"),
        ("temp/validate_integration_final.py", "Validación de Integración Completa")
    ]
    
    resultados = []
    
    # Ejecutar cada validación
    for script_path, descripcion in validaciones:
        if Path(script_path).exists():
            resultado = ejecutar_script(script_path, descripcion)
            resultados.append(resultado)
        else:
            print(f"❌ SCRIPT NO ENCONTRADO: {script_path}")
            resultados.append({
                'script': script_path,
                'descripcion': descripcion,
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': f'Script no encontrado: {script_path}'
            })
    
    # Generar reporte final
    print("\n" + "=" * 70)
    print("📊 GENERANDO REPORTE FINAL...")
    
    reporte_path = generar_reporte_final(resultados)
    
    print(f"📄 Reporte guardado en: {reporte_path}")
    
    # Resumen en consola
    exitosos = sum(1 for r in resultados if r['success'])
    total = len(resultados)
    
    print("\n🎯 RESUMEN FINAL:")
    print(f"✅ Validaciones exitosas: {exitosos}/{total}")
    print(f"📊 Porcentaje de éxito: {(exitosos/total*100):.1f}%")
    
    if exitosos == total:
        print("\n🎉 ¡FASE 3 COMPLETADA EXITOSAMENTE!")
        print("🚀 Sistema listo para producción")
        
        # Mostrar funcionalidades implementadas
        print("\n✨ FUNCIONALIDADES IMPLEMENTADAS:")
        funcionalidades = [
            "🎫 Generación de tickets de venta",
            "📦 Tickets de entrada de inventario", 
            "📄 Exportación a PDF profesional",
            "⚙️ Configuración de empresa editable",
            "🔍 Búsqueda y gestión de tickets",
            "📝 Formatos térmico y A4 soportados",
            "🧪 Tests unitarios completos",
            "🔗 Integración con sistema principal"
        ]
        
        for func in funcionalidades:
            print(f"  {func}")
        
        return True
    else:
        print(f"\n⚠️  HAY {total - exitosos} VALIDACIONES FALLIDAS")
        print("🔧 Revisar componentes antes de usar en producción")
        
        # Mostrar validaciones fallidas
        print("\n❌ VALIDACIONES FALLIDAS:")
        for resultado in resultados:
            if not resultado['success']:
                print(f"  - {resultado['descripcion']}")
        
        return False

if __name__ == "__main__":
    success = main()
    
    print(f"\n{'✅ VALIDACIÓN COMPLETADA' if success else '❌ VALIDACIÓN FALLIDA'}")
    
    if not success:
        sys.exit(1)
