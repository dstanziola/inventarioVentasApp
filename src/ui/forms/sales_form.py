"""
Ventana de procesamiento de ventas con integración de códigos de barras.

Esta clase implementa la interfaz para el procesamiento completo de ventas,
incluyendo selección de productos, cálculos automáticos y generación de tickets.

FUNCIONALIDADES:
- Selección de productos para venta
- NUEVO: Integración completa con códigos de barras
- NUEVO: Scanner automático y búsqueda manual
- Cálculo automático de totales e impuestos
- Asociación opcional de clientes
- Generación de tickets de venta
- Control de inventario automático

Autor: Sistema de Inventario Copy Point S.A.
Fecha: Junio 2025 - FASE 4 (Actualizado)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Optional
import logging
from decimal import Decimal
import threading

from db.database import get_database_connection
from services.sales_service import SalesService
from services.product_service import ProductService
from services.client_service import ClientService
from services.barcode_service import BarcodeService  # NUEVO
from utils.barcode_utils import validate_barcode, BarcodeUtils  # NUEVO


class SalesWindow:
    """Ventana de procesamiento de ventas con códigos de barras."""
    
    def __init__(self, parent: tk.Tk):
        """
        Inicializa la ventana de ventas.
        
        Args:
            parent: Ventana padre
        """
        self.parent = parent
        self.sales_service = SalesService(get_database_connection())
        self.product_service = ProductService(get_database_connection())
        self.client_service = ClientService(get_database_connection())
        self.barcode_service = BarcodeService()  # NUEVO
        
        # CORRECCIÓN CRÍTICA: Configurar ProductService en BarcodeService
        self.barcode_service.set_product_service(self.product_service)
        
        # Configurar logging
        self.logger = logging.getLogger(__name__)
        
        # Variables del scanner - NUEVO
        self.scanner_active = False
        self.scanner_thread = None
        
        # Crear ventana
        self.root = tk.Toplevel(parent)
        self.root.title("Procesamiento de Ventas - Con Códigos de Barras")
        self.root.geometry("1300x850")  # Más ancho para acomodar scanner
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
        
        # Variables del scanner - NUEVO
        self.scanner_status_var = tk.StringVar(value="Desconectado")
        self.last_scanned_var = tk.StringVar(value="")
        self.barcode_format_var = tk.StringVar(value="")
        
        # Crear interfaz
        self._create_ui()
        
        # Configurar eventos
        self._setup_events()
        
        # Cargar datos iniciales
        self._load_data()
        
        # Verificar estado del scanner - NUEVO
        self._check_scanner_status()
        
        # Iniciar verificación de scanner - NUEVO
        self._start_scanner_check()
        
    def _create_ui(self):
        """Crea los elementos de la interfaz de usuario."""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configurar grid principal
        main_frame.columnconfigure(0, weight=2)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Título
        title_label = ttk.Label(
            main_frame,
            text="Nueva Venta - Con Códigos de Barras",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Panel de entrada de productos con códigos de barras - ACTUALIZADO
        self._create_barcode_entry_panel(main_frame)
        
        # Panel de información del cliente
        self._create_client_panel(main_frame)
        
        # Panel de estado del scanner - NUEVO
        self._create_scanner_status_panel(main_frame)
        
        # Panel de lista de productos de la venta
        self._create_sale_items_panel(main_frame)
        
        # Panel de totales
        self._create_totals_panel(main_frame)
        
        # Panel de botones
        self._create_button_panel(main_frame)
        
    def _create_barcode_entry_panel(self, parent):
        """Crea el panel de entrada de productos con códigos de barras."""
        # Frame de entrada de productos - ACTUALIZADO
        entry_frame = ttk.LabelFrame(parent, text="Agregar Producto por Código", padding=10)
        entry_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Configurar grid
        entry_frame.columnconfigure(1, weight=1)
        
        # Primera fila - Campo código de barras / ID producto
        ttk.Label(entry_frame, text="Código/ID:").grid(row=0, column=0, padx=(0, 5))
        
        # Entry con estilo especial para códigos
        self.barcode_entry = ttk.Entry(
            entry_frame, 
            textvariable=self.barcode_var, 
            width=25,
            font=('Consolas', 12)  # Fuente monoespaciada para códigos
        )
        self.barcode_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # Campo cantidad
        ttk.Label(entry_frame, text="Cantidad:").grid(row=0, column=2, padx=(5, 5))
        self.quantity_entry = ttk.Entry(entry_frame, textvariable=self.quantity_var, width=8)
        self.quantity_entry.grid(row=0, column=3, padx=(0, 5))
        
        # Botón agregar
        self.add_button = ttk.Button(
            entry_frame,
            text="Agregar",
            command=self._add_product_to_sale
        )
        self.add_button.grid(row=0, column=4, padx=(5, 0))
        
        # Segunda fila - Información del código y botones del scanner
        info_frame = ttk.Frame(entry_frame)
        info_frame.grid(row=1, column=0, columnspan=5, sticky=(tk.W, tk.E), pady=(10, 0))
        info_frame.columnconfigure(1, weight=1)
        
        # Formato del código - NUEVO
        ttk.Label(info_frame, text="Formato:").grid(row=0, column=0, padx=(0, 5))
        self.format_label = ttk.Label(
            info_frame, 
            textvariable=self.barcode_format_var,
            foreground='blue',
            font=('Arial', 9, 'bold')
        )
        self.format_label.grid(row=0, column=1, sticky=tk.W)
        
        # Botón de scanner - NUEVO
        self.scanner_button = ttk.Button(
            info_frame,
            text="Activar Scanner",
            command=self._toggle_scanner
        )
        self.scanner_button.grid(row=0, column=2, padx=(10, 5))
        
        # Botón limpiar código - NUEVO
        ttk.Button(
            info_frame,
            text="Limpiar",
            command=self._clear_barcode
        ).grid(row=0, column=3)
        
        # Tercera fila - Instrucciones
        instructions = ttk.Label(
            entry_frame,
            text="• Escanee código de barras o ingrese ID del producto\n"
                 "• Presione Enter para agregar producto\n"
                 "• Active el scanner para lectura automática",
            font=("Arial", 9),
            foreground="gray",
            justify=tk.LEFT
        )
        instructions.grid(row=2, column=0, columnspan=5, pady=(10, 0), sticky=tk.W)
        
    def _create_scanner_status_panel(self, parent):
        """Crea el panel de estado del scanner - NUEVO."""
        status_frame = ttk.LabelFrame(parent, text="Estado del Scanner", padding=10)
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Configurar grid
        status_frame.columnconfigure(1, weight=1)
        
        # Estado de conexión
        ttk.Label(status_frame, text="Estado:").grid(row=0, column=0, padx=(0, 10))
        self.scanner_status_label = ttk.Label(
            status_frame, 
            textvariable=self.scanner_status_var,
            font=('Arial', 10, 'bold')
        )
        self.scanner_status_label.grid(row=0, column=1, sticky=tk.W)
        
        # Indicador visual
        self.scanner_indicator = tk.Label(
            status_frame, 
            text="●", 
            foreground='red', 
            font=('Arial', 14, 'bold')
        )
        self.scanner_indicator.grid(row=0, column=2, padx=(10, 0))
        
        # Último código escaneado
        ttk.Label(status_frame, text="Último escaneado:").grid(row=0, column=3, padx=(20, 5))
        self.last_scanned_label = ttk.Label(
            status_frame,
            textvariable=self.last_scanned_var,
            font=('Consolas', 10),
            foreground='darkgreen'
        )
        self.last_scanned_label.grid(row=0, column=4, sticky=tk.W)
        
        # Botón configurar scanner
        ttk.Button(
            status_frame,
            text="Configurar",
            command=self._configure_scanner
        ).grid(row=0, column=5, padx=(20, 0))
        
    def _create_client_panel(self, parent):
        """Crea el panel de información del cliente."""
        # Frame de cliente
        client_frame = ttk.LabelFrame(parent, text="Cliente (Opcional)", padding=10)
        client_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 10))
        
        # Configurar grid
        client_frame.columnconfigure(1, weight=1)
        
        # ComboBox de clientes
        ttk.Label(client_frame, text="Cliente:").grid(row=0, column=0, padx=(0, 5))
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
        items_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Configurar grid
        items_frame.columnconfigure(0, weight=1)
        items_frame.rowconfigure(0, weight=1)
        
        # TreeView para items de venta - ACTUALIZADO con códigos
        columns = ('Código', 'Producto', 'Cantidad', 'Precio Unit.', 'Subtotal', 'Impuesto', 'Total')
        self.items_tree = ttk.Treeview(items_frame, columns=columns, show='headings', height=10)
        
        # Configurar columnas
        for col in columns:
            self.items_tree.heading(col, text=col)
            
        self.items_tree.column('Código', width=100)      # NUEVO
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
        
        # Nuevo botón para buscar productos - NUEVO
        ttk.Button(
            items_buttons_frame,
            text="Búsqueda Avanzada",
            command=self._open_barcode_search
        ).pack(side=tk.LEFT)
        
    def _create_totals_panel(self, parent):
        """Crea el panel de totales."""
        # Frame de totales
        totals_frame = ttk.LabelFrame(parent, text="Totales", padding=10)
        totals_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
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
        button_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
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
        
        # Nuevo botón para generar etiquetas - NUEVO
        ttk.Button(
            button_frame,
            text="Generar Etiquetas",
            command=self._generate_labels_for_sale
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            button_frame,
            text="Cerrar",
            command=self._close_window
        ).pack(side=tk.RIGHT)
        
    def _setup_events(self):
        """Configura eventos de la ventana."""
        # Enter en código de barras para agregar producto
        self.barcode_entry.bind('<Return>', lambda e: self._add_product_to_sale())
        
        # Enter en cantidad para agregar producto
        self.quantity_entry.bind('<Return>', lambda e: self._add_product_to_sale())
        
        # Cambios en código de barras para detectar formato - NUEVO
        self.barcode_var.trace('w', self._on_barcode_changed)
        
        # Foco inicial en código de barras
        self.barcode_entry.focus()
        
        # Selección de cliente
        self.client_combo.bind('<<ComboboxSelected>>', self._on_client_select)
        
        # Protocolo de cierre
        self.root.protocol("WM_DELETE_WINDOW", self._close_window)
        
    def _load_data(self):
        """Carga los datos iniciales."""
        try:
            # Cargar clientes para ComboBox
            clients = self.client_service.get_all_clients()
            client_options = ["Venta sin cliente"] + [f"{client.nombre} - {client.ruc if client.ruc else 'Sin RUC'}" for client in clients]
            self.client_combo['values'] = client_options
            self.client_combo.current(0)  # Seleccionar "Venta sin cliente"
            
            self.logger.info("Datos cargados para nueva venta con códigos de barras")
            
        except Exception as e:
            self.logger.error(f"Error al cargar datos: {e}")
            messagebox.showerror("Error", f"No se pudieron cargar los datos: {e}")
    
    # === NUEVOS MÉTODOS PARA CÓDIGOS DE BARRAS ===
    
    def _check_scanner_status(self):
        """Verifica el estado del scanner - NUEVO."""
        try:
            connected = self.barcode_service.is_connected()
            
            if connected:
                self.scanner_status_var.set("Conectado")
                self.scanner_indicator.config(foreground='green')
                self.scanner_button.config(state=tk.NORMAL)
            else:
                self.scanner_status_var.set("Desconectado")
                self.scanner_indicator.config(foreground='red')
                self.scanner_button.config(state=tk.DISABLED)
                
        except Exception as e:
            self.logger.error(f"Error verificando estado del scanner: {e}")
            self.scanner_status_var.set("Error")
            self.scanner_indicator.config(foreground='orange')
    
    def _toggle_scanner(self):
        """Activa/desactiva el scanner automático - NUEVO."""
        try:
            if not self.scanner_active:
                if self.barcode_service.is_connected():
                    self.scanner_active = True
                    self.scanner_button.config(text="Detener Scanner")
                    self.scanner_indicator.config(foreground='green')
                    messagebox.showinfo("Scanner", "Scanner activado - Listo para escanear códigos")
                else:
                    messagebox.showerror("Error", "No se detectó ningún scanner conectado")
            else:
                self.scanner_active = False
                self.scanner_button.config(text="Activar Scanner")
                self._check_scanner_status()
                messagebox.showinfo("Scanner", "Scanner desactivado")
                
        except Exception as e:
            self.logger.error(f"Error activando scanner: {e}")
            messagebox.showerror("Error", f"Error con el scanner: {e}")
    
    def _start_scanner_check(self):
        """Inicia el hilo de verificación del scanner - NUEVO."""
        if self.scanner_active:
            try:
                # Leer código del scanner
                code = self.barcode_service.read_code(timeout=0.1)
                
                if code and code.strip():
                    # Código detectado automáticamente
                    self.barcode_var.set(code.strip())
                    self.last_scanned_var.set(code.strip())
                    
                    # Efecto visual
                    original_color = self.scanner_indicator.cget('foreground')
                    self.scanner_indicator.config(foreground='yellow')
                    self.root.after(300, lambda: self.scanner_indicator.config(foreground=original_color))
                    
                    # Agregar producto automáticamente si la cantidad es válida
                    if self.quantity_var.get() and int(self.quantity_var.get()) > 0:
                        self._add_product_to_sale()
                        
            except Exception as e:
                # No es crítico si no hay lectura
                pass
        
        # Programar próxima verificación
        self.root.after(100, self._start_scanner_check)
    
    def _on_barcode_changed(self, *args):
        """Maneja cambios en el campo de código de barras - NUEVO."""
        try:
            code = self.barcode_var.get().strip()
            
            if code:
                # Detectar formato del código
                if validate_barcode(code):
                    info = BarcodeUtils.extract_product_info(code)
                    format_text = info.get('format', 'DESCONOCIDO')
                    self.barcode_format_var.set(format_text)
                    self.format_label.config(foreground='green')
                else:
                    self.barcode_format_var.set('INVÁLIDO')
                    self.format_label.config(foreground='red')
            else:
                self.barcode_format_var.set('')
                
        except Exception as e:
            self.logger.debug(f"Error procesando cambio de código: {e}")
    
    def _clear_barcode(self):
        """Limpia el campo de código de barras - NUEVO."""
        self.barcode_var.set("")
        self.barcode_format_var.set("")
        self.barcode_entry.focus()
    
    def _configure_scanner(self):
        """Abre configuración del scanner - NUEVO."""
        try:
            from ui.forms.barcode_config_form import BarcodeConfigForm
            config_form = BarcodeConfigForm(self.root)
            
            # Refrescar estado después de configurar
            self.root.after(1000, self._check_scanner_status)
            
        except Exception as e:
            self.logger.error(f"Error abriendo configuración: {e}")
            messagebox.showerror("Error", f"Error abriendo configuración del scanner: {e}")
    
    def _open_barcode_search(self):
        """Abre búsqueda avanzada por códigos - NUEVO."""
        try:
            from ui.forms.barcode_search_form import BarcodeSearchForm
            search_form = BarcodeSearchForm(self.root)
            
        except Exception as e:
            self.logger.error(f"Error abriendo búsqueda: {e}")
            messagebox.showerror("Error", f"Error abriendo búsqueda por códigos: {e}")
    
    def _generate_labels_for_sale(self):
        """Genera etiquetas para productos en la venta - NUEVO."""
        try:
            if not self.sale_items:
                messagebox.showwarning("Sin Productos", "Agregue productos a la venta primero")
                return
                
            from ui.forms.label_generator_form import LabelGeneratorForm
            
            # Obtener productos únicos de la venta
            unique_products = []
            for item in self.sale_items:
                if item['product'] not in unique_products:
                    unique_products.append(item['product'])
            
            # Abrir generador preconfigurado
            label_form = LabelGeneratorForm(self.root)
            
            # TODO: Preseleccionar productos de la venta
            messagebox.showinfo("Información", "Funcionalidad de preselección en desarrollo")
            
        except Exception as e:
            self.logger.error(f"Error generando etiquetas: {e}")
            messagebox.showerror("Error", f"Error generando etiquetas: {e}")
    
    # === MÉTODOS EXISTENTES ACTUALIZADOS ===
            
    def _add_product_to_sale(self):
        """Agrega un producto a la venta usando código o ID."""
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
            
            # Buscar producto por código primero
            product = None
            search_method = "código"
            
            try:
                # Intentar buscar por código de barras
                product = self.barcode_service.search_product_by_code(code_or_id)
                search_method = "código de barras"
            except:
                pass
            
            if not product:
                try:
                    # Intentar buscar por ID
                    if code_or_id.isdigit():
                        product = self.product_service.get_product_by_id(int(code_or_id))
                        search_method = "ID"
                except:
                    pass
            
            if not product:
                messagebox.showerror(
                    "Producto No Encontrado", 
                    f"No se encontró producto con {search_method}: {code_or_id}"
                )
                return
            
            # Verificar stock disponible
            if product.stock is not None and product.stock < quantity:
                if not messagebox.askyesno(
                    "Stock Insuficiente",
                    f"Stock disponible: {product.stock}\n"
                    f"Cantidad solicitada: {quantity}\n\n"
                    f"¿Desea continuar con la venta?"
                ):
                    return
            
            # Verificar si el producto ya está en la venta
            existing_item = None
            for item in self.sale_items:
                if item['product'].id_producto == product.id_producto:
                    existing_item = item
                    break
            
            if existing_item:
                # Actualizar cantidad
                new_quantity = existing_item['quantity'] + quantity
                existing_item['quantity'] = new_quantity
                existing_item['subtotal'] = existing_item['precio_unitario'] * new_quantity
                existing_item['impuesto'] = existing_item['subtotal'] * (product.tasa_impuesto or 0) / 100
                existing_item['total'] = existing_item['subtotal'] + existing_item['impuesto']
                
                # Actualizar TreeView
                for child in self.items_tree.get_children():
                    item_values = self.items_tree.item(child, 'values')
                    if item_values[0] == code_or_id:  # Comparar por código
                        self.items_tree.item(child, values=(
                            code_or_id,
                            product.nombre,
                            str(new_quantity),
                            f"B/. {existing_item['precio_unitario']:.2f}",
                            f"B/. {existing_item['subtotal']:.2f}",
                            f"B/. {existing_item['impuesto']:.2f}",
                            f"B/. {existing_item['total']:.2f}"
                        ))
                        break
            else:
                # Agregar nuevo item
                precio_unitario = product.precio or Decimal('0.00')
                subtotal = precio_unitario * quantity
                impuesto = subtotal * (product.tasa_impuesto or 0) / 100
                total = subtotal + impuesto
                
                sale_item = {
                    'code': code_or_id,
                    'product': product,
                    'quantity': quantity,
                    'precio_unitario': precio_unitario,
                    'subtotal': subtotal,
                    'impuesto': impuesto,
                    'total': total
                }
                
                self.sale_items.append(sale_item)
                
                # Agregar al TreeView
                self.items_tree.insert('', 'end', values=(
                    code_or_id,
                    product.nombre,
                    str(quantity),
                    f"B/. {precio_unitario:.2f}",
                    f"B/. {subtotal:.2f}",
                    f"B/. {impuesto:.2f}",
                    f"B/. {total:.2f}"
                ))
            
            # Limpiar campos y actualizar totales
            self._clear_barcode()
            self.quantity_var.set("1")
            self._update_totals()
            
            # Mostrar confirmación
            messagebox.showinfo(
                "Producto Agregado",
                f"Producto agregado: {product.nombre}\n"
                f"Cantidad: {quantity}\n"
                f"Método: {search_method}"
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
            
            confirm_msg = f"Procesar venta:\n\n"
            confirm_msg += f"Productos: {item_count} items\n"
            confirm_msg += f"Total: B/. {total_amount:.2f}\n"
            
            if self.selected_client:
                confirm_msg += f"Cliente: {self.selected_client.nombre}\n"
            
            confirm_msg += "\n¿Confirmar venta?"
            
            if not messagebox.askyesno("Confirmar Venta", confirm_msg):
                return
            
            # TODO: Implementar procesamiento real de venta
            # Por ahora mostrar mensaje de éxito
            messagebox.showinfo(
                "Venta Procesada", 
                f"Venta procesada exitosamente\n"
                f"Total: B/. {total_amount:.2f}\n\n"
                f"Funcionalidad completa en desarrollo"
            )
            
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
                "¿Está seguro que desea cancelar la venta actual?\nSe perderán todos los productos agregados."
            )
            if result:
                self._clear_all_items()
                self.selected_client = None
                self.client_combo.current(0)
        
    def _close_window(self):
        """Cierra la ventana."""
        try:
            # Detener scanner si está activo
            if self.scanner_active:
                self.scanner_active = False
            
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
