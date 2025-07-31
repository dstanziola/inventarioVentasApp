#!/usr/bin/env python3
"""
Script de diagnóstico para la discrepancia entre formulario y base de datos.

Analiza:
1. Productos en BD (activos e inactivos)
2. Estado del ProductService
3. Validaciones vs realidad
"""

import sqlite3
import sys
import os
from datetime import datetime

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def analyze_database():
    """Analiza directamente la base de datos SQLite."""
    db_path = "inventario.db"
    
    if not os.path.exists(db_path):
        print(f"❌ ERROR: Base de datos no encontrada en {db_path}")
        return
    
    print("=" * 60)
    print("📊 DIAGNÓSTICO DE DISCREPANCIA PRODUCTOS")
    print("=" * 60)
    print(f"⏰ Timestamp: {datetime.now()}")
    print(f"📁 Base de datos: {db_path}")
    print()
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Para acceso por nombre de columna
        cursor = conn.cursor()
        
        # 1. ANÁLISIS GENERAL DE PRODUCTOS
        print("1️⃣ ANÁLISIS GENERAL DE PRODUCTOS:")
        print("-" * 40)
        
        # Total de productos
        cursor.execute("SELECT COUNT(*) as total FROM productos")
        total_productos = cursor.fetchone()['total']
        print(f"   📈 Total productos en BD: {total_productos}")
        
        # Productos activos
        cursor.execute("SELECT COUNT(*) as activos FROM productos WHERE activo = 1")
        productos_activos = cursor.fetchone()['activos']
        print(f"   ✅ Productos ACTIVOS (activo=1): {productos_activos}")
        
        # Productos inactivos
        cursor.execute("SELECT COUNT(*) as inactivos FROM productos WHERE activo = 0")
        productos_inactivos = cursor.fetchone()['inactivos']
        print(f"   ❌ Productos INACTIVOS (activo=0): {productos_inactivos}")
        
        print()
        
        # 2. DETALLE DE PRODUCTOS INACTIVOS
        if productos_inactivos > 0:
            print("2️⃣ PRODUCTOS INACTIVOS (ELIMINADOS SOFT DELETE):")
            print("-" * 50)
            
            cursor.execute("""
                SELECT id_producto, nombre, stock, activo, fecha_modificacion, 
                       fecha_creacion
                FROM productos 
                WHERE activo = 0 
                ORDER BY fecha_modificacion DESC
                LIMIT 10
            """)
            
            productos_eliminados = cursor.fetchall()
            
            if productos_eliminados:
                print("   🗑️  Últimos productos eliminados:")
                for prod in productos_eliminados:
                    print(f"      ID: {prod['id_producto']} | '{prod['nombre'][:30]}' | Stock: {prod['stock']} | Eliminado: {prod['fecha_modificacion']}")
            
            print()
        
        # 3. DETALLE DE PRODUCTOS ACTIVOS
        if productos_activos > 0:
            print("3️⃣ PRODUCTOS ACTIVOS (VISIBLES EN FORMULARIO):")
            print("-" * 50)
            
            cursor.execute("""
                SELECT id_producto, nombre, stock, precio, activo, fecha_modificacion
                FROM productos 
                WHERE activo = 1 
                ORDER BY id_producto
                LIMIT 10
            """)
            
            productos_activos_list = cursor.fetchall()
            
            if productos_activos_list:
                print("   ✅ Productos activos:")
                for prod in productos_activos_list:
                    print(f"      ID: {prod['id_producto']} | '{prod['nombre'][:30]}' | Stock: {prod['stock']} | Precio: {prod['precio']}")
            else:
                print("   ⚠️  NO HAY PRODUCTOS ACTIVOS - Esto explica por qué el formulario aparece vacío")
            
            print()
        
        # 4. ANÁLISIS DE STOCK
        print("4️⃣ ANÁLISIS DE STOCK:")
        print("-" * 30)
        
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN activo = 1 THEN stock ELSE 0 END) as stock_activos,
                SUM(CASE WHEN activo = 0 THEN stock ELSE 0 END) as stock_inactivos,
                SUM(stock) as stock_total
            FROM productos
        """)
        
        stock_info = cursor.fetchone()
        print(f"   📦 Stock en productos ACTIVOS: {stock_info['stock_activos'] or 0}")
        print(f"   🚫 Stock en productos INACTIVOS: {stock_info['stock_inactivos'] or 0}")
        print(f"   📊 Stock TOTAL (activos + inactivos): {stock_info['stock_total'] or 0}")
        
        print()
        
        # 5. DIAGNÓSTICO CRÍTICO
        print("5️⃣ DIAGNÓSTICO CRÍTICO:")
        print("-" * 30)
        
        if productos_activos == 0 and productos_inactivos > 0:
            print("   🚨 PROBLEMA IDENTIFICADO:")
            print("      - Todos los productos están marcados como INACTIVOS (activo=0)")
            print("      - El formulario usa get_all_products(only_active=True)")
            print("      - Por eso el formulario muestra 'productos eliminados'")
            print("      - Pero los productos persisten físicamente en la BD")
            print()
            print("   💡 CAUSA PROBABLE:")
            print("      - Operación masiva de soft-delete ejecutada por error")
            print("      - O problema en lógica de eliminación")
            
        elif productos_activos > 0:
            print("   ✅ Sistema funcionando normalmente")
            print("      - Hay productos activos visibles en el formulario")
            
        elif total_productos == 0:
            print("   ⚠️  Base de datos completamente vacía")
            
        # 6. ÚLTIMAS MODIFICACIONES
        print()
        print("6️⃣ ÚLTIMAS MODIFICACIONES:")
        print("-" * 35)
        
        cursor.execute("""
            SELECT id_producto, nombre, activo, fecha_modificacion, fecha_creacion
            FROM productos 
            ORDER BY fecha_modificacion DESC 
            LIMIT 5
        """)
        
        ultimas_modificaciones = cursor.fetchall()
        
        if ultimas_modificaciones:
            for prod in ultimas_modificaciones:
                estado = "ACTIVO" if prod['activo'] else "INACTIVO"
                print(f"   📝 ID: {prod['id_producto']} | '{prod['nombre'][:25]}' | {estado} | Mod: {prod['fecha_modificacion']}")
        
        conn.close()
        
        print()
        print("=" * 60)
        print("🎯 RESULTADO DEL DIAGNÓSTICO:")
        print("=" * 60)
        
        if productos_activos == 0 and productos_inactivos > 0:
            print("❌ DISCREPANCIA CONFIRMADA:")
            print("   - Formulario: 'Todos los productos eliminados' (correcto)")
            print("   - Base de datos: Productos persisten físicamente (correcto)")
            print("   - Causa: Soft delete masivo - productos marcados activo=0")
            print()
            print("🔧 SOLUCIONES POSIBLES:")
            print("   1. Reactivar productos: UPDATE productos SET activo=1")
            print("   2. Revisar logs para identificar cuándo ocurrió el soft delete")
            print("   3. Implementar función de 'Papelera' para restaurar productos")
        
        elif productos_activos > 0:
            print("✅ No hay discrepancia - Sistema funcionando correctamente")
            
    except Exception as e:
        print(f"❌ ERROR analizando base de datos: {e}")

def test_product_service():
    """Prueba el ProductService para confirmar comportamiento."""
    try:
        print()
        print("7️⃣ TEST DEL PRODUCTSERVICE:")
        print("-" * 35)
        
        from services.service_container import get_container
        container = get_container()
        product_service = container.get('product_service')
        
        # Test get_all_products con only_active=True (comportamiento por defecto)
        productos_activos = product_service.get_all_products(only_active=True)
        print(f"   ProductService.get_all_products(only_active=True): {len(productos_activos)} productos")
        
        # Test get_all_products con only_active=False (incluye inactivos)
        todos_productos = product_service.get_all_products(only_active=False)
        print(f"   ProductService.get_all_products(only_active=False): {len(todos_productos)} productos")
        
        if len(productos_activos) == 0 and len(todos_productos) > 0:
            print("   🎯 CONFIRMADO: El formulario usa only_active=True y no hay productos activos")
            print("   📋 Primeros 3 productos inactivos:")
            for i, producto in enumerate(todos_productos[:3]):
                print(f"      {i+1}. ID: {producto.id_producto} | '{producto.nombre}' | Stock: {producto.stock}")
        
    except Exception as e:
        print(f"   ❌ Error probando ProductService: {e}")

if __name__ == "__main__":
    analyze_database()
    test_product_service()
    print()
    print("📄 Diagnóstico completado. Revise los resultados arriba.")
