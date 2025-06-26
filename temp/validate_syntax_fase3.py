"""
Script de validación de sintaxis - FASE 3
Valida todos los archivos críticos de la Fase 3
"""

import subprocess
import sys
import os
from pathlib import Path

def validate_file_syntax(filepath):
    """Valida la sintaxis de un archivo Python"""
    try:
        result = subprocess.run([
            sys.executable, '-m', 'py_compile', filepath
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        if result.returncode == 0:
            print(f"✅ {filepath} - SINTAXIS VÁLIDA")
            return True
        else:
            print(f"❌ {filepath} - ERRORES DE SINTAXIS:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error al validar {filepath}: {e}")
        return False

def main():
    """Función principal de validación"""
    print("🔍 VALIDACIÓN DE SINTAXIS - FASE 3")
    print("=" * 50)
    
    # Archivos críticos a validar
    archivos = [
        "ui/main/main_window.py",
        "services/ticket_service.py", 
        "services/company_service.py",
        "ui/forms/ticket_preview_form.py",
        "ui/forms/company_config_form.py",
        "reports/ticket_generator.py",
        "models/ticket.py",
        "models/company_config.py"
    ]
    
    resultados = []
    
    for archivo in archivos:
        print(f"\n🔍 Validando: {archivo}")
        resultado = validate_file_syntax(archivo)
        resultados.append((archivo, resultado))
    
    print("\n" + "=" * 50)
    print("📋 RESUMEN DE VALIDACIÓN:")
    
    exitosos = 0
    fallidos = 0
    
    for archivo, resultado in resultados:
        status = "✅ VÁLIDO" if resultado else "❌ ERROR"
        print(f"  {archivo}: {status}")
        if resultado:
            exitosos += 1
        else:
            fallidos += 1
    
    print(f"\n📊 ESTADÍSTICAS:")
    print(f"  ✅ Archivos válidos: {exitosos}")
    print(f"  ❌ Archivos con errores: {fallidos}")
    print(f"  📁 Total validados: {len(archivos)}")
    
    if fallidos == 0:
        print(f"\n🎉 TODOS LOS ARCHIVOS TIENEN SINTAXIS VÁLIDA")
        return True
    else:
        print(f"\n⚠️  HAY {fallidos} ARCHIVOS CON ERRORES DE SINTAXIS")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
