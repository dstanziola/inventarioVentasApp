"""
Formulario para búsqueda avanzada por código de barras.

Este módulo proporciona una interfaz gráfica completa para:
- Búsqueda manual de productos por código
- Lectura automática con scanner
- Filtros avanzados de búsqueda
- Visualización detallada de resultados
- Exportación de resultados
- Historial de búsquedas

Autor: Sistema de Inventario Copy Point S.A.
Fecha: Junio 2025
"""

import logging
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Dict, Optional, Any
import csv
import json
import threading
import time
from datetime import datetime

# Imports del sistema
from models.producto import Producto
from models.categoria import Categoria
from services.product_service import ProductService
from services.barcode_service import BarcodeService
from services.category_service import CategoryService
from src.utils.barcode_utils import BarcodeUtils, validate_barcode
from ui.utils.window_manager import WindowManager

# Configurar logging
logger = logging.getLogger(__name__)


class BarcodeSearchForm(tk.Toplevel):
    """
    Formulario para búsqueda avanzada por código de barras.
    
    Permite buscar productos usando códigos de barras tanto manual
    como automáticamente, con filtros avanzados y exportación.
    """
    
    def __init__(self, parent=None):
        """
        Inicializar formulario de búsqueda por códigos.
        
        Args:
            parent: Ventana padre
        """
        super().__init__(parent)
        
        # Configuración de ventana
        self.title("Búsqueda por Código de Barras")
        self.geometry("1100x700")
        self.resizable(True, True)
        
        # Centrar ventana
        WindowManager.center_window(self, 1100, 700)
        
        # Variables
        self.parent = parent
        self.search_results = []
        self.search_history = []
        self.scanner_active = False
        self.scanner_thread = None
        
        # Variables Tkinter
        self.code_var = tk.StringVar()
        self.format_var = tk.StringVar()
        self.category_filter_var = tk.StringVar()
        self.min_price_var = tk.StringVar()
        self.max_price_var = tk.StringVar()
        self.stock_filter_var = tk.StringVar()
        self.scanner_status_var = tk.StringVar(value="Desconectado")
        
        # Servicios
        try:
            self.product_service = ProductService()
            self.barcode_service = BarcodeService()
            self.category_service = CategoryService()
        except Exception as e:
            logger.error(f"Error inicializando servicios: {e}")
            messagebox.showerror("Error", f"Error inicializando servicios: {e}")
            self.destroy()
            return
        
        # Datos
        self.categories = []
        
        # Configurar interfaz
        self.setup_ui()
        
        # Cargar datos iniciales
        self.load_initial_data()
        
        # Configurar eventos
        self.setup_events()
        
        # Verificar estado del scanner
        self.check_scanner_status()
        
        logger.info("BarcodeSearchForm inicializado correctamente")
    
    def setup_ui(self):
        """Configurar interfaz de usuario."""
        try:
            # Frame principal
            main_frame = ttk.Frame(self)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Panel superior - Búsqueda
            self.setup_search_panel(main_frame)
            
            # Panel central - Resultados y detalles
            center_paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
            center_paned.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
            
            # Panel izquierdo - Resultados
            self.setup_results_panel(center_paned)
            
            # Panel derecho - Detalles y filtros
            self.setup_details_panel(center_paned)
            
            # Panel inferior - Botones de acción
            self.setup_action_panel(main_frame)
            
        except Exception as e:
            logger.error(f"Error configurando UI: {e}")
            raise
    
    def setup_search_panel(self, parent):
        """Configurar panel de búsqueda."""
        search_frame = ttk.LabelFrame(parent, text="Búsqueda por Código")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Primera fila - Campo de código y botones
        input_frame = ttk.Frame(search_frame)
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(input_frame, text="Código:").pack(side=tk.LEFT)
        
        self.code_entry = ttk.Entry(input_frame, textvariable=self.code_var, 
                                   width=30, font=('Consolas', 12))
        self.code_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        self.search_button = ttk.Button(input_frame, text="Buscar", 
                                       command=self.search_by_code)
        self.search_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.clear_code_button = ttk.Button(input_frame, text="Limpiar", 
                                           command=self.clear_code)
        self.clear_code_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón de scanner
        self.scanner_button = ttk.Button(input_frame, text="Activar Scanner", 
                                        command=self.toggle_scanner)
        self.scanner_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # Segunda fila - Información de formato y estado
        info_frame = ttk.Frame(search_frame)
        info_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Label(info_frame, text="Formato:").pack(side=tk.LEFT)
        self.format_label = ttk.Label(info_frame, textvariable=self.format_var, 
                                     foreground='blue')
        self.format_label.pack(side=tk.LEFT, padx=(5, 20))
        
        ttk.Label(info_frame, text="Scanner:").pack(side=tk.LEFT)
        self.scanner_status_label = ttk.Label(info_frame, textvariable=self.scanner_status_var)
        self.scanner_status_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Indicador de actividad del scanner
        self.scanner_indicator = tk.Label(info_frame, text="●", foreground='red', 
                                         font=('Arial', 12, 'bold'))
        self.scanner_indicator.pack(side=tk.LEFT, padx=(5, 0))
    
    def setup_results_panel(self, parent):
        """Configurar panel de resultados."""
        results_frame = ttk.LabelFrame(parent, text="Resultados de Búsqueda")
        parent.add(results_frame, weight=3)
        
        # Frame para el treeview
        tree_frame = ttk.Frame(results_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview para resultados
        columns = ('codigo', 'nombre', 'categoria', 'precio', 'stock', 'formato', 'timestamp')
        self.results_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=12)
        
        # Configurar columnas
        self.results_tree.heading('codigo', text='Código')
        self.results_tree.heading('nombre', text='Producto')
        self.results_tree.heading('categoria', text='Categoría')
        self.results_tree.heading('precio', text='Precio')
        self.results_tree.heading('stock', text='Stock')
        self.results_tree.heading('formato', text='Formato')
        self.results_tree.heading('timestamp', text='Búsqueda')
        
        # Configurar ancho de columnas
        self.results_tree.column('codigo', width=120)
        self.results_tree.column('nombre', width=200)
        self.results_tree.column('categoria', width=100)
        self.results_tree.column('precio', width=80, anchor='e')
        self.results_tree.column('stock', width=60, anchor='center')
        self.results_tree.column('formato', width=80, anchor='center')
        self.results_tree.column('timestamp', width=120, anchor='center')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, 
                                   command=self.results_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, 
                                   command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=v_scrollbar.set, 
                                   xscrollcommand=h_scrollbar.set)
        
        # Empaquetar
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Frame para información de resultados
        info_frame = ttk.Frame(results_frame)
        info_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.results_count_label = ttk.Label(info_frame, text="Resultados: 0")
        self.results_count_label.pack(side=tk.LEFT)
        
        ttk.Button(info_frame, text="Limpiar Resultados", 
                  command=self.clear_results).pack(side=tk.RIGHT)
    
    def setup_details_panel(self, parent):
        """Configurar panel de detalles y filtros."""
        details_frame = ttk.LabelFrame(parent, text="Detalles y Filtros")
        parent.add(details_frame, weight=1)
        
        # Notebook para organizar contenido
        self.details_notebook = ttk.Notebook(details_frame)
        self.details_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Pestaña de detalles del producto
        self.setup_product_details_tab()
        
        # Pestaña de filtros avanzados
        self.setup_filters_tab()
        
        # Pestaña de historial
        self.setup_history_tab()
    
    def setup_product_details_tab(self):
        """Configurar pestaña de detalles del producto."""
        details_tab = ttk.Frame(self.details_notebook)
        self.details_notebook.add(details_tab, text="Detalles")
        
        # Frame scrollable para detalles
        details_canvas = tk.Canvas(details_tab)
        details_scrollbar = ttk.Scrollbar(details_tab, orient=tk.VERTICAL, 
                                         command=details_canvas.yview)
        scrollable_frame = ttk.Frame(details_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: details_canvas.configure(scrollregion=details_canvas.bbox("all"))
        )
        
        details_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        details_canvas.configure(yscrollcommand=details_scrollbar.set)
        
        # Texto para mostrar detalles
        self.details_text = tk.Text(scrollable_frame, height=15, width=40, 
                                   wrap=tk.WORD, state=tk.DISABLED)
        self.details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Empaquetar canvas
        details_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        details_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botones de acción para producto seleccionado
        product_actions = ttk.Frame(details_tab)
        product_actions.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        ttk.Button(product_actions, text="Editar Producto", 
                  command=self.edit_selected_product).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(product_actions, text="Ver en Inventario", 
                  command=self.view_in_inventory).pack(side=tk.LEFT)
    
    def setup_filters_tab(self):
        """Configurar pestaña de filtros avanzados."""
        filters_tab = ttk.Frame(self.details_notebook)
        self.details_notebook.add(filters_tab, text="Filtros")
        
        # Filtro por categoría
        category_frame = ttk.LabelFrame(filters_tab, text="Categoría")
        category_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.category_filter_combo = ttk.Combobox(category_frame, 
                                                 textvariable=self.category_filter_var,
                                                 state="readonly")
        self.category_filter_combo.pack(fill=tk.X, padx=10, pady=10)
        
        # Filtros de precio
        price_frame = ttk.LabelFrame(filters_tab, text="Rango de Precio")
        price_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        price_row1 = ttk.Frame(price_frame)
        price_row1.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(price_row1, text="Desde:").pack(side=tk.LEFT)
        ttk.Entry(price_row1, textvariable=self.min_price_var, width=15).pack(side=tk.LEFT, padx=(5, 10))
        ttk.Label(price_row1, text="Hasta:").pack(side=tk.LEFT)
        ttk.Entry(price_row1, textvariable=self.max_price_var, width=15).pack(side=tk.LEFT, padx=(5, 0))
        
        # Filtro de stock
        stock_frame = ttk.LabelFrame(filters_tab, text="Estado de Stock")
        stock_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        stock_options = ["Todos", "En Stock", "Sin Stock", "Stock Bajo"]
        self.stock_filter_combo = ttk.Combobox(stock_frame, values=stock_options,
                                              textvariable=self.stock_filter_var,
                                              state="readonly")
        self.stock_filter_combo.pack(fill=tk.X, padx=10, pady=10)
        self.stock_filter_combo.set("Todos")
        
        # Botones de filtro
        filter_buttons = ttk.Frame(filters_tab)
        filter_buttons.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(filter_buttons, text="Aplicar Filtros", 
                  command=self.apply_filters).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(filter_buttons, text="Limpiar Filtros", 
                  command=self.clear_filters).pack(side=tk.LEFT)
    
    def setup_history_tab(self):
        """Configurar pestaña de historial."""
        history_tab = ttk.Frame(self.details_notebook)
        self.details_notebook.add(history_tab, text="Historial")
        
        # Lista de búsquedas recientes
        history_frame = ttk.LabelFrame(history_tab, text="Búsquedas Recientes")
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Listbox para historial
        self.history_listbox = tk.Listbox(history_frame, height=10)
        self.history_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Botones de historial
        history_buttons = ttk.Frame(history_tab)
        history_buttons.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(history_buttons, text="Buscar Nuevamente", 
                  command=self.search_from_history).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(history_buttons, text="Limpiar Historial", 
                  command=self.clear_history).pack(side=tk.LEFT)
    
    def setup_action_panel(self, parent):
        """Configurar panel de botones de acción."""
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Frame para botones principales
        button_frame = ttk.Frame(action_frame)
        button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(button_frame, text="Exportar Resultados", 
                  command=self.export_results).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Búsqueda en Lote", 
                  command=self.batch_search_dialog).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Configurar Scanner", 
                  command=self.configure_scanner).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Cerrar", 
                  command=self.destroy).pack(side=tk.LEFT)
        
        # Label de estado
        self.status_label = ttk.Label(action_frame, text="Listo para búsqueda")
        self.status_label.pack(anchor=tk.W)
    
    def setup_events(self):
        """Configurar eventos de la interfaz."""
        # Eventos del campo de código
        self.code_entry.bind('<Return>', lambda e: self.search_by_code())
        self.code_entry.bind('<KeyRelease>', self.on_code_changed)
        
        # Eventos del treeview de resultados
        self.results_tree.bind('<<TreeviewSelect>>', self.on_result_selection_changed)
        self.results_tree.bind('<Double-1>', self.on_result_double_click)
        
        # Eventos del historial
        self.history_listbox.bind('<Double-1>', self.search_from_history)
        
        # Evento de cierre
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Timer para verificar scanner
        self.after(1000, self.check_scanner_input)
    
    def load_initial_data(self):
        """Cargar datos iniciales."""
        try:
            # Cargar categorías
            self.categories = self.category_service.get_all()
            self.load_categories_to_filter()
            
            # Cargar historial desde archivo si existe
            self.load_search_history()
            
        except Exception as e:
            logger.error(f"Error cargando datos iniciales: {e}")
    
    def load_categories_to_filter(self):
        """Cargar categorías en el filtro."""
        try:
            category_names = ["Todas"] + [cat.nombre for cat in self.categories]
            self.category_filter_combo['values'] = category_names
            self.category_filter_combo.set("Todas")
        except Exception as e:
            logger.error(f"Error cargando categorías: {e}")
    
    def search_by_code(self):
        """Buscar producto por código."""
        try:
            code = self.code_var.get().strip()
            
            if not code:
                messagebox.showwarning("Advertencia", "Ingrese un código para buscar")
                return
            
            self.update_status("Buscando producto...")
            
            # Detectar formato del código
            format_info = self.detect_code_format(code)
            self.format_var.set(format_info)
            
            # Buscar producto
            product = self.barcode_service.search_product_by_code(code)
            
            if product:
                # Agregar a resultados
                self.add_result_to_tree(product, code)
                
                # Agregar al historial
                self.add_to_history(code, format_info)
                
                self.update_status(f"Producto encontrado: {product.nombre}")
                
                # Limpiar campo de búsqueda
                self.code_var.set("")
                
            else:
                self.update_status("Producto no encontrado")
                messagebox.showinfo("No encontrado", f"No se encontró producto con código: {code}")
            
        except Exception as e:
            logger.error(f"Error en búsqueda: {e}")
            messagebox.showerror("Error", f"Error en búsqueda: {e}")
            self.update_status("Error en búsqueda")
    
    def detect_code_format(self, code: str) -> str:
        """Detectar formato del código de barras."""
        try:
            info = BarcodeUtils.extract_product_info(code)
            if info['valid']:
                return info.get('format', 'DESCONOCIDO')
            else:
                return 'INVÁLIDO'
        except Exception as e:
            logger.debug(f"Error detectando formato: {e}")
            return 'DESCONOCIDO'
    
    def validate_code_format(self) -> bool:
        """Validar formato del código actual."""
        code = self.code_var.get().strip()
        if not code:
            return False
        
        return validate_barcode(code)
    
    def add_result_to_tree(self, product: Producto, code: str):
        """Agregar resultado al treeview."""
        try:
            # Obtener nombre de categoría
            category_name = "Sin categoría"
            if product.id_categoria:
                try:
                    category = self.category_service.get_by_id(product.id_categoria)
                    category_name = category.nombre if category else "Sin categoría"
                except:
                    pass
            
            # Formatear precio
            precio_str = f"B/. {product.precio:.2f}" if product.precio else "N/A"
            
            # Detectar formato
            format_code = self.detect_code_format(code)
            
            # Timestamp
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Insertar en tree
            item = self.results_tree.insert('', 0, values=(  # Insertar al principio
                code,
                product.nombre,
                category_name,
                precio_str,
                product.stock or 0,
                format_code,
                timestamp
            ))
            
            # Seleccionar el nuevo item
            self.results_tree.selection_set(item)
            self.results_tree.focus(item)
            
            # Agregar a lista de resultados
            self.search_results.append({
                'code': code,
                'product': product,
                'format': format_code,
                'timestamp': timestamp
            })
            
            self.update_results_count()
            
        except Exception as e:
            logger.error(f"Error agregando resultado: {e}")
    
    def on_result_selection_changed(self, event):
        """Manejar cambio de selección en resultados."""
        try:
            selected_items = self.results_tree.selection()
            
            if selected_items:
                item = selected_items[0]
                values = self.results_tree.item(item, 'values')
                code = values[0]
                
                # Encontrar producto en resultados
                result = next((r for r in self.search_results if r['code'] == code), None)
                
                if result:
                    self.show_product_details(result['product'], code)
            
        except Exception as e:
            logger.error(f"Error en selección de resultado: {e}")
    
    def on_result_double_click(self, event):
        """Manejar doble clic en resultado."""
        try:
            selected_items = self.results_tree.selection()
            
            if selected_items:
                # Abrir detalles del producto
                self.edit_selected_product()
            
        except Exception as e:
            logger.error(f"Error en doble clic: {e}")
    
    def show_product_details(self, product: Producto, code: str = ""):
        """Mostrar detalles del producto seleccionado."""
        try:
            # Habilitar texto
            self.details_text.config(state=tk.NORMAL)
            self.details_text.delete('1.0', tk.END)
            
            # Formatear información
            details = f"""INFORMACIÓN DEL PRODUCTO

Código escaneado: {code}
Formato detectado: {self.detect_code_format(code)}

ID Producto: {product.id_producto}
Nombre: {product.nombre}
Precio: B/. {product.precio:.2f if product.precio else 0.00}
Costo: B/. {product.costo:.2f if product.costo else 0.00}
Stock: {product.stock if product.stock is not None else 'N/A'}
Tasa de Impuesto: {product.tasa_impuesto:.2f}% if product.tasa_impuesto else 0.00%
Estado: {'Activo' if product.activo else 'Inactivo'}

INFORMACIÓN DEL CÓDIGO

Validación: {'✓ Válido' if validate_barcode(code) else '✗ Inválido'}
"""

            # Agregar información adicional del código
            try:
                code_info = BarcodeUtils.extract_product_info(code)
                if code_info.get('country_code'):
                    details += f"Código de país: {code_info['country_code']}\n"
                if code_info.get('manufacturer_code'):
                    details += f"Código fabricante: {code_info['manufacturer_code']}\n"
                if code_info.get('metadata', {}).get('country_name'):
                    details += f"País: {code_info['metadata']['country_name']}\n"
            except:
                pass
            
            self.details_text.insert('1.0', details)
            self.details_text.config(state=tk.DISABLED)
            
        except Exception as e:
            logger.error(f"Error mostrando detalles: {e}")
    
    def toggle_scanner(self):
        """Activar/desactivar scanner automático."""
        try:
            if not self.scanner_active:
                # Verificar conexión del scanner
                if self.barcode_service.is_connected():
                    self.scanner_active = True
                    self.scanner_button.config(text="Detener Scanner")
                    self.scanner_indicator.config(foreground='green')
                    self.scanner_status_var.set("Activo")
                    self.update_status("Scanner activado - Listo para escanear")
                else:
                    messagebox.showerror("Error", "No se detectó ningún scanner conectado")
            else:
                self.scanner_active = False
                self.scanner_button.config(text="Activar Scanner")
                self.scanner_indicator.config(foreground='red')
                self.scanner_status_var.set("Inactivo")
                self.update_status("Scanner desactivado")
            
        except Exception as e:
            logger.error(f"Error toggling scanner: {e}")
            messagebox.showerror("Error", f"Error con scanner: {e}")
    
    def check_scanner_input(self):
        """Verificar entrada del scanner automáticamente."""
        try:
            if self.scanner_active:
                try:
                    # Leer código del scanner
                    code = self.barcode_service.read_code(timeout=0.1)
                    
                    if code:
                        # Procesar código automáticamente
                        self.code_var.set(code)
                        self.search_by_code()
                        
                        # Efecto visual
                        self.scanner_indicator.config(foreground='yellow')
                        self.after(200, lambda: self.scanner_indicator.config(foreground='green'))
                        
                except Exception as e:
                    # No es crítico si no hay lectura
                    pass
            
            # Programar próxima verificación
            self.after(100, self.check_scanner_input)
            
        except Exception as e:
            logger.debug(f"Error verificando scanner: {e}")
            self.after(1000, self.check_scanner_input)  # Verificar menos frecuentemente si hay error
    
    def check_scanner_status(self):
        """Verificar estado del scanner."""
        try:
            connected = self.barcode_service.is_connected()
            
            if connected:
                self.scanner_status_var.set("Conectado")
                self.scanner_button.config(state=tk.NORMAL)
            else:
                self.scanner_status_var.set("Desconectado")
                self.scanner_button.config(state=tk.DISABLED)
                
        except Exception as e:
            logger.error(f"Error verificando estado scanner: {e}")
            self.scanner_status_var.set("Error")
    
    def on_code_changed(self, event):
        """Manejar cambio en campo de código."""
        try:
            code = self.code_var.get().strip()
            
            if code:
                # Detectar formato en tiempo real
                format_info = self.detect_code_format(code)
                self.format_var.set(format_info)
                
                # Colorear según validez
                if format_info == 'INVÁLIDO':
                    self.format_label.config(foreground='red')
                elif format_info == 'DESCONOCIDO':
                    self.format_label.config(foreground='orange')
                else:
                    self.format_label.config(foreground='green')
            else:
                self.format_var.set("")
                
        except Exception as e:
            logger.debug(f"Error procesando cambio de código: {e}")
    
    def clear_code(self):
        """Limpiar campo de código."""
        self.code_var.set("")
        self.format_var.set("")
    
    def clear_results(self):
        """Limpiar resultados de búsqueda."""
        try:
            # Limpiar treeview
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)
            
            # Limpiar lista
            self.search_results.clear()
            
            # Limpiar detalles
            self.details_text.config(state=tk.NORMAL)
            self.details_text.delete('1.0', tk.END)
            self.details_text.config(state=tk.DISABLED)
            
            self.update_results_count()
            self.update_status("Resultados limpiados")
            
        except Exception as e:
            logger.error(f"Error limpiando resultados: {e}")
    
    def add_to_history(self, code: str, format_info: str):
        """Agregar búsqueda al historial."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            history_entry = {
                'code': code,
                'format': format_info,
                'timestamp': timestamp
            }
            
            # Evitar duplicados recientes
            if not any(h['code'] == code for h in self.search_history[-5:]):
                self.search_history.insert(0, history_entry)
                
                # Limitar historial a 50 entradas
                if len(self.search_history) > 50:
                    self.search_history = self.search_history[:50]
                
                # Actualizar listbox
                self.update_history_listbox()
                
                # Guardar historial
                self.save_search_history()
            
        except Exception as e:
            logger.error(f"Error agregando al historial: {e}")
    
    def update_history_listbox(self):
        """Actualizar listbox del historial."""
        try:
            self.history_listbox.delete(0, tk.END)
            
            for entry in self.search_history:
                display_text = f"{entry['code']} ({entry['format']}) - {entry['timestamp']}"
                self.history_listbox.insert(tk.END, display_text)
                
        except Exception as e:
            logger.error(f"Error actualizando historial: {e}")
    
    def search_from_history(self, event=None):
        """Buscar desde historial."""
        try:
            selection = self.history_listbox.curselection()
            
            if selection:
                index = selection[0]
                entry = self.search_history[index]
                
                # Establecer código y buscar
                self.code_var.set(entry['code'])
                self.search_by_code()
            
        except Exception as e:
            logger.error(f"Error buscando desde historial: {e}")
    
    def load_search_history(self):
        """Cargar historial desde archivo."""
        try:
            history_file = "config/search_history.json"
            
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    self.search_history = json.load(f)
                
                self.update_history_listbox()
                
        except Exception as e:
            logger.debug(f"No se pudo cargar historial: {e}")
    
    def save_search_history(self):
        """Guardar historial en archivo."""
        try:
            os.makedirs("config", exist_ok=True)
            
            with open("config/search_history.json", 'w', encoding='utf-8') as f:
                json.dump(self.search_history, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Error guardando historial: {e}")
    
    def clear_history(self):
        """Limpiar historial de búsquedas."""
        try:
            if messagebox.askyesno("Confirmar", "¿Está seguro de limpiar el historial?"):
                self.search_history.clear()
                self.update_history_listbox()
                self.save_search_history()
                self.update_status("Historial limpiado")
            
        except Exception as e:
            logger.error(f"Error limpiando historial: {e}")
    
    def apply_filters(self):
        """Aplicar filtros avanzados."""
        try:
            # TODO: Implementar lógica de filtros
            # Por ahora solo mostrar mensaje
            filters_applied = []
            
            if self.category_filter_var.get() and self.category_filter_var.get() != "Todas":
                filters_applied.append(f"Categoría: {self.category_filter_var.get()}")
            
            if self.min_price_var.get():
                filters_applied.append(f"Precio mín: {self.min_price_var.get()}")
            
            if self.max_price_var.get():
                filters_applied.append(f"Precio máx: {self.max_price_var.get()}")
            
            if self.stock_filter_var.get() and self.stock_filter_var.get() != "Todos":
                filters_applied.append(f"Stock: {self.stock_filter_var.get()}")
            
            if filters_applied:
                message = "Filtros aplicados:\n" + "\n".join(filters_applied)
                self.update_status("Filtros aplicados")
            else:
                message = "No se aplicaron filtros"
                self.update_status("Sin filtros activos")
            
            messagebox.showinfo("Filtros", message)
            
        except Exception as e:
            logger.error(f"Error aplicando filtros: {e}")
            messagebox.showerror("Error", f"Error aplicando filtros: {e}")
    
    def clear_filters(self):
        """Limpiar todos los filtros."""
        self.category_filter_var.set("Todas")
        self.min_price_var.set("")
        self.max_price_var.set("")
        self.stock_filter_var.set("Todos")
        self.update_status("Filtros limpiados")
    
    def export_results(self):
        """Exportar resultados a CSV."""
        try:
            if not self.search_results:
                messagebox.showwarning("Advertencia", "No hay resultados para exportar")
                return
            
            # Seleccionar archivo
            filename = filedialog.asksaveasfilename(
                title="Exportar Resultados",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if not filename:
                return
            
            # Escribir CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Código', 'Producto', 'Precio', 'Stock', 'Formato', 'Hora Búsqueda']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                
                for result in self.search_results:
                    product = result['product']
                    writer.writerow({
                        'Código': result['code'],
                        'Producto': product.nombre,
                        'Precio': f"B/. {product.precio:.2f}" if product.precio else "N/A",
                        'Stock': product.stock if product.stock is not None else 'N/A',
                        'Formato': result['format'],
                        'Hora Búsqueda': result['timestamp']
                    })
            
            self.update_status(f"Resultados exportados: {filename}")
            messagebox.showinfo("Éxito", f"Resultados exportados exitosamente:\n{filename}")
            
        except Exception as e:
            logger.error(f"Error exportando resultados: {e}")
            messagebox.showerror("Error", f"Error exportando: {e}")
    
    def batch_search_dialog(self):
        """Abrir diálogo para búsqueda en lote."""
        # TODO: Implementar diálogo de búsqueda en lote
        messagebox.showinfo("Información", "Funcionalidad de búsqueda en lote en desarrollo")
    
    def batch_search(self, codes: List[str]):
        """Realizar búsqueda en lote."""
        try:
            found_count = 0
            
            for code in codes:
                product = self.barcode_service.search_product_by_code(code.strip())
                
                if product:
                    self.add_result_to_tree(product, code.strip())
                    found_count += 1
            
            self.update_status(f"Búsqueda en lote completada: {found_count}/{len(codes)} encontrados")
            
        except Exception as e:
            logger.error(f"Error en búsqueda en lote: {e}")
            messagebox.showerror("Error", f"Error en búsqueda en lote: {e}")
    
    def configure_scanner(self):
        """Abrir configuración del scanner."""
        try:
            from ui.forms.barcode_config_form import BarcodeConfigForm
            config_form = BarcodeConfigForm(self)
            
        except Exception as e:
            logger.error(f"Error abriendo configuración: {e}")
            messagebox.showerror("Error", f"Error abriendo configuración: {e}")
    
    def edit_selected_product(self):
        """Editar producto seleccionado."""
        try:
            selected_items = self.results_tree.selection()
            
            if not selected_items:
                messagebox.showwarning("Advertencia", "Seleccione un producto para editar")
                return
            
            item = selected_items[0]
            values = self.results_tree.item(item, 'values')
            code = values[0]
            
            # Encontrar producto
            result = next((r for r in self.search_results if r['code'] == code), None)
            
            if result:
                # TODO: Abrir formulario de edición de producto
                messagebox.showinfo("Información", f"Abrir edición para producto: {result['product'].nombre}")
            
        except Exception as e:
            logger.error(f"Error editando producto: {e}")
            messagebox.showerror("Error", f"Error editando producto: {e}")
    
    def view_in_inventory(self):
        """Ver producto en inventario."""
        try:
            selected_items = self.results_tree.selection()
            
            if not selected_items:
                messagebox.showwarning("Advertencia", "Seleccione un producto para ver en inventario")
                return
            
            # TODO: Implementar navegación al inventario
            messagebox.showinfo("Información", "Funcionalidad en desarrollo")
            
        except Exception as e:
            logger.error(f"Error viendo en inventario: {e}")
    
    def get_search_history(self) -> List[str]:
        """Obtener historial de búsquedas."""
        return [entry['code'] for entry in self.search_history]
    
    def update_results_count(self):
        """Actualizar contador de resultados."""
        count = len(self.search_results)
        self.results_count_label.config(text=f"Resultados: {count}")
    
    def update_status(self, message: str):
        """Actualizar mensaje de estado."""
        self.status_label.config(text=message)
        self.update_idletasks()
    
    def on_closing(self):
        """Manejar cierre de ventana."""
        try:
            # Desactivar scanner
            if self.scanner_active:
                self.scanner_active = False
            
            # Guardar historial
            self.save_search_history()
            
            self.destroy()
            
        except Exception as e:
            logger.error(f"Error cerrando ventana: {e}")
            self.destroy()


if __name__ == "__main__":
    # Test independiente
    root = tk.Tk()
    root.withdraw()
    
    form = BarcodeSearchForm(root)
    root.mainloop()
