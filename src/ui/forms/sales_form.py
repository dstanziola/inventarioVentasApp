"""
Ventana de procesamiento de ventas con integración de códigos de barras - Modo Teclado.

REFACTORIZACIÓN v2.0 - MODO TECLADO:
- Eliminadas dependencias de hardware externo (hidapi, threads, device management)
- Integración directa con BarcodeEntry widget
- Código simplificado y más mantenible
- Compatible con cualquier lector HID configurado como teclado

Esta clase implementa la interfaz para el procesamiento completo de ventas,
incluyendo selección de productos, cálculos automáticos y generación de tickets.

FUNCIONALIDADES:
- Selección de productos para venta mediante códigos de barras
- Integración completa con códigos de barras en modo teclado
- Scanner automático y búsqueda manual simplificada
- Cálculo automático de totales e impuestos
- Asociación opcional de clientes
- Generación de tickets de venta
- Control de inventario automático

Autor: Sistema de Inventario Copy Point S.A.
Versión: 2.0.0 - Modo Teclado
Fecha: Julio 2025
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Optional
import logging
from decimal import Decimal

from db.database import get_database_connection
from services.sales_service import SalesService
from services.product_service import ProductService
from services.client_service import ClientService
from services.barcode_service import BarcodeService
from ui.widgets.barcode_entry import BarcodeEntry
from utils.barcode_utils import validate_barcode, BarcodeUtils


class SalesWindow:
    """Ventana de procesamiento de ventas con códigos de barras - Modo Teclado."""
    
    def __init__(self, parent: tk.Tk):
        """
        Inicializa la ventana de ventas.
        
        Args:
            parent: Ventana padre
        """
        self.parent = parent
        # Configurar servicios con dependencias correctas
        self.db_connection = get_database_connection()
        self.product_service = ProductService(self.db_connection)
        self.client_service = ClientService(self.db_connection)
        
        # Configurar SalesService con sus dependencias
        self.sales_service = SalesService(
            self.db_connection, 
            product_service=self.product_service,
            client_service=self.client_service
        )
        
        # Configurar BarcodeService sin dependencias de hardware
        self.barcode_service = BarcodeService()
        self.barcode_service.set_product_service(self.product_service)
        
        # Configurar logging
        self.logger = logging.getLogger(__name__)
        
        # Crear ventana
        self.root = tk.Toplevel(parent)
        self.root.title("Procesamiento de Ventas - Modo Teclado")
        self.root.geometry("1200x800")  # Tamaño optimizado
        self.root.transient(parent)
        self.root.grab_set()
        
        # Variables de la venta
        self.sale_items: List[Dict] = []
        self.selected_client = None
        
        # Variables de formulario
        self.barcode_var = tk.StringVar()
        self.quantity_var = tk.StringVar(value="1")
        self.client_var = tk.StringVar()
        self.subtotal_var = tk.StringVar(value="B/. 0.00")
        self.tax_var = tk.StringVar(value="B/. 0.00")
        self.total_var = tk.StringVar(value="B/. 0.00")
        
        # Crear interfaz
        self._create_ui()
        
        # Configurar eventos
        self._setup_events()
        
        # Cargar datos iniciales
        self._load_data()
        
        self.logger.info("SalesWindow inicializado en modo teclado (sin hardware)")
        
    def _create_ui(self):
        """Crea los elementos de la interfaz de usuario."""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configurar grid principal
        main_frame.columnconfigure(0, weight=2)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Título
        title_label = ttk.Label(
            main_frame,
            text="Nueva Venta - Modo Teclado",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Panel de entrada de productos con códigos de barras - ACTUALIZADO
        self._create_barcode_entry_panel(main_frame)
        
        # Panel de información del cliente
        self._create_client_panel(main_frame)
        
        # Panel de lista de productos de la venta
        self._create_sale_items_panel(main_frame)
        
        # Panel de totales
        self._create_totals_panel(main_frame)
        
        # Panel de botones
        self._create_button_panel(main_frame)
        
    def _create_barcode_entry_panel(self, parent):
        """Crea el panel de entrada de productos con códigos de barras - Modo Teclado."""
        # Frame de entrada de productos
        entry_frame = ttk.LabelFrame(parent, text="Agregar Producto por Código - Modo Teclado", padding=15)
        entry_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Configurar grid
        entry_frame.columnconfigure(1, weight=1)
        
        # Instrucciones
        instructions = ttk.Label(
            entry_frame,
            text="• Configure su lector de códigos de barras en modo HID teclado\\n"
                 "• Escanee código de barras o ingrese ID del producto manualmente\\n"
                 "• Presione Enter para agregar el producto a la venta",
            font=("Arial", 9),
            foreground="darkblue",
            justify=tk.LEFT
        )
        instructions.grid(row=0, column=0, columnspan=5, sticky=tk.W, pady=(0, 10))
        
        # Primera fila - Campo código de barras / ID producto
        ttk.Label(entry_frame, text="Código/ID:").grid(row=1, column=0, padx=(0, 5), sticky=tk.W)
        
        # Widget BarcodeEntry especializado
        self.barcode_entry = BarcodeEntry(
            entry_frame, 
            textvariable=self.barcode_var,
            on_scan_complete=self._on_barcode_scanned,
            validation_enabled=True,
            clear_after_scan=True,
            font=('Consolas', 12),
            width=25
        )
        self.barcode_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Campo cantidad
        ttk.Label(entry_frame, text="Cantidad:").grid(row=1, column=2, padx=(5, 5), sticky=tk.W)
        self.quantity_entry = ttk.Entry(entry_frame, textvariable=self.quantity_var, width=8)
        self.quantity_entry.grid(row=1, column=3, padx=(0, 10))
        
        # Botón agregar
        self.add_button = ttk.Button(
            entry_frame,
            text="Agregar",
            command=self._add_product_to_sale
        )
        self.add_button.grid(row=1, column=4)
        
        # Segunda fila - Información del producto y acciones
        info_frame = ttk.Frame(entry_frame)
        info_frame.grid(row=2, column=0, columnspan=5, sticky=(tk.W, tk.E), pady=(10, 0))
        info_frame.columnconfigure(2, weight=1)
        
        # Estado del producto encontrado
        self.product_status_label = ttk.Label(
            info_frame, 
            text="Esperando código...",
            font=('Arial', 9),
            foreground='gray'
        )
        self.product_status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Botones de acción
        ttk.Button(
            info_frame,
            text="Buscar Manual",
            command=self._manual_search,
            width=12
        ).grid(row=0, column=3, padx=(10, 5))
        
        ttk.Button(
            info_frame,
            text="Limpiar",
            command=self._clear_barcode
        ).grid(row=0, column=4, padx=(5, 0))
        
    def _create_client_panel(self, parent):
        """Crea el panel de información del cliente."""
        # Frame de cliente
        client_frame = ttk.LabelFrame(parent, text="Cliente (Opcional)", padding=10)
        client_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 10))
        
        # Configurar grid
        client_frame.columnconfigure(1, weight=1)
        
        # ComboBox de clientes
        ttk.Label(client_frame, text="Cliente:").grid(row=0, column=0, padx=(0, 5), sticky=tk.W)
        self.client_combo = ttk.Combobox(
            client_frame,
            textvariable=self.client_var,
            state='readonly',
            width=25
        )
        self.client_combo.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Botón nuevo cliente
        ttk.Button(
            client_frame,
            text="Nuevo Cliente",
            command=self._create_new_client
        ).grid(row=1, column=1, sticky=tk.E, pady=(5, 0))
        
    def _create_sale_items_panel(self, parent):
        """Crea el panel de lista de productos de la venta."""
        # Frame de items de venta
        items_frame = ttk.LabelFrame(parent, text="Productos en la Venta", padding=10)
        items_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Configurar grid
        items_frame.columnconfigure(0, weight=1)
        items_frame.rowconfigure(0, weight=1)
        
        # TreeView para items de venta - ACTUALIZADO con códigos
        columns = ('Código', 'Producto', 'Cantidad', 'Precio Unit.', 'Subtotal', 'Impuesto', 'Total')
        self.items_tree = ttk.Treeview(items_frame, columns=columns, show='headings', height=10)
        
        # Configurar columnas
        for col in columns:
            self.items_tree.heading(col, text=col)
            
        self.items_tree.column('Código', width=100)
        self.items_tree.column('Producto', width=200)
        self.items_tree.column('Cantidad', width=80)
        self.items_tree.column('Precio Unit.', width=100)
        self.items_tree.column('Subtotal', width=100)
        self.items_tree.column('Impuesto', width=100)
        self.items_tree.column('Total', width=100)
        
        # Scrollbar para TreeView
        scrollbar = ttk.Scrollbar(items_frame, orient=tk.VERTICAL, command=self.items_tree.yview)
        self.items_tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid TreeView y scrollbar
        self.items_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Frame de botones para items
        items_buttons_frame = ttk.Frame(items_frame)
        items_buttons_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Botones para manejo de items
        ttk.Button(
            items_buttons_frame,
            text="Quitar Seleccionado",
            command=self._remove_selected_item
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            items_buttons_frame,
            text="Limpiar Todo",
            command=self._clear_all_items
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Información de estado
        self.items_info_label = ttk.Label(
            items_buttons_frame,
            text="0 productos en la venta",
            font=('Arial', 9),
            foreground='gray'
        )
        self.items_info_label.pack(side=tk.RIGHT)
        
    def _create_totals_panel(self, parent):
        """Crea el panel de totales."""
        # Frame de totales
        totals_frame = ttk.LabelFrame(parent, text="Totales", padding=10)
        totals_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Configurar grid
        totals_frame.columnconfigure(1, weight=1)
        totals_frame.columnconfigure(3, weight=1)
        
        # Subtotal
        ttk.Label(totals_frame, text="Subtotal:", font=("Arial", 12)).grid(row=0, column=0, padx=(0, 10))
        ttk.Label(totals_frame, textvariable=self.subtotal_var, font=("Arial", 12, "bold")).grid(row=0, column=1)
        
        # Impuestos
        ttk.Label(totals_frame, text="Impuestos:", font=("Arial", 12)).grid(row=0, column=2, padx=(20, 10))
        ttk.Label(totals_frame, textvariable=self.tax_var, font=("Arial", 12, "bold")).grid(row=0, column=3)
        
        # Total
        ttk.Label(totals_frame, text="TOTAL:", font=("Arial", 14, "bold")).grid(row=1, column=0, columnspan=2, pady=(10, 0))
        ttk.Label(
            totals_frame, 
            textvariable=self.total_var, 
            font=("Arial", 16, "bold"), 
            foreground="darkgreen"
        ).grid(row=1, column=2, columnspan=2, pady=(10, 0))
        
    def _create_button_panel(self, parent):
        """Crea el panel de botones."""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Botones principales
        self.process_sale_button = ttk.Button(
            button_frame,
            text="Procesar Venta",
            command=self._process_sale,
            state='disabled'
        )
        self.process_sale_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            button_frame,
            text="Cancelar Venta",
            command=self._cancel_sale
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            button_frame,
            text="Cerrar",
            command=self._close_window
        ).pack(side=tk.RIGHT)
        
    def _setup_events(self):
        """Configura eventos de la ventana."""
        # Enter en cantidad para agregar producto
        self.quantity_entry.bind('<Return>', lambda e: self._add_product_to_sale())
        
        # Selección de cliente
        self.client_combo.bind('<<ComboboxSelected>>', self._on_client_select)
        
        # Protocolo de cierre
        self.root.protocol("WM_DELETE_WINDOW", self._close_window)
        
        # Foco inicial en código de barras
        self.barcode_entry.focus()
        
    def _load_data(self):
        """Carga los datos iniciales."""
        try:
            # Cargar clientes para ComboBox
            clients = self.client_service.get_all_clients()
            client_options = ["Venta sin cliente"] + [f"{client.nombre} - {client.ruc if client.ruc else 'Sin RUC'}" for client in clients]
            self.client_combo['values'] = client_options
            self.client_combo.current(0)  # Seleccionar "Venta sin cliente"
            
            self.logger.info("Datos cargados para nueva venta con códigos de barras en modo teclado")
            
        except Exception as e:
            self.logger.error(f"Error al cargar datos: {e}")
            messagebox.showerror("Error", f"No se pudieron cargar los datos: {e}")
    
    # ===== MÉTODOS DE CÓDIGOS DE BARRAS - MODO TECLADO =====
    
    def _on_barcode_scanned(self, code: str, is_valid: bool = True):
        """
        Callback ejecutado cuando se escanea un código de barras.
        
        Args:
            code: Código escaneado
            is_valid: Si el código tiene formato válido
        """
        try:
            self.logger.info(f"Código escaneado en ventas: {code}, válido: {is_valid}")
            
            if not is_valid:
                self.product_status_label.config(
                    text=f"✗ Código inválido: {code}",
                    foreground="red"
                )
                return
            
            # Actualizar estado
            self.product_status_label.config(
                text=f"Buscando producto: {code}...",
                foreground="blue"
            )
            
            # Buscar producto
            producto = self._search_product_by_code(code)
            
            if producto:
                # Producto encontrado - agregarlo automáticamente a la venta
                self._auto_add_product_to_sale(producto, code)
            else:
                self.product_status_label.config(
                    text=f"✗ Producto no encontrado: {code}",
                    foreground="red"
                )
                
                # Ofrecer búsqueda manual
                messagebox.showinfo(
                    "Producto No Encontrado",
                    f"No se encontró producto con código: {code}\\n\\n"
                    f"Verifique el código o agregue el producto manualmente."
                )
                
        except Exception as e:
            self.logger.error(f"Error procesando código escaneado {code}: {e}")
            self.product_status_label.config(
                text="Error procesando código",
                foreground="red"
            )
            messagebox.showerror("Error", f"Error procesando código: {e}")
    
    def _search_product_by_code(self, code: str):
        """
        Buscar producto por código de barras o ID.
        
        Args:
            code: Código de barras o ID del producto
            
        Returns:
            Producto encontrado o None
        """
        try:
            # Usar BarcodeService para búsqueda
            producto = self.barcode_service.search_product_by_code(code)
            
            if producto:
                self.logger.info(f"Producto encontrado por código: {code}")
                return producto
            
            # Si no se encuentra por código, intentar por ID si es numérico
            if code.isdigit():
                product_id = int(code)
                producto = self.product_service.get_product_by_id(product_id)
                
                if producto:
                    self.logger.info(f"Producto encontrado por ID: {product_id}")
                    return producto
            
            self.logger.warning(f"No se encontró producto para código: {code}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error buscando producto por código {code}: {e}")
            return None
    
    def _auto_add_product_to_sale(self, producto, code: str):
        """
        Agregar producto automáticamente a la venta después del escaneo.
        
        Args:
            producto: Producto a agregar
            code: Código escaneado
        """
        try:
            # Validar producto
            if not self._validate_product_for_sale(producto):
                return
            
            # Obtener cantidad actual
            quantity_str = self.quantity_var.get().strip()
            if not quantity_str or not quantity_str.isdigit() or int(quantity_str) <= 0:
                quantity = 1  # Cantidad por defecto
                self.quantity_var.set("1")
            else:
                quantity = int(quantity_str)
            
            # Verificar stock disponible
            if producto.stock is not None and producto.stock < quantity:
                if not messagebox.askyesno(
                    "Stock Insuficiente",
                    f"Stock disponible: {producto.stock}\\n"
                    f"Cantidad solicitada: {quantity}\\n\\n"
                    f"¿Desea continuar con la venta?"
                ):
                    self.product_status_label.config(
                        text="Venta cancelada por stock insuficiente",
                        foreground="orange"
                    )
                    return
            
            # Agregar producto a la venta
            self._add_product_item(producto, quantity, code)
            
            # Actualizar estado
            self.product_status_label.config(
                text=f"✓ Agregado: {producto.nombre} (x{quantity})",
                foreground="green"
            )
            
            # Mostrar confirmación breve
            self.root.after(2000, self._clear_product_status)
            
        except Exception as e:
            self.logger.error(f"Error agregando producto automáticamente: {e}")
            messagebox.showerror("Error", f"Error agregando producto: {e}")
    
    def _validate_product_for_sale(self, producto) -> bool:
        """
        Validar que el producto puede ser vendido.
        
        Args:
            producto: Producto a validar
            
        Returns:
            bool: True si el producto es válido para venta
        """
        try:
            # Verificar que esté activo
            if not getattr(producto, 'activo', True):
                messagebox.showwarning(
                    "Producto Inactivo",
                    f"El producto '{producto.nombre}' está marcado como inactivo."
                )
                return False
            
            # Verificar que tenga precio
            precio = getattr(producto, 'precio', 0)
            if precio <= 0:
                if not messagebox.askyesno(
                    "Sin Precio",
                    f"El producto '{producto.nombre}' no tiene precio configurado.\\n\\n"
                    f"¿Desea continuar?"
                ):
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validando producto: {e}")
            return False
    
    def _add_product_item(self, producto, quantity: int, code: str):
        """
        Agregar producto como item a la venta.
        
        Args:
            producto: Producto a agregar
            quantity: Cantidad
            code: Código usado para encontrar el producto
        """
        try:
            # Verificar si el producto ya está en la venta
            existing_item = None
            for item in self.sale_items:
                if item['product'].id_producto == producto.id_producto:
                    existing_item = item
                    break
            
            precio_unitario = getattr(producto, 'precio', Decimal('0.00'))
            tasa_impuesto = getattr(producto, 'tasa_impuesto', 0) or 0
            
            if existing_item:
                # Actualizar cantidad existente
                new_quantity = existing_item['quantity'] + quantity
                existing_item['quantity'] = new_quantity
                existing_item['subtotal'] = existing_item['precio_unitario'] * new_quantity
                existing_item['impuesto'] = existing_item['subtotal'] * tasa_impuesto / 100
                existing_item['total'] = existing_item['subtotal'] + existing_item['impuesto']
                
                # Actualizar TreeView
                for child in self.items_tree.get_children():
                    item_values = self.items_tree.item(child, 'values')
                    if item_values[0] == code:  # Comparar por código
                        self.items_tree.item(child, values=(
                            code,
                            producto.nombre,
                            str(new_quantity),
                            f"B/. {existing_item['precio_unitario']:.2f}",
                            f"B/. {existing_item['subtotal']:.2f}",
                            f"B/. {existing_item['impuesto']:.2f}",
                            f"B/. {existing_item['total']:.2f}"
                        ))
                        break
            else:
                # Agregar nuevo item
                subtotal = precio_unitario * quantity
                impuesto = subtotal * tasa_impuesto / 100
                total = subtotal + impuesto
                
                sale_item = {
                    'code': code,
                    'product': producto,
                    'quantity': quantity,
                    'precio_unitario': precio_unitario,
                    'subtotal': subtotal,
                    'impuesto': impuesto,
                    'total': total
                }
                
                self.sale_items.append(sale_item)
                
                # Agregar al TreeView
                self.items_tree.insert('', 'end', values=(
                    code,
                    producto.nombre,
                    str(quantity),
                    f"B/. {precio_unitario:.2f}",
                    f"B/. {subtotal:.2f}",
                    f"B/. {impuesto:.2f}",
                    f"B/. {total:.2f}"
                ))
            
            # Actualizar totales y UI
            self._update_totals()
            self._update_items_info()
            
        except Exception as e:
            self.logger.error(f"Error agregando item a la venta: {e}")
            raise
    
    def _manual_search(self):
        """Buscar producto manualmente usando el código ingresado."""
        try:
            code = self.barcode_var.get().strip()
            
            if not code:
                messagebox.showwarning("Código Vacío", "Ingrese un código de barras o ID de producto")
                self.barcode_entry.focus()
                return
            
            # Simular escaneo manual
            self._on_barcode_scanned(code, is_valid=True)
            
        except Exception as e:
            self.logger.error(f"Error en búsqueda manual: {e}")
            messagebox.showerror("Error", f"Error en búsqueda manual: {e}")
    
    def _clear_barcode(self):
        """Limpiar campo de código de barras."""
        self.barcode_var.set("")
        self.barcode_entry.focus()
        self._clear_product_status()
    
    def _clear_product_status(self):
        """Limpiar estado del producto."""
        self.product_status_label.config(
            text="Esperando código...",
            foreground="gray"
        )
    
    # ===== MÉTODOS DE GESTIÓN DE VENTA =====
            
    def _add_product_to_sale(self):
        """Agregar un producto a la venta usando código o ID (método manual)."""
        try:
            code_or_id = self.barcode_var.get().strip()
            quantity_str = self.quantity_var.get().strip()
            
            # Validar entrada
            if not code_or_id:
                messagebox.showwarning("Código Vacío", "Ingrese un código de barras o ID de producto")
                return
            
            if not quantity_str or not quantity_str.isdigit() or int(quantity_str) <= 0:
                messagebox.showwarning("Cantidad Inválida", "Ingrese una cantidad válida mayor a 0")
                return
            
            quantity = int(quantity_str)
            
            # Buscar producto
            product = self._search_product_by_code(code_or_id)
            
            if not product:
                messagebox.showerror(
                    "Producto No Encontrado", 
                    f"No se encontró producto con código/ID: {code_or_id}"
                )
                return
            
            # Validar producto
            if not self._validate_product_for_sale(product):
                return
            
            # Verificar stock disponible
            if product.stock is not None and product.stock < quantity:
                if not messagebox.askyesno(
                    "Stock Insuficiente",
                    f"Stock disponible: {product.stock}\\n"
                    f"Cantidad solicitada: {quantity}\\n\\n"
                    f"¿Desea continuar con la venta?"
                ):
                    return
            
            # Agregar producto
            self._add_product_item(product, quantity, code_or_id)
            
            # Limpiar campos
            self._clear_barcode()
            self.quantity_var.set("1")
            
            # Mostrar confirmación
            messagebox.showinfo(
                "Producto Agregado",
                f"Producto agregado: {product.nombre}\\n"
                f"Cantidad: {quantity}"
            )
            
        except Exception as e:
            self.logger.error(f"Error agregando producto: {e}")
            messagebox.showerror("Error", f"Error agregando producto: {e}")
        
    def _remove_selected_item(self):
        """Quita el item seleccionado de la venta."""
        try:
            selected_items = self.items_tree.selection()
            
            if not selected_items:
                messagebox.showwarning("Sin Selección", "Seleccione un producto para quitar")
                return
            
            # Obtener item seleccionado
            selected_item = selected_items[0]
            item_values = self.items_tree.item(selected_item, 'values')
            product_code = item_values[0]
            
            # Confirmar eliminación
            if messagebox.askyesno(
                "Confirmar",
                f"¿Quitar producto {item_values[1]} de la venta?"
            ):
                # Eliminar del TreeView
                self.items_tree.delete(selected_item)
                
                # Eliminar de la lista
                self.sale_items = [item for item in self.sale_items if item['code'] != product_code]
                
                self._update_totals()
                self._update_items_info()
                
        except Exception as e:
            self.logger.error(f"Error quitando item: {e}")
            messagebox.showerror("Error", f"Error quitando producto: {e}")
        
    def _clear_all_items(self):
        """Limpia todos los items de la venta."""
        if self.sale_items:
            if messagebox.askyesno(
                "Confirmar",
                "¿Está seguro de limpiar todos los productos de la venta?"
            ):
                self.sale_items.clear()
                # Limpiar TreeView
                for item in self.items_tree.get_children():
                    self.items_tree.delete(item)
                self._update_totals()
                self._update_items_info()
        
    def _update_totals(self):
        """Actualiza los totales de la venta."""
        try:
            if not self.sale_items:
                self.subtotal_var.set("B/. 0.00")
                self.tax_var.set("B/. 0.00")
                self.total_var.set("B/. 0.00")
                self.process_sale_button.config(state='disabled')
                return
            
            # Calcular totales
            subtotal = sum(item['subtotal'] for item in self.sale_items)
            impuestos = sum(item['impuesto'] for item in self.sale_items)
            total = subtotal + impuestos
            
            # Actualizar variables
            self.subtotal_var.set(f"B/. {subtotal:.2f}")
            self.tax_var.set(f"B/. {impuestos:.2f}")
            self.total_var.set(f"B/. {total:.2f}")
            
            # Habilitar botón de procesar
            self.process_sale_button.config(state='normal')
            
        except Exception as e:
            self.logger.error(f"Error actualizando totales: {e}")
    
    def _update_items_info(self):
        """Actualizar información de items."""
        count = len(self.sale_items)
        if count == 0:
            self.items_info_label.config(text="0 productos en la venta")
        elif count == 1:
            self.items_info_label.config(text="1 producto en la venta")
        else:
            self.items_info_label.config(text=f"{count} productos en la venta")
            
    def _on_client_select(self, event):
        """Maneja la selección de cliente."""
        try:
            client_selection = self.client_var.get()
            
            if client_selection and client_selection != "Venta sin cliente":
                # Extraer información del cliente
                # Format: "Nombre - RUC" or "Nombre - Sin RUC"
                client_name = client_selection.split(" - ")[0]
                clients = self.client_service.get_all_clients()
                
                self.selected_client = next(
                    (client for client in clients if client.nombre == client_name), 
                    None
                )
            else:
                self.selected_client = None
                
        except Exception as e:
            self.logger.error(f"Error seleccionando cliente: {e}")
        
    def _create_new_client(self):
        """Abre ventana para crear nuevo cliente."""
        messagebox.showinfo("En Desarrollo", "Funcionalidad de crear cliente en desarrollo")
        
    def _process_sale(self):
        """Procesa la venta completa."""
        if not self.sale_items:
            messagebox.showwarning("Venta Vacía", "Debe agregar productos a la venta")
            return
            
        try:
            # Confirmar venta
            total_amount = sum(item['total'] for item in self.sale_items)
            item_count = len(self.sale_items)
            
            confirm_msg = f"Procesar venta:\\n\\n"
            confirm_msg += f"Productos: {item_count} items\\n"
            confirm_msg += f"Total: B/. {total_amount:.2f}\\n"
            
            if self.selected_client:
                confirm_msg += f"Cliente: {self.selected_client.nombre}\\n"
            
            confirm_msg += "\\n¿Confirmar venta?"
            
            if not messagebox.askyesno("Confirmar Venta", confirm_msg):
                return
            
            # Crear venta usando SalesService
            try:
                # Obtener usuario actual para responsable
                from ui.auth.session_manager import session_manager
                current_user = session_manager.get_current_user()
                responsable = current_user.get('nombre_usuario', 'vendedor') if current_user else 'vendedor'
                
                # Crear venta
                cliente_id = self.selected_client.id_cliente if self.selected_client else None
                venta = self.sales_service.create_sale(responsable=responsable, id_cliente=cliente_id)
                
                # Agregar productos a la venta
                for sale_item in self.sale_items:
                    producto = sale_item['product']
                    cantidad = sale_item['quantity']
                    precio = float(sale_item['precio_unitario'])
                    
                    # Agregar producto (esto actualizará stock automáticamente)
                    self.sales_service.add_product_to_sale(
                        id_venta=venta.id_venta,
                        id_producto=producto.id_producto,
                        cantidad=cantidad,
                        precio_unitario=precio
                    )
                
                # Mostrar mensaje de éxito con ID real de venta
                messagebox.showinfo(
                    "Venta Procesada", 
                    f"Venta procesada exitosamente\\n"
                    f"ID Venta: {venta.id_venta}\\n"
                    f"Total: B/. {total_amount:.2f}\\n"
                    f"Stock actualizado automáticamente"
                )
                
            except Exception as venta_error:
                messagebox.showerror(
                    "Error en Venta",
                    f"Error procesando venta: {venta_error}\\n\\n"
                    f"La venta no se pudo completar."
                )
                return  # No limpiar si hay error
            
            # Limpiar venta
            self._clear_all_items()
            self.selected_client = None
            self.client_combo.current(0)
            
        except Exception as e:
            self.logger.error(f"Error procesando venta: {e}")
            messagebox.showerror("Error", f"Error procesando venta: {e}")
        
    def _cancel_sale(self):
        """Cancela la venta actual."""
        if self.sale_items:
            result = messagebox.askyesno(
                "Cancelar Venta",
                "¿Está seguro que desea cancelar la venta actual?\\nSe perderán todos los productos agregados."
            )
            if result:
                self._clear_all_items()
                self.selected_client = None
                self.client_combo.current(0)
        
    def _close_window(self):
        """Cierra la ventana."""
        try:
            if self.sale_items:
                result = messagebox.askyesno(
                    "Confirmar Cierre",
                    "Hay una venta en proceso. ¿Está seguro que desea cerrar?"
                )
                if not result:
                    return
            
            self.root.destroy()
            
        except Exception as e:
            self.logger.error(f"Error cerrando ventana: {e}")
            self.root.destroy()
