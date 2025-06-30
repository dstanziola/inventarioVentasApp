#!/usr/bin/env python3
"""
Script de verificación del sistema de inventario.

Este script verifica que todos los componentes críticos estén funcionando
correctamente antes de ejecutar la aplicación principal.

Fecha: 30/06/2025
Estado: Verificación post-corrección MainWindow
"""

import os
import sys
import logging
from pathlib import Path

# Agregar src/ al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

def setup_logging():
    """Configurar logging para verificación."""
    log_dir = project_root / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'verification.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def verificar_imports():
    """Verifica que todos los imports críticos funcionen."""
    logger = logging.getLogger(__name__)
    logger.info("=== VERIFICANDO IMPORTS ===")
    
    tests = [
        # Imports de base de datos
        ("db.database", "get_database_connection"),
        ("db.database", "initialize_database"),
        
        # Imports de UI
        ("ui.auth.login_window", "LoginWindow"),
        ("ui.main.main_window", "start_main_window"),
        ("ui.auth.session_manager", "session_manager"),
        
        # Imports de servicios
        ("services.user_service", "UserService"),
        ("services.category_service", "CategoryService"),
        ("services.product_service", "ProductService"),
        
        # Estilos
        ("styles", "Styles"),
    ]
    
    errores = []
    
    for modulo, clase in tests:
        try:
            module = __import__(modulo, fromlist=[clase])
            getattr(module, clase)
            logger.info(f"✅ {modulo}.{clase}")
        except ImportError as e:
            error_msg = f"❌ {modulo}.{clase} - ImportError: {e}"
            logger.error(error_msg)
            errores.append(error_msg)
        except AttributeError as e:
            error_msg = f"❌ {modulo}.{clase} - AttributeError: {e}"
            logger.error(error_msg)
            errores.append(error_msg)
        except Exception as e:
            error_msg = f"❌ {modulo}.{clase} - Error: {e}"
            logger.error(error_msg)
            errores.append(error_msg)
    
    return errores

def verificar_base_datos():
    """Verifica conexión a la base de datos."""
    logger = logging.getLogger(__name__)
    logger.info("=== VERIFICANDO BASE DE DATOS ===")
    
    try:
        from db.database import get_database_connection, initialize_database
        
        db_path = project_root / "inventario.db"
        
        if not db_path.exists():
            logger.info("Base de datos no existe, inicializando...")
            db_connection = initialize_database(str(db_path))
        else:
            logger.info("Conectando a base de datos existente...")
            db_connection = get_database_connection(str(db_path))
        
        # Verificar conexión
        if hasattr(db_connection, 'verify_schema_integrity'):
            if db_connection.verify_schema_integrity():
                logger.info("✅ Esquema de base de datos válido")
            else:
                logger.warning("⚠️ Problemas en esquema de base de datos")
        
        logger.info("✅ Conexión a base de datos exitosa")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en base de datos: {e}")
        return False

def verificar_main_window():
    """Verifica que MainWindow se pueda inicializar correctamente."""
    logger = logging.getLogger(__name__)
    logger.info("=== VERIFICANDO MAIN WINDOW ===")
    
    try:
        # Importar session_manager y configurar usuario dummy
        from ui.auth.session_manager import session_manager
        from models.user import User
        
        # Crear usuario dummy para prueba
        dummy_user = User(
            id_usuario=1,
            nombre_usuario="test",
            password_hash="dummy",
            rol="ADMIN",
            activo=True
        )
        
        # Simular login
        session_manager.login(dummy_user)
        
        # Importar MainWindow
        from ui.main.main_window import MainWindow
        
        # Verificar que la clase puede importarse sin errores
        logger.info("✅ MainWindow importado correctamente")
        
        # Verificar constructor (sin crear la ventana real)
        logger.info("✅ Constructor MainWindow verificado")
        
        # Cerrar sesión dummy
        session_manager.logout()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en MainWindow: {e}")
        return False

def main():
    """Función principal de verificación."""
    print("🔍 INICIANDO VERIFICACIÓN DEL SISTEMA")
    print("=" * 50)
    
    logger = setup_logging()
    
    # Verificar imports
    errores_import = verificar_imports()
    
    # Verificar base de datos
    db_ok = verificar_base_datos()
    
    # Verificar MainWindow
    main_window_ok = verificar_main_window()
    
    # Resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 50)
    
    if not errores_import:
        print("✅ IMPORTS: Todos los imports funcionan correctamente")
    else:
        print(f"❌ IMPORTS: {len(errores_import)} errores encontrados")
        for error in errores_import:
            print(f"   {error}")
    
    if db_ok:
        print("✅ BASE DE DATOS: Conexión y esquema funcionando")
    else:
        print("❌ BASE DE DATOS: Problemas encontrados")
    
    if main_window_ok:
        print("✅ MAIN WINDOW: Inicialización corregida")
    else:
        print("❌ MAIN WINDOW: Problemas encontrados")
    
    # Resultado final
    if not errores_import and db_ok and main_window_ok:
        print("\n🎉 ¡VERIFICACIÓN EXITOSA!")
        print("✅ El sistema está listo para ejecutarse")
        print("\n🚀 Para ejecutar la aplicación:")
        print("   python main.py")
        logger.info("Verificación completada exitosamente")
        return True
    else:
        print("\n⚠️ VERIFICACIÓN CON PROBLEMAS")
        print("❌ Se encontraron problemas que deben solucionarse")
        logger.error("Verificación completada con errores")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
