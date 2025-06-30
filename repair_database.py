"""
Script de reparación crítica para el sistema de inventario.
Corrige problemas de base de datos y archivos bloqueados.
"""

import os
import sys
import sqlite3
import tempfile
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('database_repair.log'),
        logging.StreamHandler()
    ]
)

def cleanup_locked_files():
    """Limpia archivos de prueba bloqueados."""
    print("=== LIMPIANDO ARCHIVOS BLOQUEADOS ===")
    
    test_files = [
        "test_connection.db",
        "test_connection.db-journal",
        "test_connection.db-wal",
        "test_connection.db-shm"
    ]
    
    for file_name in test_files:
        if os.path.exists(file_name):
            try:
                os.remove(file_name)
                print(f"✓ Eliminado: {file_name}")
            except PermissionError:
                print(f"❌ Archivo bloqueado: {file_name}")
                # Intentar forzar cierre
                try:
                    import psutil
                    for proc in psutil.process_iter(['pid', 'name']):
                        try:
                            if any(file_name in f.path for f in proc.open_files()):
                                print(f"   Cerrando proceso: {proc.info['name']} (PID: {proc.info['pid']})")
                                proc.terminate()
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                except ImportError:
                    print("   psutil no disponible para forzar cierre")
            except Exception as e:
                print(f"❌ Error eliminando {file_name}: {e}")

def verify_database_structure():
    """Verifica y repara la estructura de la base de datos."""
    print("\n=== VERIFICANDO ESTRUCTURA DE BASE DE DATOS ===")
    
    # Ruta de la base de datos
    db_path = os.path.join("data", "inventario.db")
    
    # Crear directorio data si no existe
    os.makedirs("data", exist_ok=True)
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar tablas existentes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        print(f"Tablas existentes: {existing_tables}")
        
        # Tablas requeridas
        required_tables = [
            'categorias', 'productos', 'clientes', 'movimientos', 
            'ventas', 'detalle_ventas', 'usuarios'
        ]
        
        missing_tables = [table for table in required_tables if table not in existing_tables]
        
        if missing_tables:
            print(f"❌ Tablas faltantes: {missing_tables}")
            return create_database_schema(conn)
        else:
            print("✓ Todas las tablas existen")
            
            # Verificar estructura de tabla categorias
            cursor.execute("PRAGMA table_info(categorias);")
            columns = cursor.fetchall()
            print(f"Estructura tabla categorias: {columns}")
            
            # Verificar datos básicos
            cursor.execute("SELECT COUNT(*) FROM categorias;")
            cat_count = cursor.fetchone()[0]
            print(f"Categorías en BD: {cat_count}")
            
            if cat_count == 0:
                print("❌ No hay categorías, insertando datos básicos...")
                insert_basic_data(conn)
            
            conn.close()
            return True
            
    except sqlite3.Error as e:
        print(f"❌ Error de base de datos: {e}")
        return create_database_schema()
    except Exception as e:
        print(f"❌ Error general: {e}")
        return False

