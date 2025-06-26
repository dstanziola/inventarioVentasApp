"""
Validación sintáctica rápida de archivos críticos Fase 3
"""

import py_compile
import os
import sys

def check_syntax(filepath):
    """Verifica sintaxis de un archivo Python"""
    try:
        py_compile.compile(filepath, doraise=True)
        print(f"✅ {filepath} - SINTAXIS VÁLIDA")
        return True
    except py_compile.PyCompileError as e:
        print(f"❌ {filepath} - ERROR DE SINTAXIS:")
        print(f"   {e}")
        return False
    except Exception as e:
        print(f"❌ {filepath} - ERROR INESPERADO: {e}")
        return False

# Cambiar al directorio del proyecto
os.chdir('D:/inventario_app2')

print("🔍 VALIDACIÓN SINTÁCTICA RÁPIDA - FASE 3")
print("=" * 50)

# Archivos críticos
archivos = [
    "services/ticket_service.py",
    "services/company_service.py", 
    "ui/forms/ticket_preview_form.py",
    "reports/ticket_generator.py",
    "models/ticket.py",
    "models/company_config.py",
    "ui/main/main_window.py"
]

resultados = []
for archivo in archivos:
    if os.path.exists(archivo):
        resultado = check_syntax(archivo)
        resultados.append((archivo, resultado))
    else:
        print(f"❌ {archivo} - ARCHIVO NO ENCONTRADO")
        resultados.append((archivo, False))

# Resumen
exitosos = sum(1 for _, resultado in resultados if resultado)
fallidos = len(resultados) - exitosos

print(f"\n📊 RESUMEN:")
print(f"  ✅ Válidos: {exitosos}")
print(f"  ❌ Errores: {fallidos}")
print(f"  📁 Total: {len(resultados)}")

if fallidos == 0:
    print("\n🎉 SINTAXIS CORRECTA EN TODOS LOS ARCHIVOS")
else:
    print(f"\n⚠️ HAY {fallidos} ARCHIVOS CON ERRORES")
