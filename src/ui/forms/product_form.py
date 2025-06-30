"""
Corrección para product_form.py - Solución al problema de inicialización de CategoryService
Garantiza que todos los servicios reciban correctamente la conexión a la base de datos.
CORRECCIÓN CRÍTICA: Variable global BARCODE_SUPPORT manejada correctamente.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List
import logging
from decimal import Decimal
from datetime import datetime
import tempfile
import os

# Imports corregidos con manejo de errores robusto
try:
    from db.database import get_database_connection, DatabaseConnection
    from services.product_service import ProductService
    from services.category_service import CategoryService
    from models.producto import Producto
    
    # Imports opcionales para códigos de barras (FASE 4)
    try:
        from services.label_service import LabelService
        from services.barcode_service import BarcodeService
        from utils.barcode_utils import validate_barcode, BarcodeUtils, generate_product_code
        BARCODE_SUPPORT = True
    except ImportError as e:
        print(f"Advertencia: Funcionalidades de códigos de barras no disponibles: {e}")
        BARCODE_SUPPORT = False
        
except ImportError as e:
    print(f"Error crítico importando dependencias: {e}")
    raise


class ProductWindow:
    """
    Ventana de gestión de productos con inicialización de servicios corregida.
    
    CORRECCIONES APLICADAS:
    - Inicialización robusta de servicios con manejo de errores
    - Validación de conexión de base de datos antes de crear servicios
    - Fallback para funcionalidades opcionales
    - CRÍTICO: Manejo correcto de variable global BARCODE_SUPPORT
    """
    
    def __init__(self, parent: tk.Tk):
        """Inicializa la ventana de productos con servicios correctamente configurados."""
        self.parent = parent
        
        # Configurar logging
        self.logger = logging.getLogger(f"ProductWindow.{id(self)}")
        self.logger.setLevel(logging.DEBUG)
        
        if not self.logger.handlers:
            file_handler = logging.FileHandler('product_form_debug.log')
            file_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        
        self.logger.info("=== INICIANDO ProductWindow con inicialización corregida ===")
        
        # Variable de instancia para códigos de barras (evita problemas con variable global)
        self.barcode_support = BARCODE_SUPPORT
        
        # Inicializar servicios con manejo de errores robusto
        self._initialize_services()
        
        # Continuar solo si los servicios se inicializaron correctamente
        if not self._validate_services():
            messagebox.showerror("Error Fatal", "No se pudieron inicializar los servicios necesarios")
            return
        
        # Crear ventana
        self.root = tk.Toplevel(parent)
        self.root.title("Gestión de Productos")
        window_width = 1200 if self.barcode_support else 1000
        self.root.geometry(f"{window_width}x800")
        self.root.transient(parent)
        self.root.grab_set()
        
        # Inicializar variables de formulario
        self._initialize_form_variables()
        
        # Estado del formulario
        self.editing_product: Optional[Producto] = None
        self.is_creating_new = False
        self.products: List[Producto] = []
        self.categories: List = []
        
        # Crear interfaz
        self._create_user_interface()
        self._setup_event_handlers()
        self._load_initial_data()
        
        self.logger.info("ProductWindow inicializado correctamente")
        
    def _initialize_services(self):
        """Inicializa todos los servicios con manejo de errores robusto."""
        self.logger.info("Inicializando servicios...")
        
        # Inicializar servicios principales
        self.product_service = None
        self.category_service = None
        
        # Inicializar servicios opcionales
        self.label_service = None
        self.barcode_service = None
        
        try:
            # Obtener conexión de base de datos
            self.logger.info("Obteniendo conexión a base de datos...")
            db_connection = get_database_connection()
            
            if db_connection is None:
                raise Exception("get_database_connection() retornó None")
            
            # Validar que la conexión es del tipo correcto
            if not isinstance(db_connection, DatabaseConnection):
                raise Exception(f"Conexión de tipo inesperado: {type(db_connection)}")
            
            # Probar la conexión
            test_conn = db_connection.get_connection()
            if test_conn is None:
                raise Exception("No se pudo obtener conexión SQLite")
            
            self.logger.info("Conexión de base de datos validada correctamente")
            
            # Inicializar servicios principales con conexión validada
            self.logger.info("Inicializando ProductService...")
            self.product_service = ProductService(db_connection)
            
            self.logger.info("Inicializando CategoryService...")
            self.category_service = CategoryService(db_connection)
            
            self.logger.info("Servicios principales inicializados correctamente")
            
            # Inicializar servicios opcionales (códigos de barras)
            if self.barcode_support:
                try:
                    self.logger.info("Inicializando servicios de códigos de barras...")
                    self.label_service = LabelService()
                    self.barcode_service = BarcodeService()
                    self.logger.info("Servicios de códigos de barras inicializados")
                except Exception as e:
                    self.logger.warning(f"No se pudieron inicializar servicios de códigos: {e}")
                    # CORRECCIÓN CRÍTICA: Usar variable de instancia, no global
                    self.barcode_support = False
            
        except Exception as e:
            self.logger.error(f"Error crítico inicializando servicios: {e}")
            self._show_service_error(e)
            
    def _validate_services(self) -> bool:
        """Valida que los servicios críticos estén inicializados correctamente."""
        if self.product_service is None:
            self.logger.error("ProductService no inicializado")
            return False
            
        if self.category_service is None:
            self.logger.error("CategoryService no inicializado")
            return False
            
        self.logger.info("Validación de servicios exitosa")
        return True
        
    def _show_service_error(self, error: Exception):
        """Muestra error de inicialización de servicios al usuario."""
        error_msg = f"No se pudo conectar a la base de datos: {error}"
        self.logger.error(error_msg)
        messagebox.showerror("Error de Conexión", error_msg)
        
    def _initialize_form_variables(self):
        """Inicializa todas las variables del formulario."""
        # Variables básicas
        self.product_name_var = tk.StringVar()
        self.category_var = tk.StringVar()
        self.search_var = tk.StringVar()
        self.stock_var = tk.StringVar()
        self.cost_var = tk.StringVar()
        self.price_var = tk.StringVar()
        self.tax_var = tk.StringVar()
        
        # Variables para códigos de barras (si están disponibles)
        if self.barcode_support:
            self.barcode_var = tk.StringVar()
            self.barcode_format_var = tk.StringVar()
            self.auto_generate_barcode_var = tk.BooleanVar(value=True)
            self.include_price_var = tk.BooleanVar(value=True)
            self.include_category_var = tk.BooleanVar(value=False)
            self.include_barcode_var = tk.BooleanVar(value=True)
        
    def _create_user_interface(self):
        """Crea la interfaz de usuario adaptativa."""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configurar grid
        main_frame.columnconfigure(0, weight=2)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Título
        title_text = "Gestión de Productos"
        if self.barcode_support:
            title_text += " - Con Códigos de Barras"
            
        title_label = ttk.Label(
            main_frame,
            text=title_text,
            font=("Arial", 16, "bold"),
            foreground="darkblue"
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Panel izquierdo - Lista de productos
        self._create_product_list_panel(main_frame)
        
        # Panel derecho - Formulario
        self._create_form_panel(main_frame)
        
        # Panel inferior - Botones
        self._create_button_panel(main_frame)
        
    def _create_product_list_panel(self, parent):
        """Crea el panel de lista de productos."""
        list_frame = ttk.LabelFrame(parent, text="Lista de Productos", padding=10)
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
        
        # TreeView para productos
        if self.barcode_support:
            columns = ('ID', 'Código', 'Nombre', 'Categoría', 'Stock', 'Precio', 'Impuesto')
        else:
            columns = ('ID', 'Nombre', 'Categoría', 'Stock', 'Precio', 'Impuesto')
            
        self.product_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        for col in columns:
            self.product_tree.heading(col, text=col)
            
        if self.barcode_support:
            self.product_tree.column('ID', width=50)
            self.product_tree.column('Código', width=100)
            self.product_tree.column('Nombre', width=150)
            self.product_tree.column('Categoría', width=100)
            self.product_tree.column('Stock', width=60, anchor='e')
            self.product_tree.column('Precio', width=80, anchor='e')
            self.product_tree.column('Impuesto', width=70, anchor='e')
        else:
            self.product_tree.column('ID', width=50)
            self.product_tree.column('Nombre', width=200)
            self.product_tree.column('Categoría', width=120)
            self.product_tree.column('Stock', width=80, anchor='e')
            self.product_tree.column('Precio', width=100, anchor='e')
            self.product_tree.column('Impuesto', width=80, anchor='e')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.product_tree.yview)
        self.product_tree.configure(yscrollcommand=scrollbar.set)
        
        self.product_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
    def _create_form_panel(self, parent):
        """Crea el panel del formulario."""
        form_frame = ttk.LabelFrame(parent, text="Datos del Producto", padding=10)
        form_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        form_frame.columnconfigure(1, weight=1)
        
        if self.barcode_support:
            # Usar notebook para organizar pestañas
            self.form_notebook = ttk.Notebook(form_frame)
            self.form_notebook.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            self._create_basic_info_tab()
            self._create_barcode_tab()
        else:
            # Formulario simple sin pestañas
            self._create_basic_form_fields(form_frame)
            
    def _create_basic_info_tab(self):
        """Crea la pestaña de información básica."""
        basic_frame = ttk.Frame(self.form_notebook)
        self.form_notebook.add(basic_frame, text="Información Básica")
        self._create_basic_form_fields(basic_frame)
        
    def _create_basic_form_fields(self, parent):
        """Crea los campos básicos del formulario."""
        parent.columnconfigure(1, weight=1)
        
        row = 0
        
        # Nombre
        ttk.Label(parent, text="Nombre:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(parent, textvariable=self.product_name_var, width=30)
        self.name_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Categoría
        ttk.Label(parent, text="Categoría:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.category_combo = ttk.Combobox(parent, textvariable=self.category_var, state='readonly', width=27)
        self.category_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Stock
        ttk.Label(parent, text="Stock:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.stock_entry = ttk.Entry(parent, textvariable=self.stock_var, width=30, justify='right')
        self.stock_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Costo
        ttk.Label(parent, text="Costo:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.cost_entry = ttk.Entry(parent, textvariable=self.cost_var, width=30, justify='right')
        self.cost_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Precio
        ttk.Label(parent, text="Precio:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.price_entry = ttk.Entry(parent, textvariable=self.price_var, width=30, justify='right')
        self.price_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Impuesto
        ttk.Label(parent, text="Impuesto (%):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.tax_entry = ttk.Entry(parent, textvariable=self.tax_var, width=30, justify='right')
        self.tax_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        
    def _create_barcode_tab(self):
        """Crea la pestaña de códigos de barras (solo si está disponible)."""
        if not self.barcode_support:
            return
            
        barcode_frame = ttk.Frame(self.form_notebook)
        self.form_notebook.add(barcode_frame, text="Código de Barras")
        
        barcode_frame.columnconfigure(1, weight=1)
        
        # Campo código
        ttk.Label(barcode_frame, text="Código:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.barcode_entry = ttk.Entry(
            barcode_frame, 
            textvariable=self.barcode_var, 
            width=30,
            font=('Consolas', 11)
        )
        self.barcode_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Botones
        button_frame = ttk.Frame(barcode_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Generar", command=self._generate_barcode).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Validar", command=self._validate_barcode).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Limpiar", command=self._clear_barcode).pack(side=tk.LEFT, padx=5)
        
        # Estado
        self.validation_label = ttk.Label(barcode_frame, text="Sin código", foreground='gray')
        self.validation_label.grid(row=2, column=0, columnspan=2, pady=5)
        
    def _create_button_panel(self, parent):
        """Crea el panel de botones."""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(20, 0))
        
        # Botones principales
        self.new_button = ttk.Button(button_frame, text="Nuevo", command=self._new_product)
        self.new_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.save_button = ttk.Button(button_frame, text="Guardar", command=self._save_product, state='disabled')
        self.save_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.edit_button = ttk.Button(button_frame, text="Editar", command=self._edit_product, state='disabled')
        self.edit_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.delete_button = ttk.Button(button_frame, text="Eliminar", command=self._delete_product, state='disabled')
        self.delete_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.cancel_button = ttk.Button(button_frame, text="Cancelar", command=self._cancel_edit, state='disabled')
        self.cancel_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Botones de códigos de barras (si están disponibles)
        if self.barcode_support:
            ttk.Separator(button_frame, orient='vertical').pack(side=tk.LEFT, fill='y', padx=10)
            ttk.Button(button_frame, text="Escanear", command=self._scan_barcode).pack(side=tk.LEFT, padx=(0, 5))
        
        # Botón cerrar
        ttk.Button(button_frame, text="Cerrar", command=self._close_window).pack(side=tk.RIGHT)
        
    def _setup_event_handlers(self):
        """Configura los manejadores de eventos."""
        self.product_tree.bind('<<TreeviewSelect>>', self._on_product_select)
        self.search_var.trace('w', self._on_search)
        self.product_name_var.trace('w', self._validate_form)
        self.category_var.trace('w', self._validate_form)
        
        if self.barcode_support:
            self.barcode_var.trace('w', self._on_barcode_changed)
            
        self.root.protocol("WM_DELETE_WINDOW", self._close_window)
        
    def _load_initial_data(self):
        """Carga los datos iniciales."""
        try:
            self.logger.info("Cargando datos iniciales...")
            
            # Cargar categorías
            self.categories = self.category_service.get_all_categories()
            category_names = [f"{cat.nombre} ({cat.tipo})" for cat in self.categories]
            self.category_combo['values'] = category_names
            self.logger.info(f"Cargadas {len(self.categories)} categorías")
            
            # Cargar productos
            product_dicts = self.product_service.get_all_products()
            self.products = []
            
            for prod_dict in product_dicts:
                id_categoria = (
                    prod_dict.get('id_categoria') or
                    prod_dict.get('categoria_id') or
                    0
                )
                
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
                
            self.logger.info(f"Cargados {len(self.products)} productos")
            self._update_product_list()
            
        except Exception as e:
            self.logger.error(f"Error cargando datos: {e}")
            messagebox.showerror("Error", f"Error cargando datos: {e}")
            
    def _update_product_list(self, filter_text: str = ""):
        """Actualiza la lista de productos."""
        # Limpiar
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
                
                if self.barcode_support:
                    values = (
                        product.id_producto,
                        str(product.id_producto),  # Código temporal
                        product.nombre,
                        category_name,
                        product.stock,
                        f"B/. {float(product.precio):.2f}",
                        f"{float(product.tasa_impuesto):.1f}%"
                    )
                else:
                    values = (
                        product.id_producto,
                        product.nombre,
                        category_name,
                        product.stock,
                        f"B/. {float(product.precio):.2f}",
                        f"{float(product.tasa_impuesto):.1f}%"
                    )
                
                self.product_tree.insert('', tk.END, values=values)
                
    # === MÉTODOS DE CÓDIGOS DE BARRAS (SOLO SI ESTÁN DISPONIBLES) ===
    
    def _generate_barcode(self):
        """Genera código de barras."""
        if not self.barcode_support:
            return
            
        try:
            import random
            temp_id = random.randint(100000, 999999)
            generated_code = generate_product_code(temp_id, 'CODE128')
            self.barcode_var.set(generated_code)
            messagebox.showinfo("Código Generado", f"Código: {generated_code}")
        except Exception as e:
            messagebox.showerror("Error", f"Error generando código: {e}")
            
    def _validate_barcode(self):
        """Valida el código de barras."""
        if not self.barcode_support:
            return
            
        try:
            code = self.barcode_var.get().strip()
            if not code:
                self.validation_label.config(text="Sin código", foreground='gray')
                return
                
            is_valid = validate_barcode(code)
            if is_valid:
                self.validation_label.config(text="✓ Válido", foreground='green')
            else:
                self.validation_label.config(text="✗ Inválido", foreground='red')
        except Exception as e:
            self.validation_label.config(text="Error", foreground='orange')
            
    def _clear_barcode(self):
        """Limpia el código de barras."""
        if not self.barcode_support:
            return
        self.barcode_var.set("")
        self.validation_label.config(text="Sin código", foreground='gray')
        
    def _scan_barcode(self):
        """Escanea código de barras."""
        if not self.barcode_support:
            return
        messagebox.showinfo("Scanner", "Funcionalidad de escaneo en desarrollo")
        
    def _on_barcode_changed(self, *args):
        """Maneja cambios en código de barras."""
        if self.barcode_support:
            self._validate_barcode()
            
    # === MÉTODOS PRINCIPALES DEL FORMULARIO ===
    
    def _validate_form(self, *args):
        """Valida el formulario."""
        name = self.product_name_var.get().strip()
        category = self.category_var.get().strip()
        
        if (self.is_creating_new or self.editing_product is not None) and name and category:
            self.save_button.config(state='normal')
        else:
            self.save_button.config(state='disabled')
            
    def _save_product(self):
        """Guarda el producto."""
        try:
            # Validar datos
            name = self.product_name_var.get().strip()
            if not name:
                messagebox.showerror("Error", "El nombre es obligatorio")
                return
                
            category_selection = self.category_combo.get()
            if not category_selection:
                messagebox.showerror("Error", "Debe seleccionar una categoría")
                return
                
            category_index = self.category_combo.current()
            if category_index == -1:
                messagebox.showerror("Error", "Categoría no válida")
                return
                
            selected_category = self.categories[category_index]
            
            # Valores numéricos
            try:
                stock = int(float(self.stock_var.get() or "0"))
                cost = float(self.cost_var.get() or "0")
                price = float(self.price_var.get() or "0")
                tax_rate = float(self.tax_var.get() or "0")
            except ValueError:
                messagebox.showerror("Error", "Valores numéricos inválidos")
                return
            
            # Guardar producto
            if self.is_creating_new:
                result = self.product_service.create_product(
                    nombre=name,
                    categoria_id=selected_category.id_categoria,
                    stock_inicial=stock,
                    precio_compra=cost,
                    precio_venta=price,
                    tasa_impuesto=tax_rate
                )
                
                if result:
                    messagebox.showinfo("Éxito", "Producto creado exitosamente")
                    self._load_initial_data()
                    self._cancel_edit()
                else:
                    messagebox.showerror("Error", "No se pudo crear el producto")
                    
            else:
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
                    messagebox.showinfo("Éxito", "Producto actualizado exitosamente")
                    self._load_initial_data()
                    self._cancel_edit()
                else:
                    messagebox.showerror("Error", "No se pudo actualizar el producto")
                    
        except Exception as e:
            self.logger.error(f"Error guardando producto: {e}")
            messagebox.showerror("Error", f"Error guardando producto: {e}")
            
    def _new_product(self):
        """Crear nuevo producto."""
        self._clear_form()
        self.editing_product = None
        self.is_creating_new = True
        self._enable_form()
        
        self.new_button.config(state='disabled')
        self.edit_button.config(state='disabled')
        self.delete_button.config(state='disabled')
        self.cancel_button.config(state='normal')
        
        self.name_entry.focus()
        
    def _edit_product(self):
        """Editar producto seleccionado."""
        selection = self.product_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un producto para editar")
            return
            
        item = self.product_tree.item(selection[0])
        product_id = int(item['values'][0])
        
        # Buscar producto
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
            
    def _delete_product(self):
        """Eliminar producto seleccionado."""
        selection = self.product_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un producto para eliminar")
            return
            
        item = self.product_tree.item(selection[0])
        product_id = int(item['values'][0])
        product_name = item['values'][2] if self.barcode_support else item['values'][1]
        
        result = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro que desea eliminar '{product_name}'?"
        )
        
        if result:
            try:
                success = self.product_service.delete_product(product_id)
                if success:
                    messagebox.showinfo("Éxito", "Producto eliminado exitosamente")
                    self._load_initial_data()
                    self._clear_form()
                    self._disable_form()
                    self.edit_button.config(state='disabled')
                    self.delete_button.config(state='disabled')
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el producto")
            except Exception as e:
                messagebox.showerror("Error", f"Error eliminando producto: {e}")
                
    def _cancel_edit(self):
        """Cancelar edición."""
        self.editing_product = None
        self.is_creating_new = False
        self._clear_form()
        self._disable_form()
        
        self.new_button.config(state='normal')
        self.save_button.config(state='disabled')
        self.edit_button.config(state='disabled')
        self.delete_button.config(state='disabled')
        self.cancel_button.config(state='disabled')
        
    def _clear_form(self):
        """Limpiar formulario."""
        self.product_name_var.set("")
        self.category_var.set("")
        self.stock_var.set("")
        self.cost_var.set("")
        self.price_var.set("")
        self.tax_var.set("")
        
        if self.barcode_support:
            self._clear_barcode()
            
        for item in self.product_tree.selection():
            self.product_tree.selection_remove(item)
            
    def _enable_form(self):
        """Habilitar formulario."""
        self.name_entry.config(state='normal')
        self.category_combo.config(state='readonly')
        self.stock_entry.config(state='normal')
        self.cost_entry.config(state='normal')
        self.price_entry.config(state='normal')
        self.tax_entry.config(state='normal')
        
        if self.barcode_support and hasattr(self, 'barcode_entry'):
            self.barcode_entry.config(state='normal')
            
    def _disable_form(self):
        """Deshabilitar formulario."""
        self.name_entry.config(state='readonly')
        self.category_combo.config(state='disabled')
        self.stock_entry.config(state='readonly')
        self.cost_entry.config(state='readonly')
        self.price_entry.config(state='readonly')
        self.tax_entry.config(state='readonly')
        
        if self.barcode_support and hasattr(self, 'barcode_entry'):
            self.barcode_entry.config(state='readonly')
            
    def _on_product_select(self, event):
        """Manejar selección de producto."""
        selection = self.product_tree.selection()
        if selection:
            item = self.product_tree.item(selection[0])
            product_id = int(item['values'][0])
            
            # Buscar producto
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
                
    def _show_product_in_form(self, product: Producto):
        """Mostrar producto en formulario."""
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
                
        # Mostrar código de barras si está disponible
        if self.barcode_support:
            self.barcode_var.set(str(product.id_producto))
            self._validate_barcode()
            
    def _on_search(self, *args):
        """Manejar búsqueda."""
        search_text = self.search_var.get()
        self._update_product_list(search_text)
        
    def _close_window(self):
        """Cerrar ventana."""
        if self.editing_product is not None or self.is_creating_new:
            result = messagebox.askyesno(
                "Confirmar Cierre",
                "Hay cambios sin guardar. ¿Está seguro?"
            )
            if not result:
                return
                
        self.root.destroy()


def main():
    """Función principal para pruebas."""
    root = tk.Tk()
    root.withdraw()
    
    try:
        product_window = ProductWindow(root)
        root.wait_window(product_window.root)
    except Exception as e:
        messagebox.showerror("Error", f"Error: {e}")
        
    root.destroy()


if __name__ == "__main__":
    main()