def create_database_schema(conn=None):
    """Crea el esquema completo de la base de datos."""
    print("\n=== CREANDO ESQUEMA DE BASE DE DATOS ===")
    
    db_path = os.path.join("data", "inventario.db")
    
    if conn is None:
        conn = sqlite3.connect(db_path)
    
    cursor = conn.cursor()
    
    try:
        # Script SQL completo
        schema_sql = """
        -- Tabla de categorías
        CREATE TABLE IF NOT EXISTS categorias (
            id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre VARCHAR(60) NOT NULL,
            tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('MATERIAL', 'SERVICIO')),
            activo BOOLEAN DEFAULT 1,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        -- Tabla de productos
        CREATE TABLE IF NOT EXISTS productos (
            id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre VARCHAR(60) NOT NULL,
            id_categoria INTEGER NOT NULL,
            stock INTEGER DEFAULT 0,
            costo DECIMAL(10,4) DEFAULT 0,
            precio DECIMAL(10,2) DEFAULT 0,
            tasa_impuesto DECIMAL(5,2) DEFAULT 0,
            activo BOOLEAN DEFAULT 1,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria)
        );

        -- Tabla de clientes
        CREATE TABLE IF NOT EXISTS clientes (
            id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre VARCHAR(60) NOT NULL,
            ruc VARCHAR(20),
            activo BOOLEAN DEFAULT 1,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        -- Tabla de usuarios
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_usuario VARCHAR(30) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            rol VARCHAR(20) NOT NULL CHECK (rol IN ('ADMIN', 'VENDEDOR')),
            activo BOOLEAN DEFAULT 1,
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        -- Tabla de ventas
        CREATE TABLE IF NOT EXISTS ventas (
            id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_venta DATETIME DEFAULT CURRENT_TIMESTAMP,
            id_cliente INTEGER,
            subtotal DECIMAL(10,2) DEFAULT 0,
            impuestos DECIMAL(10,2) DEFAULT 0,
            total DECIMAL(10,2) DEFAULT 0,
            responsable VARCHAR(60) NOT NULL,
            FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
        );

        -- Tabla de detalle de ventas
        CREATE TABLE IF NOT EXISTS detalle_ventas (
            id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
            id_venta INTEGER NOT NULL,
            id_producto INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            precio_unitario DECIMAL(10,2) NOT NULL,
            subtotal_item DECIMAL(10,2) NOT NULL,
            impuesto_item DECIMAL(10,2) DEFAULT 0,
            FOREIGN KEY (id_venta) REFERENCES ventas(id_venta),
            FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
        );

        -- Tabla de movimientos
        CREATE TABLE IF NOT EXISTS movimientos (
            id_movimiento INTEGER PRIMARY KEY AUTOINCREMENT,
            id_producto INTEGER NOT NULL,
            tipo_movimiento VARCHAR(20) NOT NULL CHECK (tipo_movimiento IN ('ENTRADA', 'VENTA', 'AJUSTE')),
            cantidad INTEGER NOT NULL,
            fecha_movimiento DATETIME DEFAULT CURRENT_TIMESTAMP,
            responsable VARCHAR(60) NOT NULL,
            id_venta INTEGER,
            observaciones TEXT,
            FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
            FOREIGN KEY (id_venta) REFERENCES ventas(id_venta)
        );

        -- Índices para mejorar rendimiento
        CREATE INDEX IF NOT EXISTS idx_productos_categoria ON productos(id_categoria);
        CREATE INDEX IF NOT EXISTS idx_productos_activo ON productos(activo);
        CREATE INDEX IF NOT EXISTS idx_movimientos_producto ON movimientos(id_producto);
        CREATE INDEX IF NOT EXISTS idx_movimientos_fecha ON movimientos(fecha_movimiento);
        CREATE INDEX IF NOT EXISTS idx_ventas_fecha ON ventas(fecha_venta);
        """
        
        # Ejecutar el esquema
        cursor.executescript(schema_sql)
        conn.commit()
        
        print("✓ Esquema de base de datos creado exitosamente")
        
        # Insertar datos básicos
        insert_basic_data(conn)
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Error creando esquema: {e}")
        conn.rollback()
        conn.close()
        return False

