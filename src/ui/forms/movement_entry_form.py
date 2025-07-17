"""
MovementEntryForm - Formulario para entradas al inventario
Implementa patrón MVP con servicios inyectados via ServiceContainer
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

# Imports del sistema
from services.service_container import get_container
from utils.logger import get_logger
from ui.widgets.product_search_widget import ProductSearchWidget


class MovementEntryForm:
    """
    Formulario para gestionar entradas al inventario
    
    Características:
    - Búsqueda de productos por ID o nombre
    - Validación de duplicados con suma de cantidades
    - Importación masiva Excel
    - Generación automática de tickets PDF
    - Validación tiempo real
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
        
        # Estado del formulario
        self.selected_products: List[Dict] = []
        self.current_search_results: List[Dict] = []
        
        # Logger
        self.logger = get_logger(__name__)
        
        # Crear interfaz
        self._create_interface()
        self._setup_event_bindings()
        
        self.logger.info("MovementEntryForm inicializado exitosamente")

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
        
        # Widget de búsqueda reutilizable
        self.search_widget = ProductSearchWidget(
            self.search_frame,
            self.product_service
        )
        self.search_widget.grid(row=0, column=0, sticky="ew", pady=5)
        
        # Configurar callbacks
        self.search_widget.on_product_selected = self._on_product_selected
        self.search_widget.on_search_completed = self._on_search_completed
        
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

    def _on_product_selected(self, product: Dict, double_click: bool = False):
        """Callback cuando se selecciona un producto del widget"""
        try:
            if double_click:
                # Auto-llenar cantidad con 1 en doble click
                self.quantity_var.set("1")
                self.quantity_entry.focus()
            
            self.logger.info(f"Producto seleccionado: {product['nombre']}")
            
        except Exception as e:
            self.logger.error(f"Error al seleccionar producto: {e}")

    def _on_search_completed(self, results: List[Dict]):
        """Callback cuando se completa una búsqueda"""
        self.current_search_results = results
        self.logger.info(f"Búsqueda completada: {len(results)} productos encontrados")

    def _on_add_clicked(self):
        """Manejar click en agregar producto"""
        selected_product = self.search_widget.get_selected_product()
        if not selected_product:
            messagebox.showwarning("Advertencia", "Seleccione un producto de la lista")
            return
            
        quantity_str = self.quantity_var.get().strip()
        if not self._validate_quantity(quantity_str):
            messagebox.showerror("Error", "Ingrese una cantidad válida (número entero positivo)")
            return
            
        try:
            quantity = int(quantity_str)
            
            self._add_product_to_list(selected_product, quantity)
            
            # Limpiar campos
            self.quantity_var.set("")
            self.search_widget.clear_selection()
            
        except Exception as e:
            self.logger.error(f"Error al agregar producto: {e}")
            messagebox.showerror("Error", f"Error al agregar producto: {e}")

    def _add_product_to_list(self, product: Dict, quantity: int):
        """
        Agregar producto a la lista (o sumar cantidad si ya existe)
        
        Args:
            product: Datos del producto
            quantity: Cantidad a agregar
        """
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
                'stock_original': product.get('stock', 0)
            }
            self.selected_products.append(product_data)
            self.logger.info(f"Producto agregado: {product['id']} - {quantity} unidades")
        
        # Actualizar vista
        self._update_products_tree()

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
        
        self.logger.info(f"Producto {product_id} removido de la lista")

    def _on_register_clicked(self):
        """Manejar click en registrar entrada"""
        if not self.selected_products:
            messagebox.showwarning("Advertencia", "Agregue productos antes de registrar")
            return
        
        if self._register_entry():
            messagebox.showinfo("Éxito", "Entrada registrada exitosamente")
            self._clear_form()

    def _register_entry(self) -> bool:
        """
        Registrar entrada al inventario
        
        Returns:
            bool: True si registro exitoso
        """
        try:
            current_user = self.session_manager.get_current_user()
            
            movement_data = {
                'tipo': 'ENTRADA',
                'fecha': datetime.now(),
                'responsable_id': current_user['id'],
                'productos': self.selected_products
            }
            
            result = self.movement_service.create_entry_movement(movement_data)
            
            # Generar ticket
            if result:
                ticket_path = self._generate_ticket(
                    result.get('ticket_number', 'ENT-000'),
                    self.selected_products
                )
                self.logger.info(f"Entrada registrada: {result['id']}, Ticket: {ticket_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error al registrar entrada: {e}")
            messagebox.showerror("Error", f"Error al registrar entrada: {e}")
            return False

    def _generate_ticket(self, ticket_number: str, products: List[Dict]) -> str:
        """
        Generar ticket PDF de entrada
        
        Args:
            ticket_number: Número de ticket
            products: Lista de productos
            
        Returns:
            str: Ruta del archivo PDF generado
        """
        try:
            current_user = self.session_manager.get_current_user()
            
            ticket_data = {
                'ticket_number': ticket_number,
                'tipo': 'ENTRADA',
                'fecha': datetime.now(),
                'responsable': current_user['username'],
                'productos': products
            }
            
            ticket_path = self.export_service.generate_entry_ticket(ticket_data)
            return ticket_path
            
        except Exception as e:
            self.logger.error(f"Error al generar ticket: {e}")
            return ""

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

    def _clear_form(self):
        """Limpiar todos los campos del formulario"""
        self.selected_products.clear()
        self.current_search_results.clear()
        
        self.quantity_var.set("")
        self.search_widget.clear_selection()
        self._update_products_tree()
        
        self.logger.info("Formulario limpiado")

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
