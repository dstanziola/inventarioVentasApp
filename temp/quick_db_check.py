"""
Validación rápida de base de datos para Fase 3
"""

import sqlite3
import os

# Cambiar al directorio del proyecto
os.chdir('D:/inventario_app2')

print("🗄️ VALIDACIÓN DE BASE DE DATOS - FASE 3")
print("=" * 50)

try:
    # Conectar a la base de datos
    conn = sqlite3.connect('inventario.db')
    cursor = conn.cursor()
    
    # Verificar tabla tickets
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tickets'")
    tickets_existe = cursor.fetchone() is not None
    
    # Verificar tabla company_config
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='company_config'")
    company_existe = cursor.fetchone() is not None
    
    print(f"✅ Tabla tickets: {'EXISTE' if tickets_existe else 'NO EXISTE'}")
    print(f"✅ Tabla company_config: {'EXISTE' if company_existe else 'NO EXISTE'}")
    
    if tickets_existe and company_existe:
        # Verificar datos en company_config
        cursor.execute("SELECT COUNT(*) FROM company_config")
        count = cursor.fetchone()[0]
        print(f"📊 Registros en company_config: {count}")
        
        if count > 0:
            cursor.execute("SELECT nombre, ruc FROM company_config LIMIT 1")
            config = cursor.fetchone()
            print(f"📊 Empresa: {config[0]}")
            print(f"📊 RUC: {config[1]}")
        
        # Verificar estructura de tickets
        cursor.execute("PRAGMA table_info(tickets)")
        columnas_tickets = [col[1] for col in cursor.fetchall()]
        print(f"📊 Columnas en tickets: {len(columnas_tickets)}")
        
        print("\n🎉 BASE DE DATOS LISTA PARA FASE 3")
        resultado = True
    else:
        print("\n⚠️ FALTAN TABLAS DE FASE 3")
        resultado = False
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    resultado = False

print(f"\n📈 RESULTADO: {'EXITOSO' if resultado else 'FALLIDO'}")
