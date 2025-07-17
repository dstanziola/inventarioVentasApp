"""
MovementAdjustForm - Formulario de ajustes individuales de producto
Arquitectura: Clean Architecture - Capa Presentación
Patrón: MVP + Service Layer + TDD
Requerimientos: Sección 3.2 - Ajustes de Producto
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Optional
import logging
from datetime import datetime

# Importaciones del sistema
from services.service_container import get_container
from utils.logger import get_logger

# Importaciones de widgets reutilizables
from ui.widgets.product_search_widget import ProductSearchWidget


class MovementAdjustForm:
    """
    Formulario para ajustes individuales de productos en inventario
    
    Responsabilidades:
    - Interfaz para ajustar un producto por movimiento
    - Validación de permisos de administrador
    - Búsqueda y selección de productos (via ProductSearchWidget)
    - Validación cantidades positivas/negativas
    - Motivos predefinidos de ajuste
    - Generación automática de tickets
    - Integración con MovementService
    
    Patrón Arquitectónico: MVP
    - Model: Services (MovementService, ProductService, ExportService)
    - View: Tkinter UI components  
    - Presenter: Esta clase (MovementAdjustForm)
    """
    
    def __init__(self, parent, db_connection):
        """
        Constructor del formulario de ajustes
        
        Args:
            parent: Ventana padre
            db_connection: Conexión a base de datos
            
        Raises:
            PermissionError: Si el usuario no tiene permisos de administrador
        """
        self.parent = parent
        self.db = db_connection
        self.window = None
        self.logger = get_logger(__name__)
        
        # Estado del formulario
        self.selected_product: Optional[Dict] = None
        
        # Variables de Tkinter
        self.adjustment_quantity = tk.StringVar(value="0")
        self.responsible_var = tk.StringVar()
        
        # Widgets principales
        self.product_search_widget: Optional[ProductSearchWidget] = None
        self.selected_product_label: Optional[ttk.Label] = None
        self.quantity_entry: Optional[ttk.Entry] = None
        self.reason_combobox: Optional[ttk.Combobox] = None
        self.observations_text: Optional[tk.Text] = None
        
        # Lazy loading de servicios
        self._movement_service = None
        self._product_service = None
        self._export_service = None
        self._session_manager = None
        
        # Validar permisos de administrador
        self._validate_admin_permissions()
        
        # Crear interfaz
        self._create_interface()
        
        self.logger.info("MovementAdjustForm inicializado correctamente")
    
    def _validate_admin_permissions(self):
        """
        Valida que el usuario actual tenga permisos de administrador
        
        Raises:
            PermissionError: Si el usuario no tiene permisos de administrador
        """
        current_user = self.session_manager.get_current_user()
        
        if not current_user:
            raise PermissionError("No hay usuario autenticado")
        
        if not self.session_manager.has_permission('admin'):
            raise PermissionError("Acceso denegado. Solo administradores pueden gestionar ajustes")
    
    def _create_interface(self):
        """Crear la interfaz principal del formulario"""
        # Crear ventana principal
        self.window = tk.Toplevel(self.parent)
        self.window.title("Gestión de Ajustes al Inventario")
        self.window.geometry("700x600")
        self.window.resizable(False, False)
        
        # Centrar ventana
        self._center_window()
        
        # Crear widgets principales
        self._create_title_panel()
        self._create_product_search_panel()
        self._create_adjustment_details_panel()
        self._create_buttons_panel()
        
        # Configurar validaciones
        self._setup_validations()
    
    def _center_window(self):
        """Centra la ventana en la pantalla"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def _create_title_panel(self):
        """Crear el panel de título"""
        title_frame = ttk.Frame(self.window)
        title_frame.pack(fill=tk.X, padx=20, pady=15)
        
        title_label = ttk.Label(
            title_frame, 
            text="Gestión de Ajustes al Inventario",
            font=("Arial", 16, "bold")
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            title_frame,
            text="Ajustar productos individualmente para conciliación con inventario físico",
            font=("Arial", 10)
        )
        subtitle_label.pack(pady=(5, 0))
    
    def _create_product_search_panel(self):
        """Crear panel de búsqueda de productos"""
        search_frame = ttk.LabelFrame(self.window, text="Búsqueda de Producto", padding=10)
        search_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Widget de búsqueda reutilizable
        self.product_search_widget = ProductSearchWidget(
            search_frame, 
            self.product_service
        )
        self.product_search_widget.pack(fill=tk.X)
        
        # Configurar callback para selección
        self.product_search_widget.on_product_selected = self._on_product_selected
        
        # Label para producto seleccionado
        self.selected_product_label = ttk.Label(
            search_frame,
            text="Ningún producto seleccionado",
            foreground="gray",
            font=("Arial", 10, "italic")
        )
        self.selected_product_label.pack(pady=(10, 0))
    
    def _create_adjustment_details_panel(self):
        """Crear panel de detalles del ajuste"""
        details_frame = ttk.LabelFrame(self.window, text="Detalles del Ajuste", padding=10)
        details_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Configurar grid
        details_frame.grid_columnconfigure(1, weight=1)
        
        # Cantidad de ajuste
        ttk.Label(details_frame, text="Cantidad:").grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )
        
        self.quantity_entry = ttk.Entry(
            details_frame,
            textvariable=self.adjustment_quantity,
            width=15
        )
        self.quantity_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(details_frame, text="(Positivo: suma, Negativo: resta)", 
                 foreground="gray", font=("Arial", 8)).grid(
            row=0, column=2, sticky="w", padx=5
        )
        
        # Motivo del ajuste
        ttk.Label(details_frame, text="Motivo:").grid(
            row=1, column=0, sticky="w", padx=5, pady=5
        )
        
        self.reason_combobox = ttk.Combobox(
            details_frame,
            values=[
                "CORRECCIÓN INVENTARIO FÍSICO",
                "PRODUCTO DAÑADO", 
                "OTRO"
            ],
            state="readonly",
            width=30
        )
        self.reason_combobox.grid(row=1, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        self.reason_combobox.set("CORRECCIÓN INVENTARIO FÍSICO")  # Valor por defecto
        
        # Responsable
        ttk.Label(details_frame, text="Responsable:").grid(
            row=2, column=0, sticky="w", padx=5, pady=5
        )
        
        current_user = self.session_manager.get_current_user()
        self.responsible_var.set(current_user['username'] if current_user else "")
        
        responsible_entry = ttk.Entry(
            details_frame,
            textvariable=self.responsible_var,
            width=30
        )
        responsible_entry.grid(row=2, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # Observaciones
        ttk.Label(details_frame, text="Observaciones:").grid(
            row=3, column=0, sticky="nw", padx=5, pady=5
        )
        
        self.observations_text = tk.Text(
            details_frame,
            width=50,
            height=4
        )
        self.observations_text.grid(row=3, column=1, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # Scrollbar para observaciones
        obs_scrollbar = ttk.Scrollbar(details_frame, orient="vertical", command=self.observations_text.yview)
        obs_scrollbar.grid(row=3, column=3, sticky="ns", pady=5)
        self.observations_text.configure(yscrollcommand=obs_scrollbar.set)
    
    def _create_buttons_panel(self):
        """Crear panel de botones"""
        buttons_frame = ttk.Frame(self.window)
        buttons_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Botón Registrar Ajuste
        register_btn = ttk.Button(
            buttons_frame,
            text="Registrar Ajuste",
            command=self._register_adjustment,
            style="Accent.TButton"
        )
        register_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón Limpiar
        clear_btn = ttk.Button(
            buttons_frame,
            text="Limpiar",
            command=self._clear_form
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón Cerrar
        close_btn = ttk.Button(
            buttons_frame,
            text="Cerrar",
            command=self.destroy
        )
        close_btn.pack(side=tk.RIGHT, padx=5)
    
    def _setup_validations(self):
        """Configurar validaciones en tiempo real"""
        # Validación de cantidad en tiempo real
        self.adjustment_quantity.trace("w", self._on_quantity_change)
    
    def _on_product_selected(self, product: Dict, **kwargs):
        """
        Callback cuando se selecciona un producto
        
        Args:
            product: Diccionario con datos del producto seleccionado
        """
        self.selected_product = product
        
        # Actualizar label
        stock_info = f" (Stock actual: {product.get('stock_actual', 'N/A')})" if 'stock_actual' in product else ""
        self.selected_product_label.config(
            text=f"Seleccionado: {product['nombre']}{stock_info}",
            foreground="black"
        )
        
        self.logger.debug(f"Producto seleccionado: {product['nombre']}")
    
    def _on_quantity_change(self, *args):
        """Callback cuando cambia la cantidad"""
        quantity_str = self.adjustment_quantity.get()
        
        # Validación visual
        if self._validate_quantity(quantity_str):
            self.quantity_entry.config(style="TEntry")  # Estilo normal
        else:
            self.quantity_entry.config(style="Error.TEntry")  # Estilo error
    
    def _validate_quantity(self, quantity_str: str) -> bool:
        """
        Validar que la cantidad sea un entero válido (positivo o negativo)
        
        Args:
            quantity_str: String de la cantidad a validar
            
        Returns:
            bool: True si es válida, False en caso contrario
        """
        if not quantity_str or quantity_str.strip() == "":
            return False
        
        try:
            quantity = int(quantity_str)
            # No permitir cero (debe ser ajuste real)
            return quantity != 0
        except ValueError:
            return False
    
    def _register_adjustment(self) -> bool:
        """
        Registrar el ajuste de inventario
        
        Returns:
            bool: True si se registró exitosamente, False en caso contrario
        """
        try:
            # Validaciones previas
            if not self._validate_form():
                return False
            
            # Preparar datos del ajuste
            adjustment_data = self._prepare_adjustment_data()
            
            # Crear movimiento en el servicio
            result = self.movement_service.create_adjustment_movement(adjustment_data)
            
            if result and result.get('success'):
                # Generar ticket PDF
                ticket_generated = self.export_service.generate_adjustment_ticket(
                    result['id'], 
                    adjustment_data
                )
                
                if ticket_generated:
                    messagebox.showinfo(
                        "Éxito", 
                        f"Ajuste registrado exitosamente.\nID: {result['id']}\nTicket generado."
                    )
                else:
                    messagebox.showwarning(
                        "Parcial", 
                        "Ajuste registrado pero error al generar ticket."
                    )
                
                # Limpiar formulario
                self._clear_form()
                return True
            else:
                messagebox.showerror("Error", "Error al registrar el ajuste")
                return False
                
        except Exception as e:
            self.logger.error(f"Error registrando ajuste: {e}")
            messagebox.showerror("Error", f"Error registrando ajuste: {str(e)}")
            return False
    
    def _validate_form(self) -> bool:
        """
        Validar el formulario completo
        
        Returns:
            bool: True si es válido, False en caso contrario
        """
        # Producto seleccionado
        if not self.selected_product:
            messagebox.showerror("Error", "Debe seleccionar un producto")
            return False
        
        # Cantidad válida
        if not self._validate_quantity(self.adjustment_quantity.get()):
            messagebox.showerror("Error", "La cantidad debe ser un número entero diferente de cero")
            return False
        
        # Motivo seleccionado
        if not self.reason_combobox.get():
            messagebox.showerror("Error", "Debe seleccionar un motivo")
            return False
        
        # Responsable
        if not self.responsible_var.get().strip():
            messagebox.showerror("Error", "Debe especificar el responsable")
            return False
        
        return True
    
    def _prepare_adjustment_data(self) -> Dict:
        """
        Preparar datos del ajuste para enviar al servicio
        
        Returns:
            Dict: Datos del ajuste preparados
        """
        current_user = self.session_manager.get_current_user()
        
        return {
            'product_id': self.selected_product['id'],
            'product_name': self.selected_product['nombre'],
            'quantity': int(self.adjustment_quantity.get()),
            'reason': self.reason_combobox.get(),
            'observations': self.observations_text.get('1.0', tk.END).strip(),
            'responsible': self.responsible_var.get().strip(),
            'user_id': current_user['id'] if current_user else None,
            'timestamp': datetime.now().isoformat(),
            'movement_type': 'AJUSTE'
        }
    
    def _clear_form(self):
        """Limpiar el formulario"""
        # Limpiar búsqueda de producto
        if self.product_search_widget:
            self.product_search_widget.clear_selection()
        
        # Limpiar variables
        self.selected_product = None
        self.adjustment_quantity.set("0")
        
        # Limpiar widgets
        self.selected_product_label.config(
            text="Ningún producto seleccionado",
            foreground="gray"
        )
        
        self.reason_combobox.set("CORRECCIÓN INVENTARIO FÍSICO")
        self.observations_text.delete('1.0', tk.END)
        
        # Mantener responsable actual
        current_user = self.session_manager.get_current_user()
        self.responsible_var.set(current_user['username'] if current_user else "")
        
        self.logger.debug("Formulario limpiado")
    
    # Lazy loading de servicios (Properties)
    @property
    def movement_service(self):
        """Lazy loading del MovementService"""
        if self._movement_service is None:
            container = get_container()
            self._movement_service = container.get('movement_service')
        return self._movement_service
    
    @property
    def product_service(self):
        """Lazy loading del ProductService"""
        if self._product_service is None:
            container = get_container()
            self._product_service = container.get('product_service')
        return self._product_service
    
    @property
    def export_service(self):
        """Lazy loading del ExportService"""
        if self._export_service is None:
            container = get_container()
            self._export_service = container.get('export_service')
        return self._export_service
    
    @property
    def session_manager(self):
        """Lazy loading del SessionManager"""
        if self._session_manager is None:
            container = get_container()
            self._session_manager = container.get('session_manager')
        return self._session_manager
    
    def destroy(self):
        """Destruir la ventana y limpiar recursos"""
        try:
            if self.window:
                self.window.destroy()
                self.window = None
            self.logger.info("MovementAdjustForm destruido correctamente")
        except Exception as e:
            self.logger.error(f"Error al destruir MovementAdjustForm: {e}")
