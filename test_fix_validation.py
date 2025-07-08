"""
Script de prueba rápida para validar correcciones del Service Container.

Este script intenta ejecutar el setup del Service Container para verificar
que las correcciones de rutas de importación funcionan correctamente.
"""

import sys
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_service_container_fix():
    """Probar las correcciones del Service Container."""
    try:
        logger.info("=== PRUEBA DE CORRECCIÓN SERVICE CONTAINER ===")
        
        # Agregar src/ al path (simulando main.py)
        project_root = os.path.dirname(__file__)
        src_path = os.path.join(project_root, 'src')
        sys.path.insert(0, src_path)
        
        logger.info(f"Path agregado: {src_path}")
        
        # Intentar importar setup_default_container (corregido)
        logger.info("1. Importando setup_default_container...")
        from services.service_container import setup_default_container
        logger.info("✅ Import exitoso")
        
        # Intentar ejecutar setup_default_container
        logger.info("2. Ejecutando setup_default_container...")
        container = setup_default_container()
        logger.info("✅ Función ejecutada exitosamente")
        
        # Verificar servicios registrados
        logger.info("3. Verificando servicios registrados...")
        services = container.get_registered_services()
        logger.info(f"✅ {len(services)} servicios registrados: {services}")
        
        # Verificar servicio 'database' específicamente
        logger.info("4. Verificando servicio 'database'...")
        if container.is_registered('database'):
            logger.info("✅ Servicio 'database' está registrado")
        else:
            logger.error("❌ Servicio 'database' NO está registrado")
            return False
        
        # Intentar obtener estadísticas
        logger.info("5. Obteniendo estadísticas del container...")
        stats = container.get_container_stats()
        logger.info(f"✅ Stats obtenidas: {stats['total_registered']} servicios")
        
        # Cleanup
        logger.info("6. Limpiando container...")
        container.cleanup()
        logger.info("✅ Cleanup completado")
        
        logger.info("=== ✅ TODAS LAS PRUEBAS PASARON ===")
        return True
        
    except ImportError as e:
        logger.error(f"❌ Error de importación: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error durante prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_service_container_fix()
    sys.exit(0 if success else 1)
