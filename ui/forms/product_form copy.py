"""
SOLUCIÓN INTEGRAL: Formulario de Productos con Visualización Corregida
Sistema de Inventario v2.0

PROBLEMA RESUELTO:
Al crear un nuevo producto ahora SÍ se muestran correctamente los datos del producto 
en el formulario: categoría, costo, precio, impuesto.

MEJORAS IMPLEMENTADAS:
- Auto-selección simplificada y robusta
- Widgets de entrada simplificados sin timing issues
- Mapeo de datos unificado y consistente
- Debugging detallado para identificar problemas
- Visualización inmediata después de crear productos
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List
import logging
from decimal import Decimal
from datetime import datetime

from db.database import get_database_connection
from services.product_service import ProductService
from services.category_service import CategoryService
from models.producto import Producto

class ProductWindow:
    """
    Ventana de gestión de productos con visualización corregida.
    
    CORRECCIONES IMPLEMENTADAS:
    - Auto-selección robusta después de crear productos
    - Widgets simplificados sin problemas de timing
    - Debugging detallado para troubleshooting
    - Mapeo consistente de datos
    """
    
    def __init__(self, parent: tk.Tk):
        """Inicializa la ventana de productos con correcciones aplicadas."""
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
        
        self.logger.info("=== INICIANDO ProductWindow con correcciones ==")
        
        # Inicializar servicios con manejo de errores mejorado
        try:
            db_connection = get_database_connection()
            self.product_service = ProductService(db_connection)
            self.category_service = CategoryService(db_connection)
            self.logger.info("Servicios inicializados correctamente")
        except Exception as e:
            self.logger.error(f"Error conectando a la base de datos: {e}")
            messagebox.showerror("Error", f"No se pudo conectar a la base de datos: {e}")
            return
        
        # Crear ventana
        self.root = tk.Toplevel(parent)
        self.root.title("Gestión de Productos")
        self.root.geometry("1000x700")
        self.root.transient(parent)
        self.root.grab_set()
        
        # Variables de formulario
        self.product_name_var = tk.StringVar()
        self.category_var = tk.StringVar()
        self.search_var = tk.StringVar()
        
        # Variables para campos numéricos (simplificadas)
        self.stock_var = tk.StringVar()
        self.cost_var = tk.StringVar()
        self.price_var = tk.StringVar()
        self.tax_var = tk.StringVar()
        
        # Estado del formulario
        self.editing_product: Optional[Producto] = None
        self.is_creating_new = False
        self.products: List[Producto] = []
        self.categories: List = []
        
        # Flag para modo debug
        self.debug_mode = True
        
        # Crear interfaz simplificada
        self._create_ui()
        self._setup_events()
        self._load_data()
        
        self.logger.info("ProductWindow inicializado completamente")
        
    def _create_ui(self):
        """Crea la interfaz de usuario simplificada."""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configurar grid principal
        main_frame.columnconfigure(0, weight=2)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Título con indicador de versión corregida
        title_label = ttk.Label(
            main_frame,
            text="Gestión de Productos",
            font=("Arial", 16, "bold"),
            foreground="green"
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Panel izquierdo - Lista de productos
        self._create_list_panel(main_frame)
        
        # Panel derecho - Formulario simplificado
        self._create_form_panel_simple(main_frame)
        
        # Panel inferior - Botones con modo debug
        self._create_button_panel(main_frame)
        
    def _create_list_panel(self, parent):
        """Crea el panel de lista de productos."""
        list_frame = ttk.LabelFrame(parent, text="Productos Existentes", padding=10)
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
        
        # TreeView para lista de productos
        columns = ('ID', 'Nombre', 'Categoría', 'Stock', 'Precio', 'Impuesto')
        self.product_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        self.product_tree.heading('ID', text='ID')
        self.product_tree.heading('Nombre', text='Nombre')
        self.product_tree.heading('Categoría', text='Categoría')
        self.product_tree.heading('Stock', text='Stock')
        self.product_tree.heading('Precio', text='Precio')
        self.product_tree.heading('Impuesto', text='Impuesto%')
        
        self.product_tree.column('ID', width=50)
        self.product_tree.column('Nombre', width=180)
        self.product_tree.column('Categoría', width=100)
        self.product_tree.column('Stock', width=60)
        self.product_tree.column('Precio', width=80)
        self.product_tree.column('Impuesto', width=70)
        
        # Scrollbar para TreeView
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.product_tree.yview)
        self.product_tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid TreeView y scrollbar
        self.product_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
    def _create_form_panel_simple(self, parent):
        """Crea el formulario simplificado sin widgets complejos."""
        form_frame = ttk.LabelFrame(parent, text="Datos de Producto", padding=10)
        form_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        form_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Campo nombre
        ttk.Label(form_frame, text="Nombre:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(form_frame, textvariable=self.product_name_var, width=30)
        self.name_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Campo categoría
        ttk.Label(form_frame, text="Categoría:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.category_combo = ttk.Combobox(form_frame, textvariable=self.category_var, state='readonly', width=27)
        self.category_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Campo stock - ENTRADA SIMPLIFICADA
        ttk.Label(form_frame, text="Stock:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.stock_entry = ttk.Entry(form_frame, textvariable=self.stock_var, width=30, justify='right')
        self.stock_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Campo costo - ENTRADA SIMPLIFICADA
        ttk.Label(form_frame, text="Costo:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.cost_entry = ttk.Entry(form_frame, textvariable=self.cost_var, width=30, justify='right')
        self.cost_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Campo precio - ENTRADA SIMPLIFICADA
        ttk.Label(form_frame, text="Precio:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.price_entry = ttk.Entry(form_frame, textvariable=self.price_var, width=30, justify='right')
        self.price_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Campo impuesto - ENTRADA SIMPLIFICADA
        ttk.Label(form_frame, text="Impuesto (%):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.tax_entry = ttk.Entry(form_frame, textvariable=self.tax_var, width=30, justify='right')
        self.tax_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # Información de debug
        if self.debug_mode:
            debug_frame = ttk.LabelFrame(form_frame, text="Debug Info", padding=5)
            debug_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(20, 0))
            debug_frame.columnconfigure(0, weight=1)
            
            self.debug_text = tk.Text(debug_frame, height=6, width=40, font=("Consolas", 8))
            debug_scrollbar = ttk.Scrollbar(debug_frame, orient=tk.VERTICAL, command=self.debug_text.yview)
            self.debug_text.configure(yscrollcommand=debug_scrollbar.set)
            
            self.debug_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            debug_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
            
            self._log_debug("Formulario inicializado en modo debug")
        
    def _create_button_panel(self, parent):
        """Crea el panel de botones con funciones de debug."""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(20, 0))
        
        # Botones principales
        self.new_button = ttk.Button(button_frame, text="Nuevo", command=self._new_product)
        self.new_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.save_button = ttk.Button(button_frame, text="Guardar", command=self._save_product_corrected, state='disabled')
        self.save_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.edit_button = ttk.Button(button_frame, text="Editar", command=self._edit_product, state='disabled')
        self.edit_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.delete_button = ttk.Button(button_frame, text="Eliminar", command=self._delete_product, state='disabled')
        self.delete_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.cancel_button = ttk.Button(button_frame, text="Cancelar", command=self._cancel_edit, state='disabled')
        self.cancel_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Botones de debug
        if self.debug_mode:
            ttk.Separator(button_frame, orient='vertical').pack(side=tk.LEFT, fill='y', padx=10)
            
            ttk.Button(button_frame, text="Test Auto-Selección", 
                      command=self._test_auto_selection).pack(side=tk.LEFT, padx=(0, 5))
            
            ttk.Button(button_frame, text="Debug Datos", 
                      command=self._debug_current_data).pack(side=tk.LEFT, padx=(0, 5))
        
        # Botón cerrar
        ttk.Button(button_frame, text="Cerrar", command=self._close_window).pack(side=tk.RIGHT)
        
    def _setup_events(self):
        """Configura eventos simplificados."""
        # Selección en TreeView
        self.product_tree.bind('<<TreeviewSelect>>', self._on_product_select)
        
        # Búsqueda en tiempo real
        self.search_var.trace('w', self._on_search)
        
        # Validación simplificada
        self.product_name_var.trace('w', self._validate_form_simple)
        self.category_var.trace('w', self._validate_form_simple)
        
        # Protocolo de cierre
        self.root.protocol("WM_DELETE_WINDOW", self._close_window)
        
    def _load_data(self):
        """Carga los datos desde la base de datos con logging detallado."""
        self.logger.info("=== INICIANDO CARGA DE DATOS ==")
        
        try:
            # Cargar productos desde el servicio
            product_dicts = self.product_service.get_all_products()
            self.logger.info(f"Obtenidos {len(product_dicts)} productos del servicio")
            
            # Debug: mostrar estructura del primer producto
            if product_dicts:
                first_product = product_dicts[0]
                self.logger.debug(f"Estructura del primer producto: {first_product.keys()}")
                self._log_debug(f"Primer producto keys: {list(first_product.keys())}")
            
            # Convertir a objetos Producto con mapeo corregido
            self.products = []
            for i, prod_dict in enumerate(product_dicts):
                try:
                    # MAPEO UNIFICADO Y ROBUSTO
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
                    
                    if i < 3:  # Log primeros 3 productos para debug
                        self.logger.debug(f"Producto {i}: {producto.nombre}, Cat: {producto.id_categoria}, Precio: {producto.precio}, Impuesto: {producto.tasa_impuesto}")
                        
                except Exception as e:
                    self.logger.error(f"Error procesando producto {i}: {e}")
                    self._log_debug(f"ERROR en producto {i}: {e}")
            
            self.logger.info(f"Convertidos {len(self.products)} productos a objetos Producto")
            self._update_product_list()
            
            # Cargar categorías para ComboBox
            self.categories = self.category_service.get_all_categories()
            category_names = [f"{cat.nombre} ({cat.tipo})" for cat in self.categories]
            self.category_combo['values'] = category_names
            
            self.logger.info(f"Cargadas {len(self.categories)} categoría")
            self._log_debug(f"Carga completa: {len(self.products)} productos, {len(self.categories)} categoría")
            
        except Exception as e:
            self.logger.error(f"Error en carga de datos: {e}")
            self._log_debug(f"ERROR CARGA: {e}")
            messagebox.showerror("Error", f"No se pudieron cargar los datos: {e}")
    
    def _extract_categoria_id(self, prod_dict):
        """Extrae categoria_id de forma unificada y robusta."""
        # Mapeo robusto con múltiples fallbacks
        id_categoria = (
            prod_dict.get('id_categoria') or    # Nombre del esquema BD
            prod_dict.get('categoria_id') or    # Nombre alternativo
            0  # Fallback
        )
        
        # Log de mapeo para debug
        if 'id_categoria' in prod_dict and 'categoria_id' in prod_dict:
            self.logger.debug(f"Producto tiene ambos campos: id_categoria={prod_dict['id_categoria']}, categoria_id={prod_dict['categoria_id']}")
        
        return id_categoria
        
    def _update_product_list(self, filter_text: str = ""):
        """Actualiza la lista de productos con información mejorada."""
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
                        
                # Insertar con información de impuesto
                self.product_tree.insert('', tk.END, values=(
                    product.id_producto,
                    product.nombre,
                    category_name,
                    product.stock,
                    f"${float(product.precio):.2f}",
                    f"{float(product.tasa_impuesto):.1f}%"
                ))
                
    def _on_product_select(self, event):
        """Maneja la selección de un producto con logging detallado."""
        selection = self.product_tree.selection()
        if selection:
            item = self.product_tree.item(selection[0])
            product_id = int(item['values'][0])
            
            self.logger.info(f"=== PRODUCTO SELECCIONADO: ID {product_id} ==")
            self._log_debug(f"Seleccionado producto ID: {product_id}")
            
            # Buscar producto seleccionado
            selected_product = None
            for product in self.products:
                if product.id_producto == product_id:
                    selected_product = product
                    break
                    
            if selected_product:
                self._show_product_in_form(selected_product)
                
                # Habilitar botones de edición
                self.edit_button.config(state='normal')
                self.delete_button.config(state='normal')
                
                # Deshabilitar campos de formulario
                self._disable_form()
            else:
                self.logger.error(f"No se encontró producto con ID {product_id}")
                self._log_debug(f"ERROR: Producto ID {product_id} no encontrado")
    
    def _show_product_in_form(self, product: Producto):
        """
        Muestra los datos del producto en el formulario de forma simplificada.
        CORRECCIÓN PRINCIPAL: Sin widgets complejos, sin timing issues.
        """
        self.logger.info(f"Mostrando producto en formulario: {product.nombre}")
        
        try:
            # Establecer nombre
            self.product_name_var.set(product.nombre)
            
            # Establecer valores numéricos DIRECTAMENTE (sin formateo complejo)
            self.stock_var.set(str(product.stock))
            self.cost_var.set(f"{float(product.costo):.2f}")
            self.price_var.set(f"{float(product.precio):.2f}")
            self.tax_var.set(f"{float(product.tasa_impuesto):.2f}")
            
            # Seleccionar categoría
            for i, cat in enumerate(self.categories):
                if cat.id_categoria == product.id_categoria:
                    self.category_combo.current(i)
                    break
            
            # Log de éxito
            datos_mostrados = {
                'nombre': product.nombre,
                'categoria': product.id_categoria,
                'stock': product.stock,
                'costo': product.costo,
                'precio': product.precio,
                'impuesto': product.tasa_impuesto
            }
            
            self.logger.info(f"Datos mostrados correctamente: {datos_mostrados}")
            self._log_debug(f"Mostrado: {product.nombre}, ${product.precio}, {product.tasa_impuesto}%")
            
        except Exception as e:
            self.logger.error(f"Error mostrando producto en formulario: {e}")
            self._log_debug(f"ERROR mostrando: {e}")

    def _save_product_corrected(self):
        """
        Versión corregida del método de guardado con auto-selección robusta.
        CORRECCIÓN PRINCIPAL: Auto-selección inmediata y confiable.
        """
        self.logger.info("=== INICIANDO GUARDADO DE PRODUCTO (CORREGIDO) ===")
        self._log_debug("Iniciando guardado...")
        
        try:
            # Validar datos obligatorios
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
                
            # Obtener ID de categoría seleccionada
            category_index = self.category_combo.current()
            if category_index == -1:
                messagebox.showerror("Error", "Categoría no válida")
                return
                
            selected_category = self.categories[category_index]
            
            # Obtener y validar valores numéricos
            try:
                stock = int(float(self.stock_var.get() or "0"))
                cost = float(self.cost_var.get() or "0")
                price = float(self.price_var.get() or "0")
                tax_rate = float(self.tax_var.get() or "0")
            except ValueError as e:
                messagebox.showerror("Error", f"Valores numéricos inválidos: {e}")
                return

            self.logger.info(f"Datos validados: {name}, Cat:{selected_category.id_categoria}, ${price}, {tax_rate}%")

            # Guardar producto
            if self.is_creating_new:  # Nuevo producto
                self.logger.info("Creando nuevo producto...")
                
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
                    self.logger.info(f"Producto creado exitosamente con ID: {result.id_producto}")
                    
                    # AUTO-SELECCIÓN CORREGIDA: Inmediata y robusta
                    self._auto_select_created_product(result.id_producto, name)
                    
                else:
                    messagebox.showerror("Error", "No se pudo crear el producto")
                    return
                    
            else:  # Editar producto existente
                self.logger.info(f"Actualizando producto ID: {self.editing_product.id_producto}")
                
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
                    self.logger.info(f"Producto actualizado exitosamente")

                    # Recargar y cancelar edición
                    self._load_data()
                    self._cancel_edit()
                else:
                    messagebox.showerror("Error", "No se pudo actualizar el producto")
                    return
            
        except Exception as e:
            self.logger.error(f"Error guardando producto: {e}")
            self._log_debug(f"ERROR GUARDADO: {e}")
            messagebox.showerror("Error", f"Error inesperado al guardar: {e}")
    
    def _auto_select_created_product(self, product_id: int, product_name: str):
        """
        Auto-selección robusta del producto recién creado.
        CORRECCIÓN PRINCIPAL: Simplificada, inmediata, con debugging detallado.
        """
        self.logger.info(f"=== AUTO-SELECCIÓN DEL PRODUCTO CREADO: ID {product_id} ===")
        self._log_debug(f"Auto-seleccionando producto: {product_name} (ID: {product_id})")

        try:
            # Paso 1: Recargar datos PRIMERO
            self.logger.info("Paso 1: Recargando datos...")
            self._load_data()
            
            # Paso 2: Buscar el producto en la lista actualizada
            self.logger.info("Paso 2: Buscando producto en lista...")
            target_product = None
            for product in self.products:
                if product.id_producto == product_id:
                    target_product = product
                    break
            
            if not target_product:
                self.logger.warning(f"Producto ID {product_id} no encontrado después de recarga")
                self._log_debug(f"ADVERTENCIA: Producto {product_id} no encontrado")
                return False
            
            # Paso 3: Buscar y seleccionar en TreeView
            self.logger.info("Paso 3: Seleccionando en TreeView...")
            for item in self.product_tree.get_children():
                item_values = self.product_tree.item(item)['values']
                if item_values and int(item_values[0]) == product_id:
                    # Seleccionar el item
                    self.product_tree.selection_set(item)
                    self.product_tree.focus(item)
                    self.product_tree.see(item)

                    self.logger.info("Paso 4: Mostrando datos en formulario...")
                    # Mostrar datos en formulario
                    self._show_product_in_form(target_product)
                    
                    # Configurar estado de botones
                    self.new_button.config(state='normal')
                    self.save_button.config(state='disabled')
                    self.cancel_button.config(state='disabled')
                    self.edit_button.config(state='normal')
                    self.delete_button.config(state='normal')
                    
                    # Deshabilitar formulario (modo visualización)
                    self._disable_form()
                    
                    self.logger.info(f"[OK] AUTO-SELECCIÓN EXITOSA: {product_name}")
                    self._log_debug(f"[OK] AUTO-SELECCIÓN EXITOSA: {product_name}")
                    return True

            self.logger.warning(f"Item de TreeView para producto {product_id} no encontrado")
            self._log_debug(f"ADVERTENCIA: Item TreeView no encontrado")
            return False
            
        except Exception as e:
            self.logger.error(f"Error en auto-selección: {e}")
            self._log_debug(f"ERROR AUTO-SELECCIÓN: {e}")
            return False
    
    def _test_auto_selection(self):
        """Función de debug para probar auto-selección."""
        if self.products:
            first_product = self.products[0]
            self.logger.info(f"TESTING auto-selección con producto: {first_product.nombre}")
            self._auto_select_created_product(first_product.id_producto, first_product.nombre)
        else:
            self._log_debug("No hay productos para probar auto-selección")
    
    def _debug_current_data(self):
        """Función de debug para mostrar datos actuales."""
        debug_info = {
            'productos_cargados': len(self.products),
            'categorias_cargadas': len(self.categories),
            'nombre_actual': self.product_name_var.get(),
            'categoria_actual': self.category_var.get(),
            'stock_actual': self.stock_var.get(),
            'precio_actual': self.price_var.get(),
            'impuesto_actual': self.tax_var.get()
        }

        self.logger.info(f"DEBUG - Estado actual: {debug_info}")
        self._log_debug(f"DEBUG Estado: {debug_info}")

    def _log_debug(self, message: str):
        """Registra mensaje en el área de debug si está disponible."""
        if hasattr(self, 'debug_text') and self.debug_mode:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.debug_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.debug_text.see(tk.END)
    
    # Métodos simplificados para operaciones básicas
    def _validate_form_simple(self, *args):
        """Validación simplificada del formulario."""
        name = self.product_name_var.get().strip()
        category = self.category_var.get().strip()
        
        if (self.is_creating_new or self.editing_product is not None) and name and category:
            self.save_button.config(state='normal')
        else:
            self.save_button.config(state='disabled')
    
    def _new_product(self):
        """Inicia creación de nuevo producto."""
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
        """Inicia edición de producto seleccionado."""
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
        """Elimina producto seleccionado."""
        selection = self.product_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un producto para eliminar")
            return
            
        item = self.product_tree.item(selection[0])
        product_id = int(item['values'][0])
        product_name = item['values'][1]
        
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
        """Cancela la edición actual."""
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
        """Limpia el formulario."""
        self.product_name_var.set("")
        self.category_var.set("")
        self.stock_var.set("")
        self.cost_var.set("")
        self.price_var.set("")
        self.tax_var.set("")
        
        for item in self.product_tree.selection():
            self.product_tree.selection_remove(item)
    
    def _enable_form(self):
        """Habilita campos del formulario."""
        self.name_entry.config(state='normal')
        self.category_combo.config(state='readonly')
        self.stock_entry.config(state='normal')
        self.cost_entry.config(state='normal')
        self.price_entry.config(state='normal')
        self.tax_entry.config(state='normal')
    
    def _disable_form(self):
        """Deshabilita campos del formulario."""
        self.name_entry.config(state='readonly')
        self.category_combo.config(state='disabled')
        self.stock_entry.config(state='readonly')
        self.cost_entry.config(state='readonly')
        self.price_entry.config(state='readonly')
        self.tax_entry.config(state='readonly')
    
    def _on_search(self, *args):
        """Maneja búsqueda en tiempo real."""
        search_text = self.search_var.get()
        self._update_product_list(search_text)
    
    def _close_window(self):
        """Cierra la ventana."""
        if self.editing_product is not None or self.is_creating_new:
            result = messagebox.askyesno(
                "Confirmar Cierre",
                "Hay cambios sin guardar. ¿Está seguro que desea cerrar?"
            )
            if not result:
                return

        self.logger.info("Cerrando ProductWindow...")
        self.root.destroy()

def main():
    """Función principal para probar la ventana corregida."""
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal
    
    # Configurar logging
    logging.basicConfig(level=logging.DEBUG)
    
    try:
        # Crear ventana de productos corregida
        product_window = ProductWindow(root)
        root.wait_window(product_window.root)
    except Exception as e:
        messagebox.showerror("Error", f"Error iniciando aplicación: {e}")
    
    root.destroy()

if __name__ == "__main__":
    main()
