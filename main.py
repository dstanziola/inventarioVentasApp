"""
Punto de entrada principal para el sistema de gestión de inventario.

Fecha: 11/05/2025 22:20:00
Ruta: D:/inventory_app/main.py
"""
import os
import sys
import tkinter as tk
import logging
import configparser
from tkinter import messagebox, ttk

# Configurar logging
logging.basicConfig(
    filename='eventos.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importar módulos necesarios
try:
    from src.db.database_connection import DatabaseConnection
    from src.ui.main_window import MainWindow
    from src.utils.directory_utils import ensure_app_directories
    from styles import Styles
    
    # Asegurar que los directorios de componentes existan
    components_dir = os.path.join('src', 'ui', 'components')
    if not os.path.exists(components_dir):
        os.makedirs(components_dir)
        logger.info(f"Directorio de componentes creado: {components_dir}")
    
    logger.info("Módulos importados correctamente")
except ImportError as e:
    logger.critical(f"Error al importar módulos: {e}")
    messagebox.showerror("Error", f"Error al importar módulos: {e}")
    exit(1)

def setup_configuration():
    """
    Carga la configuración del programa desde un archivo config.ini.
    :return: Diccionario con la configuración.
    """
    config = configparser.ConfigParser()
    
    # Verificar que existe el directorio config
    if not os.path.exists('config'):
        logger.info("Creando directorio 'config'...")
        os.makedirs('config')
        
    # Verificar que existe config.ini
    config_path = 'config/config.ini'
    if not os.path.exists(config_path):
        logger.warning("Archivo config.ini no encontrado. Usando valores por defecto.")
        # Crear config.ini con valores por defecto
        config['database'] = {
            'db_type': 'sqlite',
            'db_name': 'inventario.db',
            'db_host': 'localhost',
            'db_user': 'root',
            'db_password': ''
        }
        config['paths'] = {
            'reports': './data/reports/'
        }
        config['monetary'] = {
            'currency_symbol': 'B/.',
            'decimal_places': '2',
            'use_locale': 'True'
        }
        
        with open(config_path, 'w') as configfile:
            config.write(configfile)
            logger.info(f"Creado archivo de configuración: {config_path}")
    else:
        config.read(config_path)

    # Configuración de la base de datos
    db_config = {
        'db_type': config.get('database', 'db_type', fallback='sqlite'),
        'db_name': config.get('database', 'db_name', fallback='inventario.db'),
        'db_host': config.get('database', 'db_host', fallback='localhost'),
        'db_user': config.get('database', 'db_user', fallback='root'),
        'db_password': config.get('database', 'db_password', fallback='')
    }
    
    # Configuración monetaria
    monetary_config = {
        'currency_symbol': config.get('monetary', 'currency_symbol', fallback='B/.'),
        'decimal_places': config.getint('monetary', 'decimal_places', fallback=2),
        'use_locale': config.getboolean('monetary', 'use_locale', fallback=True)
    }

    return db_config, monetary_config

def main():
    """
    Función principal que inicia la aplicación.
    """
    try:
        # Asegurar que existan los directorios necesarios
        directories = ensure_app_directories()
        logger.info("Directorios verificados")
        
        # Cargar configuración
        db_config, monetary_config = setup_configuration()
        logger.info("Configuración cargada")
        
        # Inicializar conexión a la base de datos
        db_connection = DatabaseConnection()
        db_connection.connect()
        db_connection.create_tables()
        logger.info("Conexión a la base de datos establecida")
        
        # Crear ventana principal
        root = tk.Tk()
        
        # Aplicar estilo
        style = ttk.Style()
        style.theme_use("clam")  # ← Cambia a un tema más configurable
        Styles.configure_ttk_styles(style)
        
        # Mostrar ventana principal
        app = MainWindow(root, db_connection)
        logger.info("Ventana principal inicializada")
        
        # Iniciar el bucle principal
        root.mainloop()
        
        # Cerrar conexión a la base de datos al salir
        db_connection.disconnect()
        logger.info("Aplicación finalizada correctamente")
        
    except Exception as e:
        logger.critical(f"Error al iniciar la aplicación: {e}", exc_info=True)
        if 'root' in locals() and isinstance(root, tk.Tk):
            messagebox.showerror("Error", f"Error al iniciar la aplicación: {e}")
        else:
            print(f"Error al iniciar la aplicación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()