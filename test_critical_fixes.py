"""
Test crítico para validar correcciones de errores identificados.
Protocolo TDD: Test primero, luego implementar las correcciones.

Errores a corregir:
1. CategoryService.__init__() missing db_connection parameter
2. Database: no such column: activo
3. BarcodeService missing is_scanner_available method
4. hidapi dependency (optional)
"""

import unittest
import sys
import os

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from db.database import get_database_connection, initialize_database
from services.category_service import CategoryService
from services.barcode_service import BarcodeService


class TestCriticalFixes(unittest.TestCase):
    """
    Tests para validar que las correcciones funcionan correctamente.
    """
    
    def setUp(self):
        """Configurar base de datos de prueba."""
        self.test_db_path = "test_critical_fixes.db"
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        
        self.db_connection = initialize_database(self.test_db_path)
        
    def tearDown(self):
        """Limpiar después de cada test."""
        if hasattr(self, 'db_connection'):
            self.db_connection.close()
        
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_category_service_initialization(self):
        """Test que CategoryService se inicialice correctamente con db_connection."""
        # Este test debe pasar después de la corrección
        category_service = CategoryService(self.db_connection)
        
        # Verificar que se inicializó correctamente
        self.assertIsNotNone(category_service.db)
        self.assertEqual(category_service.db, self.db_connection)
    
    def test_database_has_activo_column(self):
        """Test que la tabla categorias tenga la columna 'activo'."""
        cursor = self.db_connection.get_connection().cursor()
        
        # Verificar que la columna activo existe
        cursor.execute("PRAGMA table_info(categorias)")
        columns = cursor.fetchall()
        
        column_names = [column[1] for column in columns]
        self.assertIn('activo', column_names, "La columna 'activo' debe existir en la tabla categorias")
    
    def test_category_service_crud_operations(self):
        """Test que CategoryService funcione correctamente con la columna activo."""
        category_service = CategoryService(self.db_connection)
        
        # Crear categoría
        categoria = category_service.create_category(
            nombre="Categoría Test",
            tipo="MATERIAL",
            descripcion="Descripción test",
            activo=True
        )
        
        self.assertIsNotNone(categoria)
        self.assertEqual(categoria.nombre, "Categoría Test")
        self.assertEqual(categoria.tipo, "MATERIAL")
        self.assertTrue(categoria.activo)
        
        # Leer categoría
        categoria_leida = category_service.get_category_by_id(categoria.id_categoria)
        self.assertIsNotNone(categoria_leida)
        self.assertEqual(categoria_leida.nombre, "Categoría Test")
        self.assertTrue(categoria_leida.activo)
        
        # Listar categorías activas
        categorias_activas = category_service.get_active_categories()
        self.assertGreater(len(categorias_activas), 0)
        
        # Verificar que todas las categorías activas tienen activo=True
        for cat in categorias_activas:
            self.assertTrue(cat.activo)
    
    def test_barcode_service_has_scanner_available_method(self):
        """Test que BarcodeService tenga el método is_scanner_available."""
        barcode_service = BarcodeService()
        
        # Verificar que el método existe
        self.assertTrue(hasattr(barcode_service, 'is_scanner_available'))
        
        # Verificar que el método es callable
        self.assertTrue(callable(getattr(barcode_service, 'is_scanner_available')))
        
        # Verificar que retorna un boolean
        result = barcode_service.is_scanner_available()
        self.assertIsInstance(result, bool)
    
    def test_barcode_service_initialization(self):
        """Test que BarcodeService se inicialice correctamente."""
        barcode_service = BarcodeService()
        
        # Verificar que se inicializó correctamente
        self.assertIsNotNone(barcode_service.logger)
        self.assertIsNotNone(barcode_service.device_manager)
        
        # Verificar que los métodos principales existen
        self.assertTrue(hasattr(barcode_service, 'is_connected'))
        self.assertTrue(hasattr(barcode_service, 'read_code'))
        self.assertTrue(hasattr(barcode_service, 'validate_barcode'))
    
    def test_database_integrity_after_fixes(self):
        """Test que la base de datos mantenga integridad después de las correcciones."""
        # Verificar que las tablas principales existen
        cursor = self.db_connection.get_connection().cursor()
        
        expected_tables = [
            'usuarios', 'categorias', 'productos', 'clientes', 
            'ventas', 'detalle_ventas', 'movimientos'
        ]
        
        for table in expected_tables:
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table,)
            )
            result = cursor.fetchone()
            self.assertIsNotNone(result, f"La tabla {table} debe existir")
        
        # Verificar integridad de foreign keys
        cursor.execute("PRAGMA foreign_key_check")
        foreign_key_errors = cursor.fetchall()
        self.assertEqual(len(foreign_key_errors), 0, "No debe haber errores de foreign keys")
    
    def test_integration_category_service_with_database(self):
        """Test de integración completo CategoryService con base de datos."""
        category_service = CategoryService(self.db_connection)
        
        # Crear múltiples categorías
        categoria1 = category_service.create_category("Test 1", "MATERIAL", "Desc 1", True)
        categoria2 = category_service.create_category("Test 2", "SERVICIO", "Desc 2", True)
        categoria3 = category_service.create_category("Test 3", "MATERIAL", "Desc 3", False)
        
        # Verificar que se crearon correctamente
        self.assertIsNotNone(categoria1)
        self.assertIsNotNone(categoria2)
        self.assertIsNotNone(categoria3)
        
        # Verificar categorías activas
        categorias_activas = category_service.get_active_categories()
        active_names = [cat.nombre for cat in categorias_activas]
        
        self.assertIn("Test 1", active_names)
        self.assertIn("Test 2", active_names)
        self.assertNotIn("Test 3", active_names)  # Esta está inactiva
        
        # Verificar todas las categorías
        todas_categorias = category_service.get_all_categories()
        all_names = [cat.nombre for cat in todas_categorias]
        
        self.assertIn("Test 1", all_names)
        self.assertIn("Test 2", all_names)
        self.assertIn("Test 3", all_names)


if __name__ == '__main__':
    unittest.main()
