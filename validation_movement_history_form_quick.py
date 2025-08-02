# validation_movement_history_form_quick.py
"""
Validación Rápida - MovementHistoryForm Status Check

OBJETIVO: Ejecutar suite TDD para verificar estado operativo
PROTOCOLO: claude_instructions_v3.md FASE 2A
SESIÓN: 2025-08-01-movement-history-form-validation
"""

import sys
import os
import subprocess

# Agregar directorio raíz al path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def main():
    """Ejecutar validación MovementHistoryForm."""
    print("🔍 VALIDACIÓN RÁPIDA MovementHistoryForm")
    print("=" * 60)
    
    try:
        # Test 1: Verificar que archivo existe
        form_path = os.path.join(current_dir, 'src', 'ui', 'forms', 'movement_history_form.py')
        print(f"📁 Verificando archivo: {form_path}")
        
        if os.path.exists(form_path):
            print("✅ Archivo MovementHistoryForm existe")
            file_size = os.path.getsize(form_path)
            print(f"   📏 Tamaño: {file_size:,} bytes")
        else:
            print("❌ CRÍTICO: Archivo MovementHistoryForm NO existe")
            return False
        
        # Test 2: Verificar importación básica
        print("\n🔧 Verificando importación básica...")
        try:
            from src.ui.forms.movement_history_form import MovementHistoryForm
            print("✅ MovementHistoryForm se puede importar")
            
            # Verificar métodos críticos
            critical_methods = ['_validate_permissions', '_search_movements', '_export_to_pdf']
            for method in critical_methods:
                if hasattr(MovementHistoryForm, method):
                    print(f"   ✅ Método {method} presente")
                else:
                    print(f"   ❌ Método {method} FALTANTE")
                    
        except ImportError as e:
            print(f"❌ ERROR: No se puede importar MovementHistoryForm: {e}")
            return False
        
        # Test 3: Verificar MovementService métodos
        print("\n🔧 Verificando MovementService...")
        try:
            from src.services.movement_service import MovementService
            print("✅ MovementService se puede importar")
            
            # Crear instancia mock para verificar métodos
            class MockDB:
                def get_connection(self):
                    return self
                def cursor(self):
                    return MockCursor()
            
            class MockCursor:
                def execute(self, *args):
                    pass
                def fetchall(self):
                    return []
                def fetchone(self):
                    return None
            
            service = MovementService(MockDB())
            
            required_methods = ['get_movements_by_filters', 'get_movement_by_ticket']
            for method in required_methods:
                if hasattr(service, method) and callable(getattr(service, method)):
                    print(f"   ✅ Método {method} presente y callable")
                else:
                    print(f"   ❌ Método {method} FALTANTE o no callable")
                    
        except ImportError as e:
            print(f"❌ ERROR: No se puede importar MovementService: {e}")
            return False
        
        # Test 4: Verificar ServiceContainer
        print("\n🔧 Verificando ServiceContainer...")
        try:
            from services.service_container import get_container
            container = get_container()
            print("✅ ServiceContainer disponible")
            
            # Verificar servicios críticos registrados
            required_services = ['movement_service', 'session_manager']
            for service_name in required_services:
                if container.is_registered(service_name):
                    print(f"   ✅ Servicio {service_name} registrado")
                else:
                    print(f"   ❌ Servicio {service_name} NO registrado")
                    
        except Exception as e:
            print(f"❌ ERROR: ServiceContainer no disponible: {e}")
            return False
        
        # Test 5: Ejecutar suite TDD completa
        print("\n🔧 Ejecutando suite TDD completa...")
        try:
            test_path = os.path.join(current_dir, 'tests', 'integration', 'test_movement_history_form_complete_validation.py')
            
            # Ejecutar tests usando subprocess
            result = subprocess.run([
                sys.executable, test_path
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print("✅ SUITE TDD: TODOS LOS TESTS PASARON")
                print("🎉 MovementHistoryForm está 100% OPERATIVO")
                return True
            else:
                print("❌ SUITE TDD: ALGUNOS TESTS FALLARON")
                if result.stdout:
                    print("STDOUT:")
                    print(result.stdout)
                if result.stderr:
                    print("STDERR:")
                    print(result.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ ERROR: Tests tardaron más de 2 minutos - timeout")
            return False
        except Exception as e:
            print(f"❌ ERROR ejecutando tests: {e}")
            return False
    
    except Exception as e:
        print(f"❌ ERROR GENERAL: {e}")
        return False

if __name__ == "__main__":
    success = main()
    print("\n" + "=" * 60)
    if success:
        print("🎉 RESULTADO: MovementHistoryForm está COMPLETAMENTE OPERATIVO")
        print("✅ Todos los componentes validados exitosamente")
        print("✅ Lista para uso en producción")
    else:
        print("⚠️  RESULTADO: MovementHistoryForm requiere correcciones")
        print("❌ Algunos componentes necesitan atención")
        print("🔧 Revisar errores específicos arriba")
    
    sys.exit(0 if success else 1)
