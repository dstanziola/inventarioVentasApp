"""
Ventana de autenticación de usuarios.

Esta clase implementa la interfaz gráfica para el login de usuarios,
incluyendo validación de credenciales y manejo de errores.

FUNCIONALIDADES:
- Formulario de login con usuario y contraseña
- Validación en tiempo real
- Integración con servicio de usuarios
- Manejo de errores de autenticación
- Redirección a ventana principal tras login exitoso
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional
import logging

from db.database import get_database_connection
from services.user_service import UserService
from .session_manager import session_manager


class LoginWindow:
    """Ventana de autenticación de usuarios."""
    
    def __init__(self, on_login_success: Callable[[], None]):
        """
        Inicializa la ventana de login.
        
        Args:
            on_login_success: Callback a ejecutar tras login exitoso
        """
        self.on_login_success = on_login_success
        self.user_service = UserService(get_database_connection())
        
        # Configurar logging
        self.logger = logging.getLogger(__name__)
        
        # Crear ventana principal
        self.root = tk.Tk()
        self.root.title("Sistema de Inventario - Login")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Centrar ventana en pantalla
        self._center_window()
        
        # Variables de formulario
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        
        # Crear interfaz
        self._create_ui()
        
        # Configurar eventos
        self._setup_events()
        
    def _center_window(self):
        """Centra la ventana en la pantalla."""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (300 // 2)
        self.root.geometry(f"400x300+{x}+{y}")
        
    def _create_ui(self):
        """Crea los elementos de la interfaz de usuario."""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Título
        title_label = ttk.Label(
            main_frame, 
            text="Sistema de Inventario", 
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Información de empresa
        company_label = ttk.Label(
            main_frame,
            text="Copy Point S.A.",
            font=("Arial", 12)
        )
        company_label.grid(row=1, column=0, columnspan=2, pady=(0, 30))
        
        # Campo usuario
        ttk.Label(main_frame, text="Usuario:").grid(
            row=2, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.username_entry = ttk.Entry(
            main_frame, 
            textvariable=self.username_var,
            width=25
        )
        self.username_entry.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Campo contraseña
        ttk.Label(main_frame, text="Contraseña:").grid(
            row=4, column=0, sticky=tk.W, pady=(0, 5)
        )
        self.password_entry = ttk.Entry(
            main_frame, 
            textvariable=self.password_var,
            show="*",
            width=25
        )
        self.password_entry.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Botón login
        self.login_button = ttk.Button(
            main_frame,
            text="Iniciar Sesión",
            command=self._handle_login
        )
        self.login_button.grid(row=6, column=0, columnspan=2, pady=(0, 10))
        
        # Mensaje de estado
        self.status_label = ttk.Label(
            main_frame,
            text="",
            foreground="red"
        )
        self.status_label.grid(row=7, column=0, columnspan=2)
        
        # Información de usuario por defecto
        default_info = ttk.Label(
            main_frame,
            text="Usuario por defecto: admin / Password: admin123",
            font=("Arial", 8),
            foreground="gray"
        )
        default_info.grid(row=8, column=0, columnspan=2, pady=(20, 0))
        
    def _setup_events(self):
        """Configura eventos de la ventana."""
        # Enter key para login
        self.root.bind('<Return>', lambda event: self._handle_login())
        
        # Focus inicial en campo usuario
        self.username_entry.focus()
        
        # Validación en tiempo real
        self.username_var.trace('w', self._validate_form)
        self.password_var.trace('w', self._validate_form)
        
    def _validate_form(self, *args):
        """Valida el formulario en tiempo real."""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        # Habilitar/deshabilitar botón según validación
        if username and password:
            self.login_button.config(state='normal')
            self.status_label.config(text="")
        else:
            self.login_button.config(state='disabled')
            
    def _handle_login(self):
        """Maneja el proceso de autenticación."""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        # Validar campos obligatorios
        if not username or not password:
            self.status_label.config(text="Usuario y contraseña son obligatorios")
            return
            
        try:
            # Deshabilitar botón durante procesamiento
            self.login_button.config(state='disabled', text="Verificando...")
            self.root.update()
            
            # Intentar autenticación
            user = self.user_service.authenticate(username, password)
            
            if user:
                # Login exitoso
                session_manager.login(user)
                self.logger.info(f"Usuario {username} autenticado exitosamente")
                
                # Cerrar ventana de login
                self.root.destroy()
                
                # Ejecutar callback de éxito
                self.on_login_success()
                
            else:
                # Credenciales inválidas
                self.status_label.config(text="Usuario o contraseña incorrectos")
                self.password_var.set("")  # Limpiar contraseña
                self.password_entry.focus()
                
        except Exception as e:
            self.logger.error(f"Error durante autenticación: {e}")
            self.status_label.config(text="Error de conexión. Intente nuevamente.")
            
        finally:
            # Rehabilitar botón
            self.login_button.config(state='normal', text="Iniciar Sesión")
            
    def show(self):
        """Muestra la ventana de login."""
        self.root.mainloop()
        
    def destroy(self):
        """Destruye la ventana de login."""
        if self.root:
            self.root.destroy()
