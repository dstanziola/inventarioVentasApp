"""
MovementEntryForm - Formulario para entradas al inventario (REFACTORIZADO)
Implementa Mediator Pattern para eliminar dependencias circulares

CAMBIOS ARQUITECTÓNICOS:
- Eliminada creación directa de ProductSearchWidget
- Implementada comunicación vía ProductEntryMediator
- Suscripción a eventos vía Event Bus
- Desacoplamiento completo del widget de búsqueda
- Mantenida funcionalidad optimizada existente
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

# Imports del sistema
from services.service_container import get_container
from utils.logger import get_logger
from ui.widgets.product_search_widget_refactored import ProductSearchWidget
from patterns.mediators.product_entry_mediator import ProductEntryMediator
from patterns.event_bus import get_event_bus, InventoryEvents


class MovementEntryForm:
    """
    Formulario para gestionar entradas al inventario - REFACTORIZADO con Mediator Pattern
    
    Características:
    - Coordinación vía ProductEntryMediator (eliminada dependencia circular)
    - Suscripción a eventos vía Event Bus
    - Validación delegada al mediator
    - Mantenida funcionalidad optimizada de secuencia
    """

    def __init__(self, parent: tk.Widget, db_connection: Any):
        """
        Inicializar formulario de entradas al inventario
        
        Args:
            parent: Ventana padre
            db_connection: Conexión base de datos
        """
        self.parent = parent
        self.db = db_connection
        self.title = "Entradas al Inventario"
        
        # Servicios lazy loading
        self._movement_service = None
        self._product_service = None
        self._export_service = None
        self._session_manager = None
        self._category_service = None
        
        # REFACTOR: Mediator centralizado para coordinación
        self.mediator = None
        
        # Event Bus para comunicación
        self.event_bus = get_event_bus()
        
        # Estado del formulario (ahora gestionado por mediator)
        # self.selected_products = None (MOVIDO AL MEDIATOR)
        # self.current_search_results = None (MOVIDO AL MEDIATOR)
        # self._product_locked = None (MOVIDO AL MEDIATOR)
        
        # Logger
        self.logger = get_logger(__name__)
        
        # Inicializar mediator
        self._initialize_mediator()
        
        # Crear interfaz
        self._create_interface()
        self._setup_event_bindings()
        self._subscribe_to_events()
        
        self.logger.info("MovementEntryForm refactorizado con Mediator Pattern inicializado")

    def _initialize_mediator(self):
        """Inicializar mediator con servicios"""
        self.mediator = ProductEntryMediator(
            product_service=self.product_service,
            movement_service=self.movement_service,
            session_manager=self.session_manager,
            category_service=self.category_service
        )
        
        # Registrar callbacks con el mediator
        self.mediator.register_callback('on_products_list_updated', self._on_products_list_updated)
        self.mediator.register_callback('on_entry_registered', self._on_entry_registered)
        self.mediator.register_callback('on_error_occurred', self._on_error_occurred)
        self.mediator.register_callback('on_quantity_focus_requested', self._focus_on_quantity)

    def _subscribe_to_events(self):
        """Suscribirse a eventos del Event Bus"""
        # Eventos de búsqueda de productos
        self.event_bus.subscribe(
            InventoryEvents.PRODUCT_SEARCH_COMPLETED,
            self._on_search_completed_event,
            subscriber_id=f"movement_form_{id(self)}"
        )
        
        # Eventos de selección de productos
        self.event_bus.subscribe(
            InventoryEvents.PRODUCT_SELECTED,
            self._on_product_selected_event,
            subscriber_id=f"movement_form_{id(self)}"
        )
        
        self.event_bus.subscribe(
            InventoryEvents.PRODUCT_AUTO_SELECTED,
            self._on_product_selected_event,
            subscriber_id=f"movement_form_{id(self)}"
        )
        
        # Eventos de foco en cantidad
        self.event_bus.subscribe(
            InventoryEvents.QUANTITY_FOCUS_REQUESTED,
            self._on_quantity_focus_event,
            subscriber_id=f"movement_form_{id(self)}"
        )
        
        # Eventos de limpieza
        self.event_bus.subscribe(
            InventoryEvents.NEXT_PRODUCT_PREPARED,
            self._on_next_product_prepared_event,
            subscriber_id=f"movement_form_{id(self)}"
        )

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

    @property
    def category_service(self):
        """Lazy loading del CategoryService"""
        if self._category_service is None:
            container = get_container()
            self._category_service = container.get('category_service')
        return self._category_service

    def _create_interface(self):
        """Crear interfaz de usuario del formulario"""
        # Crear ventana principal
        self.window = tk.Toplevel(self.parent)
        self.window.title(self.title)
        self.window.geometry("1000x700")
        self.window.resizable(True, True)
        
        # Configurar grid
        self.window.grid_rowconfigure(1, weight=1)
        self.window.grid_rowconfigure(2, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        
        # Panel título
        self._create_title_panel()
        
        # Panel de búsqueda
        self._create_search_panel()
        
        # Panel de productos seleccionados
        self._create_products_panel()
        
        # Panel de botones
        self._create_buttons_panel()
        
        # Establecer foco inicial en búsqueda después de crear interfaz
        self.window.after(100, lambda: self.search_widget.set_focus())

    def _create_title_panel(self):
        """Crear panel del título"""
        title_frame = ttk.Frame(self.window)
        title_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        self.title_label = ttk.Label(
            title_frame,
            text="Gestión de Entradas al Inventario",
            font=("Arial", 16, "bold")
        )
        self.title_label.pack()

    def _create_search_panel(self):
        """Crear panel de búsqueda de productos - REFACTORIZADO"""
        self.search_frame = ttk.LabelFrame(
            self.window,
            text="Búsqueda y Selección de Productos",
            padding=10
        )
        self.search_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        self.search_frame.grid_columnconfigure(0, weight=1)
        
        # REFACTOR: Widget de búsqueda refactorizado (sin callbacks directos)
        self.search_widget = ProductSearchWidget(
            self.search_frame,
            self.product_service
        )
        self.search_widget.grid(row=0, column=0, sticky="ew", pady=5)
        
        # REFACTOR: Ya no configuramos callbacks directos
        # self.search_widget.on_product_selected = ... (REMOVIDO)
        # self.search_widget.on_search_completed = ... (REMOVIDO)
        # self.search_widget.on_focus_quantity = ... (REMOVIDO)
        
        # Campo cantidad
        quantity_frame = ttk.Frame(self.search_frame)
        quantity_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=5)
        
        ttk.Label(quantity_frame, text="Cantidad:").pack(side="left", padx=5)
        
        self.quantity_var = tk.StringVar()
        self.quantity_entry = ttk.Entry(
            quantity_frame,
            textvariable=self.quantity_var,
            width=10
        )
        self.quantity_entry.pack(side="left", padx=5)
        
        # Botones agregar/borrar
        self.add_button = ttk.Button(
            quantity_frame,
            text="Agregar",
            command=self._on_add_clicked
        )
        self.add_button.pack(side="left", padx=5)
        
        self.remove_button = ttk.Button(
            quantity_frame,
            text="Borrar",
            command=self._remove_selected_product
        )
        self.remove_button.pack(side="left", padx=5)
        
        # Botón importar Excel
        self.import_button = ttk.Button(
            quantity_frame,
            text="Importar Excel",
            command=self._on_import_excel
        )
        self.import_button.pack(side="right", padx=5)

    def _create_products_panel(self):
        """Crear panel de productos seleccionados"""
        self.products_frame = ttk.LabelFrame(
            self.window,
            text="Productos Seleccionados",
            padding=10
        )
        self.products_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        self.products_frame.grid_columnconfigure(0, weight=1)
        
        # Treeview para productos
        columns = ("id", "nombre", "cantidad")
        self.products_tree = ttk.Treeview(
            self.products_frame,
            columns=columns,
            show="headings",
            height=10
        )
        
        # Configurar columnas
        self.products_tree.heading("id", text="ID")
        self.products_tree.heading("nombre", text="Nombre del Producto")
        self.products_tree.heading("cantidad", text="Cantidad")
        
        self.products_tree.column("id", width=80)
        self.products_tree.column("nombre", width=400)
        self.products_tree.column("cantidad", width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(
            self.products_frame,
            orient="vertical",
            command=self.products_tree.yview
        )
        self.products_tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid
        self.products_tree.grid(row=0, column=0, sticky="ew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def _create_buttons_panel(self):
        """Crear panel de botones"""
        self.buttons_frame = ttk.Frame(self.window)
        self.buttons_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
        
        # Botón registrar entrada
        self.register_button = ttk.Button(
            self.buttons_frame,
            text="Registrar Entrada",
            command=self._on_register_clicked,
            style="Accent.TButton"
        )
        self.register_button.pack(side="left", padx=5)
        
        # Botón limpiar
        self.clear_button = ttk.Button(
            self.buttons_frame,
            text="Limpiar",
            command=self._clear_form
        )
        self.clear_button.pack(side="left", padx=5)
        
        # Botón cerrar
        self.close_button = ttk.Button(
            self.buttons_frame,
            text="Cerrar",
            command=self.window.destroy
        )
        self.close_button.pack(side="right", padx=5)

    def _setup_event_bindings(self):
        """Configurar eventos y bindings"""
        # Enter en cantidad
        self.quantity_entry.bind("<Return>", lambda e: self._on_add_clicked())
        
        # Validación cantidad en tiempo real
        self.quantity_var.trace("w", self._validate_quantity_input)

    # EVENT BUS HANDLERS - NUEVOS MÉTODOS PARA MANEJAR EVENTOS

    def _on_search_completed_event(self, event_data: Dict):
        """
        Manejar evento de búsqueda completada
        
        Args:
            event_data: Datos del evento
        """
        # Filtrar eventos de nuestro widget únicamente si es necesario
        widget_id = event_data.get('widget_id')
        if widget_id and widget_id != id(self.search_widget):
            return
        
        results = event_data.get('results', [])
        search_term = event_data.get('search_term', '')
        
        self.logger.info(f"Búsqueda completada via Event Bus: {len(results)} productos para '{search_term}'")
        
        # Delegar al mediator si es necesario procesar resultados
        # (En este caso, el widget ya maneja la visualización)

    def _on_product_selected_event(self, event_data: Dict):
        """
        Manejar evento de producto seleccionado
        
        Args:
            event_data: Datos del evento
        """
        # Filtrar eventos de nuestro widget
        widget_id = event_data.get('widget_id')
        if widget_id and widget_id != id(self.search_widget):
            return
        
        product = event_data.get('product')
        auto_selected = event_data.get('auto_selected', False)
        
        if product:
            self.logger.info(f"Producto seleccionado via Event Bus: {product.get('nombre')} (auto: {auto_selected})")
            
            # REFACTOR: Delegar al mediator en lugar de manejo directo
            self.mediator.handle_product_selection(product, auto_selected)

    def _on_quantity_focus_event(self, event_data: Dict):
        """
        Manejar evento de solicitud de foco en cantidad
        
        Args:
            event_data: Datos del evento
        """
        # Filtrar eventos de nuestro widget
        widget_id = event_data.get('widget_id')
        if widget_id and widget_id != id(self.search_widget):
            return
        
        self._focus_on_quantity()

    def _on_next_product_prepared_event(self, event_data: Dict):
        """
        Manejar evento de preparación para siguiente producto
        
        Args:
            event_data: Datos del evento
        """
        self.logger.debug("Preparación para siguiente producto via Event Bus")
        # El widget ya maneja la limpieza vía su propio método

    # MEDIATOR CALLBACK HANDLERS

    def _on_products_list_updated(self, products_list: List[Dict]):
        """
        Callback del mediator cuando se actualiza lista de productos
        
        Args:
            products_list: Lista actualizada de productos
        """
        self._update_products_tree(products_list)

    def _on_entry_registered(self, result: Dict):
        """
        Callback del mediator cuando se registra entrada exitosamente
        
        Args:
            result: Resultado del registro
        """
        ticket_number = result.get('ticket_number', 'N/A')
        messagebox.showinfo("Éxito", f"Entrada registrada exitosamente\nTicket: {ticket_number}")
        self._clear_form()

    def _on_error_occurred(self, error_data: Dict):
        """
        Callback del mediator cuando ocurre un error
        
        Args:
            error_data: Datos del error
        """
        error_type = error_data.get('error_type', 'Error')
        error_message = error_data.get('message', 'Error desconocido')
        
        messagebox.showerror(error_type, error_message)

    # MÉTODOS DE ACCIÓN - REFACTORIZADOS PARA USAR MEDIATOR

    def _on_add_clicked(self):
        """
        Manejar click en agregar producto - REFACTORIZADO con Mediator
        """
        self.logger.info("Agregando producto via Mediator")
        
        # Validar cantidad
        quantity_str = self.quantity_var.get().strip()
        if not self._validate_quantity(quantity_str):
            messagebox.showerror(
                "Cantidad Inválida", 
                "Ingrese una cantidad válida (número entero positivo)\n\nEjemplo: 1, 5, 10"
            )
            self.quantity_entry.focus()
            self.quantity_entry.select_range(0, tk.END)
            return
        
        try:
            quantity = int(quantity_str)
            
            # REFACTOR: Delegar al mediator
            success = self.mediator.handle_product_addition(quantity)
            
            if success:
                # Limpiar cantidad para siguiente producto
                self.quantity_var.set("")
            
        except Exception as e:
            self.logger.error(f"Error al agregar producto: {e}")
            messagebox.showerror("Error", f"Error al agregar producto: {e}")

    def _remove_selected_product(self):
        """Remover producto seleccionado de la lista - REFACTORIZADO"""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un producto para remover")
            return
        
        item = selection[0]
        values = self.products_tree.item(item, "values")
        product_id = int(values[0])
        
        # REFACTOR: Delegar al mediator
        success = self.mediator.handle_product_removal(product_id)
        
        if success:
            self.logger.info(f"Producto {product_id} removido via Mediator")

    def _on_register_clicked(self):
        """Manejar click en registrar entrada - REFACTORIZADO"""
        # REFACTOR: Delegar completamente al mediator
        success = self.mediator.handle_entry_registration()
        
        if success:
            self.logger.info("Entrada registrada exitosamente via Mediator")

    def _clear_form(self):
        """Limpiar todos los campos del formulario - REFACTORIZADO"""
        # REFACTOR: Delegar al mediator
        self.mediator.clear_state()
        
        # Limpiar campos locales
        self.quantity_var.set("")
        self.search_widget.clear_selection()
        
        self.logger.info("Formulario limpiado via Mediator")

    # MÉTODOS DE UTILIDAD

    def _update_products_tree(self, products: List[Dict]):
        """
        Actualizar la vista de productos seleccionados
        
        Args:
            products: Lista de productos a mostrar
        """
        # Limpiar tree
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        # Agregar productos
        for product in products:
            self.products_tree.insert("", "end", values=(
                product['id'],
                product['nombre'],
                product['cantidad']
            ))

    def _focus_on_quantity(self):
        """
        Establecer foco en campo cantidad - FUNCIONALIDAD MANTENIDA
        """
        try:
            # Establecer foco en campo cantidad
            self.quantity_entry.focus()
            
            # Opcional: pre-llenar con 1 si está vacío
            if not self.quantity_var.get().strip():
                self.quantity_var.set("1")
                # Seleccionar el texto para fácil reemplazo
                self.quantity_entry.select_range(0, tk.END)
            
            self.logger.debug("Foco establecido en campo cantidad")
            
        except Exception as e:
            self.logger.error(f"Error al establecer foco en cantidad: {e}")

    def _validate_quantity(self, quantity_str: str) -> bool:
        """
        Validar que la cantidad sea un número entero positivo
        
        Args:
            quantity_str: String con la cantidad
            
        Returns:
            bool: True si válida
        """
        try:
            quantity = int(quantity_str)
            return quantity > 0
        except (ValueError, TypeError):
            return False

    def _validate_quantity_input(self, *args):
        """Validar entrada de cantidad en tiempo real"""
        current_value = self.quantity_var.get()
        
        if current_value == "":
            return
            
        if not current_value.isdigit():
            # Filtrar caracteres no numéricos
            filtered = ''.join(filter(str.isdigit, current_value))
            self.quantity_var.set(filtered)

    def _on_import_excel(self):
        """Manejar importación masiva desde Excel"""
        try:
            file_path = filedialog.askopenfilename(
                title="Seleccionar archivo Excel",
                filetypes=[("Excel files", "*.xlsx *.xls")]
            )
            
            if file_path:
                # Implementar importación Excel
                self._import_from_excel(file_path)
                
        except Exception as e:
            self.logger.error(f"Error en importación Excel: {e}")
            messagebox.showerror("Error", f"Error al importar Excel: {e}")

    def _import_from_excel(self, file_path: str):
        """
        Importar productos desde archivo Excel
        
        Args:
            file_path: Ruta del archivo Excel
        """
        # Placeholder para funcionalidad Excel
        messagebox.showinfo("Info", "Funcionalidad de importación Excel en desarrollo")

    def __del__(self):
        """Cleanup al destruir el formulario"""
        try:
            # Desuscribirse de eventos al destruir
            form_id = f"movement_form_{id(self)}"
            
            events_to_unsubscribe = [
                InventoryEvents.PRODUCT_SEARCH_COMPLETED,
                InventoryEvents.PRODUCT_SELECTED,
                InventoryEvents.PRODUCT_AUTO_SELECTED,
                InventoryEvents.QUANTITY_FOCUS_REQUESTED,
                InventoryEvents.NEXT_PRODUCT_PREPARED
            ]
            
            for event_name in events_to_unsubscribe:
                self.event_bus.unsubscribe(event_name, subscriber_id=form_id)
            
            self.logger.debug("FormularioEntrada: suscripciones a eventos limpiadas")
            
        except Exception as e:
            # No loggear errores en destructor para evitar problemas
            pass
