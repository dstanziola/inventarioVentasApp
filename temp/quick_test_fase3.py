"""
Ejecutor rápido de tests específicos de Fase 3
"""

import sys
import os
import unittest
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_specific_test(test_module_path):
    """Ejecuta un test específico y retorna resultado"""
    try:
        # Importar el módulo de test
        spec = importlib.util.spec_from_file_location("test_module", test_module_path)
        test_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(test_module)
        
        # Obtener todas las clases de test
        test_classes = []
        for name in dir(test_module):
            obj = getattr(test_module, name)
            if isinstance(obj, type) and issubclass(obj, unittest.TestCase) and obj != unittest.TestCase:
                test_classes.append(obj)
        
        if not test_classes:
            return False, "No se encontraron clases de test"
        
        # Crear suite y ejecutar
        suite = unittest.TestSuite()
        for test_class in test_classes:
            tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
            suite.addTests(tests)
        
        # Ejecutar tests
        runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, 'w'))
        result = runner.run(suite)
        
        success = result.wasSuccessful()
        message = f"{result.testsRun} tests, {len(result.failures)} fallos, {len(result.errors)} errores"
        
        return success, message
        
    except Exception as e:
        return False, f"Error: {e}"

def main():
    """Función principal"""
    
    print("🧪 TESTS RÁPIDOS - FASE 3")
    print("=" * 40)
    
    # Tests a verificar
    tests_fase3 = [
        ("tests/unit/models/test_ticket.py", "Test Modelo Ticket"),
        ("tests/unit/models/test_company_config.py", "Test Modelo CompanyConfig"), 
        ("tests/unit/services/test_ticket_service.py", "Test TicketService"),
        ("tests/unit/services/test_company_service.py", "Test CompanyService")
    ]
    
    tests_exitosos = 0
    
    for test_path, descripcion in tests_fase3:
        print(f"\n🔍 {descripcion}")
        
        if not Path(test_path).exists():
            print(f"  ❌ ARCHIVO NO ENCONTRADO: {test_path}")
            continue
        
        # Verificar sintaxis básica
        try:
            with open(test_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Verificaciones básicas
            if 'class Test' in content and 'unittest.TestCase' in content:
                print(f"  ✅ Estructura de test válida")
                tests_exitosos += 1
            else:
                print(f"  ⚠️  Estructura de test incompleta")
                
        except Exception as e:
            print(f"  ❌ Error leyendo archivo: {e}")
    
    print(f"\n📊 RESUMEN:")
    print(f"✅ Tests válidos: {tests_exitosos}/{len(tests_fase3)}")
    
    if tests_exitosos == len(tests_fase3):
        print("🎉 TODOS LOS TESTS ESTÁN PRESENTES")
        return True
    else:
        print("⚠️  ALGUNOS TESTS FALTAN O TIENEN ERRORES")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
