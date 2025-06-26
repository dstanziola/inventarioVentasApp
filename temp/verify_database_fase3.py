#!/usr/bin/env python3
"""
Script para verificar y crear las tablas requeridas para el sistema de tickets - FASE 3
"""

import sqlite3
import os

def verificar_base_datos():
    """Verificar y crear tablas requeridas para sistema de tickets"""
    
    db_path = r"D:\inventario_app2\inventario.db"
    
    print("🔍 Verificando base de datos para sistema de tickets...")
    print(f"📍 Ruta: {db_path}")
    
    if not os.path.exists(db_path):
        print("❌ La base de datos no existe")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar tablas existentes
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            ORDER BY name;
        """)
        
        existing_tables = [row[0] for row in cursor.fetchall()]
        print(f"📊 Tablas existentes: {len(existing_tables)}")
        for table in existing_tables:
            print(f"   ✓ {table}")
        
        # Verificar tabla tickets
        print(f"\n🎫 Verificando tabla 'tickets'...")
        if 'tickets' in existing_tables:
            print("   ✅ Tabla 'tickets' existe")
            
            # Verificar estructura
            cursor.execute("PRAGMA table_info(tickets)")
            columns = cursor.fetchall()
            print(f"   📋 Columnas: {len(columns)}")
            for col in columns:
                print(f"      - {col[1]} ({col[2]})")
        else:
            print("   ❌ Tabla 'tickets' NO existe")
            print("   🔧 Creando tabla 'tickets'...")
            
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
                );
            """)
            
            # Crear índices
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tickets_type ON tickets (ticket_type);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tickets_venta ON tickets (id_venta);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tickets_movimiento ON tickets (id_movimiento);")
            
            print("   ✅ Tabla 'tickets' creada exitosamente")
        
        # Verificar tabla company_config
        print(f"\n🏢 Verificando tabla 'company_config'...")
        if 'company_config' in existing_tables:
            print("   ✅ Tabla 'company_config' existe")
            
            # Verificar estructura
            cursor.execute("PRAGMA table_info(company_config)")
            columns = cursor.fetchall()
            print(f"   📋 Columnas: {len(columns)}")
            for col in columns:
                print(f"      - {col[1]} ({col[2]})")
                
            # Verificar si tiene datos
            cursor.execute("SELECT COUNT(*) FROM company_config")
            count = cursor.fetchone()[0]
            print(f"   📊 Registros: {count}")
            
            if count == 0:
                print("   🔧 Insertando configuración por defecto...")
                cursor.execute("""
                    INSERT INTO company_config (
                        nombre, ruc, direccion, telefono, email, 
                        itbms_rate, moneda, updated_at
                    ) VALUES (
                        'Copy Point S.A.',
                        '888-888-8888',
                        'Las Lajas, Las Cumbres, Panamá',
                        '6666-6666',
                        'copy.point@gmail.com',
                        7.00,
                        'USD',
                        CURRENT_TIMESTAMP
                    );
                """)
                print("   ✅ Configuración por defecto insertada")
        else:
            print("   ❌ Tabla 'company_config' NO existe")
            print("   🔧 Creando tabla 'company_config'...")
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS company_config (
                    config_id INTEGER PRIMARY KEY DEFAULT 1,
                    nombre VARCHAR(100) NOT NULL,
                    ruc VARCHAR(20) NOT NULL,
                    direccion VARCHAR(255) NOT NULL,
                    telefono VARCHAR(20) NOT NULL,
                    email VARCHAR(100) NOT NULL,
                    itbms_rate DECIMAL(5,2) DEFAULT 7.00,
                    moneda VARCHAR(10) DEFAULT 'USD',
                    logo_path VARCHAR(255),
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    CHECK (config_id = 1)
                );
            """)
            
            # Insertar configuración por defecto
            cursor.execute("""
                INSERT INTO company_config (
                    nombre, ruc, direccion, telefono, email, 
                    itbms_rate, moneda, updated_at
                ) VALUES (
                    'Copy Point S.A.',
                    '888-888-8888',
                    'Las Lajas, Las Cumbres, Panamá',
                    '6666-6666',
                    'copy.point@gmail.com',
                    7.00,
                    'USD',
                    CURRENT_TIMESTAMP
                );
            """)
            
            print("   ✅ Tabla 'company_config' creada con configuración por defecto")
        
        # Verificar directorio para PDFs
        pdf_dir = r"D:\inventario_app2\data\reports"
        if not os.path.exists(pdf_dir):
            os.makedirs(pdf_dir, exist_ok=True)
            print(f"📁 Directorio para PDFs creado: {pdf_dir}")
        else:
            print(f"📁 Directorio para PDFs existe: {pdf_dir}")
        
        # Confirmar cambios
        conn.commit()
        conn.close()
        
        print(f"\n{'='*60}")
        print("🎯 VERIFICACIÓN DE BASE DE DATOS COMPLETADA")
        print("✅ Sistema de tickets listo para usar")
        print("✅ Configuración de empresa inicializada")
        print("✅ Directorios necesarios creados")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando base de datos: {e}")
        return False

if __name__ == "__main__":
    verificar_base_datos()
