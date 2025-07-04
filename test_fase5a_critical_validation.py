#!/usr/bin/env python3
"""
Test de validación crítica para FASE 5A
Sistema de Inventario Copy Point S.A.

RESPONSABILIDAD:
- Validar que todos los módulos críticos estén correctamente configurados
- Verificar que los imports funcionen correctamente
- Validar configuración de pytest
- Asegurar que las correcciones se aplicaron correctamente

PROTOCOLO:
- TDD: Test escrito ANTES de ejecutar correcciones
- Cobertura: Validar aspectos críticos identificados
- Atomicidad: Test debe validar un problema específico
"""

import pytest
import sys
import os
import importlib
from pathlib import Path
from typing import List, Dict, Any

# Agregar proyecto al path para imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class TestFase5ACriticalValidation:
    """Test crítico para validar correcciones FASE 5A."""
    
    def setup_method(self):
        """Setup para cada test."""
        self.project_root = Path(__file__).parent
        self.src_path = self.project_root / "src"
        self.utils_path = self.src_path / "utils"
        self.helpers_path = self.src_path / "helpers"
    
    def test_01_validation_helper_exists_and_importable(self):
        """Test CRÍTICO 1: validation_helper debe existir y ser importable."""
        # Verificar que existe en alguna ubicación válida
        validation_helper_utils = self.utils_path / "validation_helper.py"
        validation_helper_helpers = self.helpers_path / "validation_helper.py"
        
        assert (validation_helper_utils.exists() or validation_helper_helpers.exists()), \
            "validation_helper.py debe existir en src/utils/ o src/helpers/"
        
        # Probar import desde helpers (ubicación original)
        try:
            from src.helpers.validation_helper import ValidationHelper
            helper = ValidationHelper()
            assert hasattr(helper, 'validate_product_data'), \
                "ValidationHelper debe tener método validate_product_data"
            print("✅ validation_helper importable desde helpers")
        except ImportError:
            pytest.fail("No se puede importar ValidationHelper desde helpers")
    
    def test_02_logging_helper_exists_and_importable(self):
        """Test CRÍTICO 2: logging_helper debe existir y ser importable."""
        # Verificar que existe en alguna ubicación válida
        logging_helper_utils = self.utils_path / "logging_helper.py"
        logging_helper_helpers = self.helpers_path / "logging_helper.py"
        
        assert (logging_helper_utils.exists() or logging_helper_helpers.exists()), \
            "logging_helper.py debe existir en src/utils/ o src/helpers/"
        
        # Probar import desde helpers (ubicación original)
        try:
            from src.helpers.logging_helper import LoggingHelper
            assert hasattr(LoggingHelper, 'get_service_logger'), \
                "LoggingHelper debe tener método get_service_logger"
            print("✅ logging_helper importable desde helpers")
        except ImportError:
            pytest.fail("No se puede importar LoggingHelper desde helpers")
    
    def test_03_database_helper_importable(self):
        """Test CRÍTICO 3: database_helper debe ser importable."""
        try:
            from src.utils.database_helper import DatabaseHelper
            # Verificar que tiene métodos críticos
            assert hasattr(DatabaseHelper, 'safe_execute'), \
                "DatabaseHelper debe tener método safe_execute"
            print("✅ database_helper importable correctamente")
        except ImportError as e:
            pytest.fail(f"No se puede importar DatabaseHelper: {e}")
    
    def test_04_pytest_configuration_valid(self):
        """Test CRÍTICO 4: pytest.ini debe estar correctamente configurado."""
        pytest_ini_path = self.project_root / "pytest.ini"
        
        assert pytest_ini_path.exists(), "pytest.ini debe existir"
        
        with open(pytest_ini_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar formato correcto (no [tool:pytest])
        assert '[pytest]' in content, "pytest.ini debe usar [pytest] no [tool:pytest]"
        assert '[tool:pytest]' not in content, "pytest.ini no debe usar [tool:pytest]"
        
        # Verificar configuraciones críticas
        assert 'testpaths = tests' in content, "pytest.ini debe especificar testpaths"
        assert 'python_files = test_*.py' in content, "pytest.ini debe especificar python_files"
        
        print("✅ pytest.ini configurado correctamente")
    
    def test_05_product_service_imports_correctly(self):
        """Test CRÍTICO 5: ProductService debe importar helpers correctamente."""
        try:
            # Test import del ProductService
            from src.services.product_service import ProductService
            
            # Verificar que el servicio se puede instanciar
            # (sin conexión real a BD para el test)
            assert ProductService is not None, "ProductService debe ser importable"
            print("✅ ProductService imports funcionando")
            
        except ImportError as e:
            # Si hay error de import, capturar detalles
            pytest.fail(f"Error importando ProductService: {e}")
    
    def test_06_critical_services_importable(self):
        """Test CRÍTICO 6: Servicios críticos deben ser importables."""
        critical_services = [
            'src.services.product_service',
            'src.services.category_service', 
            'src.services.client_service',
            'src.services.user_service',
            'src.services.sales_service'
        ]
        
        import_errors = []
        
        for service_module in critical_services:
            try:
                importlib.import_module(service_module)
                print(f"✅ {service_module} importable")
            except ImportError as e:
                import_errors.append(f"{service_module}: {e}")
        
        if import_errors:
            pytest.fail(f"Errores de import en servicios críticos:\n" + 
                       "\n".join(import_errors))
    
    def test_07_database_connection_import_correct(self):
        """Test CRÍTICO 7: DatabaseConnection debe importarse correctamente (no doble)."""
        try:
            from src.db.database import DatabaseConnection
            
            # Verificar que es la clase correcta
            assert hasattr(DatabaseConnection, 'get_connection'), \
                "DatabaseConnection debe tener método get_connection"
            
            print("✅ DatabaseConnection import correcto")
            
        except ImportError as e:
            pytest.fail(f"Error importando DatabaseConnection: {e}")
    
    def test_08_models_importable(self):
        """Test CRÍTICO 8: Modelos críticos deben ser importables."""
        critical_models = [
            'src.models.producto',
            'src.models.categoria',
            'src.models.cliente',
            'src.models.usuario',
            'src.models.venta'
        ]
        
        import_errors = []
        
        for model_module in critical_models:
            try:
                importlib.import_module(model_module)
                print(f"✅ {model_module} importable")
            except ImportError as e:
                import_errors.append(f"{model_module}: {e}")
        
        if import_errors:
            pytest.fail(f"Errores de import en modelos críticos:\n" + 
                       "\n".join(import_errors))
    
    def test_09_ui_forms_importable(self):
        """Test CRÍTICO 9: Formularios UI críticos deben ser importables."""
        critical_forms = [
            'src.ui.forms.product_form',
            'src.ui.forms.category_form',
            'src.ui.forms.client_form',
            'src.ui.forms.sales_form',
            'src.ui.main.main_window'
        ]
        
        import_errors = []
        
        for form_module in critical_forms:
            try:
                importlib.import_module(form_module)
                print(f"✅ {form_module} importable")
            except ImportError as e:
                import_errors.append(f"{form_module}: {e}")
        
        if import_errors:
            pytest.fail(f"Errores de import en formularios críticos:\n" + 
                       "\n".join(import_errors))
    
    def test_10_project_structure_valid(self):
        """Test CRÍTICO 10: Estructura de proyecto debe ser válida."""
        required_dirs = [
            self.src_path,
            self.src_path / "db",
            self.src_path / "models", 
            self.src_path / "services",
            self.src_path / "ui",
            self.src_path / "utils",
            self.src_path / "helpers",
            self.project_root / "tests"
        ]
        
        missing_dirs = []
        for dir_path in required_dirs:
            if not dir_path.exists():
                missing_dirs.append(str(dir_path))
        
        assert not missing_dirs, f"Directorios faltantes: {missing_dirs}"
        print("✅ Estructura de proyecto válida")
    
    def test_11_compatibility_helpers_vs_utils(self):
        """Test CRÍTICO 11: Verificar compatibilidad entre helpers y utils."""
        # Si existen ambas versiones, deben ser funcionalmente equivalentes
        validation_helper_utils = self.utils_path / "validation_helper.py"
        validation_helper_helpers = self.helpers_path / "validation_helper.py"
        
        if validation_helper_utils.exists() and validation_helper_helpers.exists():
            # Importar ambas versiones
            try:
                from src.utils.validation_helper import ValidationHelper as ValidationHelper_Utils
                from src.helpers.validation_helper import ValidationHelper as ValidationHelper_Helpers
                
                # Verificar que ambas tienen los métodos críticos
                critical_methods = ['validate_product_data', 'validate_category_data']
                
                for method in critical_methods:
                    assert hasattr(ValidationHelper_Utils, method), \
                        f"ValidationHelper de utils debe tener {method}"
                    assert hasattr(ValidationHelper_Helpers, method), \
                        f"ValidationHelper de helpers debe tener {method}"
                
                print("✅ Compatibilidad entre helpers y utils validada")
                
            except ImportError as e:
                pytest.fail(f"Error de compatibilidad helpers/utils: {e}")
    
    def test_12_system_ready_for_testing(self):
        """Test CRÍTICO 12: Sistema debe estar listo para testing completo."""
        
        # Verificar que se pueden hacer imports básicos sin errores
        basic_imports = [
            'src.db.database',
            'src.utils.database_helper', 
            'src.helpers.validation_helper',
            'src.helpers.logging_helper'
        ]
        
        for module_name in basic_imports:
            try:
                importlib.import_module(module_name)
            except ImportError as e:
                pytest.fail(f"Sistema no listo: Error importando {module_name}: {e}")
        
        # Verificar que pytest puede descubrir tests
        tests_dir = self.project_root / "tests"
        test_files = list(tests_dir.glob("test_*.py"))
        
        assert len(test_files) > 0, "Debe haber archivos de test disponibles"
        
        print(f"✅ Sistema listo para testing - {len(test_files)} archivos de test encontrados")


if __name__ == "__main__":
    # Ejecutar tests críticos directamente
    pytest.main([__file__, "-v", "--tb=short"])
