import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

print("Verificando correcciones...")

# Test 1: Verificar que CompanyService se puede importar
try:
    from services.company_service import CompanyService
    print("✅ CompanyService importado exitosamente")
except Exception as e:
    print(f"❌ Error importando CompanyService: {e}")

# Test 2: Verificar constructor
try:
    from unittest.mock import Mock
    mock_db = Mock()
    service = CompanyService(mock_db)
    print("✅ CompanyService constructor funciona")
except Exception as e:
    print(f"❌ Error en constructor: {e}")

# Test 3: Verificar Service Container
try:
    from services.service_container import setup_default_container
    container = setup_default_container()
    if container.is_registered('company_service'):
        print("✅ company_service registrado en container")
    else:
        print("❌ company_service NO registrado")
except Exception as e:
    print(f"❌ Error en container: {e}")

print("Verificación completada.")
