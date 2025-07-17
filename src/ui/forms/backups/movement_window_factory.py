"""
Factory para crear ventana de movimientos de inventario.

Esta función factory proporciona compatibilidad con el patrón de otros
formularios del sistema, encapsulando MovementForm en una ventana Toplevel.

Autor: Sistema de Inventario Copy Point S.A.
Versión: 1.0.0
Fecha: Julio 2025
"""

import tkinter as tk
from tkinter import messagebox
import logging
from ui.forms.movement_form import MovementForm

# Configurar logging
logger = logging.getLogger(__name__)

def create_movement_window(parent, db_connection):
    """
    Crear ventana de movimientos siguiendo el patrón de otros formularios.
    
    Esta función wrapper encapsula MovementForm en una ventana Toplevel
    para mantener consistencia con otros formularios del sistema.
    
    Args:
        parent: Ventana padre
        db_connection: Conexión a base de datos
        
    Returns:
        tk.Toplevel: Ventana de movimientos creada
        
    Raises:
        PermissionError: Si el usuario no tiene permisos de administrador
    """
    try:
        # Crear ventana Toplevel
        movement_window = tk.Toplevel(parent)
        movement_window.title("Gestión de Movimientos de Inventario")
        movement_window.geometry("1200x800")
        movement_window.transient(parent)
        movement_window.grab_set()
        
        # Centrar ventana
        movement_window.update_idletasks()
        width = 1200
        height = 800
        x = (movement_window.winfo_screenwidth() // 2) - (width // 2)
        y = (movement_window.winfo_screenheight() // 2) - (height // 2)
        movement_window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Crear instancia de MovementForm dentro de la ventana
        movement_form = MovementForm(movement_window, db_connection)
        
        # Configurar protocolo de cierre
        def on_closing():
            if messagebox.askokcancel("Cerrar", "¿Está seguro que desea cerrar la ventana de movimientos?"):
                try:
                    movement_window.grab_release()
                    movement_window.destroy()
                    logger.info("Ventana de movimientos cerrada exitosamente")
                except Exception as e:
                    logger.error(f"Error al cerrar ventana de movimientos: {e}")
        
        movement_window.protocol("WM_DELETE_WINDOW", on_closing)
        
        logger.info("Ventana de movimientos creada exitosamente")
        return movement_window
        
    except PermissionError:
        # Re-lanzar errores de permisos sin modificar
        raise
    except Exception as e:
        logger.error(f"Error creando ventana de movimientos: {e}")
        messagebox.showerror("Error", f"No se pudo crear la ventana de movimientos: {e}")
        return None
