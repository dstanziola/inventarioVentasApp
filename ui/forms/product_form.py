"""
FORMULARIO DE PRODUCTOS CON CÓDIGOS DE BARRAS - FASE 4 ACTUALIZADO
Sistema de Inventario v2.1 - Con integración completa de códigos de barras

NUEVAS FUNCIONALIDADES AGREGADAS:
- Campo específico para código de barras del producto
- Generación automática de códigos por ID
- Validación en tiempo real de códigos de barras
- Preview de etiqueta del producto
- Botón para imprimir etiqueta individual
- Integración con servicios de códigos de barras

Autor: Sistema de Inventario Copy Point S.A.
Fecha: Junio 2025 - FASE 4 FINAL
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List
import logging
from decimal import Decimal
from datetime import datetime
import tempfile
import os

from db.database import get_database_connection
from services.product_service import ProductService
from services.category_service import CategoryService
from services.label_service import LabelService  # NUEVO
from services.barcode_service import BarcodeService  # NUEVO
from utils.barcode_utils import validate_barcode, BarcodeUtils, generate_product_code  # NUEVO
from models.producto import Producto

class ProductWindow:
    """
    Ventana de gestión de productos con códigos de barras integrados.
    
    NUEVAS FUNCIONALIDADES FASE 4:
    - Gestión completa de códigos de barras
    - Generación automática de códigos
    - Preview y generación de etiquetas
    - Validación en tiempo real
    """
    
    def __init__(self, parent: tk.Tk):
        """Inicializa la ventana de productos con códigos de barras."""
        self.parent = parent
        
        # Configurar logging detallado
        self.logger = logging.getLogger(f"ProductWindow.{id(self)}")
        self.logger.setLevel(logging.DEBUG)
        
        # Crear handler para archivo si no existe
        if not self.logger.handlers:
            file_handler = logging.FileHandler('product_form_debug.log')
            file_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        
        self.logger.info("=== INICIANDO ProductWindow con CÓDIGOS DE BARRAS ===")
        
        # Inicializar servicios con manejo de errores mejorado
        try:
            db_connection = get_database_connection()
            self.product_service = ProductService(db_connection)
            self.category_service = CategoryService(db_connection)
            self.label_service = LabelService()  # NUEVO
            self.barcode_service = BarcodeService()  # NUEVO
            self.logger.info("Servicios inicializados correctamente - incluyendo códigos de barras")
        except Exception as e:
            self.logger.error(f"Error conectando a la base de datos: {e}")
            messagebox.showerror("Error", f"No se pudo conectar a la base de datos: {e}")
            return
        
        # Crear ventana
        self.root = tk.Toplevel(parent)
        self.root.title("Gestión de Productos - Con Códigos de Barras")
        self.root.geometry("1200x800")  # Más grande para acomodar códigos
        self.root.transient(parent)
        self.root.grab_set()
        
        # Variables de formulario existentes
        self.product_name_var = tk.StringVar()
        self.category_var = tk.StringVar()
        self.search_var = tk.StringVar()
        self.stock_var = tk.StringVar()
        self.cost_var = tk.StringVar()
        self.price_var = tk.StringVar()
        self.tax_var = tk.StringVar()
        
        # Nuevas variables para códigos de barras - NUEVO
        self.barcode_var = tk.StringVar()
        self.barcode_format_var = tk.StringVar()
        self.auto_generate_barcode_var = tk.BooleanVar(value=True)
        
        # Estado del formulario
        self.editing_product: Optional[Producto] = None
        self.is_creating_new = False
        self.products: List[Producto] = []
        self.categories: List = []
        
        # Flag para modo debug
        self.debug_mode = True
        
        # Crear interfaz actualizada con códigos de barras
        self._create_ui_with_barcodes()
        self._setup_events_with_barcodes()
        self._load_data()
        
        self.logger.info("ProductWindow inicializado completamente con códigos de barras")
        
    def _create_ui_with_barcodes(self):
        """Crea la interfaz de usuario con códigos de barras integrados."""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configurar grid principal
        main_frame.columnconfigure(0, weight=2)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Título actualizado
        title_label = ttk.Label(
            main_frame,
            text="Gestión de Productos - Con Códigos de Barras",
            font=("Arial", 16, "bold"),
            foreground="darkblue"
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Panel izquierdo - Lista de productos actualizada
        self._create_list_panel_with_barcodes(main_frame)
        
        # Panel derecho - Formulario con códigos de barras
        self._create_form_panel_with_barcodes(main_frame)
        
        # Panel inferior - Botones con códigos de barras
        self._create_button_panel_with_barcodes(main_frame)
        
    def _create_list_panel_with_barcodes(self, parent):
        """Crea el panel de lista de productos con información de códigos."""
        list_frame = ttk.LabelFrame(parent, text="Productos y Códigos", padding=10)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(1, weight=1)
        
        # Campo de búsqueda
        search_frame = ttk.Frame(list_frame)
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="Buscar:").grid(row=0, column=0, padx=(0, 5))
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # TreeView para lista de productos - ACTUALIZADO con códigos
        columns = ('ID', 'Código', 'Nombre', 'Categoría', 'Stock', 'Precio', 'Impuesto')
        self.product_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        self.product_tree.heading('ID', text='ID')
        self.product_tree.heading('Código', text='Código')  # NUEVO
        self.product_tree.heading('Nombre', text='Nombre')
        self.product_tree.heading('Categoría', text='Categoría')
        self.product_tree.heading('Stock', text='Stock')
        self.product_tree.heading('Precio', text='Precio')
        self.product_tree.heading('Impuesto', text='Impuesto%')
        
        self.product_tree.column('ID', width=50)
        self.product_tree.column('Código', width=100)  # NUEVO
        self.product_tree.column('Nombre', width=150)
        self.product_tree.column('Categoría', width=100)
        self.product_tree.column('Stock', width=60, anchor='e')
        self.product_tree.column('Precio', width=80, anchor='e')
        self.product_tree.column('Impuesto', width=70, anchor='e')
        
        # Scrollbar para TreeView
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.product_tree.yview)
        self.product_tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid TreeView y scrollbar
        self.product_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
    def _create_form_panel_with_barcodes(self, parent):
        """Crea el formulario con sección de códigos de barras."""
        form_frame = ttk.LabelFrame(parent, text="Datos de Producto", padding=10)
        form_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        form_frame.columnconfigure(1, weight=1)
        
        # Crear notebook para organizar mejor
        self.form_notebook = ttk.Notebook(form_frame)
        self.form_notebook.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Pestaña información básica
        self._create_basic_info_tab()
        
        # Pestaña códigos de barras - NUEVO
        self._create_barcode_tab()
        
        # Pestaña etiquetas - NUEVO
        self._create_label_tab()
        
        # Debug info si está habilitado
        if self.debug_mode:
            self._create_debug_tab()
    
    def _create_basic_info_tab(self):
        """Crea la pestaña de información básica del producto."""
        basic_frame = ttk.Frame(self.form_notebook)
        self.form_notebook.add(basic_frame, text="Información Básica")
        
        basic_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Campo nombre
        ttk.Label(basic_frame, text="Nombre:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(basic_frame, textvariable=self.product_name_var, width=30)
        self.name_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Campo categoría
        ttk.Label(basic_frame, text="Categoría:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.category_combo = ttk.Combobox(basic_frame, textvariable=self.category_var, state='readonly', width=27)
        self.category_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Campo stock
        ttk.Label(basic_frame, text="Stock:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.stock_entry = ttk.Entry(basic_frame, textvariable=self.stock_var, width=30, justify='right')
        self.stock_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Campo costo
        ttk.Label(basic_frame, text="Costo:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.cost_entry = ttk.Entry(basic_frame, textvariable=self.cost_var, width=30, justify='right')
        self.cost_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Campo precio
        ttk.Label(basic_frame, text="Precio:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.price_entry = ttk.Entry(basic_frame, textvariable=self.price_var, width=30, justify='right')
        self.price_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Campo impuesto
        ttk.Label(basic_frame, text="Impuesto (%):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.tax_entry = ttk.Entry(basic_frame, textvariable=self.tax_var, width=30, justify='right')
        self.tax_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
    
    def _create_barcode_tab(self):
        """Crea la pestaña de códigos de barras - NUEVO."""
        barcode_frame = ttk.Frame(self.form_notebook)
        self.form_notebook.add(barcode_frame, text="Código de Barras")
        
        barcode_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Sección código de barras
        code_section = ttk.LabelFrame(barcode_frame, text="Código de Barras", padding=10)
        code_section.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        code_section.columnconfigure(1, weight=1)
        
        # Campo código
        ttk.Label(code_section, text="Código:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.barcode_entry = ttk.Entry(
            code_section, 
            textvariable=self.barcode_var, 
            width=30,
            font=('Consolas', 11)  # Fuente monoespaciada
        )
        self.barcode_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Botones de código
        barcode_buttons = ttk.Frame(code_section)
        barcode_buttons.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        self.generate_code_btn = ttk.Button(
            barcode_buttons, 
            text="Generar Automático", 
            command=self._generate_barcode
        )
        self.generate_code_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.validate_code_btn = ttk.Button(
            barcode_buttons, 
            text="Validar Código", 
            command=self._validate_barcode
        )
        self.validate_code_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            barcode_buttons, 
            text="Limpiar", 
            command=self._clear_barcode
        ).pack(side=tk.LEFT)
        
        # Información del código
        info_section = ttk.LabelFrame(barcode_frame, text="Información del Código", padding=10)
        info_section.grid(row=row+1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        info_section.columnconfigure(1, weight=1)
        
        # Formato detectado
        ttk.Label(info_section, text="Formato:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.format_display_label = ttk.Label(
            info_section,
            textvariable=self.barcode_format_var,
            font=('Arial', 10, 'bold'),
            foreground='blue'
        )
        self.format_display_label.grid(row=0, column=1, sticky=tk.W, pady=2)
        
        # Estado de validación
        ttk.Label(info_section, text="Estado:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.validation_label = ttk.Label(
            info_section,
            text="Sin validar",
            foreground='gray'
        )
        self.validation_label.grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # Opción auto-generar
        ttk.Checkbutton(
            barcode_frame,
            text="Auto-generar código al crear producto",
            variable=self.auto_generate_barcode_var
        ).grid(row=row+2, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
    def _create_label_tab(self):
        """Crea la pestaña de etiquetas - NUEVO."""
        label_frame = ttk.Frame(self.form_notebook)
        self.form_notebook.add(label_frame, text="Etiquetas")
        
        label_frame.columnconfigure(0, weight=1)
        
        # Sección preview
        preview_section = ttk.LabelFrame(label_frame, text="Preview de Etiqueta", padding=10)
        preview_section.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Canvas para preview
        self.preview_canvas = tk.Canvas(preview_section, width=300, height=180, bg='white', relief=tk.SUNKEN, bd=1)
        self.preview_canvas.pack(pady=10)
        
        # Botones de etiqueta
        label_buttons = ttk.Frame(label_frame)
        label_buttons.pack(fill=tk.X, pady=(0, 10))
        
        self.preview_label_btn = ttk.Button(
            label_buttons,
            text="Generar Preview",
            command=self._preview_product_label
        )
        self.preview_label_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.print_label_btn = ttk.Button(
            label_buttons,
            text="Imprimir Etiqueta",
            command=self._print_single_label
        )
        self.print_label_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            label_buttons,
            text="Configurar Etiquetas",
            command=self._configure_labels
        ).pack(side=tk.LEFT)
        
        # Opciones de etiqueta
        options_section = ttk.LabelFrame(label_frame, text="Opciones de Etiqueta", padding=10)
        options_section.pack(fill=tk.X)
        
        self.include_price_var = tk.BooleanVar(value=True)
        self.include_category_var = tk.BooleanVar(value=False)
        self.include_barcode_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(options_section, text="Incluir Precio", variable=self.include_price_var).pack(anchor=tk.W)
        ttk.Checkbutton(options_section, text="Incluir Categoría", variable=self.include_category_var).pack(anchor=tk.W)
        ttk.Checkbutton(options_section, text="Incluir Código de Barras", variable=self.include_barcode_var).pack(anchor=tk.W)
    
    def _create_debug_tab(self):
        """Crea la pestaña de debug."""
        debug_frame = ttk.Frame(self.form_notebook)
        self.form_notebook.add(debug_frame, text="Debug")
        
        debug_frame.columnconfigure(0, weight=1)
        debug_frame.rowconfigure(0, weight=1)
        
        self.debug_text = tk.Text(debug_frame, height=10, width=40, font=("Consolas", 8))
        debug_scrollbar = ttk.Scrollbar(debug_frame, orient=tk.VERTICAL, command=self.debug_text.yview)
        self.debug_text.configure(yscrollcommand=debug_scrollbar.set)
        
        self.debug_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        debug_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self._log_debug("Formulario de productos con códigos de barras inicializado")
        
    def _create_button_panel_with_barcodes(self, parent):
        """Crea el panel de botones con funciones de códigos de barras."""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(20, 0))
        
        # Botones principales
        self.new_button = ttk.Button(button_frame, text="Nuevo", command=self._new_product)
        self.new_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.save_button = ttk.Button(button_frame, text="Guardar", command=self._save_product_with_barcode, state='disabled')
        self.save_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.edit_button = ttk.Button(button_frame, text="Editar", command=self._edit_product, state='disabled')
        self.edit_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.delete_button = ttk.Button(button_frame, text="Eliminar", command=self._delete_product, state='disabled')
        self.delete_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.cancel_button = ttk.Button(button_frame, text="Cancelar", command=self._cancel_edit, state='disabled')
        self.cancel_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Separador
        ttk.Separator(button_frame, orient='vertical').pack(side=tk.LEFT, fill='y', padx=10)
        
        # Botones de códigos de barras - NUEVO
        self.scan_button = ttk.Button(
            button_frame,
            text="Escanear Código",
            command=self._scan_barcode
        )
        self.scan_button.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            button_frame,
            text="Búsqueda por Código",
            command=self._open_barcode_search
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            button_frame,
            text="Generar Etiquetas Masivas",
            command=self._open_label_generator
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        # Botón cerrar
        ttk.Button(button_frame, text="Cerrar", command=self._close_window).pack(side=tk.RIGHT)
        
    def _setup_events_with_barcodes(self):
        """Configura eventos incluyendo códigos de barras."""
        # Eventos existentes
        self.product_tree.bind('<<TreeviewSelect>>', self._on_product_select)
        self.search_var.trace('w', self._on_search)
        self.product_name_var.trace('w', self._validate_form_simple)
        self.category_var.trace('w', self._validate_form_simple)
        
        # Nuevos eventos para códigos de barras
        self.barcode_var.trace('w', self._on_barcode_changed)
        self.barcode_entry.bind('<Return>', lambda e: self._validate_barcode())
        
        # Protocolo de cierre
        self.root.protocol("WM_DELETE_WINDOW", self._close_window)
        
    # === NUEVOS MÉTODOS PARA CÓDIGOS DE BARRAS ===
    
    def _generate_barcode(self):
        """Genera código de barras automático - NUEVO."""
        try:
            # Verificar si hay un producto seleccionado o en creación
            if self.is_creating_new:
                # Para productos nuevos, generar código temporal
                import random
                temp_id = random.randint(100000, 999999)
                generated_code = generate_product_code(temp_id, 'CODE128')
                self._log_debug(f"Código temporal generado para producto nuevo: {generated_code}")
            elif self.editing_product:
                # Para productos existentes, usar su ID
                generated_code = generate_product_code(self.editing_product.id_producto, 'CODE128')
                self._log_debug(f"Código generado para producto ID {self.editing_product.id_producto}: {generated_code}")
            else:
                messagebox.showwarning("Advertencia", "Seleccione un producto o cree uno nuevo")
                return
            
            self.barcode_var.set(generated_code)
            self._validate_barcode_format()
            
            messagebox.showinfo("Código Generado", f"Código generado: {generated_code}")
            
        except Exception as e:
            self.logger.error(f"Error generando código: {e}")
            messagebox.showerror("Error", f"Error generando código: {e}")
    
    def _validate_barcode(self):
        """Valida el código de barras actual - NUEVO."""
        try:
            code = self.barcode_var.get().strip()
            
            if not code:
                self.validation_label.config(text="Sin código", foreground='gray')
                return
            
            is_valid = validate_barcode(code)
            
            if is_valid:
                self.validation_label.config(text="✓ Válido", foreground='green')
                
                # Obtener información detallada
                info = BarcodeUtils.extract_product_info(code)
                format_text = info.get('format', 'DESCONOCIDO')
                self.barcode_format_var.set(format_text)
                
                self._log_debug(f"Código válido: {code} ({format_text})")
                messagebox.showinfo("Validación", f"Código válido\nFormato: {format_text}")
                
            else:
                self.validation_label.config(text="✗ Inválido", foreground='red')
                self.barcode_format_var.set('INVÁLIDO')
                messagebox.showerror("Validación", f"Código inválido: {code}")
                
        except Exception as e:
            self.logger.error(f"Error validando código: {e}")
            self.validation_label.config(text="Error", foreground='orange')
    
    def _validate_barcode_format(self):
        """Valida formato en tiempo real - NUEVO."""
        try:
            code = self.barcode_var.get().strip()
            
            if not code:
                self.barcode_format_var.set('')
                self.validation_label.config(text="Sin código", foreground='gray')
                return
            
            is_valid = validate_barcode(code)
            
            if is_valid:
                info = BarcodeUtils.extract_product_info(code)
                format_text = info.get('format', 'DESCONOCIDO')
                self.barcode_format_var.set(format_text)
                self.validation_label.config(text="✓ Válido", foreground='green')
            else:
                self.barcode_format_var.set('INVÁLIDO')
                self.validation_label.config(text="✗ Inválido", foreground='red')
                
        except Exception as e:
            self.logger.debug(f"Error en validación en tiempo real: {e}")
    
    def _on_barcode_changed(self, *args):
        """Maneja cambios en el campo de código de barras - NUEVO."""
        self._validate_barcode_format()
    
    def _clear_barcode(self):
        """Limpia el campo de código de barras - NUEVO."""
        self.barcode_var.set("")
        self.barcode_format_var.set("")
        self.validation_label.config(text="Sin código", foreground='gray')
    
    def _scan_barcode(self):
        """Escanea código usando scanner - NUEVO."""
        try:
            if not self.barcode_service.is_connected():
                messagebox.showerror("Error", "No hay scanner conectado")
                return
            
            messagebox.showinfo("Scanner", "Escanee un código de barras...")
            
            # Leer código del scanner con timeout
            code = self.barcode_service.read_code(timeout=10.0)
            
            if code:
                self.barcode_var.set(code.strip())
                self._validate_barcode()
                self._log_debug(f"Código escaneado: {code}")
            else:
                messagebox.showwarning("Timeout", "No se escaneó ningún código")
                
        except Exception as e:
            self.logger.error(f"Error escaneando código: {e}")
            messagebox.showerror("Error", f"Error con el scanner: {e}")
    
    def _preview_product_label(self):
        """Genera preview de etiqueta del producto - NUEVO."""
        try:
            # Verificar que hay un producto
            if not (self.editing_product or self.is_creating_new):
                messagebox.showwarning("Advertencia", "Seleccione un producto")
                return
            
            # Crear producto temporal para preview
            if self.is_creating_new:
                temp_product = Producto(
                    id_producto=999999,  # ID temporal
                    nombre=self.product_name_var.get() or "Producto Nuevo",
                    precio=float(self.price_var.get() or 0),
                    stock=int(self.stock_var.get() or 0),
                    costo=float(self.cost_var.get() or 0),
                    tasa_impuesto=float(self.tax_var.get() or 0)
                )
            else:
                temp_product = self.editing_product
            
            # Generar etiqueta
            label_image_data = self.label_service.create_product_label(
                temp_product,
                format='standard',
                include_category=self.include_category_var.get(),
                include_price=self.include_price_var.get(),
                include_barcode=self.include_barcode_var.get()
            )
            
            # Mostrar en canvas
            self._show_label_preview(label_image_data)
            
            self._log_debug("Preview de etiqueta generado")
            
        except Exception as e:
            self.logger.error(f"Error generando preview: {e}")
            messagebox.showerror("Error", f"Error generando preview: {e}")
    
    def _show_label_preview(self, image_data: bytes):
        """Muestra preview de etiqueta en canvas - NUEVO."""
        try:
            from PIL import Image, ImageTk
            from io import BytesIO
            
            # Crear imagen PIL
            image_buffer = BytesIO(image_data)
            pil_image = Image.open(image_buffer)
            
            # Redimensionar para el canvas
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width, canvas_height = 300, 180
            
            pil_image.thumbnail((canvas_width - 20, canvas_height - 20), Image.Resampling.LANCZOS)
            
            # Convertir para Tkinter
            tk_image = ImageTk.PhotoImage(pil_image)
            
            # Limpiar canvas y mostrar imagen
            self.preview_canvas.delete("all")
            
            # Centrar imagen
            x = canvas_width // 2
            y = canvas_height // 2
            self.preview_canvas.create_image(x, y, image=tk_image)
            
            # Mantener referencia
            self.preview_canvas.image = tk_image
            
        except Exception as e:
            self.logger.error(f"Error mostrando preview: {e}")
            self.preview_canvas.delete("all")
            self.preview_canvas.create_text(150, 90, text=f"Error: {e}", fill="red")
    
    def _print_single_label(self):
        """Imprime etiqueta individual del producto - NUEVO."""
        try:
            if not (self.editing_product or self.is_creating_new):
                messagebox.showwarning("Advertencia", "Seleccione un producto")
                return
            
            # Crear producto para imprimir
            if self.is_creating_new:
                messagebox.showwarning("Advertencia", "Guarde el producto antes de imprimir etiqueta")
                return
            
            product = self.editing_product
            
            # Generar etiqueta
            label_image_data = self.label_service.create_product_label(
                product,
                format='standard',
                include_category=self.include_category_var.get(),
                include_price=self.include_price_var.get(),
                include_barcode=self.include_barcode_var.get()
            )
            
            # Generar PDF temporal
            pdf_data = self.label_service.generate_labels_pdf(
                [product],
                template='a4_standard',
                use_quantities=False,
                label_format='standard'
            )
            
            # Imprimir
            success = self.label_service.print_labels(pdf_data)
            
            if success:
                messagebox.showinfo("Éxito", "Etiqueta enviada a impresión")
                self._log_debug(f"Etiqueta impresa para: {product.nombre}")
            else:
                messagebox.showerror("Error", "Error enviando etiqueta a impresión")
                
        except Exception as e:
            self.logger.error(f"Error imprimiendo etiqueta: {e}")
            messagebox.showerror("Error", f"Error imprimiendo etiqueta: {e}")
    
    def _configure_labels(self):
        """Abre configuración de etiquetas - NUEVO."""
        try:
            from ui.forms.barcode_config_form import BarcodeConfigForm
            config_form = BarcodeConfigForm(self.root)
            
        except Exception as e:
            self.logger.error(f"Error abriendo configuración: {e}")
            messagebox.showerror("Error", f"Error abriendo configuración: {e}")
    
    def _open_barcode_search(self):
        """Abre búsqueda por códigos de barras - NUEVO."""
        try:
            from ui.forms.barcode_search_form import BarcodeSearchForm
            search_form = BarcodeSearchForm(self.root)
            
        except Exception as e:
            self.logger.error(f"Error abriendo búsqueda: {e}")
            messagebox.showerror("Error", f"Error abriendo búsqueda por códigos: {e}")
    
    def _open_label_generator(self):
        """Abre generador de etiquetas masivo - NUEVO."""
        try:
            from ui.forms.label_generator_form import LabelGeneratorForm
            generator_form = LabelGeneratorForm(self.root)
            
        except Exception as e:
            self.logger.error(f"Error abriendo generador: {e}")
            messagebox.showerror("Error", f"Error abriendo generador de etiquetas: {e}")
    
    # === MÉTODOS EXISTENTES ACTUALIZADOS ===
    
    def _save_product_with_barcode(self):
        """Versión actualizada del guardado con códigos de barras."""
        self.logger.info("=== GUARDANDO PRODUCTO CON CÓDIGO DE BARRAS ===")
        self._log_debug("Iniciando guardado con códigos...")
        
        try:
            # Validar datos básicos
            name = self.product_name_var.get().strip()
            if not name:
                messagebox.showerror("Error", "El nombre es obligatorio")
                self.name_entry.focus()
                return
                
            category_selection = self.category_combo.get()
            if not category_selection:
                messagebox.showerror("Error", "Debe seleccionar una categoría")
                self.category_combo.focus()
                return
                
            # Obtener ID de categoría
            category_index = self.category_combo.current()
            if category_index == -1:
                messagebox.showerror("Error", "Categoría no válida")
                return
                
            selected_category = self.categories[category_index]
            
            # Validar valores numéricos
            try:
                stock = int(float(self.stock_var.get() or "0"))
                cost = float(self.cost_var.get() or "0")
                price = float(self.price_var.get() or "0")
                tax_rate = float(self.tax_var.get() or "0")
            except ValueError as e:
                messagebox.showerror("Error", f"Valores numéricos inválidos: {e}")
                return
            
            # Validar código de barras si se proporciona
            barcode = self.barcode_var.get().strip()
            if barcode and not validate_barcode(barcode):
                if not messagebox.askyesno(
                    "Código Inválido",
                    f"El código de barras '{barcode}' no es válido.\n¿Desea continuar sin código?"
                ):
                    return
                barcode = ""
            
            # Auto-generar código si está habilitado y no hay código
            if self.auto_generate_barcode_var.get() and not barcode and self.is_creating_new:
                import random
                temp_id = random.randint(100000, 999999)
                barcode = generate_product_code(temp_id, 'CODE128')
                self.barcode_var.set(barcode)
                self._log_debug(f"Código auto-generado: {barcode}")

            self.logger.info(f"Datos validados con código: {barcode}")

            # Guardar producto
            if self.is_creating_new:
                self.logger.info("Creando nuevo producto con código...")
                
                result = self.product_service.create_product(
                    nombre=name,
                    categoria_id=selected_category.id_categoria,
                    stock_inicial=stock,
                    precio_compra=cost,
                    precio_venta=price,
                    tasa_impuesto=tax_rate
                )
                
                if result:
                    # TODO: Agregar campo de código de barras a la BD
                    # Por ahora solo mostrar mensaje
                    success_msg = f"Producto creado exitosamente"
                    if barcode:
                        success_msg += f"\nCódigo de barras: {barcode}"
                    
                    messagebox.showinfo("Éxito", success_msg)
                    self.logger.info(f"Producto creado con código: {barcode}")
                    
                    # Auto-selección
                    self._auto_select_created_product(result.id_producto, name)
                    
                else:
                    messagebox.showerror("Error", "No se pudo crear el producto")
                    return
                    
            else:
                self.logger.info(f"Actualizando producto con código...")
                
                success = self.product_service.update_product(
                    id_producto=self.editing_product.id_producto,
                    nombre=name,
                    id_categoria=selected_category.id_categoria,
                    stock=stock,
                    costo=cost,
                    precio=price,
                    tasa_impuesto=tax_rate
                )
                
                if success:
                    # TODO: Actualizar código de barras en BD
                    success_msg = "Producto actualizado exitosamente"
                    if barcode:
                        success_msg += f"\nCódigo de barras: {barcode}"
                    
                    messagebox.showinfo("Éxito", success_msg)
                    self.logger.info(f"Producto actualizado con código: {barcode}")

                    self._load_data()
                    self._cancel_edit()
                else:
                    messagebox.showerror("Error", "No se pudo actualizar el producto")
                    return
            
        except Exception as e:
            self.logger.error(f"Error guardando producto con código: {e}")
            messagebox.showerror("Error", f"Error inesperado al guardar: {e}")
    
    def _update_product_list(self, filter_text: str = ""):
        """Actualiza la lista con información de códigos - ACTUALIZADO."""
        # Limpiar TreeView
        for item in self.product_tree.get_children():
            self.product_tree.delete(item)
            
        # Agregar productos filtrados
        for product in self.products:
            if not filter_text or filter_text.lower() in product.nombre.lower():
                # Buscar nombre de categoría
                category_name = "N/A"
                for cat in self.categories:
                    if cat.id_categoria == product.id_categoria:
                        category_name = cat.nombre
                        break
                
                # TODO: Obtener código de barras real de BD
                # Por ahora generar código basado en ID
                barcode_display = str(product.id_producto)
                
                # Insertar con información de código
                self.product_tree.insert('', tk.END, values=(
                    product.id_producto,
                    barcode_display,  # NUEVO
                    product.nombre,
                    category_name,
                    product.stock,
                    f"B/. {float(product.precio):.2f}",
                    f"{float(product.tasa_impuesto):.1f}%"
                ))
    
    def _show_product_in_form(self, product: Producto):
        """Muestra producto incluyendo código de barras - ACTUALIZADO."""
        self.logger.info(f"Mostrando producto con códigos: {product.nombre}")
        
        try:
            # Establecer datos básicos
            self.product_name_var.set(product.nombre)
            self.stock_var.set(str(product.stock))
            self.cost_var.set(f"{float(product.costo):.2f}")
            self.price_var.set(f"{float(product.precio):.2f}")
            self.tax_var.set(f"{float(product.tasa_impuesto):.2f}")
            
            # Seleccionar categoría
            for i, cat in enumerate(self.categories):
                if cat.id_categoria == product.id_categoria:
                    self.category_combo.current(i)
                    break
            
            # TODO: Cargar código de barras real de BD
            # Por ahora generar código basado en ID
            product_barcode = str(product.id_producto)
            self.barcode_var.set(product_barcode)
            self._validate_barcode_format()
            
            self.logger.info(f"Producto mostrado con código: {product_barcode}")
            self._log_debug(f"Mostrado: {product.nombre}, código: {product_barcode}")
            
        except Exception as e:
            self.logger.error(f"Error mostrando producto: {e}")
            self._log_debug(f"ERROR mostrando: {e}")
    
    # Mantener métodos existentes sin cambios
    def _load_data(self):
        """Cargar datos (método existente sin cambios)."""
        self.logger.info("=== CARGANDO DATOS CON CÓDIGOS DE BARRAS ===")

        try:
            # Cargar categorías
            self.categories = self.category_service.get_all_categories()
            category_names = [f"{cat.nombre} ({cat.tipo})" for cat in self.categories]
            self.category_combo['values'] = category_names
            self.logger.info(f"Cargadas {len(self.categories)} categorías")

            # Cargar productos
            product_dicts = self.product_service.get_all_products()
            self.logger.info(f"Obtenidos {len(product_dicts)} productos del servicio")

            self.products = []
            for prod_dict in product_dicts:
                id_categoria = self._extract_categoria_id(prod_dict)
                producto = Producto(
                    nombre=prod_dict.get('nombre', ''),
                    id_categoria=id_categoria,
                    stock=prod_dict.get('stock_actual', prod_dict.get('stock', 0)),
                    costo=prod_dict.get('precio_compra', prod_dict.get('costo', 0)) or 0,
                    precio=prod_dict.get('precio_venta', prod_dict.get('precio', 0)),
                    tasa_impuesto=prod_dict.get('tasa_impuesto', 0),
                    id_producto=prod_dict.get('id_producto')
                )
                self.products.append(producto)

            self.logger.info(f"Convertidos {len(self.products)} productos")
            self._update_product_list()
            self._log_debug(f"Carga completa con códigos: {len(self.products)} productos")

        except Exception as e:
            self.logger.error(f"Error en carga de datos: {e}")
            messagebox.showerror("Error", f"No se pudieron cargar los datos: {e}")
    
    # Mantener otros métodos existentes
    def _extract_categoria_id(self, prod_dict):
        """Método existente sin cambios."""
        id_categoria = (
            prod_dict.get('id_categoria') or
            prod_dict.get('categoria_id') or
            0
        )
        return id_categoria
        
    def _on_product_select(self, event):
        """Método existente sin cambios."""
        selection = self.product_tree.selection()
        if selection:
            item = self.product_tree.item(selection[0])
            product_id = int(item['values'][0])
            
            self.logger.info(f"=== PRODUCTO SELECCIONADO: ID {product_id} ==")
            self._log_debug(f"Seleccionado producto ID: {product_id}")
            
            selected_product = None
            for product in self.products:
                if product.id_producto == product_id:
                    selected_product = product
                    break
                    
            if selected_product:
                self._show_product_in_form(selected_product)
                self.edit_button.config(state='normal')
                self.delete_button.config(state='normal')
                self._disable_form()
    
    def _auto_select_created_product(self, product_id: int, product_name: str):
        """Método existente actualizado."""
        self.logger.info(f"=== AUTO-SELECCIÓN CON CÓDIGOS: ID {product_id} ===")
        
        try:
            self._load_data()
            
            target_product = None
            for product in self.products:
                if product.id_producto == product_id:
                    target_product = product
                    break
            
            if not target_product:
                self.logger.warning(f"Producto ID {product_id} no encontrado")
                return False
            
            for item in self.product_tree.get_children():
                item_values = self.product_tree.item(item)['values']
                if item_values and int(item_values[0]) == product_id:
                    self.product_tree.selection_set(item)
                    self.product_tree.focus(item)
                    self.product_tree.see(item)

                    self._show_product_in_form(target_product)
                    
                    self.new_button.config(state='normal')
                    self.save_button.config(state='disabled')
                    self.cancel_button.config(state='disabled')
                    self.edit_button.config(state='normal')
                    self.delete_button.config(state='normal')
                    
                    self._disable_form()
                    
                    self.logger.info(f"[OK] AUTO-SELECCIÓN CON CÓDIGOS: {product_name}")
                    return True

            return False
            
        except Exception as e:
            self.logger.error(f"Error en auto-selección: {e}")
            return False
    
    def _log_debug(self, message: str):
        """Método existente sin cambios."""
        if hasattr(self, 'debug_text') and self.debug_mode:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.debug_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.debug_text.see(tk.END)
    
    # Mantener métodos básicos existentes sin cambios
    def _validate_form_simple(self, *args):
        """Validación existente."""
        name = self.product_name_var.get().strip()
        category = self.category_var.get().strip()
        
        if (self.is_creating_new or self.editing_product is not None) and name and category:
            self.save_button.config(state='normal')
        else:
            self.save_button.config(state='disabled')
    
    def _new_product(self):
        """Método existente."""
        self._clear_form()
        self.editing_product = None
        self.is_creating_new = True
        self._enable_form()
        
        self.new_button.config(state='disabled')
        self.edit_button.config(state='disabled')
        self.delete_button.config(state='disabled')
        self.cancel_button.config(state='normal')
        
        self.name_entry.focus()
        self._log_debug("Modo nuevo producto activado")
    
    def _edit_product(self):
        """Método existente."""
        selection = self.product_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un producto para editar")
            return
            
        item = self.product_tree.item(selection[0])
        product_id = int(item['values'][0])
        
        selected_product = None
        for product in self.products:
            if product.id_producto == product_id:
                selected_product = product
                break
                
        if selected_product:
            self.editing_product = selected_product
            self.is_creating_new = False
            self._enable_form()
            
            self.new_button.config(state='disabled')
            self.edit_button.config(state='disabled')
            self.delete_button.config(state='disabled')
            self.cancel_button.config(state='normal')
            
            self.name_entry.focus()
            self._log_debug(f"Modo edición activado para: {selected_product.nombre}")

    def _delete_product(self):
        """Método existente."""
        selection = self.product_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un producto para eliminar")
            return
            
        item = self.product_tree.item(selection[0])
        product_id = int(item['values'][0])
        product_name = item['values'][2]  # Ajustado por nueva columna código
        
        result = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro que desea eliminar el producto '{product_name}'?\n\n"
            "Esta acción no se puede deshacer."
        )
        
        if result:
            try:
                success = self.product_service.delete_product(product_id)
                
                if success:
                    messagebox.showinfo("Éxito", "Producto eliminado exitosamente")
                    self.logger.info(f"Producto eliminado: {product_name}")

                    self._load_data()
                    self._clear_form()
                    self._disable_form()
                    
                    self.edit_button.config(state='disabled')
                    self.delete_button.config(state='disabled')
                    
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el producto")
                    
            except Exception as e:
                self.logger.error(f"Error eliminando producto: {e}")
                messagebox.showerror("Error", f"Error al eliminar producto: {e}")
    
    def _cancel_edit(self):
        """Método existente."""
        self.editing_product = None
        self.is_creating_new = False
        self._clear_form()
        self._disable_form()
        
        self.new_button.config(state='normal')
        self.save_button.config(state='disabled')
        self.edit_button.config(state='disabled')
        self.delete_button.config(state='disabled')
        self.cancel_button.config(state='disabled')

        self._log_debug("Edición cancelada")

    def _clear_form(self):
        """Método existente actualizado con códigos."""
        self.product_name_var.set("")
        self.category_var.set("")
        self.stock_var.set("")
        self.cost_var.set("")
        self.price_var.set("")
        self.tax_var.set("")
        
        # Limpiar códigos de barras
        self._clear_barcode()
        
        for item in self.product_tree.selection():
            self.product_tree.selection_remove(item)
    
    def _enable_form(self):
        """Método existente actualizado."""
        self.name_entry.config(state='normal')
        self.category_combo.config(state='readonly')
        self.stock_entry.config(state='normal')
        self.cost_entry.config(state='normal')
        self.price_entry.config(state='normal')
        self.tax_entry.config(state='normal')
        
        # Habilitar códigos de barras
        self.barcode_entry.config(state='normal')
    
    def _disable_form(self):
        """Método existente actualizado."""
        self.name_entry.config(state='readonly')
        self.category_combo.config(state='disabled')
        self.stock_entry.config(state='readonly')
        self.cost_entry.config(state='readonly')
        self.price_entry.config(state='readonly')
        self.tax_entry.config(state='readonly')
        
        # Deshabilitar códigos de barras
        self.barcode_entry.config(state='readonly')
    
    def _on_search(self, *args):
        """Método existente."""
        search_text = self.search_var.get()
        self._update_product_list(search_text)
    
    def _close_window(self):
        """Método existente."""
        if self.editing_product is not None or self.is_creating_new:
            result = messagebox.askyesno(
                "Confirmar Cierre",
                "Hay cambios sin guardar. ¿Está seguro que desea cerrar?"
            )
            if not result:
                return

        self.logger.info("Cerrando ProductWindow con códigos de barras...")
        self.root.destroy()


def main():
    """Función principal para probar la ventana con códigos de barras."""
    root = tk.Tk()
    root.withdraw()
    
    logging.basicConfig(level=logging.DEBUG)
    
    try:
        product_window = ProductWindow(root)
        root.wait_window(product_window.root)
    except Exception as e:
        messagebox.showerror("Error", f"Error iniciando aplicación: {e}")
    
    root.destroy()


if __name__ == "__main__":
    main()
