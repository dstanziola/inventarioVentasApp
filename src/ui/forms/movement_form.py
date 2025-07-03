"""
Formulario para gestión de movimientos de inventario con códigos de barras.
Permite crear, visualizar y gestionar entradas, ventas y ajustes de inventario.

ARQUITECTURA LIMPIA:
- Separación entre UI y lógica de negocio
- Validación en tiempo real
- Manejo robusto de errores
- Interfaz intuitiva y responsiva

TDD COMPATIBLE:
- Métodos testables separados
- Validaciones explícitas
- Manejo de estados bien definido

FASE 4 - CÓDIGOS DE BARRAS:
- Scanner automático para movimientos
- Búsqueda por código de barras
- Validación en tiempo real
- Integración con hardware USB/Serial
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
import threading
import logging

from services.movement_service import MovementService
from services.product_service import ProductService
from services.barcode_service import BarcodeService
from services.ticket_service import TicketService
from ui.auth.session_manager import session_manager
from ui.widgets.decimal_entry import DecimalEntry
from utils.barcode_utils import BarcodeUtils

# Configurar logging
logger = logging.getLogger(__name__)


class MovementForm:
    """
    Formulario para gestión de movimientos de inventario con códigos de barras.
    
    Funcionalidades:
    - Crear movimientos de entrada, venta y ajuste
    - Visualizar historial de movimientos
    - Validación en tiempo real
    - Búsqueda de productos
    - Cálculo automático de stock
    - Scanner automático de códigos de barras
    - Búsqueda por código
    - Integración con hardware USB/Serial
    """
    
    def __init__(self, parent, db_connection):
        """
        Inicializar formulario de movimientos.
        
        Args:
            parent: Ventana padre
            db_connection: Conexión a base de datos
        """
        self.parent = parent
        self.db = db_connection
        self.movement_service = MovementService(db_connection)
        self.product_service = ProductService(db_connection)
        self.barcode_service = BarcodeService(db_connection)
        
        # Variables del formulario
        self.producto_var = tk.StringVar()
        self.tipo_movimiento_var = tk.StringVar(value='ENTRADA')
        self.cantidad_var = tk.StringVar()
        self.observaciones_var = tk.StringVar()
        self.costo_unitario_var = tk.StringVar()
        
        # FASE 4: Variables de códigos de barras
        self.barcode_var = tk.StringVar()
        self.barcode_format_var = tk.StringVar()
        self.scanner_status_var = tk.StringVar(value="Scanner: Desconectado")
        self.scanner_active = False
        self.scanner_thread = None
        self.scan_history = []
        
        # Control de estado
        self.producto_seleccionado = None
        self.productos_disponibles = []
        self.last_scanned_code = None
        
        # Configurar eventos de barcode
        self.barcode_var.trace('w', self._on_barcode_changed)
        
        # Crear interfaz
        self.create_widgets()
        self.load_productos()
        self.update_form_state()
        
        # Inicializar scanner al abrir
        self._initialize_barcode_system()
    
    def create_widgets(self):
        """Crear widgets de la interfaz."""
        # Frame principal
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_label = ttk.Label(
            self.main_frame,
            text="Gestión de Movimientos de Inventario",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Crear notebook para organizar secciones
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña: Crear Movimiento
        self.crear_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.crear_frame, text="Crear Movimiento")
        self.create_movement_form()
        
        # Pestaña: Historial
        self.historial_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.historial_frame, text="Historial de Movimientos")
        self.create_history_section()
        
        # Pestaña: Productos con Stock Bajo
        self.stock_bajo_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stock_bajo_frame, text="Stock Bajo")
        self.create_low_stock_section()
    
    def create_movement_form(self):
        """Crear formulario para crear movimientos."""
        # Frame para el formulario
        form_frame = ttk.LabelFrame(self.crear_frame, text="Nuevo Movimiento", padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # FASE 4: Sección de códigos de barras (primera)
        self.setup_barcode_section(form_frame)
        
        # Separador
        ttk.Separator(form_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Fila 1: Producto
        producto_frame = ttk.Frame(form_frame)
        producto_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(producto_frame, text="Producto:", width=15).pack(side=tk.LEFT)
        
        self.producto_combo = ttk.Combobox(
            producto_frame,
            textvariable=self.producto_var,
            state='readonly',
            width=40
        )
        self.producto_combo.pack(side=tk.LEFT, padx=(5, 10))
        self.producto_combo.bind('<<ComboboxSelected>>', self.on_producto_selected)
        
        self.stock_actual_label = ttk.Label(producto_frame, text="Stock: 0", foreground="blue")
        self.stock_actual_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Fila 2: Tipo de Movimiento
        tipo_frame = ttk.Frame(form_frame)
        tipo_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(tipo_frame, text="Tipo:", width=15).pack(side=tk.LEFT)
        
        tipo_combo = ttk.Combobox(
            tipo_frame,
            textvariable=self.tipo_movimiento_var,
            values=['ENTRADA', 'VENTA', 'AJUSTE'],
            state='readonly',
            width=20
        )
        tipo_combo.pack(side=tk.LEFT, padx=(5, 0))
        tipo_combo.bind('<<ComboboxSelected>>', self.on_tipo_changed)
        
        # Fila 3: Cantidad
        cantidad_frame = ttk.Frame(form_frame)
        cantidad_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(cantidad_frame, text="Cantidad:", width=15).pack(side=tk.LEFT)
        
        self.cantidad_entry = ttk.Entry(
            cantidad_frame,
            textvariable=self.cantidad_var,
            width=20
        )
        self.cantidad_entry.pack(side=tk.LEFT, padx=(5, 10))
        self.cantidad_entry.bind('<KeyRelease>', self.validate_form_data)
        
        self.cantidad_info_label = ttk.Label(
            cantidad_frame,
            text="",
            foreground="gray"
        )
        self.cantidad_info_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Fila 4: Costo Unitario (opcional para entradas)
        costo_frame = ttk.Frame(form_frame)
        costo_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(costo_frame, text="Costo Unitario:", width=15).pack(side=tk.LEFT)
        
        self.costo_entry = DecimalEntry(
            costo_frame,
            textvariable=self.costo_unitario_var,
            width=20
        )
        self.costo_entry.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Label(costo_frame, text="(Opcional para entradas)", foreground="gray").pack(side=tk.LEFT)
        
        # Fila 5: Observaciones
        obs_frame = ttk.Frame(form_frame)
        obs_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(obs_frame, text="Observaciones:", width=15).pack(side=tk.LEFT)
        
        self.observaciones_entry = ttk.Entry(
            obs_frame,
            textvariable=self.observaciones_var,
            width=50
        )
        self.observaciones_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        
        # Frame para información y validación
        info_frame = ttk.Frame(form_frame)
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.validation_label = ttk.Label(
            info_frame,
            text="",
            foreground="red",
            font=("Arial", 9)
        )
        self.validation_label.pack(side=tk.LEFT)
        
        # Frame para botones
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Botón Crear Movimiento
        self.crear_button = ttk.Button(
            button_frame,
            text="Crear Movimiento",
            command=self.create_movement,
            style="Accent.TButton"
        )
        self.crear_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Botón Limpiar
        ttk.Button(
            button_frame,
            text="Limpiar",
            command=self.clear_form
        ).pack(side=tk.RIGHT)
        
        # Botón Validar
        ttk.Button(
            button_frame,
            text="Validar",
            command=self.validate_movement
        ).pack(side=tk.RIGHT, padx=(0, 10))
    
    def setup_barcode_section(self, parent_frame):
        """FASE 4: Configurar sección de códigos de barras."""
        # Frame principal para códigos de barras
        self.barcode_frame = ttk.LabelFrame(
            parent_frame,
            text="Código de Barras",
            padding=15
        )
        self.barcode_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Primera fila: Scanner y estado
        scanner_frame = ttk.Frame(self.barcode_frame)
        scanner_frame.pack(fill=tk.X, pady=(0, 8))
        
        # Estado del scanner
        self.scanner_status_label = ttk.Label(
            scanner_frame,
            textvariable=self.scanner_status_var,
            font=("Arial", 9),
            foreground="gray"
        )
        self.scanner_status_label.pack(side=tk.LEFT)
        
        # Botón toggle scanner
        self.scanner_button = ttk.Button(
            scanner_frame,
            text="Activar Scanner",
            command=self.toggle_scanner,
            width=15
        )
        self.scanner_button.pack(side=tk.RIGHT)
        
        # Segunda fila: Entry de código y formato
        code_frame = ttk.Frame(self.barcode_frame)
        code_frame.pack(fill=tk.X, pady=(0, 8))
        
        ttk.Label(code_frame, text="Código:", width=10).pack(side=tk.LEFT)
        
        self.barcode_entry = ttk.Entry(
            code_frame,
            textvariable=self.barcode_var,
            font=('Consolas', 12),
            width=25
        )
        self.barcode_entry.pack(side=tk.LEFT, padx=(5, 15))
        
        # Formato detectado
        ttk.Label(code_frame, text="Formato:", width=8).pack(side=tk.LEFT)
        self.barcode_format_label = ttk.Label(
            code_frame,
            textvariable=self.barcode_format_var,
            font=('Arial', 9),
            foreground="blue"
        )
        self.barcode_format_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Tercera fila: Botones de acción
        action_frame = ttk.Frame(self.barcode_frame)
        action_frame.pack(fill=tk.X)
        
        ttk.Button(
            action_frame,
            text="Buscar Producto",
            command=self.search_product_by_barcode,
            width=15
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            action_frame,
            text="Limpiar Código",
            command=self.clear_barcode,
            width=15
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Estado de última búsqueda
        self.barcode_result_label = ttk.Label(
            action_frame,
            text="",
            font=('Arial', 9)
        )
        self.barcode_result_label.pack(side=tk.LEFT, padx=(15, 0))
    
    def _initialize_barcode_system(self):
        """FASE 4: Inicializar sistema de códigos de barras."""
        try:
            # Verificar disponibilidad de scanner
            if self.barcode_service.is_scanner_available():
                self.scanner_status_var.set("Scanner: Disponible")
                self.scanner_status_label.config(foreground="green")
                self.scanner_button.config(state='normal')
            else:
                self.scanner_status_var.set("Scanner: No detectado")
                self.scanner_status_label.config(foreground="orange")
                self.scanner_button.config(state='normal')  # Permitir intentar activar
                
        except Exception as e:
            logger.error(f"Error inicializando barcode system: {e}")
            self.scanner_status_var.set("Scanner: Error de conexión")
            self.scanner_status_label.config(foreground="red")
            self.scanner_button.config(state='disabled')
    
    def toggle_scanner(self):
        """FASE 4: Activar/desactivar scanner automático."""
        try:
            if not self.scanner_active:
                # Activar scanner
                success = self.barcode_service.start_scanning()
                if success:
                    self.scanner_active = True
                    self.scanner_button.config(text="Desactivar Scanner")
                    self.scanner_status_var.set("Scanner: Activo")
                    self.scanner_status_label.config(foreground="green")
                    
                    # Iniciar thread de monitoreo
                    self._start_scanner_check()
                    
                    # Mostrar instrucciones
                    messagebox.showinfo(
                        "Scanner Activado",
                        "El scanner está activo.\\n"
                        "Escanee un código de barras para buscar productos automáticamente."
                    )
                else:
                    messagebox.showerror(
                        "Error",
                        "No se pudo activar el scanner.\\n"
                        "Verifique que el dispositivo esté conectado."
                    )
            else:
                # Desactivar scanner
                self.barcode_service.stop_scanning()
                self.scanner_active = False
                self.scanner_button.config(text="Activar Scanner")
                self.scanner_status_var.set("Scanner: Inactivo")
                self.scanner_status_label.config(foreground="gray")
                
                if self.scanner_thread and self.scanner_thread.is_alive():
                    self.scanner_thread = None
                    
        except Exception as e:
            logger.error(f"Error toggle scanner: {e}")
            messagebox.showerror("Error", f"Error controlando scanner: {e}")
    
    def _start_scanner_check(self):
        """FASE 4: Iniciar thread de verificación de scanner."""
        if self.scanner_active:
            self.scanner_thread = threading.Thread(
                target=self._scanner_check_loop,
                daemon=True
            )
            self.scanner_thread.start()
    
    def _scanner_check_loop(self):
        """FASE 4: Loop de verificación de scanner en thread separado."""
        while self.scanner_active:
            try:
                # Verificar códigos escaneados
                scanned_code = self.barcode_service.get_scanned_code()
                if scanned_code and scanned_code != self.last_scanned_code:
                    self.last_scanned_code = scanned_code
                    
                    # Programar procesamiento en thread principal
                    self.parent.after(0, lambda: self.on_barcode_scan(scanned_code))
                
                # Verificar cada 100ms
                threading.Event().wait(0.1)
                
            except Exception as e:
                logger.error(f"Error en scanner check loop: {e}")
                # Programar desactivación en thread principal
                self.parent.after(0, self._handle_scanner_error)
                break
    
    def _handle_scanner_error(self):
        """FASE 4: Manejar errores del scanner."""
        self.scanner_active = False
        self.scanner_button.config(text="Activar Scanner")
        self.scanner_status_var.set("Scanner: Error")
        self.scanner_status_label.config(foreground="red")
    
    def on_barcode_scan(self, scanned_code: str):
        """FASE 4: Procesar código escaneado."""
        try:
            # Actualizar UI
            self.barcode_var.set(scanned_code)
            
            # Agregar al historial
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.scan_history.append({
                'code': scanned_code,
                'timestamp': timestamp,
                'found': False
            })
            
            # Buscar producto automáticamente
            self.auto_fill_product_by_code(scanned_code)
            
        except Exception as e:
            logger.error(f"Error procesando código escaneado: {e}")
    
    def _on_barcode_changed(self, *args):
        """FASE 4: Callback cuando cambia el código en el entry."""
        try:
            code = self.barcode_var.get().strip()
            if code:
                # Detectar formato
                format_info = BarcodeUtils.detect_barcode_format(code)
                self.barcode_format_var.set(format_info.get('format', 'Desconocido'))
                
                # Validar formato
                if BarcodeUtils.validate_barcode(code):
                    self.barcode_entry.config(foreground="black")
                else:
                    self.barcode_entry.config(foreground="red")
            else:
                self.barcode_format_var.set("")
                self.barcode_entry.config(foreground="black")
                
        except Exception as e:
            logger.error(f"Error en barcode changed: {e}")
    
    def search_product_by_barcode(self):
        """FASE 4: Buscar producto por código de barras."""
        try:
            code = self.barcode_var.get().strip()
            if not code:
                messagebox.showwarning("Advertencia", "Ingrese un código de barras")
                return
            
            # Buscar producto
            found = self.auto_fill_product_by_code(code, show_message=True)
            
            if found:
                self.barcode_result_label.config(
                    text="Producto encontrado",
                    foreground="green"
                )
            else:
                self.barcode_result_label.config(
                    text="Producto no encontrado",
                    foreground="red"
                )
                
        except Exception as e:
            logger.error(f"Error buscando por código: {e}")
            messagebox.showerror("Error", f"Error en búsqueda: {e}")
    
    def auto_fill_product_by_code(self, barcode: str, show_message: bool = False) -> bool:
        """FASE 4: Auto-completar producto por código de barras."""
        try:
            # Buscar producto por código
            producto = self.product_service.get_product_by_barcode(barcode)
            
            if producto:
                # Producto encontrado - seleccionarlo
                self.producto_seleccionado = producto
                product_text = f"{producto['id_producto']} - {producto['nombre']}"
                self.producto_var.set(product_text)
                
                # Actualizar stock
                stock_actual = producto.get('stock_actual', producto.get('stock', 0))
                self.stock_actual_label.config(text=f"Stock: {stock_actual}")
                
                # Validar formulario
                self.validate_form_data()
                
                # Actualizar historial
                if self.scan_history:
                    self.scan_history[-1]['found'] = True
                
                if show_message:
                    messagebox.showinfo(
                        "Producto Encontrado",
                        f"Producto: {producto['nombre']}\\n"
                        f"Stock actual: {stock_actual}"
                    )
                
                return True
            else:
                # Producto no encontrado
                if show_message:
                    # Ofrecer búsqueda alternativa
                    if messagebox.askyesno(
                        "Producto No Encontrado",
                        f"No se encontró ningún producto con el código: {barcode}\\n\\n"
                        "¿Desea buscar por coincidencias parciales?"
                    ):
                        self._search_partial_barcode_matches(barcode)
                
                return False
                
        except Exception as e:
            logger.error(f"Error auto-llenando producto: {e}")
            if show_message:
                messagebox.showerror("Error", f"Error buscando producto: {e}")
            return False
    
    def _search_partial_barcode_matches(self, barcode: str):
        """FASE 4: Buscar coincidencias parciales de código."""
        try:
            # Buscar productos con códigos similares
            productos = self.product_service.search_products_by_partial_code(barcode)
            
            if productos:
                # Mostrar diálogo de selección
                self._show_product_selection_dialog(productos, barcode)
            else:
                messagebox.showinfo(
                    "Sin Coincidencias",
                    "No se encontraron productos con códigos similares."
                )
                
        except Exception as e:
            logger.error(f"Error búsqueda parcial: {e}")
            messagebox.showerror("Error", f"Error en búsqueda parcial: {e}")
    
    def _show_product_selection_dialog(self, productos: List[Dict], original_code: str):
        """FASE 4: Mostrar diálogo de selección de productos."""
        try:
            # Crear ventana de selección
            dialog = tk.Toplevel(self.parent)
            dialog.title("Seleccionar Producto")
            dialog.geometry("500x300")
            dialog.transient(self.parent)
            dialog.grab_set()
            
            # Centrar en la ventana padre
            dialog.geometry("+%d+%d" % (
                self.parent.winfo_rootx() + 50,
                self.parent.winfo_rooty() + 50
            ))
            
            # Etiqueta de información
            info_label = ttk.Label(
                dialog,
                text=f"Productos encontrados para código: {original_code}",
                font=("Arial", 10, "bold")
            )
            info_label.pack(pady=10)
            
            # Treeview con productos
            tree_frame = ttk.Frame(dialog)
            tree_frame.pack(fill=tk.BOTH, expand=True, padx=10)
            
            columns = ('ID', 'Nombre', 'Stock')
            tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=8)
            
            tree.heading('ID', text='ID')
            tree.heading('Nombre', text='Nombre')
            tree.heading('Stock', text='Stock')
            
            tree.column('ID', width=80)
            tree.column('Nombre', width=250)
            tree.column('Stock', width=80)
            
            # Cargar productos
            for producto in productos:
                stock = producto.get('stock_actual', producto.get('stock', 0))
                tree.insert('', 'end', values=(
                    producto['id_producto'],
                    producto['nombre'],
                    stock
                ))
            
            tree.pack(fill=tk.BOTH, expand=True)
            
            # Frame de botones
            button_frame = ttk.Frame(dialog)
            button_frame.pack(fill=tk.X, padx=10, pady=10)
            
            # Variable para resultado
            selected_product = [None]
            
            def on_select():
                selection = tree.selection()
                if selection:
                    item = tree.item(selection[0])
                    id_producto = int(item['values'][0])
                    
                    # Buscar producto completo
                    for p in productos:
                        if p['id_producto'] == id_producto:
                            selected_product[0] = p
                            break
                    
                    dialog.destroy()
                else:
                    messagebox.showwarning("Selección", "Seleccione un producto")
            
            def on_cancel():
                dialog.destroy()
            
            ttk.Button(button_frame, text="Seleccionar", command=on_select).pack(side=tk.RIGHT, padx=(5, 0))
            ttk.Button(button_frame, text="Cancelar", command=on_cancel).pack(side=tk.RIGHT)
            
            # Esperar cierre del diálogo
            dialog.wait_window()
            
            # Procesar selección
            if selected_product[0]:
                producto = selected_product[0]
                self.producto_seleccionado = producto
                product_text = f"{producto['id_producto']} - {producto['nombre']}"
                self.producto_var.set(product_text)
                
                stock_actual = producto.get('stock_actual', producto.get('stock', 0))
                self.stock_actual_label.config(text=f"Stock: {stock_actual}")
                self.validate_form_data()
                
        except Exception as e:
            logger.error(f"Error en diálogo selección: {e}")
            messagebox.showerror("Error", f"Error mostrando selección: {e}")
    
    def validate_scanned_product(self, producto: Dict[str, Any]) -> bool:
        """FASE 4: Validar producto escaneado."""
        try:
            # Verificar que esté activo
            if not producto.get('activo', True):
                messagebox.showwarning(
                    "Producto Inactivo",
                    f"El producto '{producto['nombre']}' está marcado como inactivo."
                )
                return False
            
            # Verificar stock para movimientos de venta
            if self.tipo_movimiento_var.get() == 'VENTA':
                stock_actual = producto.get('stock_actual', producto.get('stock', 0))
                if stock_actual <= 0:
                    messagebox.showwarning(
                        "Sin Stock",
                        f"El producto '{producto['nombre']}' no tiene stock disponible."
                    )
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validando producto escaneado: {e}")
            return False
    
    def clear_barcode(self):
        """FASE 4: Limpiar código de barras."""
        self.barcode_var.set("")
        self.barcode_format_var.set("")
        self.barcode_result_label.config(text="")
        self.last_scanned_code = None
    
    def create_history_section(self):
        """Crear sección de historial de movimientos."""
        # Frame para filtros
        filter_frame = ttk.LabelFrame(self.historial_frame, text="Filtros", padding=10)
        filter_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        # Filtro por producto
        ttk.Label(filter_frame, text="Producto:").pack(side=tk.LEFT)
        self.filter_producto_combo = ttk.Combobox(filter_frame, state='readonly', width=30)
        self.filter_producto_combo.pack(side=tk.LEFT, padx=(5, 20))
        
        # Filtro por tipo
        ttk.Label(filter_frame, text="Tipo:").pack(side=tk.LEFT)
        self.filter_tipo_combo = ttk.Combobox(
            filter_frame,
            values=['Todos', 'ENTRADA', 'VENTA', 'AJUSTE'],
            state='readonly',
            width=15
        )
        self.filter_tipo_combo.set('Todos')
        self.filter_tipo_combo.pack(side=tk.LEFT, padx=(5, 20))
        
        # Botón filtrar
        ttk.Button(
            filter_frame,
            text="Filtrar",
            command=self.filter_movements
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Botón actualizar
        ttk.Button(
            filter_frame,
            text="Actualizar",
            command=self.load_movements_history
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # Treeview para mostrar movimientos
        tree_frame = ttk.Frame(self.historial_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
        
        # Crear Treeview
        columns = ('ID', 'Fecha', 'Producto', 'Tipo', 'Cantidad', 'Stock Ant.', 'Stock Nuevo', 'Responsable')
        self.movements_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            height=15
        )
        
        # Configurar columnas
        column_widths = {'ID': 60, 'Fecha': 130, 'Producto': 200, 'Tipo': 80, 
                        'Cantidad': 80, 'Stock Ant.': 80, 'Stock Nuevo': 80, 'Responsable': 120}
        
        for col in columns:
            self.movements_tree.heading(col, text=col)
            self.movements_tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.movements_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.movements_tree.xview)
        
        self.movements_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Empaquetar
        self.movements_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Cargar datos iniciales
        self.load_movements_history()
    
    def create_low_stock_section(self):
        """Crear sección de productos con stock bajo."""
        info_label = ttk.Label(
            self.stock_bajo_frame,
            text="Productos con stock por debajo del mínimo",
            font=("Arial", 12, "bold")
        )
        info_label.pack(pady=(10, 5))
        
        # Treeview para productos con stock bajo
        tree_frame = ttk.Frame(self.stock_bajo_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ('Producto', 'Stock Actual', 'Stock Mínimo', 'Faltante')
        self.low_stock_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            height=10
        )
        
        # Configurar columnas
        for col in columns:
            self.low_stock_tree.heading(col, text=col)
            self.low_stock_tree.column(col, width=150)
        
        # Scrollbar
        scrollbar_low = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.low_stock_tree.yview)
        self.low_stock_tree.configure(yscrollcommand=scrollbar_low.set)
        
        self.low_stock_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_low.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botón actualizar
        ttk.Button(
            self.stock_bajo_frame,
            text="Actualizar Lista",
            command=self.load_low_stock_products
        ).pack(pady=5)
        
        # Cargar datos iniciales
        self.load_low_stock_products()
    
    def load_productos(self):
        """Cargar lista de productos disponibles."""
        try:
            productos = self.product_service.get_all_products(only_active=True)
            self.productos_disponibles = productos
            
            # Crear lista para combobox
            producto_items = []
            for producto in productos:
                # CORRECCIÓN: Usar atributos de objeto en lugar de subscript
                item = f"{producto.id_producto} - {producto.nombre}"
                producto_items.append(item)
            
            # Actualizar comboboxes
            self.producto_combo['values'] = producto_items
            
            # También actualizar el filtro de historial
            filter_items = ['Todos'] + producto_items
            self.filter_producto_combo['values'] = filter_items
            self.filter_producto_combo.set('Todos')
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando productos: {e}")
    
    def on_producto_selected(self, event=None):
        """Manejar selección de producto."""
        try:
            selected = self.producto_var.get()
            if not selected:
                self.producto_seleccionado = None
                return
            
            # Extraer ID del producto
            id_producto = int(selected.split(' - ')[0])
            
            # Buscar producto en la lista
            self.producto_seleccionado = None
            for producto in self.productos_disponibles:
                # CORRECCIÓN: Usar atributo de objeto
                if producto.id_producto == id_producto:
                    self.producto_seleccionado = producto
                    break
            
            if self.producto_seleccionado:
                # CORRECCIÓN: Usar atributos de objeto para acceso a stock
                stock_actual = getattr(self.producto_seleccionado, 'stock', 0)
                self.stock_actual_label.config(text=f"Stock: {stock_actual}")
                
                # FASE 4: Actualizar código de barras si tiene
                if hasattr(self.producto_seleccionado, 'barcode') and self.producto_seleccionado.barcode:
                    self.barcode_var.set(self.producto_seleccionado.barcode)
                
                # Validar formulario
                self.validate_form_data()
        
        except Exception as e:
            logger.error(f"Error en selección de producto: {e}")
    
    def on_tipo_changed(self, event=None):
        """Manejar cambio de tipo de movimiento."""
        tipo = self.tipo_movimiento_var.get()
        
        # Actualizar información según tipo
        if tipo == 'ENTRADA':
            self.cantidad_info_label.config(text="(Cantidad a ingresar)")
            self.costo_entry.config(state='normal')
        elif tipo == 'VENTA':
            self.cantidad_info_label.config(text="(Cantidad a vender)")
            self.costo_entry.config(state='disabled')
            self.costo_unitario_var.set('')
        else:  # AJUSTE
            self.cantidad_info_label.config(text="(+/- para ajustar)")
            self.costo_entry.config(state='disabled')
            self.costo_unitario_var.set('')
        
        self.validate_form_data()
    
    def validate_form_data(self, event=None):
        """Validar datos del formulario en tiempo real."""
        try:
            # Limpiar mensaje anterior
            self.validation_label.config(text="", foreground="red")
            
            if not self.producto_seleccionado:
                self.validation_label.config(text="Seleccione un producto")
                self.crear_button.config(state='disabled')
                return
            
            # Validar cantidad
            cantidad_str = self.cantidad_var.get().strip()
            if not cantidad_str:
                self.validation_label.config(text="Ingrese una cantidad")
                self.crear_button.config(state='disabled')
                return
            
            try:
                cantidad = int(cantidad_str)
                if cantidad == 0:
                    self.validation_label.config(text="La cantidad no puede ser cero")
                    self.crear_button.config(state='disabled')
                    return
            except ValueError:
                self.validation_label.config(text="La cantidad debe ser un número entero")
                self.crear_button.config(state='disabled')
                return
            
            # Validaciones específicas por tipo
            tipo = self.tipo_movimiento_var.get()
            if tipo in ['ENTRADA', 'VENTA'] and cantidad < 0:
                self.validation_label.config(text=f"Las {tipo.lower()}s deben tener cantidad positiva")
                self.crear_button.config(state='disabled')
                return
            
            # Validar stock suficiente para ventas
            if tipo == 'VENTA':
                # CORRECCIÓN: Usar atributos de objeto
                stock_actual = getattr(self.producto_seleccionado, 'stock', 0)
                if cantidad > stock_actual:
                    self.validation_label.config(
                        text=f"Stock insuficiente. Disponible: {stock_actual}, Solicitado: {cantidad}"
                    )
                    self.crear_button.config(state='disabled')
                    return
            
            # Si llegamos aquí, los datos son válidos
            self.validation_label.config(text="✓ Datos válidos", foreground="green")
            self.crear_button.config(state='normal')
            
        except Exception as e:
            self.validation_label.config(text=f"Error en validación: {e}")
            self.crear_button.config(state='disabled')
    
    def validate_movement(self):
        """Validar movimiento usando el servicio."""
        try:
            if not self.producto_seleccionado:
                messagebox.showwarning("Validación", "Seleccione un producto")
                return
            
            # Recopilar datos
            movement_data = self.get_form_data()
            if not movement_data:
                return
            
            # Validar con el servicio
            is_valid, errors = self.movement_service.validate_movement_data(**movement_data)
            
            if is_valid:
                messagebox.showinfo("Validación", "✓ Los datos del movimiento son válidos")
            else:
                error_message = "Errores encontrados:\\n" + "\\n".join(errors)
                messagebox.showerror("Validación", error_message)
        
        except Exception as e:
            messagebox.showerror("Error", f"Error durante validación: {e}")
    
    def create_movement(self):
        """Crear un nuevo movimiento."""
        try:
            # Validar formulario
            self.validate_form_data()
            if self.crear_button['state'] == 'disabled':
                messagebox.showwarning("Validación", "Complete correctamente todos los campos")
                return
            
            # Recopilar datos
            movement_data = self.get_form_data()
            if not movement_data:
                return
            
            # Confirmar acción
            tipo = movement_data['tipo_movimiento']
            # CORRECCIÓN: Usar atributo de objeto
            producto_nombre = self.producto_seleccionado.nombre
            cantidad = movement_data['cantidad']
            
            mensaje = f"¿Confirma crear {tipo.lower()} de {abs(cantidad)} unidades del producto '{producto_nombre}'?"
            
            if not messagebox.askyesno("Confirmar Movimiento", mensaje):
                return
            
            # Crear movimiento
            movimiento = self.movement_service.create_movement(**movement_data)
            
            # Mostrar éxito
            messagebox.showinfo(
                "Éxito",
                f"Movimiento creado exitosamente\\n"
                f"ID: {movimiento.id_movimiento}\\n"
                f"Tipo: {movimiento.tipo_movimiento}\\n"
                f"Producto: {producto_nombre}"
            )
            
            # FASE 4: Preguntar si desea generar ticket para movimientos de ENTRADA
            if movimiento.tipo_movimiento == 'ENTRADA':
                self._offer_ticket_generation(movimiento.id_movimiento, producto_nombre, cantidad)
            
            # Limpiar formulario
            self.clear_form()
            
            # Actualizar stock mostrado
            self.load_productos()
            
            # Actualizar historial si está visible
            self.load_movements_history()
            
            # Actualizar productos con stock bajo
            self.load_low_stock_products()
        
        except Exception as e:
            messagebox.showerror("Error", f"Error creando movimiento: {e}")
    
    def get_form_data(self) -> Optional[Dict[str, Any]]:
        """Recopilar datos del formulario."""
        try:
            if not self.producto_seleccionado:
                return None
            
            # Obtener cantidad
            cantidad_str = self.cantidad_var.get().strip()
            if not cantidad_str:
                return None
            
            cantidad = int(cantidad_str)
            
            # Obtener costo unitario si está disponible
            costo_str = self.costo_unitario_var.get().strip()
            costo_unitario = None
            if costo_str:
                try:
                    costo_unitario = Decimal(costo_str)
                except ValueError:
                    messagebox.showerror("Error", "El costo unitario debe ser un número válido")
                    return None
            
            # Obtener usuario actual
            current_user = session_manager.get_current_user()
            responsable = current_user.get('nombre_usuario', 'usuario') if current_user else 'usuario'
            
            return {
                # CORRECCIÓN: Usar atributo de objeto
                'id_producto': self.producto_seleccionado.id_producto,
                'tipo_movimiento': self.tipo_movimiento_var.get(),
                'cantidad': cantidad,
                'responsable': responsable,
                'observaciones': self.observaciones_var.get().strip() or None,
                'costo_unitario': costo_unitario
            }
        
        except Exception as e:
            messagebox.showerror("Error", f"Error recopilando datos: {e}")
            return None
    
    def clear_form(self):
        """Limpiar formulario."""
        self.producto_var.set('')
        self.tipo_movimiento_var.set('ENTRADA')
        self.cantidad_var.set('')
        self.observaciones_var.set('')
        self.costo_unitario_var.set('')
        
        # FASE 4: Limpiar también códigos de barras
        self.clear_barcode()
        
        self.producto_seleccionado = None
        self.stock_actual_label.config(text="Stock: 0")
        self.validation_label.config(text="")
        self.cantidad_info_label.config(text="(Cantidad a ingresar)")
        
        self.crear_button.config(state='disabled')
        self.costo_entry.config(state='normal')
    
    def load_movements_history(self):
        """Cargar historial de movimientos."""
        try:
            # Limpiar tree
            for item in self.movements_tree.get_children():
                self.movements_tree.delete(item)
            
            # Obtener movimientos
            movimientos = self.movement_service.get_all_movements(limit=200)
            
            for mov in movimientos:
                # Formatear fecha
                fecha_str = mov['fecha_movimiento']
                if isinstance(fecha_str, str):
                    try:
                        fecha_dt = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
                        fecha_formatted = fecha_dt.strftime('%d/%m/%Y %H:%M')
                    except:
                        fecha_formatted = fecha_str
                else:
                    fecha_formatted = str(fecha_str)
                
                # Formatear cantidad según tipo
                cantidad = mov['cantidad']
                if mov['tipo_movimiento'] == 'ENTRADA':
                    cantidad_str = f"+{cantidad}"
                elif mov['tipo_movimiento'] == 'VENTA':
                    cantidad_str = f"{cantidad}"  # Ya viene negativo
                else:  # AJUSTE
                    cantidad_str = f"{cantidad:+d}"
                
                # Insertar en tree
                self.movements_tree.insert('', 'end', values=(
                    mov['id_movimiento'],
                    fecha_formatted,
                    mov['producto_nombre'],
                    mov['tipo_movimiento'],
                    cantidad_str,
                    mov.get('cantidad_anterior', ''),
                    mov.get('cantidad_nueva', ''),
                    mov['responsable']
                ))
        
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando historial: {e}")
    
    def filter_movements(self):
        """Aplicar filtros al historial."""
        try:
            # Obtener filtros
            producto_filter = self.filter_producto_combo.get()
            tipo_filter = self.filter_tipo_combo.get()
            
            # Determinar parámetros de filtro
            id_producto = None
            if producto_filter and producto_filter != 'Todos':
                id_producto = int(producto_filter.split(' - ')[0])
            
            tipo_movimiento = None
            if tipo_filter and tipo_filter != 'Todos':
                tipo_movimiento = tipo_filter
            
            # Limpiar tree
            for item in self.movements_tree.get_children():
                self.movements_tree.delete(item)
            
            # Obtener movimientos filtrados
            if id_producto:
                movimientos = self.movement_service.get_movements_by_product(id_producto)
            else:
                movimientos = self.movement_service.get_all_movements(
                    limit=200,
                    tipo_movimiento=tipo_movimiento
                )
            
            # Aplicar filtro de tipo si es necesario y no se aplicó en la query
            if tipo_movimiento and not id_producto:
                movimientos = [mov for mov in movimientos if mov['tipo_movimiento'] == tipo_movimiento]
            elif tipo_movimiento and id_producto:
                movimientos = [mov for mov in movimientos if mov['tipo_movimiento'] == tipo_movimiento]
            
            # Mostrar resultados
            for mov in movimientos:
                fecha_str = mov['fecha_movimiento']
                if isinstance(fecha_str, str):
                    try:
                        fecha_dt = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
                        fecha_formatted = fecha_dt.strftime('%d/%m/%Y %H:%M')
                    except:
                        fecha_formatted = fecha_str
                else:
                    fecha_formatted = str(fecha_str)
                
                cantidad = mov['cantidad']
                if mov['tipo_movimiento'] == 'ENTRADA':
                    cantidad_str = f"+{cantidad}"
                elif mov['tipo_movimiento'] == 'VENTA':
                    cantidad_str = f"{cantidad}"
                else:
                    cantidad_str = f"{cantidad:+d}"
                
                self.movements_tree.insert('', 'end', values=(
                    mov['id_movimiento'],
                    fecha_formatted,
                    mov['producto_nombre'],
                    mov['tipo_movimiento'],
                    cantidad_str,
                    mov.get('cantidad_anterior', ''),
                    mov.get('cantidad_nueva', ''),
                    mov['responsable']
                ))
        
        except Exception as e:
            messagebox.showerror("Error", f"Error aplicando filtros: {e}")
    
    def load_low_stock_products(self):
        """Cargar productos con stock bajo."""
        try:
            # Limpiar tree
            for item in self.low_stock_tree.get_children():
                self.low_stock_tree.delete(item)
            
            # Obtener productos con stock bajo
            productos_bajo_stock = self.movement_service.get_productos_bajo_stock()
            
            for producto in productos_bajo_stock:
                self.low_stock_tree.insert('', 'end', values=(
                    producto['nombre'],
                    producto['stock'],
                    producto['stock_minimo'],
                    producto['faltante']
                ))
            
            # Mostrar cantidad
            if productos_bajo_stock:
                messagebox.showinfo(
                    "Stock Bajo",
                    f"Se encontraron {len(productos_bajo_stock)} productos con stock bajo"
                )
        
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando productos con stock bajo: {e}")
    
    def update_form_state(self):
        """Actualizar estado del formulario."""
        self.on_tipo_changed()
        self.validate_form_data()
    
    def _offer_ticket_generation(self, id_movimiento: int, producto_nombre: str, cantidad: int):
        """Ofrecer generar ticket para movimiento de entrada - FASE 4"""
        try:
            # Preguntar si desea generar ticket
            if messagebox.askyesno(
                "Generar Ticket",
                f"¿Desea generar un ticket para el movimiento de entrada?\n"
                f"Producto: {producto_nombre}\n"
                f"Cantidad: {cantidad} unidades"
            ):
                ticket_service = TicketService(self.db)
                
                # Obtener usuario actual
                current_user = session_manager.get_current_user()
                responsable = current_user.get('nombre_usuario', 'usuario') if current_user else 'usuario'
                
                # Generar ticket
                ticket = ticket_service.generar_ticket_entrada(
                    id_movimiento=id_movimiento,
                    responsable=responsable
                )
                
                messagebox.showinfo(
                    "Ticket Generado",
                    f"Ticket de entrada generado exitosamente\n"
                    f"Número: {ticket.ticket_number}\n"
                    f"Archivo: {ticket.pdf_path}"
                )
                
                # Preguntar si desea abrir el archivo PDF
                if messagebox.askyesno("Abrir PDF", "¿Desea abrir el archivo PDF generado?"):
                    import os
                    import subprocess
                    if os.path.exists(ticket.pdf_path):
                        try:
                            os.startfile(ticket.pdf_path)  # Windows
                        except AttributeError:
                            subprocess.run(['xdg-open', ticket.pdf_path])  # Linux
                        except Exception:
                            messagebox.showinfo("Archivo Listo", f"El archivo se guardó en: {ticket.pdf_path}")
                            
        except Exception as e:
            logger.error(f"Error generando ticket: {e}")
            messagebox.showerror("Error", f"Error al generar ticket: {e}")
            # No interrumpir el flujo normal si hay error con el ticket
    
    def __del__(self):
        """FASE 4: Destructor - limpiar recursos."""
        try:
            if hasattr(self, 'scanner_active') and self.scanner_active:
                self.barcode_service.stop_scanning()
        except:
            pass


def create_movement_window(parent, db_connection):
    """
    Crear ventana de gestión de movimientos.
    
    Args:
        parent: Ventana padre
        db_connection: Conexión a base de datos
    """
    try:
        # Crear ventana
        window = tk.Toplevel(parent)
        window.title("Gestión de Movimientos de Inventario - Con Códigos de Barras")
        window.geometry("1100x800")
        window.minsize(900, 700)
        
        # Centrar ventana
        window.transient(parent)
        window.grab_set()
        
        # Crear formulario
        movement_form = MovementForm(window, db_connection)
        
        # Configurar cierre de ventana
        def on_closing():
            try:
                # Detener scanner si está activo
                if hasattr(movement_form, 'scanner_active') and movement_form.scanner_active:
                    movement_form.barcode_service.stop_scanning()
            except:
                pass
            window.destroy()
        
        window.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Foco inicial
        window.focus()
        
        return window
        
    except Exception as e:
        messagebox.showerror("Error", f"Error creando ventana de movimientos: {e}")
        return None
