"""
Validación de Base de Datos - FASE 3
Verifica que las tablas de tickets y company_config estén creadas correctamente
"""

import sqlite3
import sys
import os
from pathlib import Path

def verificar_base_datos():
    """Verifica la estructura de la base de datos para Fase 3"""
    
    db_path = Path("inventario.db")
    
    if not db_path.exists():
        print("❌ ERROR: Base de datos no encontrada")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        print("🔍 VERIFICANDO ESTRUCTURA DE BASE DE DATOS - FASE 3")
        print("=" * 60)
        
        # Verificar tablas requeridas para Fase 3
        tablas_fase3 = [
            ('tickets', [
                'id_ticket',
                'ticket_type', 
                'ticket_number',
                'id_venta',
                'id_movimiento',
                'generated_at',
                'generated_by',
                'pdf_path',
                'reprint_count'
            ]),
            ('company_config', [
                'config_id',
                'nombre',
                'ruc', 
                'direccion',
                'telefono',
                'email',
                'itbms_rate',
                'moneda',
                'logo_path',
                'updated_at'
            ])
        ]
        
        tablas_existentes = []
        
        # Verificar cada tabla
        for tabla, columnas_esperadas in tablas_fase3:
            print(f"\n🔍 Verificando tabla: {tabla}")
            
            # Verificar si la tabla existe
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
            """, (tabla,))
            
            if cursor.fetchone():
                print(f"  ✅ Tabla '{tabla}' existe")
                tablas_existentes.append(tabla)
                
                # Verificar columnas
                cursor.execute(f"PRAGMA table_info({tabla})")
                columnas_actuales = [col[1] for col in cursor.fetchall()]
                
                print(f"  📋 Columnas encontradas: {len(columnas_actuales)}")
                
                columnas_faltantes = []
                for col_esperada in columnas_esperadas:
                    if col_esperada in columnas_actuales:
                        print(f"    ✅ {col_esperada}")
                    else:
                        print(f"    ❌ FALTA: {col_esperada}")
                        columnas_faltantes.append(col_esperada)
                
                if columnas_faltantes:
                    print(f"  ⚠️  Faltan {len(columnas_faltantes)} columnas en '{tabla}'")
                else:
                    print(f"  ✅ Todas las columnas presentes en '{tabla}'")
                    
            else:
                print(f"  ❌ Tabla '{tabla}' NO EXISTE")
        
        # Verificar datos iniciales en company_config
        if 'company_config' in tablas_existentes:
            print(f"\n🔍 Verificando datos en company_config:")
            cursor.execute("SELECT COUNT(*) FROM company_config")
            count = cursor.fetchone()[0]
            
            if count > 0:
                print(f"  ✅ Configuración de empresa presente ({count} registros)")
                
                # Mostrar configuración actual
                cursor.execute("SELECT nombre, ruc, direccion FROM company_config LIMIT 1")
                config = cursor.fetchone()
                if config:
                    print(f"    📊 Empresa: {config[0]}")
                    print(f"    📊 RUC: {config[1]}")
                    print(f"    📊 Dirección: {config[2]}")
            else:
                print(f"  ⚠️  No hay datos de configuración de empresa")
        
        # Verificar indices y restricciones
        print(f"\n🔍 Verificando índices y restricciones:")
        
        # Verificar índice único en ticket_number
        cursor.execute("""
            SELECT sql FROM sqlite_master 
            WHERE type='index' AND tbl_name='tickets'
        """)
        indices = cursor.fetchall()
        
        tiene_unique_ticket = any('ticket_number' in str(idx[0]) and 'UNIQUE' in str(idx[0]) 
                                 for idx in indices if idx[0])
        
        if tiene_unique_ticket:
            print("  ✅ Índice único en ticket_number presente")
        else:
            print("  ⚠️  Falta índice único en ticket_number")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE VALIDACIÓN:")
        print(f"  ✅ Tablas encontradas: {len(tablas_existentes)}/2")
        print(f"  📁 Base de datos: inventario.db")
        print(f"  📏 Tamaño: {db_path.stat().st_size / 1024:.1f} KB")
        
        if len(tablas_existentes) == 2:
            print("\n🎉 BASE DE DATOS LISTA PARA FASE 3")
            return True
        else:
            print(f"\n⚠️  FALTAN {2 - len(tablas_existentes)} TABLAS")
            return False
            
    except Exception as e:
        print(f"❌ Error al verificar base de datos: {e}")
        return False

def crear_tablas_faltantes():
    """Crea las tablas faltantes para Fase 3"""
    
    print("\n🔧 CREANDO TABLAS FALTANTES...")
    
    try:
        conn = sqlite3.connect("inventario.db")
        cursor = conn.cursor()
        
        # Crear tabla tickets
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id_ticket INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_type VARCHAR(20) NOT NULL,
                ticket_number VARCHAR(50) NOT NULL UNIQUE,
                id_venta INTEGER,
                id_movimiento INTEGER,
                generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                generated_by VARCHAR(60) NOT NULL,
                pdf_path VARCHAR(255),
                reprint_count INTEGER DEFAULT 0,
                FOREIGN KEY (id_venta) REFERENCES ventas (id_venta),
                FOREIGN KEY (id_movimiento) REFERENCES movimientos (id_movimiento)
            )
        """)
        
        # Crear tabla company_config
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS company_config (
                config_id INTEGER PRIMARY KEY DEFAULT 1,
                nombre VARCHAR(100) NOT NULL DEFAULT 'Copy Point S.A.',
                ruc VARCHAR(20) NOT NULL DEFAULT '888-888-8888',
                direccion VARCHAR(255) NOT NULL DEFAULT 'Las Lajas, Las Cumbres, Panamá',
                telefono VARCHAR(20) NOT NULL DEFAULT '6666-6666',
                email VARCHAR(100) NOT NULL DEFAULT 'copy.point@gmail.com',
                itbms_rate DECIMAL(5,2) DEFAULT 7.00,
                moneda VARCHAR(10) DEFAULT 'USD',
                logo_path VARCHAR(255),
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insertar configuración por defecto si no existe
        cursor.execute("SELECT COUNT(*) FROM company_config")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO company_config 
                (nombre, ruc, direccion, telefono, email, itbms_rate, moneda)
                VALUES 
                ('Copy Point S.A.', '888-888-8888', 'Las Lajas, Las Cumbres, Panamá', 
                 '6666-6666', 'copy.point@gmail.com', 7.00, 'USD')
            """)
        
        conn.commit()
        conn.close()
        
        print("✅ Tablas creadas exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error al crear tablas: {e}")
        return False

def main():
    """Función principal"""
    print("🗄️  VALIDACIÓN DE BASE DE DATOS - FASE 3")
    
    # Verificar estructura
    estructura_ok = verificar_base_datos()
    
    if not estructura_ok:
        respuesta = input("\n❓ ¿Desea crear las tablas faltantes? (s/n): ")
        if respuesta.lower() == 's':
            if crear_tablas_faltantes():
                print("\n🔄 Re-validando estructura...")
                estructura_ok = verificar_base_datos()
    
    if estructura_ok:
        print("\n✅ VALIDACIÓN COMPLETADA - BASE DE DATOS LISTA")
    else:
        print("\n❌ VALIDACIÓN FALLIDA - REVISAR BASE DE DATOS")
    
    return estructura_ok

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