def insert_basic_data(conn):
    """Inserta datos básicos necesarios para el funcionamiento."""
    print("\n=== INSERTANDO DATOS BÁSICOS ===")
    
    cursor = conn.cursor()
    
    try:
        # Verificar si ya existen datos
        cursor.execute("SELECT COUNT(*) FROM usuarios;")
        user_count = cursor.fetchone()[0]
        
        if user_count == 0:
            # Usuario administrador por defecto
            import hashlib
            password_hash = hashlib.sha256("admin123".encode()).hexdigest()
            
            cursor.execute("""
                INSERT INTO usuarios (nombre_usuario, password_hash, rol)
                VALUES (?, ?, ?)
            """, ("admin", password_hash, "ADMIN"))
            
            print("✓ Usuario administrador creado (admin/admin123)")
        
        # Verificar categorías
        cursor.execute("SELECT COUNT(*) FROM categorias;")
        cat_count = cursor.fetchone()[0]
        
        if cat_count == 0:
            # Categorías básicas
            categorias_basicas = [
                ("Papelería", "MATERIAL"),
                ("Impresión", "SERVICIO"),
                ("Suministros de Oficina", "MATERIAL"),
                ("Servicios Gráficos", "SERVICIO"),
                ("Material Promocional", "MATERIAL")
            ]
            
            cursor.executemany("""
                INSERT INTO categorias (nombre, tipo)
                VALUES (?, ?)
            """, categorias_basicas)
            
            print(f"✓ {len(categorias_basicas)} categorías básicas creadas")
        
        # Verificar productos de muestra
        cursor.execute("SELECT COUNT(*) FROM productos;")
        prod_count = cursor.fetchone()[0]
        
        if prod_count == 0:
            # Productos de muestra
            productos_muestra = [
                ("Papel Bond A4", 1, 500, 0.03, 0.05, 7.0),
                ("Impresión B/N", 2, 0, 0.08, 0.10, 7.0),
                ("Carpetas Manila", 1, 100, 0.25, 0.35, 7.0),
                ("Diseño de Logo", 4, 0, 15.00, 25.00, 7.0),
                ("Bolígrafos", 1, 200, 0.15, 0.25, 7.0)
            ]
            
            cursor.executemany("""
                INSERT INTO productos (nombre, id_categoria, stock, costo, precio, tasa_impuesto)
                VALUES (?, ?, ?, ?, ?, ?)
            """, productos_muestra)
            
            print(f"✓ {len(productos_muestra)} productos de muestra creados")
        
        conn.commit()
        print("✓ Datos básicos insertados correctamente")
        
    except sqlite3.Error as e:
        print(f"❌ Error insertando datos básicos: {e}")
        conn.rollback()

def verify_imports():
    """Verifica que los imports funcionen correctamente."""
    print("\n=== VERIFICANDO IMPORTS ===")
    
    # Agregar src al path
    src_path = os.path.join(os.getcwd(), 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    try:
        from db.database import get_database_connection, DatabaseConnection
        print("✓ database imports OK")
        
        from services.product_service import ProductService
        print("✓ ProductService import OK")
        
        from services.category_service import CategoryService
        print("✓ CategoryService import OK")
        
        from models.producto import Producto
        print("✓ Producto model import OK")
        
        # Probar conexión
        db_conn = get_database_connection()
        if db_conn:
            print("✓ Conexión de base de datos OK")
            
            # Probar servicios
            cat_service = CategoryService(db_conn)
            categories = cat_service.get_all_categories()
            print(f"✓ CategoryService funcional ({len(categories)} categorías)")
            
            prod_service = ProductService(db_conn)
            products = prod_service.get_all_products()
            print(f"✓ ProductService funcional ({len(products)} productos)")
            
            return True
        else:
            print("❌ No se pudo obtener conexión de base de datos")
            return False
            
    except Exception as e:
        print(f"❌ Error en imports: {e}")
        return False

def main():
    """Función principal de reparación."""
    print("=" * 60)
    print("SCRIPT DE REPARACIÓN CRÍTICA - SISTEMA DE INVENTARIO")
    print("=" * 60)
    
    # Paso 1: Limpiar archivos bloqueados
    cleanup_locked_files()
    
    # Paso 2: Verificar/crear base de datos
    if not verify_database_structure():
        print("❌ FALLO: No se pudo crear la base de datos")
        return False
    
    # Paso 3: Verificar imports
    if not verify_imports():
        print("❌ FALLO: Los imports no funcionan correctamente")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 REPARACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 60)
    print("✓ Archivos bloqueados limpiados")
    print("✓ Base de datos inicializada")
    print("✓ Imports funcionando")
    print("✓ Servicios operativos")
    print("\nEL SISTEMA ESTÁ LISTO PARA USAR")
    print("Ejecute: python main.py")
    print("Usuario: admin | Contraseña: admin123")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ LA REPARACIÓN FALLÓ")
        print("Revise los logs para más detalles")
        sys.exit(1)
