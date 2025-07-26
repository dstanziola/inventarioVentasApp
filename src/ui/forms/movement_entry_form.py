"""
MovementEntryForm - Formulario para entradas al inventario
Implementa patrón MVP con servicios inyectados via ServiceContainer

REFACTORIZACIÓN: Integración con Event Bus para eliminar dependencias circulares
Patrón: Event Listener via Event Bus + Mediator coordination
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import logging

# Imports del sistema
from services.service_container import get_container
from utils.logger import get_logger
from ui.widgets.product_search_widget import ProductSearchWidget, create_product_search_widget

# Event Bus integration - CORRECCIÓN CRÍTICA: tkinter compatible
from ui.shared.event_bus_tkinter import get_event_bus_tkinter, EventBusTkinter, EventData
from ui.shared.events import (
    EventTypes, EventSources,
    create_movement_entry_event_data, create_search_request_event_data
)
from ui.shared.mediator_tkinter import create_product_movement_mediator_tkinter, ProductMovementMediatorTkinter


class MovementEntryForm:
    """
    Formulario para gestionar entradas al inventario
    
    Características:
    - Búsqueda de productos por ID o nombre
    - Validación de duplicados con suma de cantidades
    - Importación masiva Excel
    - Generación automática de tickets PDF
    - Validación tiempo real
    
    REFACTORIZACIÓN:
    - Eliminadas dependencias circulares con ProductSearchWidget
    - Comunicación via Event Bus
    - Integración con ProductMovementMediator
    - Event Listener pattern implementation
    """

    def __init__(self, parent: tk.Widget, db_connection: Any, event_bus: Optional[EventBusTkinter] = None):
        """
        Inicializar formulario de entradas al inventario
        
        Args:
            parent: Ventana padre
            db_connection: Conexión base de datos
            event_bus: Event Bus instance (opcional, usa singleton por defecto)
        """
        self.parent = parent
        self.db = db_connection
        self.title = "Entradas al Inventario"
        
        # Event Bus integration - CORRECCIÓN CRÍTICA: tkinter compatible
        self._event_bus = event_bus or get_event_bus_tkinter()
        self._mediator: Optional[ProductMovementMediatorTkinter] = None
        
        # Servicios lazy loading
        self._movement_service = None
        self._product_service = None
        self._export_service = None
        self._session_manager = None
        
        # Estado del formulario
        self.selected_products: List[Dict] = []
        self.current_search_results: List[Dict] = []
        self._product_locked: bool = False
        self._current_selected_product: Optional[Dict] = None  # Para Event Bus
        
        # Logger
        self.logger = get_logger(__name__)
        
        # Inicializar Event Bus y Mediator
        self._setup_event_integration()
        
        # Crear interfaz
        self._create_interface()
        self._setup_event_bindings()
        
        self.logger.info("MovementEntryForm inicializado con Event Bus")

    def _setup_event_integration(self):
        """Configurar integración con Event Bus y Mediator"""
        try:
            # Crear mediator para coordinar comunicación - tkinter compatible
            self._mediator = create_product_movement_mediator_tkinter(self._event_bus)
            
            # Configurar Event Bus con tkinter root
            if self.parent and hasattr(self.parent, 'winfo_toplevel'):
                root = self.parent.winfo_toplevel()
                if hasattr(self._event_bus, 'set_tkinter_root'):
                    self._event_bus.set_tkinter_root(root)
            
            # Registrar listeners para eventos relevantes
            self._register_event_listeners()
            
            self.logger.info("Event Bus y Mediator configurados exitosamente")
            
        except Exception as e:
            self.logger.error(f"Error configurando Event Bus: {e}")

    def _register_event_listeners(self):
        """Registrar listeners para eventos del Event Bus"""
        try:
            # Escuchar eventos de selección de productos
            self._event_bus.register(
                EventTypes.MOVEMENT_ENTRY_ACTION,
                self._handle_movement_entry_action_event
            )
            
            # Escuchar eventos de validación
            self._event_bus.register(
                EventTypes.VALIDATION_ERROR,
                self._handle_validation_error_event
            )
            
            # Escuchar advertencias de reglas de negocio
            self._event_bus.register(
                EventTypes.BUSINESS_RULE_VIOLATION,
                self._handle_business_rule_violation_event
            )
            
            self.logger.debug("Event listeners registrados para MovementEntryForm")
            
        except Exception as e:
            self.logger.error(f"Error registrando event listeners: {e}")

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

    def _create_interface(self):
        """Crear interfaz de usuario del formulario"""
        # Crear ventana principal
        self.window = tk.Toplevel(self.parent)
        # ———> Hacer modal respecto al padre:
        self.window.transient(self.parent)   # liga la ventana al padre
        self.window.grab_set()               # captura todos los eventos
        self.window.focus_force()            # fuerza el foco aquí
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
        
        # Establecer foco inicial después de crear interfaz
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
        """Crear panel de búsqueda de productos"""
        self.search_frame = ttk.LabelFrame(
            self.window,
            text="Búsqueda y Selección de Productos",
            padding=10
        )
        self.search_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        self.search_frame.grid_columnconfigure(0, weight=1)
        
        # REFACTORIZACIÓN: Widget de búsqueda con Event Bus
        self.search_widget = create_product_search_widget(
            self.search_frame,
            self.product_service,
            self._event_bus  # Pasar Event Bus explícitamente
        )
        self.search_widget.grid(row=0, column=0, sticky="ew", pady=5)
        
        # ELIMINADO: Configuración de callbacks directos
        # Se mantienen solo para compatibilidad, pero la comunicación real es via Event Bus
        
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
            command=self._close_form
        )
        self.close_button.pack(side="right", padx=5)

    def _setup_event_bindings(self):
        """Configurar eventos y bindings"""
        # Enter en cantidad
        self.quantity_entry.bind("<Return>", lambda e: self._on_add_clicked())
        
        # Validación cantidad en tiempo real
        self.quantity_var.trace("w", self._validate_quantity_input)

    # ==================== EVENT BUS EVENT HANDLERS ====================

    def _handle_movement_entry_action_event(self, event_data: EventData):
        """
        Manejar eventos de acción en formulario de movimientos
        
        Args:
            event_data: Datos del evento
        """
        try:
            action = event_data.data.get("action")
            
            if action == "product_selected":
                self._handle_product_selected_via_event_bus(event_data)
            elif action == "search_request":
                self._handle_search_request_via_event_bus(event_data)
            
        except Exception as e:
            self.logger.error(f"Error manejando evento movement_entry_action: {e}")

    def _handle_product_selected_via_event_bus(self, event_data: EventData):
        """
        Manejar selección de producto via Event Bus
        
        Args:
            event_data: Datos del evento de selección
        """
        try:
            product_data = event_data.data.get("product_data")
            if not product_data:
                self.logger.warning("Evento product_selected sin datos de producto")
                return
            
            self.logger.info(f"Producto seleccionado via Event Bus: {product_data.get('nombre', 'UNKNOWN')}")
            
            # Actualizar estado interno
            self._current_selected_product = product_data
            
            # Validación automática del bloqueo de selección
            if hasattr(self, '_product_locked') and self._product_locked:
                self.logger.warning("Producto ya bloqueado, ignorando nueva selección via Event Bus")
                return
            
            # Establecer bloqueo
            self._product_locked = True
            
            # Enfocar cantidad automáticamente
            self.quantity_entry.focus()
            
            # Pre-llenar cantidad con 1 si está vacío
            if not self.quantity_var.get().strip():
                self.quantity_var.set("1")
                self.quantity_entry.select_range(0, tk.END)
            
            self.logger.info(f"Selección via Event Bus procesada: {product_data['nombre']}")
            
        except Exception as e:
            self.logger.error(f"Error manejando selección via Event Bus: {e}")

    def _handle_search_request_via_event_bus(self, event_data: EventData):
        """
        Manejar solicitud de búsqueda via Event Bus
        
        Args:
            event_data: Datos del evento de búsqueda
        """
        try:
            search_term = event_data.data.get("search_term", "")
            
            if search_term:
                # Solicitar búsqueda al widget (que publicará sus propios eventos)
                self.search_widget.set_search_term(search_term)
                
                self.logger.debug(f"Solicitud de búsqueda via Event Bus: '{search_term}'")
            
        except Exception as e:
            self.logger.error(f"Error manejando búsqueda via Event Bus: {e}")

    def _handle_validation_error_event(self, event_data: EventData):
        """
        Manejar eventos de error de validación
        
        Args:
            event_data: Datos del evento de error
        """
        try:
            error_messages = event_data.data.get("error_messages", [])
            field_name = event_data.data.get("field_name", "unknown")
            
            if error_messages:
                error_text = "\n".join(error_messages)
                messagebox.showerror(
                    "Error de Validación",
                    f"Error en {field_name}:\n\n{error_text}"
                )
                
                self.logger.warning(f"Error de validación via Event Bus: {field_name}")
            
        except Exception as e:
            self.logger.error(f"Error manejando validation_error event: {e}")

    def _handle_business_rule_violation_event(self, event_data: EventData):
        """
        Manejar eventos de violación de reglas de negocio
        
        Args:
            event_data: Datos del evento de violación
        """
        try:
            warnings = event_data.data.get("warnings", [])
            is_blocking = event_data.data.get("is_blocking", False)
            
            if warnings:
                warning_text = "\n".join([f"• {warning}" for warning in warnings])
                
                if is_blocking:
                    messagebox.showerror(
                        "Regla de Negocio Violada",
                        f"No se puede continuar:\n\n{warning_text}"
                    )
                else:
                    messagebox.showwarning(
                        "Advertencia de Regla de Negocio",
                        f"Advertencia:\n\n{warning_text}\n\nPuede continuar pero tenga en cuenta estas restricciones."
                    )
                
                self.logger.info(f"Regla de negocio via Event Bus: {'BLOQUEANTE' if is_blocking else 'ADVERTENCIA'}")
            
        except Exception as e:
            self.logger.error(f"Error manejando business_rule_violation event: {e}")

    # ==================== MÉTODOS MODIFICADOS PARA EVENT BUS ====================

    def _on_add_clicked(self):
        """Manejar click en agregar producto - REFACTORIZADO para Event Bus"""
        self.logger.info("DEBUGGING _on_add_clicked con Event Bus")
        
        # NUEVA FUNCIONALIDAD: Usar producto del Event Bus si está disponible
        selected_product = self._current_selected_product or self.search_widget.get_selected_product()
        
        if not selected_product:
            # Publicar evento de solicitud de validación
            self._publish_validation_request_event()
            
            # Fallback a validación tradicional
            validation_state = self._validate_product_selection_state()
            if not validation_state['valid']:
                self._handle_invalid_product_selection(validation_state)
                return
            selected_product = self.search_widget.get_selected_product()
        
        # Validación de cantidad
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
            
            self.logger.info(
                f"Agregando producto via Event Bus: {selected_product['nombre']} x{quantity}"
            )
            
            # Publicar evento de adición
            self._publish_item_addition_event(selected_product, quantity)
            
            self._add_product_to_list(selected_product, quantity)
            
            # Preparación para siguiente producto
            self._prepare_for_next_product()
            
        except Exception as e:
            self.logger.error(f"Error al agregar producto: {e}")
            messagebox.showerror("Error", f"Error al agregar producto: {e}")

    def _publish_validation_request_event(self):
        """Publicar evento de solicitud de validación"""
        try:
            form_state = {
                "selected_products_count": len(self.selected_products),
                "current_search_results": len(getattr(self.search_widget, 'current_results', [])),
                "product_locked": getattr(self, '_product_locked', False)
            }
            
            event_data = create_movement_entry_event_data(
                action="validate",
                movement_type="ENTRADA",
                form_state=form_state
            )
            
            self._event_bus.publish(
                EventTypes.MOVEMENT_VALIDATION,
                event_data.__dict__,
                EventSources.MOVEMENT_ENTRY_FORM
            )
            
        except Exception as e:
            self.logger.error(f"Error publicando validation request: {e}")

    def _publish_item_addition_event(self, product: Dict, quantity: int):
        """Publicar evento de adición de item"""
        try:
            event_data = create_movement_entry_event_data(
                action="add",
                movement_type="ENTRADA",
                form_state={"total_products": len(self.selected_products) + 1},
                product_data=product,
                quantity=quantity
            )
            
            self._event_bus.publish(
                EventTypes.MOVEMENT_ITEM_ADDED,
                event_data.__dict__,
                EventSources.MOVEMENT_ENTRY_FORM
            )
            
        except Exception as e:
            self.logger.error(f"Error publicando item addition event: {e}")

    def _prepare_for_next_product(self):
        """
        Preparar formulario para el siguiente producto - REFACTORIZADO para Event Bus
        """
        try:
            self.logger.info("DEBUGGING _prepare_for_next_product con Event Bus")
            
            # Limpiar cantidad
            self.quantity_var.set("")
            
            # Limpiar selección del widget de búsqueda
            self.search_widget._clear_code_and_selection()
            
            # Desbloquear selección y limpiar estado del Event Bus
            self._product_locked = False
            self._current_selected_product = None
            
            # Publicar evento de limpieza del formulario
            self._publish_form_cleared_event()
            
            self.logger.info("Formulario preparado para siguiente producto via Event Bus")
            
        except Exception as e:
            self.logger.error(f"Error al preparar para siguiente producto: {e}")

    def _publish_form_cleared_event(self):
        """Publicar evento de formulario limpiado"""
        try:
            event_data = create_movement_entry_event_data(
                action="clear",
                movement_type="ENTRADA",
                form_state={"ready_for_next": True}
            )
            
            self._event_bus.publish(
                EventTypes.MOVEMENT_FORM_CLEARED,
                event_data.__dict__,
                EventSources.MOVEMENT_ENTRY_FORM
            )
            
        except Exception as e:
            self.logger.error(f"Error publicando form cleared event: {e}")

    def _close_form(self):
        """Cerrar formulario con cleanup del Event Bus"""
        try:
            # Cleanup del mediator
            if self._mediator:
                self._mediator.cleanup()
            
            # Desregistrar listeners
            self._unregister_event_listeners()
            
            # Liberar el grab para devolver el foco a la app principal
            try:
                self.window.grab_release()
            except Exception:
                pass
            # Cerrar ventana
            self.window.destroy()
            
            self.logger.info("MovementEntryForm cerrado con cleanup de Event Bus")
            
        except Exception as e:
            self.logger.error(f"Error cerrando formulario: {e}")
            self.window.destroy()

    def _unregister_event_listeners(self):
        """Desregistrar listeners del Event Bus"""
        try:
            self._event_bus.unregister(
                EventTypes.MOVEMENT_ENTRY_ACTION,
                self._handle_movement_entry_action_event
            )
            
            self._event_bus.unregister(
                EventTypes.VALIDATION_ERROR,
                self._handle_validation_error_event
            )
            
            self._event_bus.unregister(
                EventTypes.BUSINESS_RULE_VIOLATION,
                self._handle_business_rule_violation_event
            )
            
            self.logger.debug("Event listeners desregistrados")
            
        except Exception as e:
            self.logger.error(f"Error desregistrando listeners: {e}")

    # ==================== MÉTODOS ORIGINALES (Sin cambios críticos) ====================

    def _add_product_to_list(self, product: Dict, quantity: int):
        """Agregar producto a la lista (método original sin cambios)"""
        try:
            # Validación de categoría (sin cambios)
            if not self._validate_product_for_inventory(product):
                return
            
            # Buscar si el producto ya está en la lista
            existing_index = None
            for i, selected_product in enumerate(self.selected_products):
                if selected_product['id'] == product['id']:
                    existing_index = i
                    break
            
            if existing_index is not None:
                # Sumar cantidades
                self.selected_products[existing_index]['cantidad'] += quantity
                self.logger.info(f"Cantidad sumada para producto {product['id']}: {quantity}")
            else:
                # Agregar nuevo producto
                product_data = {
                    'id': product['id'],
                    'nombre': product['nombre'],
                    'cantidad': quantity,
                    'stock_original': product.get('stock', 0),
                    'categoria_tipo': product.get('categoria_tipo', 'UNKNOWN')
                }
                self.selected_products.append(product_data)
                self.logger.info(f"Producto MATERIAL agregado: {product['id']} - {quantity} unidades")
            
            # Actualizar vista
            self._update_products_tree()
            
        except Exception as e:
            self.logger.error(f"Error al agregar producto a lista: {e}")
            messagebox.showerror("Error", f"No se pudo agregar el producto: {e}")

    def _update_products_tree(self):
        """Actualizar la vista de productos seleccionados"""
        # Limpiar tree
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        # Agregar productos
        for product in self.selected_products:
            self.products_tree.insert("", "end", values=(
                product['id'],
                product['nombre'],
                product['cantidad']
            ))

    def _remove_selected_product(self):
        """Remover producto seleccionado de la lista"""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un producto para remover")
            return
        
        item = selection[0]
        values = self.products_tree.item(item, "values")
        product_id = int(values[0])
        
        # Remover de la lista
        self.selected_products = [
            p for p in self.selected_products if p['id'] != product_id
        ]
        
        # Actualizar vista
        self._update_products_tree()
        
        # Publicar evento de item removido
        try:
            event_data = create_movement_entry_event_data(
                action="remove",
                movement_type="ENTRADA",
                form_state={"total_products": len(self.selected_products)},
                product_data={"id": product_id}
            )
            
            self._event_bus.publish(
                EventTypes.MOVEMENT_ITEM_REMOVED,
                event_data.__dict__,
                EventSources.MOVEMENT_ENTRY_FORM
            )
            
        except Exception as e:
            self.logger.error(f"Error publicando item removed event: {e}")
        
        self.logger.info(f"Producto {product_id} removido de la lista")

    # ==================== MÉTODOS SIN CAMBIOS (por brevedad) ====================
    
    def _on_register_clicked(self):
        """Manejar click en registrar entrada"""
        if not self.selected_products:
            messagebox.showwarning("Advertencia", "Agregue productos antes de registrar")
            return
        
        if self._register_entry():
            messagebox.showinfo("Éxito", "Entrada registrada exitosamente")
            self._clear_form()

    def _register_entry(self) -> bool:
        """Registrar entrada al inventario (método original sin cambios críticos)"""
        try:
            # Pre-validación
            es_valido, errores_validacion = self._pre_validate_products_for_entry()
            
            if not es_valido:
                error_msg = "Errores de validación encontrados:\n\n"
                error_msg += "\n".join([f"• {error}" for error in errores_validacion])
                error_msg += "\n\nCorrija los errores antes de continuar."
                
                self.logger.error(f"Pre-validación falló: {len(errores_validacion)} errores")
                messagebox.showerror("Error de Validación", error_msg)
                return False
            
            # CORRECCIÓN CRÍTICA: Obtener usuario actual correctamente
            current_user_obj = self.session_manager.get_current_user()
            if not current_user_obj:
                raise ValueError("No se pudo obtener información del usuario actual")
            
            # CORRECCIÓN CRÍTICA: Acceder a propiedades del objeto Usuario, no como diccionario
            current_user = {
                'id': current_user_obj.id,
                'username': current_user_obj.username,
                'rol': current_user_obj.rol,
                'activo': current_user_obj.activo
            }
            
            # Validar que el usuario tenga ID válido
            if not current_user['id']:
                raise ValueError("El usuario actual no tiene ID válido")
            
            # Preparar datos del movimiento
            movement_data = {
                'tipo': 'ENTRADA',
                'fecha': datetime.now(),
                'responsable_id': current_user['id'],
                'productos': self.selected_products
            }
            
            self.logger.info(
                f"Iniciando registro de entrada: {len(self.selected_products)} productos válidos, "
                f"usuario: {current_user.get('username', 'unknown')}"
            )
            
            # Llamar servicio
            result = self.movement_service.create_entry_movement(movement_data)
            
            # Validación de respuesta
            if not result or not isinstance(result, dict):
                raise ValueError("El servicio no retornó resultado válido")
            
            required_fields = ['id', 'ticket_number']
            missing_fields = [field for field in required_fields if field not in result]
            
            if missing_fields:
                raise ValueError(
                    f"Respuesta incompleta del servicio. Campos faltantes: {missing_fields}"
                )
            
            # Extraer datos
            entry_id = result['id']
            ticket_number = result.get('ticket_number', f'ENT-{entry_id:06d}')
            
            self.logger.info(f"Entrada registrada exitosamente: ID={entry_id}, Ticket={ticket_number}")
            
            # Generar ticket PDF
            try:
                ticket_path = self._generate_ticket(ticket_number, self.selected_products)
                if ticket_path:
                    self.logger.info(f"Ticket PDF generado: {ticket_path}")
            except Exception as ticket_error:
                self.logger.error(f"Error generando ticket PDF: {ticket_error}")
            
            return True
            
        except Exception as e:
            error_msg = self._handle_entry_registration_error(e)
            self.logger.error(f"Error al registrar entrada: {e}")
            messagebox.showerror("Error", error_msg)
            return False

    def _clear_form(self):
        """Limpiar todos los campos del formulario"""
        self.selected_products.clear()
        self.current_search_results.clear()
        
        self.quantity_var.set("")
        self.search_widget.clear_selection()
        self._update_products_tree()
        
        # Limpiar estado del Event Bus
        self._current_selected_product = None
        self._product_locked = False
        
        self.logger.info("Formulario limpiado con Event Bus")

    # Métodos auxiliares sin cambios críticos (por brevedad)
    def _validate_quantity(self, quantity_str: str) -> bool:
        try:
            quantity = int(quantity_str)
            return quantity > 0
        except (ValueError, TypeError):
            return False

    def _validate_product_for_inventory(self, product: Dict) -> bool:
        try:
            id_categoria = product.get('id_categoria')
            if not id_categoria:
                messagebox.showerror(
                    "Error de Validación", 
                    f"El producto '{product.get('nombre', 'UNKNOWN')}' no tiene categoría asignada."
                )
                return False
            
            container = get_container()
            category_service = container.get('category_service')
            categoria = category_service.get_category_by_id(id_categoria)
            
            if not categoria:
                messagebox.showerror(
                    "Error de Validación", 
                    f"No se pudo obtener información de la categoría para '{product.get('nombre', 'UNKNOWN')}'"
                )
                return False
            
            if categoria.tipo == 'SERVICIO':
                messagebox.showwarning(
                    "Producto No Válido para Inventario",
                    f"\"{ product.get('nombre', 'UNKNOWN')}\" es un SERVICIO.\n\n"
                    f"❌ Los SERVICIOS no pueden agregarse al inventario.\n"
                    f"✅ Solo productos de tipo MATERIAL pueden tener stock.\n\n"
                    f"Los servicios generan ventas pero no requieren inventario."
                )
                self.logger.warning(f"Intento de agregar SERVICIO al inventario: {product.get('nombre')} (ID: {product.get('id')})")
                return False
            
            if categoria.tipo == 'MATERIAL':
                product['categoria_tipo'] = 'MATERIAL'
                return True
            
            messagebox.showerror(
                "Error de Categoría", 
                f"El producto '{product.get('nombre', 'UNKNOWN')}' tiene un tipo de categoría no reconocido: {categoria.tipo}"
            )
            return False
            
        except Exception as e:
            self.logger.error(f"Error validando producto para inventario: {e}")
            messagebox.showerror(
                "Error de Validación", 
                f"No se pudo validar el producto '{product.get('nombre', 'UNKNOWN')}': {e}"
            )
            return False

    def _validate_product_selection_state(self) -> dict:
        """Validar estado de selección de productos (método original)"""
        try:
            selected_product = self.search_widget.get_selected_product()
            current_results = getattr(self.search_widget, 'current_results', [])
            
            if selected_product:
                return {
                    'valid': True,
                    'reason': 'Producto seleccionado correctamente',
                    'action': 'proceed',
                    'auto_selected': len(current_results) == 1
                }
            
            if not current_results:
                return {
                    'valid': False,
                    'reason': 'No hay productos en la búsqueda',
                    'action': 'search_required',
                    'message': 'Busque un producto antes de agregar'
                }
            
            if len(current_results) > 1:
                return {
                    'valid': False,
                    'reason': 'Múltiples productos encontrados sin selección',
                    'action': 'selection_required',
                    'message': f'Seleccione uno de los {len(current_results)} productos encontrados'
                }
            
            return {
                'valid': False,
                'reason': 'Un producto encontrado pero no seleccionado',
                'action': 'auto_select_failed',
                'message': 'Error en auto-selección. Seleccione manualmente.'
            }
            
        except Exception as e:
            self.logger.error(f"Error validando estado de selección: {e}")
            return {
                'valid': False,
                'reason': f'Error interno: {e}',
                'action': 'error',
                'message': 'Error interno en validación'
            }

    def _handle_invalid_product_selection(self, validation_state: dict):
        """Manejar estados de selección inválidos (método original)"""
        action = validation_state.get('action', 'unknown')
        message = validation_state.get('message', 'Error desconocido')
        
        if action == 'search_required':
            messagebox.showwarning(
                "Sin Productos", 
                f"{message}\n\nIngrese un código o nombre de producto."
            )
            self.search_widget.set_focus()
        elif action == 'selection_required':
            messagebox.showwarning(
                "Selección Requerida", 
                f"{message}.\n\nSeleccione uno de la lista para continuar."
            )
        elif action == 'auto_select_failed':
            messagebox.showwarning(
                "Error de Autoselección", 
                f"{message}\n\nIntente buscar nuevamente."
            )
            self.search_widget.set_focus()
        else:
            messagebox.showerror(
                "Error de Selección", 
                f"Error en selección de producto: {message}"
            )

    def _pre_validate_products_for_entry(self) -> Tuple[bool, List[str]]:
        """Pre-validar productos (método original sin cambios)"""
        errores = []
        
        try:
            if not self.selected_products:
                errores.append("No hay productos seleccionados")
                return False, errores
            
            productos_problematicos = []
            
            for i, producto in enumerate(self.selected_products):
                producto_nombre = producto.get('nombre', f'Producto #{i+1}')
                producto_id = producto.get('id')
                cantidad = producto.get('cantidad', 0)
                
                if not producto_id or not isinstance(producto_id, int):
                    errores.append(f"{producto_nombre}: ID inválido ({producto_id})")
                    continue
                
                if cantidad <= 0:
                    errores.append(f"{producto_nombre}: Cantidad inválida ({cantidad})")
                
                categoria_tipo = producto.get('categoria_tipo')
                if categoria_tipo == 'SERVICIO':
                    productos_problematicos.append(producto_nombre)
            
            if productos_problematicos:
                errores.append(
                    f"Productos SERVICIO detectados (no permitidos en inventario): "
                    f"{', '.join(productos_problematicos)}"
                )
            
            ids_vistos = set()
            for producto in self.selected_products:
                producto_id = producto.get('id')
                if producto_id in ids_vistos:
                    errores.append(f"Producto duplicado encontrado: ID {producto_id}")
                ids_vistos.add(producto_id)
            
            es_valido = len(errores) == 0
            
            if es_valido:
                self.logger.info(f"Pre-validación exitosa: {len(self.selected_products)} productos válidos")
            else:
                self.logger.warning(f"Pre-validación falló: {len(errores)} errores encontrados")
            
            return es_valido, errores
            
        except Exception as e:
            self.logger.error(f"Error en pre-validación de productos: {e}")
            return False, [f"Error interno en validación: {e}"]

    def _handle_entry_registration_error(self, error: Exception) -> str:
        """Manejar errores de registro (método original)"""
        error_str = str(error).lower()
        
        if 'servicio' in error_str:
            return (
                "Error de Validación: Productos SERVICIO Detectados\n\n"
                "Los SERVICIOS no pueden agregarse al inventario.\n"
                "Solo productos de tipo MATERIAL tienen stock.\n\n"
                "Revise la lista y remueva cualquier servicio."
            )
        
        if any(term in error_str for term in ['database', 'connection', 'sqlite']):
            return (
                "Error de Base de Datos\n\n"
                "No se pudo conectar con la base de datos.\n"
                "Verifique que el sistema esté funcionando correctamente."
            )
        
        return f"Error al registrar entrada: {error}"

    def _generate_ticket(self, ticket_number: str, products: List[Dict]) -> str:
        """Generar ticket PDF (CORRECCIÓN: Acceso correcto a Usuario)"""
        try:
            # CORRECCIÓN CRÍTICA: Acceso correcto a objeto Usuario
            current_user_obj = self.session_manager.get_current_user()
            if not current_user_obj:
                raise ValueError("No hay usuario autenticado para generar ticket")
            
            ticket_data = {
                'ticket_number': ticket_number,
                'tipo': 'ENTRADA',
                'fecha': datetime.now(),
                'responsable': current_user_obj.username,  # Acceso directo a la propiedad
                'productos': products
            }
            
            ticket_path = self.export_service.generate_entry_ticket(ticket_data)
            return ticket_path
            
        except Exception as e:
            self.logger.error(f"Error al generar ticket: {e}")
            return ""

    def _on_import_excel(self):
        """Importar desde Excel (placeholder)"""
        try:
            file_path = filedialog.askopenfilename(
                title="Seleccionar archivo Excel",
                filetypes=[("Excel files", "*.xlsx *.xls")]
            )
            
            if file_path:
                self._import_from_excel(file_path)
                
        except Exception as e:
            self.logger.error(f"Error en importación Excel: {e}")
            messagebox.showerror("Error", f"Error al importar Excel: {e}")

    def _import_from_excel(self, file_path: str):
        """Importar desde Excel (placeholder)"""
        messagebox.showinfo("Info", "Funcionalidad de importación Excel en desarrollo")

    def _validate_quantity_input(self, *args):
        """Validar entrada de cantidad en tiempo real"""
        current_value = self.quantity_var.get()
        
        if current_value == "":
            return
            
        if not current_value.isdigit():
            filtered = ''.join(filter(str.isdigit, current_value))
            self.quantity_var.set(filtered)


# ==================== FACTORY FUNCTION ====================

def create_movement_entry_form(
    parent: tk.Widget,
    db_connection: Any,
    event_bus: Optional[EventBusTkinter] = None
) -> MovementEntryForm:
    """
    Factory para crear MovementEntryForm con Event Bus
    
    Args:
        parent: Widget padre
        db_connection: Conexión a base de datos
        event_bus: Event Bus instance (opcional)
        
    Returns:
        MovementEntryForm: Formulario configurado con Event Bus
    """
    return MovementEntryForm(parent, db_connection, event_bus)


if __name__ == "__main__":
    # Test básico del formulario con Event Bus
    import sys
    import tkinter as tk
    from unittest.mock import Mock
    
    # Mock de servicios
    mock_db = Mock()
    
    # Crear ventana de prueba
    root = tk.Tk()
    root.title("Test MovementEntryForm con Event Bus")
    
    # Crear formulario
    form = create_movement_entry_form(root, mock_db)
    
    # Test event listener
    def test_listener(event_data):
        print(f"Evento recibido: {event_data.event_type}")
        print(f"Datos: {event_data.data}")
    
    event_bus = get_event_bus_tkinter()
    event_bus.register(EventTypes.MOVEMENT_ITEM_ADDED, test_listener)
    
    root.mainloop()
