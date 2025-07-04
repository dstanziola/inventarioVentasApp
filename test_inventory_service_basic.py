"""
Test unitario básico para InventoryService - FASE 5A
===================================================

OBJETIVO:
Test básico para InventoryService que es crítico para el seguimiento
de movimientos de inventario en el sistema.

COBERTURA:
- Creación de movimientos
- Validaciones de entrada
- Obtención de movimientos por producto
- Obtención de todos los movimientos
- Manejo de errores

Autor: Sistema de Inventario Copy Point S.A.
Fecha: Julio 3, 2025 - FASE 5A Completar Cobertura
"""

import unittest
import sys
import os
import tempfile
from datetime import datetime
from typing import List, Dict, Any, Optional

# Agregar path del proyecto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Imports principales
from src.db.database import DatabaseConnection
from src.services.inventory_service import InventoryService
from src.services.product_service import ProductService
from src.services.category_service import CategoryService
from src.models.movimiento import Movimiento


class TestInventoryServiceBasic(unittest.TestCase):
    """Test suite básico para InventoryService."""
    
    @classmethod
    def setUpClass(cls):
        """Configuración inicial para todos los tests."""
        # Base de datos temporal
        cls.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        cls.temp_db.close()
        
        cls.db_connection = DatabaseConnection(cls.temp_db.name)
        cls.db_connection.connect()
        cls.db_connection.create_tables()
        
        print(f"\n🧪 === TESTS BÁSICOS INVENTORYSERVICE ===")
        print(f"📁 Base de datos temporal: {cls.temp_db.name}")
    
    @classmethod 
    def tearDownClass(cls):
        """Limpieza después de todos los tests."""
        if hasattr(cls, 'db_connection'):
            cls.db_connection.disconnect()
        if os.path.exists(cls.temp_db.name):
            os.unlink(cls.temp_db.name)
    
    def setUp(self):
        """Configuración antes de cada test."""
        # Limpiar datos
        connection = self.db_connection.get_connection()
        cursor = connection.cursor()
        
        cursor.execute("DELETE FROM movimientos")
        cursor.execute("DELETE FROM productos")
        cursor.execute("DELETE FROM categorias")
        connection.commit()
        
        # Crear datos de prueba
        self.category_service = CategoryService(self.db_connection)
        self.product_service = ProductService(self.db_connection)
        self.inventory_service = InventoryService(self.db_connection)
        
        # Crear categoría y producto de prueba
        self.categoria_test = self.category_service.create_category(
            'Materiales Test', 'MATERIAL'
        )
        
        self.producto_test = self.product_service.create_product(
            nombre='Martillo Test',
            id_categoria=self.categoria_test.id_categoria,
            stock_inicial=50,
            precio_venta=15.00
        )
    
    # ========== TESTS DE CREACIÓN DE MOVIMIENTOS ==========
    
    def test_create_movement_entrada_success(self):
        """Test crear movimiento de entrada exitoso."""
        print("\n1️⃣ TEST: Crear movimiento de entrada...")
        
        movimiento = self.inventory_service.create_movement(
            id_producto=self.producto_test.id_producto,
            tipo_movimiento='ENTRADA',
            cantidad=20,
            responsable='Usuario Test',
            observaciones='Entrada de prueba'
        )
        
        # Verificaciones
        self.assertIsInstance(movimiento, Movimiento)
        self.assertEqual(movimiento.id_producto, self.producto_test.id_producto)
        self.assertEqual(movimiento.tipo_movimiento, 'ENTRADA')
        self.assertEqual(movimiento.cantidad, 20)
        self.assertEqual(movimiento.responsable, 'Usuario Test')
        self.assertEqual(movimiento.observaciones, 'Entrada de prueba')
        
        print(f"   ✅ Movimiento creado: ID {movimiento.id_movimiento}")
    
    def test_create_movement_venta_success(self):
        """Test crear movimiento de venta exitoso."""
        print("\n2️⃣ TEST: Crear movimiento de venta...")
        
        movimiento = self.inventory_service.create_movement(
            id_producto=self.producto_test.id_producto,
            tipo_movimiento='VENTA',
            cantidad=5,
            responsable='Vendedor Test',
            id_venta=1001,
            observaciones='Venta de prueba'
        )
        
        # Verificaciones
        self.assertIsInstance(movimiento, Movimiento)
        self.assertEqual(movimiento.tipo_movimiento, 'VENTA')
        self.assertEqual(movimiento.cantidad, 5)
        self.assertEqual(movimiento.id_venta, 1001)
        
        print(f"   ✅ Movimiento venta creado: ID {movimiento.id_movimiento}")
    
    def test_create_movement_ajuste_success(self):
        """Test crear movimiento de ajuste exitoso."""
        print("\n3️⃣ TEST: Crear movimiento de ajuste...")
        
        movimiento = self.inventory_service.create_movement(
            id_producto=self.producto_test.id_producto,
            tipo_movimiento='AJUSTE',
            cantidad=10,
            responsable='Supervisor Test',
            observaciones='Ajuste de inventario'
        )
        
        # Verificaciones
        self.assertIsInstance(movimiento, Movimiento)
        self.assertEqual(movimiento.tipo_movimiento, 'AJUSTE')
        self.assertEqual(movimiento.cantidad, 10)
        
        print(f"   ✅ Movimiento ajuste creado: ID {movimiento.id_movimiento}")
    
    # ========== TESTS DE VALIDACIÓN ==========
    
    def test_create_movement_invalid_product(self):
        """Test crear movimiento con producto inexistente."""
        print("\n4️⃣ TEST: Producto inexistente...")
        
        with self.assertRaises(ValueError) as context:
            self.inventory_service.create_movement(
                id_producto=99999,  # Producto inexistente
                tipo_movimiento='ENTRADA',
                cantidad=10,
                responsable='Usuario Test'
            )
        
        self.assertIn('producto', str(context.exception).lower())
        
        print("   ✅ Validación producto inexistente funcionando")
    
    def test_create_movement_invalid_type(self):
        """Test crear movimiento con tipo inválido."""
        print("\n5️⃣ TEST: Tipo de movimiento inválido...")
        
        with self.assertRaises(ValueError) as context:
            self.inventory_service.create_movement(
                id_producto=self.producto_test.id_producto,
                tipo_movimiento='TIPO_INVALIDO',
                cantidad=10,
                responsable='Usuario Test'
            )
        
        self.assertIn('tipo', str(context.exception).lower())
        
        print("   ✅ Validación tipo movimiento funcionando")
    
    def test_create_movement_invalid_quantity(self):
        """Test crear movimiento con cantidad inválida."""
        print("\n6️⃣ TEST: Cantidad inválida...")
        
        # Cantidad cero
        with self.assertRaises(ValueError) as context:
            self.inventory_service.create_movement(
                id_producto=self.producto_test.id_producto,
                tipo_movimiento='ENTRADA',
                cantidad=0,
                responsable='Usuario Test'
            )
        
        self.assertIn('cantidad', str(context.exception).lower())
        
        # Cantidad negativa
        with self.assertRaises(ValueError):
            self.inventory_service.create_movement(
                id_producto=self.producto_test.id_producto,
                tipo_movimiento='ENTRADA',
                cantidad=-5,
                responsable='Usuario Test'
            )
        
        print("   ✅ Validación cantidad funcionando")
    
    def test_create_movement_invalid_responsable(self):
        """Test crear movimiento con responsable inválido."""
        print("\n7️⃣ TEST: Responsable inválido...")
        
        # Responsable vacío
        with self.assertRaises(ValueError) as context:
            self.inventory_service.create_movement(
                id_producto=self.producto_test.id_producto,
                tipo_movimiento='ENTRADA',
                cantidad=10,
                responsable=''
            )
        
        self.assertIn('responsable', str(context.exception).lower())
        
        # Responsable None
        with self.assertRaises(ValueError):
            self.inventory_service.create_movement(
                id_producto=self.producto_test.id_producto,
                tipo_movimiento='ENTRADA',
                cantidad=10,
                responsable=None
            )
        
        print("   ✅ Validación responsable funcionando")
    
    # ========== TESTS DE CONSULTA ==========
    
    def test_get_product_movements(self):
        """Test obtener movimientos de un producto."""
        print("\n8️⃣ TEST: Obtener movimientos de producto...")
        
        # Crear varios movimientos para el producto
        movimientos_data = [
            {'tipo_movimiento': 'ENTRADA', 'cantidad': 20, 'responsable': 'Usuario 1'},
            {'tipo_movimiento': 'VENTA', 'cantidad': 5, 'responsable': 'Usuario 2'},
            {'tipo_movimiento': 'AJUSTE', 'cantidad': 10, 'responsable': 'Usuario 3'}
        ]
        
        for data in movimientos_data:
            self.inventory_service.create_movement(
                id_producto=self.producto_test.id_producto,
                **data
            )
        
        # Obtener movimientos
        movimientos = self.inventory_service.get_product_movements(self.producto_test.id_producto)
        
        # Verificaciones
        self.assertIsInstance(movimientos, list)
        self.assertEqual(len(movimientos), 3)
        self.assertTrue(all(isinstance(m, Movimiento) for m in movimientos))
        
        # Verificar que todos son del mismo producto
        for movimiento in movimientos:
            self.assertEqual(movimiento.id_producto, self.producto_test.id_producto)
        
        print(f"   ✅ Obtenidos {len(movimientos)} movimientos del producto")
    
    def test_get_product_movements_with_limit(self):
        """Test obtener movimientos con límite."""
        print("\n9️⃣ TEST: Movimientos con límite...")
        
        # Crear 5 movimientos
        for i in range(5):
            self.inventory_service.create_movement(
                id_producto=self.producto_test.id_producto,
                tipo_movimiento='ENTRADA',
                cantidad=10,
                responsable=f'Usuario {i+1}'
            )
        
        # Obtener con límite de 3
        movimientos = self.inventory_service.get_product_movements(
            self.producto_test.id_producto, limit=3
        )
        
        # Verificaciones
        self.assertEqual(len(movimientos), 3)
        
        print(f"   ✅ Límite aplicado correctamente: {len(movimientos)} movimientos")
    
    def test_get_all_movements(self):
        """Test obtener todos los movimientos del sistema."""
        print("\n🔟 TEST: Obtener todos los movimientos...")
        
        # Crear segundo producto para diversificar
        producto2 = self.product_service.create_product(
            nombre='Destornillador Test',
            id_categoria=self.categoria_test.id_categoria,
            stock_inicial=30
        )
        
        # Crear movimientos para ambos productos
        movimientos_data = [
            {'id_producto': self.producto_test.id_producto, 'tipo_movimiento': 'ENTRADA', 'cantidad': 20},
            {'id_producto': self.producto_test.id_producto, 'tipo_movimiento': 'VENTA', 'cantidad': 5},
            {'id_producto': producto2.id_producto, 'tipo_movimiento': 'ENTRADA', 'cantidad': 15},
            {'id_producto': producto2.id_producto, 'tipo_movimiento': 'AJUSTE', 'cantidad': 8}
        ]
        
        for data in movimientos_data:
            self.inventory_service.create_movement(
                responsable='Usuario Test',
                **data
            )
        
        # Obtener todos los movimientos
        movimientos = self.inventory_service.get_all_movements()
        
        # Verificaciones
        self.assertIsInstance(movimientos, list)
        self.assertEqual(len(movimientos), 4)
        
        # Verificar que hay movimientos de ambos productos
        productos_ids = {m.id_producto for m in movimientos}
        self.assertIn(self.producto_test.id_producto, productos_ids)
        self.assertIn(producto2.id_producto, productos_ids)
        
        print(f"   ✅ Obtenidos {len(movimientos)} movimientos totales")
    
    def test_get_all_movements_with_limit(self):
        """Test obtener todos los movimientos con límite."""
        print("\n1️⃣1️⃣ TEST: Todos los movimientos con límite...")
        
        # Crear varios movimientos
        for i in range(7):
            self.inventory_service.create_movement(
                id_producto=self.producto_test.id_producto,
                tipo_movimiento='ENTRADA',
                cantidad=10,
                responsable=f'Usuario {i+1}'
            )
        
        # Obtener con límite de 5
        movimientos = self.inventory_service.get_all_movements(limit=5)
        
        # Verificaciones
        self.assertEqual(len(movimientos), 5)
        
        print(f"   ✅ Límite aplicado correctamente: {len(movimientos)} movimientos")
    
    # ========== TESTS DE CASOS ESPECÍFICOS ==========
    
    def test_movement_date_consistency(self):
        """Test consistencia de fechas en movimientos."""
        print("\n1️⃣2️⃣ TEST: Consistencia de fechas...")
        
        # Crear movimiento y verificar fecha
        antes = datetime.now()
        
        movimiento = self.inventory_service.create_movement(
            id_producto=self.producto_test.id_producto,
            tipo_movimiento='ENTRADA',
            cantidad=10,
            responsable='Usuario Test'
        )
        
        despues = datetime.now()
        
        # Verificar que la fecha está dentro del rango esperado
        self.assertIsInstance(movimiento.fecha_movimiento, datetime)
        self.assertGreaterEqual(movimiento.fecha_movimiento, antes)
        self.assertLessEqual(movimiento.fecha_movimiento, despues)
        
        print("   ✅ Fechas de movimiento consistentes")
    
    def test_movement_with_observaciones(self):
        """Test movimiento con observaciones."""
        print("\n1️⃣3️⃣ TEST: Movimiento con observaciones...")
        
        observaciones = "Entrada por compra directa al proveedor XYZ"
        
        movimiento = self.inventory_service.create_movement(
            id_producto=self.producto_test.id_producto,
            tipo_movimiento='ENTRADA',
            cantidad=15,
            responsable='Usuario Test',
            observaciones=observaciones
        )
        
        # Verificar observaciones
        self.assertEqual(movimiento.observaciones, observaciones)
        
        print("   ✅ Observaciones guardadas correctamente")
    
    def test_movement_with_venta_id(self):
        """Test movimiento asociado a venta."""
        print("\n1️⃣4️⃣ TEST: Movimiento asociado a venta...")
        
        id_venta = 1001
        
        movimiento = self.inventory_service.create_movement(
            id_producto=self.producto_test.id_producto,
            tipo_movimiento='VENTA',
            cantidad=3,
            responsable='Vendedor Test',
            id_venta=id_venta,
            observaciones='Venta directa'
        )
        
        # Verificar asociación con venta
        self.assertEqual(movimiento.id_venta, id_venta)
        self.assertEqual(movimiento.tipo_movimiento, 'VENTA')
        
        print(f"   ✅ Movimiento asociado a venta {id_venta}")
    
    def test_responsable_trimmed(self):
        """Test que el responsable se limpia de espacios."""
        print("\n1️⃣5️⃣ TEST: Limpieza de responsable...")
        
        responsable_con_espacios = "  Usuario Test  "
        
        movimiento = self.inventory_service.create_movement(
            id_producto=self.producto_test.id_producto,
            tipo_movimiento='ENTRADA',
            cantidad=10,
            responsable=responsable_con_espacios
        )
        
        # Verificar que se limpiaron los espacios
        self.assertEqual(movimiento.responsable, "Usuario Test")
        
        print("   ✅ Espacios del responsable limpiados")


def run_inventory_service_tests():
    """Ejecutar todos los tests de InventoryService."""
    print("\n" + "="*70)
    print("🧪 EJECUTANDO TESTS BÁSICOS INVENTORYSERVICE")
    print("="*70)
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestInventoryServiceBasic)
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Resumen
    total = result.testsRun
    errors = len(result.errors)
    failures = len(result.failures)
    success = total - errors - failures
    
    print(f"\n📊 RESUMEN INVENTORYSERVICE TESTS:")
    print(f"   ✅ Exitosos: {success}/{total}")
    print(f"   ❌ Fallidos: {failures}")
    print(f"   ⚠️ Errores: {errors}")
    print(f"   📈 Tasa éxito: {(success/total)*100:.1f}%")
    
    if success == total:
        print("\n🎉 TODOS LOS TESTS INVENTORYSERVICE PASARON!")
        print("✅ InventoryService está funcionando correctamente")
    else:
        print("\n⚠️ ALGUNOS TESTS FALLARON")
        print("❌ Revisar implementación de InventoryService")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    run_inventory_service_tests()
