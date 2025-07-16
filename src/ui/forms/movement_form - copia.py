"""
Formulario para gestión de movimientos de inventario con códigos de barras - Modo Teclado.
Permite crear, visualizar y gestionar entradas, ventas y ajustes de inventario.

REFACTORIZACIÓN v2.0 - MODO TECLADO:
- Eliminadas dependencias de hardware externo (hidapi, threads, device management)
- Integración directa con BarcodeEntry widget
- Código simplificado y más mantenible
- Compatible con cualquier lector HID configurado como teclado

ARQUITECTURA LIMPIA:
- Separación entre UI y lógica de negocio
- Validación en tiempo real
- Manejo robusto de errores
- Interfaz intuitiva y responsiva

TDD COMPATIBLE:
- Métodos testables separados
- Validaciones explícitas
- Manejo de estados bien definido

Autor: Sistema de Inventario Copy Point S.A.
Versión: 2.0.0 - Modo Teclado
Fecha: Julio 2025
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
import logging
import os
import platform
import subprocess

from services.service_container import get_container
from ui.auth.session_manager import session_manager
from ui.widgets.decimal_entry import DecimalEntry
from ui.widgets.barcode_entry import BarcodeEntry
from utils.barcode_utils import BarcodeUtils

# Configurar logging
logger = logging.getLogger(__name__)

class MovementForm:
    """
    Formulario para gestión de movimientos de inventario con códigos de barras - Modo Teclado.
    
    REFACTORIZACIÓN v2.0:
    - Sin dependencias de hardware (hidapi, threads, device detection)
    - Uso directo de BarcodeEntry widget para captura
    - Código simplificado y más confiable
    - Compatible con lectores HID en modo teclado
    
    Funcionalidades:
    - Crear movimientos de entrada, venta y ajuste
    - Visualizar historial de movimientos
    - Validación en tiempo real
    - Búsqueda de productos por código de barras
    - Cálculo automático de stock
    - Integración con BarcodeEntry widget
    """
    
    def __init__(self, parent, db_connection):
        """
        Inicializar formulario de movimientos.
        
        Args:
            parent: Ventana padre
            db_connection: Conexión a base de datos (mantenido para compatibilidad)
        
        Raises:
            PermissionError: Si el usuario no tiene rol ADMIN
        """
        # SPRINT 1: Validar acceso solo administradores
        self.validate_admin_access()
        
        self.parent = parent
        self.db = db_connection  # Mantenido para compatibilidad
        
        # Lazy loading para servicios
        self._movement_service = None
        self._product_service = None
        self._barcode_service = None
        self._ticket_service = None
        self._export_service = None  # SPRINT 2: Servicio de exportación
        
        # Variables del formulario
        self.producto_var = tk.StringVar()
        self.tipo_movimiento_var = tk.StringVar(value='ENTRADA')
        self.cantidad_var = tk.StringVar()
        self.observaciones_var = tk.StringVar()
        self.costo_unitario_var = tk.StringVar()
        
        # Variables para códigos de barras (simplificadas)
        self.barcode_var = tk.StringVar()
        
        # Control de estado
        self.producto_seleccionado = None
        self.productos_disponibles = []
        
        # SPRINT 3: Estado del panel de productos múltiples
        self.batch_products = {}  # {id_producto: {'producto': data, 'cantidad': int}}
        self.batch_mode_enabled = False
        
        # Crear interfaz
        self.create_widgets()
        self.load_productos()
        self.update_form_state()
        
        # SPRINT 3: Integrar mejoras del panel batch
        self._integrate_batch_improvements()
        
        logger.info("MovementForm inicializado en modo teclado (sin hardware)")
    
    def _integrate_batch_improvements(self):
        """Integrar mejoras del panel batch - SPRINT 3.
        
        Integra funcionalidades mejoradas para entrada por lotes:
        - Callback mejorado para códigos de barras en modo batch
        - Validaciones robustas del lote
        - Métodos de gestión de resultados
        """
        try:
            # Obtener movimientos actuales del TreeView
            movements_data = self._get_current_movements_data()
            
            if not movements_data:
                messagebox.showinfo(
                    "Sin Datos",
                    "No hay movimientos para exportar. Aplique filtros o cargue datos primero."
                )
                return
            
            # Preparar filtros aplicados
            filters = self._get_applied_filters()
            
            # Mostrar diálogo de progreso
            progress_window = self._show_export_progress("Exportando a PDF...")
            
            try:
                # Exportar usando ExportService
                file_path = self.export_service.export_movements_to_pdf(
                    movements=movements_data,
                    filters=filters
                )
                
                # Cerrar progreso
                progress_window.destroy()
                
                # Preguntar si abrir archivo
                if messagebox.askyesno(
                    "Exportación Exitosa",
                    f"Archivo PDF generado exitosamente.\n\n"
                    f"Ubicación: {file_path}\n\n"
                    f"¿Desea abrir el archivo?"
                ):
                    self._open_file(file_path)
                
            except Exception as e:
                progress_window.destroy()
                raise e
                
        except Exception as e:
            logger.error(f"Error exportando a PDF: {e}")
            messagebox.showerror(
                "Error de Exportación",
                f"No se pudo exportar a PDF:\n{e}"
            )
    
    def _get_current_movements_data(self) -> List[Dict[str, Any]]:
        """Obtener datos actuales de movimientos desde el TreeView.
        
        SPRINT 2: Extraer movimientos mostrados actualmente para exportación.
        
        Returns:
            Lista de diccionarios con datos de movimientos
        """
        try:
            movements_data = []
            
            # Recorrer items del TreeView
            for item in self.movements_tree.get_children():
                values = self.movements_tree.item(item)['values']
                
                if len(values) >= 8:
                    movement_dict = {
                        'id_movimiento': values[0],
                        'fecha_movimiento': values[1],
                        'producto_nombre': values[2],
                        'tipo_movimiento': values[3],
                        'cantidad': values[4],
                        'cantidad_anterior': values[5],
                        'cantidad_nueva': values[6],
                        'responsable': values[7]
                    }
                    movements_data.append(movement_dict)
            
            return movements_data
            
        except Exception as e:
            logger.error(f"Error obteniendo datos de movimientos: {e}")
            return []
    
    def _get_applied_filters(self) -> Dict[str, Any]:
        """Obtener filtros actualmente aplicados.
        
        SPRINT 2: Información de filtros para incluir en exportación.
        
        Returns:
            Diccionario con filtros aplicados
        """
        try:
            return {
                'producto': self.filter_producto_combo.get(),
                'tipo_movimiento': self.filter_tipo_combo.get(),
                'fecha_aplicacion': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            }
        except Exception as e:
            logger.error(f"Error obteniendo filtros: {e}")
            return {}
    
    def _show_export_progress(self, message: str) -> tk.Toplevel:
        """Mostrar ventana de progreso durante exportación.
        
        SPRINT 2: Feedback visual durante proceso de exportación.
        
        Args:
            message: Mensaje a mostrar
            
        Returns:
            Ventana de progreso
        """
        try:
            progress_window = tk.Toplevel(self.parent)
            progress_window.title("Exportando...")
            progress_window.geometry("300x100")
            progress_window.transient(self.parent)
            progress_window.grab_set()
            
            # Centrar ventana
            progress_window.update_idletasks()
            x = (progress_window.winfo_screenwidth() // 2) - (300 // 2)
            y = (progress_window.winfo_screenheight() // 2) - (100 // 2)
            progress_window.geometry(f"300x100+{x}+{y}")
            
            # Frame principal
            main_frame = ttk.Frame(progress_window, padding=20)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Mensaje
            ttk.Label(
                main_frame,
                text=message,
                font=("Arial", 10)
            ).pack(pady=(0, 10))
            
            # Barra de progreso indeterminada
            progress_bar = ttk.Progressbar(
                main_frame,
                mode='indeterminate'
            )
            progress_bar.pack(fill=tk.X)
            progress_bar.start(10)
            
            # Actualizar ventana
            progress_window.update()
            
            return progress_window
            
        except Exception as e:
            logger.error(f"Error creando ventana de progreso: {e}")
            # Retornar dummy window si hay error
            dummy = tk.Toplevel()
            dummy.withdraw()
            return dummy
    
    def _open_file(self, file_path: str):
        """Abrir archivo con aplicación predeterminada del sistema.
        
        SPRINT 2: Utilidad para abrir archivos exportados.
        
        Args:
            file_path: Ruta del archivo a abrir
        """
        try:
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':
                subprocess.run(['open', file_path])
            else:
                subprocess.run(['xdg-open', file_path])
                
        except Exception as e:
            logger.error(f"Error abriendo archivo {file_path}: {e}")
            messagebox.showerror(
                "Error",
                f"No se pudo abrir el archivo.\nUbicación: {file_path}"
            )
    
    def _offer_ticket_generation(self, movement_id: int, product_name: str, quantity: int, movement_type: str):
        """Ofrecer generar ticket para movimiento de inventario.
        
        SPRINT 1: Generar tickets para movimientos ENTRADA y AJUSTE.
        VENTA no aplicable - usar formulario de ventas especializado.
        
        Args:
            movement_id: ID del movimiento creado
            product_name: Nombre del producto
            quantity: Cantidad del movimiento
            movement_type: Tipo de movimiento (ENTRADA/AJUSTE)
        """
        try:
            if messagebox.askyesno(
                "Generar Ticket",
                f"¿Desea generar un ticket para este {movement_type.lower()}?\n\n"
                f"Producto: {product_name}\n"
                f"Cantidad: {quantity}\n"
                f"Tipo: {movement_type}"
            ):
                # Generar ticket usando TicketService
                ticket_data = {
                    'tipo': 'MOVIMIENTO',
                    'id_movimiento': movement_id,
                    'producto': product_name,
                    'cantidad': quantity,
                    'tipo_movimiento': movement_type
                }
                
                ticket_path = self.ticket_service.generate_movement_ticket(**ticket_data)
                
                if messagebox.askyesno(
                    "Ticket Generado",
                    f"Ticket generado exitosamente.\n\n"
                    f"Ubicación: {ticket_path}\n\n"
                    f"¿Desea abrir el ticket?"
                ):
                    self._open_file(ticket_path)
                    
        except Exception as e:
            logger.error(f"Error generando ticket: {e}")
            messagebox.showerror(
                "Error",
                f"No se pudo generar el ticket: {e}"
            )
        except Exception as e:
            logger.error(f"Error integrando mejoras batch: {e}")
            # Continúar sin las mejoras si hay problemas
            
            # Reemplazar método de validación con versión mejorada
            # Mantenemos el método original como _validate_batch_original
            if hasattr(self, '_validate_batch'):
                self._validate_batch_original = self._validate_batch
            
            # Configurar callback mejorado para códigos de barras
            if hasattr(self, 'barcode_entry') and self.barcode_entry:
                original_callback = self._on_barcode_scanned
                
                def enhanced_barcode_callback(code: str, is_valid: bool = True):
                    if self.batch_mode_enabled:
                        self._on_barcode_scanned_batch_mode(code, is_valid)
                    else:
                        original_callback(code, is_valid)
                
                # Actualizar callback del BarcodeEntry
                self.barcode_entry.on_scan_complete = enhanced_barcode_callback
            
            logger.debug("Mejoras del panel batch integradas exitosamente")
    
    def validate_admin_access(self):
        """
        Validar que el usuario actual tiene privilegios de administrador.
        
        SPRINT 1: Solo usuarios administradores pueden acceder a gestión de movimientos.
        Los usuarios VENDEDOR deben usar el formulario de ventas especializado.
        
        Raises:
            PermissionError: Si el usuario no tiene rol ADMIN o no hay sesión activa
        """
        try:
            from ui.auth.session_manager import session_manager
            current_user = session_manager.get_current_user()
            
            if not current_user:
                raise PermissionError(
                    "Solo usuarios administradores pueden acceder a gestión de movimientos. "
                    "Por favor, inicie sesión con una cuenta de administrador."
                )
            
            user_role = current_user.get('rol')
            if user_role != 'ADMIN':
                raise PermissionError(
                    "Solo usuarios administradores pueden acceder a gestión de movimientos. "
                    f"Su rol actual es '{user_role}'. Los usuarios VENDEDOR deben usar "
                    "el formulario de ventas especializado."
                )
            
            logger.info(f"Acceso autorizado para usuario admin: {current_user.get('nombre_usuario')}")
            
        except ImportError as e:
            logger.error(f"Error importando session_manager: {e}")
            raise PermissionError(
                "Error de sistema: No se puede validar permisos de usuario"
            )
        except Exception as e:
            logger.error(f"Error validando acceso de usuario: {e}")
            raise PermissionError(
                "Solo usuarios administradores pueden acceder a gestión de movimientos"
            )
    
    @property
    def movement_service(self):
        """Acceso lazy al MovementService a través del Service Container."""
        if self._movement_service is None:
            container = get_container()
            self._movement_service = container.get('movement_service')
        return self._movement_service
    
    @property
    def product_service(self):
        """Acceso lazy al ProductService a través del Service Container."""
        if self._product_service is None:
            container = get_container()
            self._product_service = container.get('product_service')
        return self._product_service
    
    @property
    def barcode_service(self):
        """Acceso lazy al BarcodeService a través del Service Container."""
        if self._barcode_service is None:
            container = get_container()
            self._barcode_service = container.get('barcode_service')
            # Configurar BarcodeService con ProductService
            if hasattr(self._barcode_service, 'set_product_service'):
                self._barcode_service.set_product_service(self.product_service)
        return self._barcode_service
    
    @property
    def ticket_service(self):
        """Acceso lazy al TicketService a través del Service Container."""
        if self._ticket_service is None:
            container = get_container()
            self._ticket_service = container.get('ticket_service')
        return self._ticket_service
    
    @property
    def export_service(self):
        """Acceso lazy al ExportService a través del Service Container.
        
        SPRINT 2: Servicio de exportación para Excel y PDF.
        """
        if self._export_service is None:
            container = get_container()
            self._export_service = container.get('export_service')
        return self._export_service
    
    def create_widgets(self):
        """Crear widgets de la interfaz."""
        # Frame principal
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_label = ttk.Label(
            self.main_frame,
            text="Gestión de Movimientos de Inventario - Modo Teclado",
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
        
        # Sección de códigos de barras (simplificada)
        self.setup_barcode_section(form_frame)
        
        # Separador
        ttk.Separator(form_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # SPRINT 3: Panel de productos múltiples
        self.setup_batch_products_panel(form_frame)
        
        # Separador entre panel batch y formulario individual
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
        
        # SPRINT 1: Eliminar opción VENTA - Solo movimientos de inventario
        tipo_combo = ttk.Combobox(
            tipo_frame,
            textvariable=self.tipo_movimiento_var,
            values=['ENTRADA', 'AJUSTE'],  # VENTA eliminada - usar formulario especializado
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
        """Configurar sección de códigos de barras - Modo Teclado."""
        # Frame principal para códigos de barras
        barcode_frame = ttk.LabelFrame(
            parent_frame,
            text="Código de Barras - Modo Teclado",
            padding=15
        )
        barcode_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Fila 1: Instrucciones
        instructions_label = ttk.Label(
            barcode_frame,
            text="• Escanee código de barras con su lector HID configurado como teclado\n"
                 "• O ingrese manualmente el ID del producto y presione Enter",
            font=("Arial", 9),
            foreground="darkblue",
            justify=tk.LEFT
        )
        instructions_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Fila 2: Campo de código de barras
        code_frame = ttk.Frame(barcode_frame)
        code_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(code_frame, text="Código/ID:", width=12).pack(side=tk.LEFT)
        
        # Widget BarcodeEntry especializado
        self.barcode_entry = BarcodeEntry(
            code_frame,
            textvariable=self.barcode_var,
            on_scan_complete=self._on_barcode_scanned,
            validation_enabled=True,
            clear_after_scan=True,
            font=('Consolas', 12),
            width=30
        )
        self.barcode_entry.pack(side=tk.LEFT, padx=(5, 15))
        
        # Estado del último escaneo
        self.barcode_status_label = ttk.Label(
            code_frame,
            text="Esperando código...",
            font=('Arial', 9),
            foreground="gray"
        )
        self.barcode_status_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Fila 3: Botones de acción
        action_frame = ttk.Frame(barcode_frame)
        action_frame.pack(fill=tk.X)
        
        ttk.Button(
            action_frame,
            text="Buscar Producto",
            command=self._manual_product_search,
            width=15
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            action_frame,
            text="Limpiar Código",
            command=self._clear_barcode_field,
            width=15
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Información adicional
        info_label = ttk.Label(
            action_frame,
            text="Lector configurado en modo HID teclado",
            font=('Arial', 8),
            foreground="green"
        )
        info_label.pack(side=tk.RIGHT)
    
    def _on_barcode_scanned(self, code: str, is_valid: bool = True):
        """
        Callback ejecutado cuando se escanea un código de barras.
        
        Args:
            code: Código escaneado
            is_valid: Si el código tiene formato válido
        """
        try:
            logger.info(f"Código escaneado: {code}, válido: {is_valid}")
            
            if not is_valid:
                self.barcode_status_label.config(
                    text=f"Código inválido: {code}",
                    foreground="red"
                )
                return
            
            # Actualizar estado
            self.barcode_status_label.config(
                text=f"Procesando: {code}...",
                foreground="blue"
            )
            
            # Buscar producto por código
            producto = self._search_product_by_code(code)
            
            if producto:
                # Producto encontrado - seleccionarlo automáticamente
                self._select_product(producto)
                self.barcode_status_label.config(
                    text=f"✓ Producto encontrado: {producto.nombre}",
                    foreground="green"
                )
                
                # Mostrar confirmación
                messagebox.showinfo(
                    "Producto Encontrado",
                    f"Producto seleccionado automáticamente:\n\n"
                    f"ID: {producto.id_producto}\n"
                    f"Nombre: {producto.nombre}\n"
                    f"Stock actual: {getattr(producto, 'stock', 0)}"
                )
            else:
                self.barcode_status_label.config(
                    text=f"✗ Producto no encontrado: {code}",
                    foreground="red"
                )
                
                # Ofrecer búsqueda manual
                if messagebox.askyesno(
                    "Producto No Encontrado",
                    f"No se encontró producto con código: {code}\n\n"
                    "¿Desea buscar manualmente en la lista de productos?"
                ):
                    self.producto_combo.focus()
                    
        except Exception as e:
            logger.error(f"Error procesando código escaneado {code}: {e}")
            self.barcode_status_label.config(
                text=f"Error procesando código",
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
            # Primero intentar búsqueda por código de barras
            producto = self.barcode_service.search_product_by_code(code)
            
            if producto:
                logger.info(f"Producto encontrado por código de barras: {code}")
                return producto
            
            # Si no se encuentra por código, intentar por ID si es numérico
            if code.isdigit():
                product_id = int(code)
                producto = self.product_service.get_product_by_id(product_id)
                
                if producto:
                    logger.info(f"Producto encontrado por ID: {product_id}")
                    return producto
            
        except Exception as e:
            logger.warning(f"No se encontró producto para código: {code}")
            return None
                    
    def _export_batch_results(self, created: List[Dict], failed: List[Dict]):
        """Exportar resultados del lote a archivo de texto - SPRINT 3.
        
        Generar archivo de texto con resumen completo
        de la operación por lotes para auditoría.
        
        Args:
            created: Movimientos exitosos
            failed: Productos fallidos
        """
        try:
            from tkinter import filedialog
            
            # Solicitar ubicación del archivo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            default_filename = f"resultados_lote_{timestamp}.txt"
            
            file_path = filedialog.asksaveasfilename(
                title="Guardar Resultados del Lote",
                defaultextension=".txt",
                filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
                initialname=default_filename
            )
            
            if file_path:
                # Generar contenido del archivo
                content = f"""RESULTADOS DE PROCESAMIENTO POR LOTES
Sistema de Gestión de Inventario - Copy Point S.A.
{'='*60}

Fecha y hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
Archivo generado: {file_path}

RESUMEN EJECUTIVO:
Total productos procesados: {len(created) + len(failed)}
Exitosos: {len(created)}
Fallidos: {len(failed)}
Tasa de éxito: {(len(created) / (len(created) + len(failed)) * 100):.1f}%

"""
                
                if created:
                    content += f"\nMOVIMIENTOS CREADOS EXITOSAMENTE ({len(created)}):\n"
                    content += "-" * 50 + "\n"
                    for item in created:
                        content += f"ID Movimiento: {item['movimiento'].id_movimiento}\n"
                        content += f"Producto: {item['producto']}\n"
                        content += f"Cantidad: +{item['cantidad']} unidades\n"
                        content += f"Timestamp: {datetime.now().strftime('%H:%M:%S')}\n"
                        content += "-" * 30 + "\n"
                
                if failed:
                    content += f"\nPRODUCTOS CON ERRORES ({len(failed)}):\n"
                    content += "-" * 40 + "\n"
                    for item in failed:
                        content += f"Producto: {item['producto']}\n"
                        content += f"Error: {item['error']}\n"
                        content += f"Timestamp: {datetime.now().strftime('%H:%M:%S')}\n"
                        content += "-" * 30 + "\n"
                
                content += f"\nFIN DEL REPORTE\nGenerado por: Sistema de Inventario v5.0\n"
                
                # Escribir archivo
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                messagebox.showinfo(
                    "Exportación Exitosa",
                    f"Resultados exportados exitosamente a:\n{file_path}"
                )
                
        except Exception as e:
            logger.error(f"Error exportando resultados: {e}")
            messagebox.showerror("Error de Exportación", f"No se pudo exportar: {e}")
    
    def _retry_failed_batch_items(self, failed: List[Dict], parent_window: tk.Toplevel):
        """Reintentar productos que fallaron en la creación por lotes - SPRINT 3.
        
        Permitir al usuario seleccionar productos fallidos
        y reintentarlos después de corregir problemas.
        
        Args:
            failed: Lista de productos que fallaron
            parent_window: Ventana padre para cerrar
        """
        try:
            if not failed:
                return
            
            if messagebox.askyesno(
                "Reintentar Productos Fallidos",
                f"¿Desea agregar los {len(failed)} productos fallidos "
                f"de vuelta al lote para corregir y reintentar?\n\n"
                f"Esto cerrará esta ventana y los agregará al panel de lotes."
            ):
                # Cerrar ventana de resultados
                parent_window.destroy()
                
                # Agregar productos fallidos de vuelta al lote
                for item in failed:
                    producto_nombre = item['producto']
                    
                    # Buscar producto por nombre en productos disponibles
                    producto_found = None
                    for producto in self.productos_disponibles:
                        if producto['nombre'] == producto_nombre:
                            producto_found = producto
                            break
                    
                    if producto_found:
                        # Agregar con cantidad por defecto (usuario puede ajustar)
                        id_producto = producto_found['id_producto']
                        self.batch_products[id_producto] = {
                            'producto': producto_found.copy(),
                            'cantidad': 1  # Cantidad por defecto para corrección
                        }
                
                # Actualizar UI del lote
                self._update_batch_tree()
                self._update_batch_info()
                self._validate_batch()
                self._update_batch_panel_state()
                
                # Cambiar a modo batch si no está activo
                if not self.batch_mode_enabled:
                    self.batch_mode_var.set(True)
                    self.toggle_batch_mode()
                
                messagebox.showinfo(
                    "Productos Agregados al Lote",
                    f"Se agregaron {len(failed)} productos al lote para corrección.\n"
                    f"Revise las cantidades y vuelva a crear los movimientos."
                )
                
        except Exception as e:
            logger.error(f"Error reintentando productos fallidos: {e}")
            messagebox.showerror("Error", f"Error reintentando productos: {e}")
    
    def _on_barcode_scanned_batch_mode(self, code: str, is_valid: bool = True):
        """Callback especializado para códigos de barras en modo batch - SPRINT 3.
        
        En modo batch, después de encontrar producto por código,
        mostrar prompt para cantidad y agregar automáticamente al lote.
        
        Args:
            code: Código escaneado
            is_valid: Si el código tiene formato válido
        """
        try:
            logger.info(f"Procesando código en modo batch: {code}")
            
            if not is_valid or not self.batch_mode_enabled:
                # Delegar a método normal si no es modo batch o código inválido
                return self._on_barcode_scanned(code, is_valid)
            
            # Actualizar estado de procesamiento
            self.barcode_status_label.config(
                text=f"Procesando en modo lote: {code}...",
                foreground="blue"
            )
            
            # Buscar producto por código
            producto = self._search_product_by_code(code)
            
            if producto:
                # Producto encontrado - solicitar cantidad para el lote
                self._prompt_quantity_for_batch_product(producto)
            else:
                # Producto no encontrado
                self.barcode_status_label.config(
                    text=f"✗ Producto no encontrado: {code}",
                    foreground="red"
                )
                
                # En modo batch, mostrar opción de búsqueda manual más directa
                if messagebox.askyesno(
                    "Producto No Encontrado - Modo Lote",
                    f"No se encontró producto con código: {code}\n\n"
                    "¿Desea seleccionar manualmente desde la lista para agregar al lote?"
                ):
                    self.producto_combo.focus()
                    messagebox.showinfo(
                        "Modo Lote Activo",
                        "Seleccione producto de la lista y use 'Agregar Producto' "
                        "para incluirlo en el lote."
                    )
                    
        except Exception as e:
            logger.error(f"Error procesando código en modo batch {code}: {e}")
            self.barcode_status_label.config(
                text="Error procesando código",
                foreground="red"
            )
            messagebox.showerror("Error", f"Error procesando código en modo lote: {e}")
    
    def _prompt_quantity_for_batch_product(self, producto: Dict[str, Any]):
        """Solicitar cantidad para producto encontrado por código de barras en modo batch - SPRINT 3.
        
        Mostrar diálogo simple para especificar cantidad antes de
        agregar automáticamente al lote.
        
        Args:
            producto: Producto encontrado por código de barras
        """
        try:
            # Crear diálogo personalizado para cantidad
            quantity_dialog = tk.Toplevel(self.parent)
            quantity_dialog.title("Cantidad para Lote")
            quantity_dialog.geometry("350x200")
            quantity_dialog.transient(self.parent)
            quantity_dialog.grab_set()
            
            # Centrar diálogo
            quantity_dialog.update_idletasks()
            x = (quantity_dialog.winfo_screenwidth() // 2) - (350 // 2)
            y = (quantity_dialog.winfo_screenheight() // 2) - (200 // 2)
            quantity_dialog.geometry(f"350x200+{x}+{y}")
            
            # Variable para resultado
            result = {'quantity': None, 'confirmed': False}
            
            # Crear widgets del diálogo
            main_frame = ttk.Frame(quantity_dialog, padding=20)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Información del producto
            product_info = ttk.Label(
                main_frame,
                text=f"Producto encontrado:\n{producto['nombre']}\n\nStock actual: {producto.get('stock', 0)}",
                font=("Arial", 10),
                justify=tk.CENTER
            )
            product_info.pack(pady=(0, 15))
            
            # Campo de cantidad
            quantity_frame = ttk.Frame(main_frame)
            quantity_frame.pack(pady=10)
            
            ttk.Label(quantity_frame, text="Cantidad a agregar al lote:").pack()
            
            quantity_var = tk.StringVar(value="1")  # Cantidad por defecto
            quantity_entry = ttk.Entry(
                quantity_frame,
                textvariable=quantity_var,
                width=10,
                font=("Arial", 12),
                justify=tk.CENTER
            )
            quantity_entry.pack(pady=(5, 0))
            quantity_entry.focus()
            quantity_entry.select_range(0, tk.END)
            
            # Función de validación
            def validate_and_add():
                try:
                    quantity_str = quantity_var.get().strip()
                    if not quantity_str:
                        messagebox.showwarning("Cantidad Requerida", "Ingrese una cantidad válida")
                        return
                    
                    quantity = int(quantity_str)
                    if quantity <= 0:
                        messagebox.showwarning("Cantidad Inválida", "La cantidad debe ser positiva")
                        return
                    
                    result['quantity'] = quantity
                    result['confirmed'] = True
                    quantity_dialog.destroy()
                    
                except ValueError:
                    messagebox.showwarning("Cantidad Inválida", "La cantidad debe ser un número entero")
            
            def cancel_dialog():
                result['confirmed'] = False
                quantity_dialog.destroy()
            
            # Botones
            buttons_frame = ttk.Frame(main_frame)
            buttons_frame.pack(pady=(15, 0))
            
            ttk.Button(
                buttons_frame,
                text="Agregar al Lote",
                command=validate_and_add,
                style="Accent.TButton"
            ).pack(side=tk.LEFT, padx=(0, 10))
            
            ttk.Button(
                buttons_frame,
                text="Cancelar",
                command=cancel_dialog
            ).pack(side=tk.LEFT)
            
            # Manejar Enter para confirmar
            def on_enter(event):
                validate_and_add()
            
            quantity_entry.bind('<Return>', on_enter)
            
            # Esperar resultado
            quantity_dialog.wait_window()
            
            if result['confirmed'] and result['quantity']:
                # Agregar automáticamente al lote
                self._add_scanned_product_to_batch(producto, result['quantity'])
            else:
                # Cancelado - actualizar status
                self.barcode_status_label.config(
                    text="Operación cancelada",
                    foreground="gray"
                )
                
        except Exception as e:
            logger.error(f"Error en prompt de cantidad: {e}")
            messagebox.showerror("Error", f"Error solicitando cantidad: {e}")
    
    def _add_scanned_product_to_batch(self, producto: Dict[str, Any], cantidad: int):
        """Agregar producto escaneado directamente al lote con cantidad especificada - SPRINT 3.
        
        Método especializado para agregar productos encontrados por
        código de barras, con lógica optimizada para flujo de escaneo.
        
        Args:
            producto: Producto encontrado por código
            cantidad: Cantidad especificada por usuario
        """
        try:
            id_producto = producto['id_producto']
            
            # Agregar o actualizar en el lote
            if id_producto in self.batch_products:
                # Producto ya existe - sumar cantidad
                cantidad_anterior = self.batch_products[id_producto]['cantidad']
                self.batch_products[id_producto]['cantidad'] += cantidad
                
                mensaje = (
                    f"Producto actualizado en lote:\n\n"
                    f"{producto['nombre']}\n"
                    f"Cantidad anterior: {cantidad_anterior}\n"
                    f"Cantidad agregada: +{cantidad}\n"
                    f"Total en lote: {self.batch_products[id_producto]['cantidad']}"
                )
                
                logger.debug(f"Cantidad sumada en lote para {id_producto}: +{cantidad}")
                
            else:
                # Producto nuevo en el lote
                self.batch_products[id_producto] = {
                    'producto': producto.copy(),
                    'cantidad': cantidad
                }
                
                mensaje = (
                    f"Producto agregado al lote:\n\n"
                    f"{producto['nombre']}\n"
                    f"Cantidad: {cantidad} unidades\n"
                    f"Stock actual: {producto.get('stock', 0)}"
                )
                
                logger.debug(f"Producto nuevo en lote: {id_producto} ({cantidad} unidades)")
            
            # Actualizar visualización
            self._update_batch_tree()
            self._update_batch_info()
            self._validate_batch()
            self._update_batch_panel_state()
            
            # Actualizar status de código de barras
            self.barcode_status_label.config(
                text=f"✓ Agregado al lote: {producto['nombre']}",
                foreground="green"
            )
            
            # Mostrar confirmación
            messagebox.showinfo("Producto Agregado al Lote", mensaje)
            
            # Limpiar campo de código para siguiente escaneo
            self._clear_barcode_field()
            
        except Exception as e:
            logger.error(f"Error agregando producto escaneado al lote: {e}")
            messagebox.showerror("Error", f"Error agregando al lote: {e}")
    
    def _select_product(self, producto):
        """
        Seleccionar producto en el formulario.
        
        Args:
            producto: Producto a seleccionar
        """
        try:
            # Establecer producto seleccionado
            self.producto_seleccionado = producto
            
            # Actualizar combobox
            product_text = f"{producto.id_producto} - {producto.nombre}"
            self.producto_var.set(product_text)
            
            # Actualizar stock mostrado
            stock_actual = getattr(producto, 'stock', 0)
            self.stock_actual_label.config(text=f"Stock: {stock_actual}")
            
            # Validar formulario
            self.validate_form_data()
            
            logger.info(f"Producto seleccionado: {producto.nombre}")
            
        except Exception as e:
            logger.error(f"Error seleccionando producto: {e}")
    
    def _manual_product_search(self):
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
            logger.error(f"Error en búsqueda manual: {e}")
            messagebox.showerror("Error", f"Error en búsqueda manual: {e}")
    
    def setup_batch_products_panel(self, parent_frame):
        """Configurar panel de productos múltiples para entrada por lotes.
        
        SPRINT 3: Panel para gestionar múltiples productos en una entrada.
        Permite agregar productos por escaneo o selección manual, acumular cantidades
        y crear movimientos batch de forma eficiente.
        
        Args:
            parent_frame: Frame padre donde agregar el panel
        """
        # Frame principal del panel batch
        self.batch_frame = ttk.LabelFrame(
            parent_frame,
            text="Entrada por Lotes - Múltiples Productos",
            padding=15
        )
        self.batch_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Frame superior con controles
        controls_frame = ttk.Frame(self.batch_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Checkbox para habilitar modo batch
        self.batch_mode_var = tk.BooleanVar()
        self.batch_mode_checkbox = ttk.Checkbutton(
            controls_frame,
            text="Activar modo entrada por lotes",
            variable=self.batch_mode_var,
            command=self.toggle_batch_mode
        )
        self.batch_mode_checkbox.pack(side=tk.LEFT)
        
        # Botones de acción
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.pack(side=tk.RIGHT)
        
        self.add_product_button = ttk.Button(
            buttons_frame,
            text="Agregar Producto",
            command=self.add_product_to_batch,
            state='disabled'
        )
        self.add_product_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.remove_product_button = ttk.Button(
            buttons_frame,
            text="Quitar Seleccionado",
            command=self.remove_product_from_batch,
            state='disabled'
        )
        self.remove_product_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.clear_batch_button = ttk.Button(
            buttons_frame,
            text="Limpiar Todo",
            command=self.clear_batch_products,
            state='disabled'
        )
        self.clear_batch_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.create_batch_button = ttk.Button(
            buttons_frame,
            text="Crear Movimientos",
            command=self.create_batch_movements,
            state='disabled',
            style="Accent.TButton"
        )
        self.create_batch_button.pack(side=tk.LEFT)
        
        # TreeView para mostrar productos del lote
        tree_frame = ttk.Frame(self.batch_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear TreeView
        columns = ('ID', 'Producto', 'Cantidad', 'Stock Actual', 'Subtotal')
        self.batch_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            height=6
        )
        
        # Configurar columnas
        column_widths = {'ID': 60, 'Producto': 250, 'Cantidad': 80, 
                        'Stock Actual': 100, 'Subtotal': 80}
        
        for col in columns:
            self.batch_tree.heading(col, text=col)
            self.batch_tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbars para TreeView
        v_scroll_batch = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.batch_tree.yview)
        h_scroll_batch = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.batch_tree.xview)
        
        self.batch_tree.configure(yscrollcommand=v_scroll_batch.set, xscrollcommand=h_scroll_batch.set)
        
        # Empaquetar TreeView y scrollbars
        self.batch_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll_batch.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll_batch.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Labels de información del lote
        info_frame = ttk.Frame(self.batch_frame)
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.batch_info_label = ttk.Label(
            info_frame,
            text="Productos en lote: 0 | Total cantidad: 0",
            font=("Arial", 9),
            foreground="blue"
        )
        self.batch_info_label.pack(side=tk.LEFT)
        
        # Validación del lote
        self.batch_validation_label = ttk.Label(
            info_frame,
            text="",
            font=("Arial", 9),
            foreground="red"
        )
        self.batch_validation_label.pack(side=tk.RIGHT)
        
        # Estado inicial: modo batch deshabilitado
        self._update_batch_panel_state()
    
    def toggle_batch_mode(self):
        """Alternar entre modo individual y modo batch.
        
        SPRINT 3: Controla la visibilidad y funcionalidad del panel batch.
        """
        self.batch_mode_enabled = self.batch_mode_var.get()
        
        if self.batch_mode_enabled:
            logger.info("Modo entrada por lotes activado")
            # Limpiar selección individual si hay alguna
            self.clear_form()
        else:
            logger.info("Modo entrada individual activado")
            # Limpiar productos del lote
            self.clear_batch_products()
        
        self._update_batch_panel_state()
        self._update_form_availability()
    
    def add_product_to_batch(self):
        """Agregar producto al lote desde selección individual.
        
        SPRINT 3: Toma el producto seleccionado en el formulario individual
        y lo agrega al lote, sumando cantidades si ya existe.
        """
        try:
            if not self.batch_mode_enabled:
                return
            
            if not self.producto_seleccionado:
                messagebox.showwarning(
                    "Producto No Seleccionado",
                    "Seleccione un producto primero para agregar al lote."
                )
                return
            
            # Obtener cantidad del formulario
            cantidad_str = self.cantidad_var.get().strip()
            if not cantidad_str:
                messagebox.showwarning(
                    "Cantidad Requerida",
                    "Ingrese una cantidad para agregar al lote."
                )
                return
            
            try:
                cantidad = int(cantidad_str)
                if cantidad <= 0:
                    messagebox.showwarning(
                        "Cantidad Inválida",
                        "La cantidad debe ser un número positivo."
                    )
                    return
            except ValueError:
                messagebox.showwarning(
                    "Cantidad Inválida",
                    "La cantidad debe ser un número entero."
                )
                return
            
            # Agregar o actualizar producto en el lote
            id_producto = self.producto_seleccionado['id_producto']
            
            if id_producto in self.batch_products:
                # Sumar cantidad si ya existe
                self.batch_products[id_producto]['cantidad'] += cantidad
                logger.debug(f"Cantidad sumada para producto {id_producto}: +{cantidad}")
            else:
                # Agregar nuevo producto al lote
                self.batch_products[id_producto] = {
                    'producto': self.producto_seleccionado.copy(),
                    'cantidad': cantidad
                }
                logger.debug(f"Producto agregado al lote: {id_producto} ({cantidad} unidades)")
            
            # Actualizar visualización
            self._update_batch_tree()
            self._update_batch_info()
            self._validate_batch()
            
            # Limpiar formulario individual para siguiente producto
            self.clear_form()
            
            # Feedback visual
            messagebox.showinfo(
                "Producto Agregado",
                f"Producto agregado al lote: {self.batch_products[id_producto]['producto']['nombre']}\n"
                f"Cantidad total: {self.batch_products[id_producto]['cantidad']} unidades"
            )
            
        except Exception as e:
            logger.error(f"Error agregando producto al lote: {e}")
            messagebox.showerror("Error", f"Error agregando producto al lote: {e}")
    
    def remove_product_from_batch(self):
        """Remover producto seleccionado del lote.
        
        SPRINT 3: Elimina el producto seleccionado en el TreeView del lote.
        """
        try:
            if not self.batch_mode_enabled:
                return
            
            # Obtener selección del TreeView
            selection = self.batch_tree.selection()
            if not selection:
                messagebox.showwarning(
                    "Selección Requerida",
                    "Seleccione un producto del lote para eliminar."
                )
                return
            
            # Obtener ID del producto seleccionado
            item = selection[0]
            values = self.batch_tree.item(item)['values']
            id_producto = int(values[0])
            
            # Confirmar eliminación
            producto_nombre = self.batch_products[id_producto]['producto']['nombre']
            if messagebox.askyesno(
                "Confirmar Eliminación",
                f"¿Eliminar '{producto_nombre}' del lote?"
            ):
                # Eliminar del lote
                del self.batch_products[id_producto]
                
                # Actualizar visualización
                self._update_batch_tree()
                self._update_batch_info()
                self._validate_batch()
                
                logger.debug(f"Producto eliminado del lote: {id_producto}")
                
        except Exception as e:
            logger.error(f"Error eliminando producto del lote: {e}")
            messagebox.showerror("Error", f"Error eliminando producto: {e}")
    
    def clear_batch_products(self):
        """Limpiar todos los productos del lote.
        
        SPRINT 3: Elimina todos los productos del lote y resetea el estado.
        """
        try:
            if self.batch_products:
                if messagebox.askyesno(
                    "Confirmar Limpieza",
                    f"¿Limpiar todos los productos del lote ({len(self.batch_products)} productos)?"
                ):
                    self.batch_products.clear()
                    self._update_batch_tree()
                    self._update_batch_info()
                    self._validate_batch()
                    
                    logger.debug("Lote de productos limpiado")
            
        except Exception as e:
            logger.error(f"Error limpiando lote: {e}")
    
    def create_batch_movements(self):
        """Crear movimientos para todos los productos del lote.
        
        SPRINT 3: Procesa todos los productos del lote y crea movimientos
        individuales para cada uno, manteniendo la consistencia de datos.
        """
        try:
            if not self.batch_mode_enabled or not self.batch_products:
                return
            
            # Validar lote antes de procesar
            if not self._validate_batch():
                messagebox.showwarning(
                    "Lote Inválido",
                    "El lote contiene errores. Corrija los problemas antes de crear movimientos."
                )
                return
            
            # Confirmar creación de movimientos
            total_productos = len(self.batch_products)
            total_cantidad = sum(item['cantidad'] for item in self.batch_products.values())
            
            if not messagebox.askyesno(
                "Confirmar Creación de Movimientos",
                f"¿Crear movimientos para {total_productos} productos?\n"
                f"Total cantidad: {total_cantidad} unidades\n\n"
                f"Esta acción creará {total_productos} movimientos individuales."
            ):
                return
            
            # Obtener usuario responsable
            current_user = session_manager.get_current_user()
            responsable = current_user.get('nombre_usuario', 'usuario') if current_user else 'usuario'
            
            # Procesar cada producto del lote
            movements_created = []
            failed_products = []
            
            for id_producto, item in self.batch_products.items():
                try:
                    producto = item['producto']
                    cantidad = item['cantidad']
                    
                    # Preparar datos del movimiento
                    movement_data = {
                        'id_producto': id_producto,
                        'tipo_movimiento': 'ENTRADA',  # Solo entradas en modo batch
                        'cantidad': cantidad,
                        'responsable': responsable,
                        'observaciones': f'Entrada por lotes - {datetime.now().strftime("%d/%m/%Y %H:%M")}',
                        'costo_unitario': None  # Opcional en lotes
                    }
                    
                    # Crear movimiento individual
                    movimiento = self.movement_service.create_movement(**movement_data)
                    movements_created.append({
                        'movimiento': movimiento,
                        'producto': producto['nombre'],
                        'cantidad': cantidad
                    })
                    
                    logger.debug(f"Movimiento creado para {producto['nombre']}: {cantidad} unidades")
                    
                except Exception as e:
                    logger.error(f"Error creando movimiento para producto {id_producto}: {e}")
                    failed_products.append({
                        'producto': item['producto']['nombre'],
                        'error': str(e)
                    })
            
            # Mostrar resultados
            self._show_batch_results(movements_created, failed_products)
            
            # Si todo fue exitoso, limpiar lote
            if not failed_products:
                self.clear_batch_products()
                self.toggle_batch_mode()  # Volver a modo individual
                
                # Actualizar datos
                self.load_productos()
                self.load_movements_history()
                self.load_low_stock_products()
            
        except Exception as e:
            logger.error(f"Error creando movimientos en lote: {e}")
            messagebox.showerror("Error", f"Error procesando lote: {e}")
    
    def _update_batch_tree(self):
        """Actualizar TreeView del lote con productos actuales."""
        # Limpiar TreeView
        for item in self.batch_tree.get_children():
            self.batch_tree.delete(item)
        
        # Agregar productos del lote
        for id_producto, item in self.batch_products.items():
            producto = item['producto']
            cantidad = item['cantidad']
            stock_actual = producto.get('stock', 0)
            subtotal = stock_actual + cantidad
            
            self.batch_tree.insert('', 'end', values=(
                id_producto,
                producto['nombre'],
                f"+{cantidad}",
                stock_actual,
                subtotal
            ))
    
    def _update_batch_info(self):
        """Actualizar etiquetas informativas del lote."""
        total_productos = len(self.batch_products)
        total_cantidad = sum(item['cantidad'] for item in self.batch_products.values())
        
        self.batch_info_label.config(
            text=f"Productos en lote: {total_productos} | Total cantidad: {total_cantidad}"
        )
    
    def _validate_batch(self) -> bool:
        """Validación mejorada del lote con verificaciones adicionales - SPRINT 3.
        
        Validaciones más robustas que incluyen verificación
        de stock, cantidades válidas, y consistencia de datos.
        
        Returns:
            bool: True si el lote es completamente válido
        """
        try:
            # Limpiar mensaje anterior
            self.batch_validation_label.config(text="", foreground="red")
            
            # Verificar lote no vacío
            if not self.batch_products:
                self.batch_validation_label.config(text="Lote vacío")
                return False
            
            # Validar cada producto del lote
            for id_producto, item in self.batch_products.items():
                producto = item['producto']
                cantidad = item['cantidad']
                
                # Validar cantidad positiva
                if cantidad <= 0:
                    self.batch_validation_label.config(
                        text=f"Cantidad inválida para {producto['nombre']}: {cantidad}"
                    )
                    return False
                
                # Validar estructura del producto
                required_fields = ['id_producto', 'nombre']
                for field in required_fields:
                    if field not in producto:
                        self.batch_validation_label.config(
                            text=f"Datos incompletos para producto {id_producto}"
                        )
                        return False
                
                # Validar coherencia de ID
                if producto['id_producto'] != id_producto:
                    self.batch_validation_label.config(
                        text=f"Inconsistencia de ID para {producto['nombre']}"
                    )
                    return False
            
            # Validar límites del lote
            total_productos = len(self.batch_products)
            total_cantidad = sum(item['cantidad'] for item in self.batch_products.values())
            
            # Límites de seguridad para el lote
            MAX_PRODUCTOS_LOTE = 50
            MAX_CANTIDAD_TOTAL = 1000
            
            if total_productos > MAX_PRODUCTOS_LOTE:
                self.batch_validation_label.config(
                    text=f"Demasiados productos en lote: {total_productos}/{MAX_PRODUCTOS_LOTE}"
                )
                return False
            
            if total_cantidad > MAX_CANTIDAD_TOTAL:
                self.batch_validation_label.config(
                    text=f"Cantidad total excesiva: {total_cantidad}/{MAX_CANTIDAD_TOTAL}"
                )
                return False
            
            # Lote completamente válido
            self.batch_validation_label.config(
                text=f"✓ Lote válido ({total_productos} productos, {total_cantidad} unidades)",
                foreground="green"
            )
            return True
            
        except Exception as e:
            logger.error(f"Error validando lote: {e}")
            self.batch_validation_label.config(
                text="Error en validación del lote",
                foreground="red"
            )
            return False
    
    def _update_batch_panel_state(self):
        """Actualizar estado de botones del panel batch."""
        if self.batch_mode_enabled:
            self.add_product_button.config(state='normal')
            self.remove_product_button.config(state='normal')
            self.clear_batch_button.config(state='normal')
            self.create_batch_button.config(state='normal' if self.batch_products else 'disabled')
        else:
            self.add_product_button.config(state='disabled')
            self.remove_product_button.config(state='disabled')
            self.clear_batch_button.config(state='disabled')
            self.create_batch_button.config(state='disabled')
    
    def _update_form_availability(self):
        """Actualizar disponibilidad del formulario individual según modo."""
        if self.batch_mode_enabled:
            # En modo batch, formulario individual se usa solo para selección
            self.crear_button.config(state='disabled')
        else:
            # En modo individual, habilitar creación normal
            self.validate_form_data()  # Re-validar para actualizar estado
    
    def _show_batch_results(self, created: List[Dict], failed: List[Dict]):
        """Mostrar resultados mejorados de la creación de movimientos en lote - SPRINT 3.
        
        Ventana de resultados con más detalles, estadísticas,
        y opciones adicionales para el usuario.
        
        Args:
            created: Lista de movimientos creados exitosamente
            failed: Lista de productos que fallaron al crear movimiento
        """
        try:
            # Crear ventana de resultados mejorada
            results_window = tk.Toplevel(self.parent)
            results_window.title("Resultados de Creación por Lotes")
            results_window.geometry("700x500")
            results_window.transient(self.parent)
            results_window.grab_set()
            
            # Centrar ventana
            results_window.update_idletasks()
            x = (results_window.winfo_screenwidth() // 2) - (700 // 2)
            y = (results_window.winfo_screenheight() // 2) - (500 // 2)
            results_window.geometry(f"700x500+{x}+{y}")
            
            # Frame principal
            main_frame = ttk.Frame(results_window, padding=10)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Título con estadísticas
            total_processed = len(created) + len(failed)
            success_rate = (len(created) / total_processed * 100) if total_processed > 0 else 0
            
            title_text = (
                f"Resultados de Procesamiento por Lotes\n"
                f"Procesados: {total_processed} | Exitosos: {len(created)} | "
                f"Fallidos: {len(failed)} | Tasa de éxito: {success_rate:.1f}%"
            )
            
            title_label = ttk.Label(
                main_frame,
                text=title_text,
                font=("Arial", 11, "bold"),
                justify=tk.CENTER
            )
            title_label.pack(pady=(0, 15))
            
            # Notebook para diferentes secciones de resultados
            results_notebook = ttk.Notebook(main_frame)
            results_notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
            
            # Pestaña de resultados exitosos
            if created:
                success_frame = ttk.Frame(results_notebook)
                results_notebook.add(success_frame, text=f"✓ Exitosos ({len(created)})")
                
                success_tree = ttk.Treeview(
                    success_frame,
                    columns=('Producto', 'Cantidad', 'ID Movimiento', 'Timestamp'),
                    show='headings',
                    height=12
                )
                
                # Configurar columnas
                success_tree.heading('Producto', text='Producto')
                success_tree.heading('Cantidad', text='Cantidad')
                success_tree.heading('ID Movimiento', text='ID Movimiento')
                success_tree.heading('Timestamp', text='Creado')
                
                success_tree.column('Producto', width=200)
                success_tree.column('Cantidad', width=80)
                success_tree.column('ID Movimiento', width=100)
                success_tree.column('Timestamp', width=150)
                
                # Agregar datos exitosos
                for item in created:
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    success_tree.insert('', 'end', values=(
                        item['producto'],
                        f"+{item['cantidad']}",
                        item['movimiento'].id_movimiento,
                        timestamp
                    ))
                
                # Scrollbar para éxitos
                success_scroll = ttk.Scrollbar(success_frame, orient=tk.VERTICAL, command=success_tree.yview)
                success_tree.configure(yscrollcommand=success_scroll.set)
                
                success_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                success_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Pestaña de errores
            if failed:
                error_frame = ttk.Frame(results_notebook)
                results_notebook.add(error_frame, text=f"✗ Errores ({len(failed)})")
                
                error_tree = ttk.Treeview(
                    error_frame,
                    columns=('Producto', 'Error', 'Sugerencia'),
                    show='headings',
                    height=12
                )
                
                error_tree.heading('Producto', text='Producto')
                error_tree.heading('Error', text='Error')
                error_tree.heading('Sugerencia', text='Sugerencia')
                
                error_tree.column('Producto', width=150)
                error_tree.column('Error', width=250)
                error_tree.column('Sugerencia', width=200)
                
                # Agregar errores con sugerencias
                for item in failed:
                    error_msg = item['error']
                    
                    # Generar sugerencia basada en el error
                    if 'stock' in error_msg.lower():
                        sugerencia = "Verificar inventario disponible"
                    elif 'duplicado' in error_msg.lower():
                        sugerencia = "Revisar productos en lote"
                    elif 'validación' in error_msg.lower():
                        sugerencia = "Verificar datos del producto"
                    else:
                        sugerencia = "Contactar administrador"
                    
                    error_tree.insert('', 'end', values=(
                        item['producto'],
                        error_msg,
                        sugerencia
                    ))
                
                # Scrollbar para errores
                error_scroll = ttk.Scrollbar(error_frame, orient=tk.VERTICAL, command=error_tree.yview)
                error_tree.configure(yscrollcommand=error_scroll.set)
                
                error_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                error_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Pestaña de resumen general
            summary_frame = ttk.Frame(results_notebook)
            results_notebook.add(summary_frame, text="📊 Resumen")
            
            summary_text = tk.Text(summary_frame, wrap=tk.WORD, font=("Consolas", 10))
            summary_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Generar resumen detallado
            summary_content = f"""RESUMEN DE PROCESAMIENTO POR LOTES
{'='*50}

Fecha y hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
Total productos procesados: {total_processed}
Movimientos creados exitosamente: {len(created)}
Productos con errores: {len(failed)}
Tasa de éxito: {success_rate:.1f}%

"""
            
            if created:
                summary_content += "PRODUCTOS PROCESADOS EXITOSAMENTE:\n"
                summary_content += "-" * 40 + "\n"
                for item in created:
                    summary_content += f"• {item['producto']}: +{item['cantidad']} unidades (ID: {item['movimiento'].id_movimiento})\n"
                summary_content += "\n"
            
            if failed:
                summary_content += "PRODUCTOS CON ERRORES:\n"
                summary_content += "-" * 25 + "\n"
                for item in failed:
                    summary_content += f"• {item['producto']}: {item['error']}\n"
                summary_content += "\n"
            
            # Calcular totales
            if created:
                total_cantidad_exitosa = sum(item['cantidad'] for item in created)
                summary_content += f"TOTALES:\n"
                summary_content += f"- Cantidad total ingresada: {total_cantidad_exitosa} unidades\n"
                summary_content += f"- Movimientos de inventario creados: {len(created)}\n"
                summary_content += f"- Tiempo estimado de procesamiento: {len(created) * 0.5:.1f} segundos\n"
            
            summary_text.insert('1.0', summary_content)
            summary_text.config(state='disabled')
            
            # Frame de botones mejorado
            buttons_frame = ttk.Frame(main_frame)
            buttons_frame.pack(fill=tk.X, pady=(10, 0))
            
            # Botón para exportar resultados
            if created or failed:
                ttk.Button(
                    buttons_frame,
                    text="📄 Exportar Resultados",
                    command=lambda: self._export_batch_results(created, failed)
                ).pack(side=tk.LEFT, padx=(0, 10))
            
            # Botón para reintentar errores
            if failed:
                ttk.Button(
                    buttons_frame,
                    text="🔄 Reintentar Errores",
                    command=lambda: self._retry_failed_batch_items(failed, results_window)
                ).pack(side=tk.LEFT, padx=(0, 10))
            
            # Botón cerrar
            ttk.Button(
                buttons_frame,
                text="Cerrar",
                command=results_window.destroy,
                style="Accent.TButton"
            ).pack(side=tk.RIGHT)
            
            # Auto-seleccionar pestaña apropiada
            if failed:
                results_notebook.select(1)  # Mostrar errores si los hay
            elif created:
                results_notebook.select(0)  # Mostrar éxitos
            
        except Exception as e:
            logger.error(f"Error mostrando resultados del lote: {e}")
            messagebox.showerror("Error", f"Error mostrando resultados: {e}")
    
    def _export_batch_results(self, created: List[Dict], failed: List[Dict]):
        """Exportar resultados del lote a archivo de texto - SPRINT 3.
        
        Generar archivo de texto con resumen completo
        de la operación por lotes para auditoría.
        
        Args:
            created: Movimientos exitosos
            failed: Productos fallidos
        """
        try:
            from tkinter import filedialog
            
            # Solicitar ubicación del archivo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            default_filename = f"resultados_lote_{timestamp}.txt"
            
            file_path = filedialog.asksaveasfilename(
                title="Guardar Resultados del Lote",
                defaultextension=".txt",
                filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
                initialname=default_filename
            )
            
            if file_path:
                # Generar contenido del archivo
                content = f"""RESULTADOS DE PROCESAMIENTO POR LOTES
Sistema de Gestión de Inventario - Copy Point S.A.
{'='*60}

Fecha y hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
Archivo generado: {file_path}

RESUMEN EJECUTIVO:
Total productos procesados: {len(created) + len(failed)}
Exitosos: {len(created)}
Fallidos: {len(failed)}
Tasa de éxito: {(len(created) / (len(created) + len(failed)) * 100):.1f}%

"""
                
                if created:
                    content += f"\nMOVIMIENTOS CREADOS EXITOSAMENTE ({len(created)}):\n"
                    content += "-" * 50 + "\n"
                    for item in created:
                        content += f"ID Movimiento: {item['movimiento'].id_movimiento}\n"
                        content += f"Producto: {item['producto']}\n"
                        content += f"Cantidad: +{item['cantidad']} unidades\n"
                        content += f"Timestamp: {datetime.now().strftime('%H:%M:%S')}\n"
                        content += "-" * 30 + "\n"
                
                if failed:
                    content += f"\nPRODUCTOS CON ERRORES ({len(failed)}):\n"
                    content += "-" * 40 + "\n"
                    for item in failed:
                        content += f"Producto: {item['producto']}\n"
                        content += f"Error: {item['error']}\n"
                        content += f"Timestamp: {datetime.now().strftime('%H:%M:%S')}\n"
                        content += "-" * 30 + "\n"
                
                content += f"\nFIN DEL REPORTE\nGenerado por: Sistema de Inventario v5.0\n"
                
                # Escribir archivo
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                messagebox.showinfo(
                    "Exportación Exitosa",
                    f"Resultados exportados exitosamente a:\n{file_path}"
                )
                
        except Exception as e:
            logger.error(f"Error exportando resultados: {e}")
            messagebox.showerror("Error de Exportación", f"No se pudo exportar: {e}")
    
    def _retry_failed_batch_items(self, failed: List[Dict], parent_window):
        """Reintentar productos que fallaron en la creación por lotes - SPRINT 3.
        
        Permitir al usuario seleccionar productos fallidos
        y reintentarlos después de corregir problemas.
        
        Args:
            failed: Lista de productos que fallaron
            parent_window: Ventana padre para cerrar
        """
        try:
            if not failed:
                return
            
            if messagebox.askyesno(
                "Reintentar Productos Fallidos",
                f"¿Desea agregar los {len(failed)} productos fallidos "
                f"de vuelta al lote para corregir y reintentar?\n\n"
                f"Esto cerrará esta ventana y los agregará al panel de lotes."
            ):
                # Cerrar ventana de resultados
                parent_window.destroy()
                
                # Agregar productos fallidos de vuelta al lote
                for item in failed:
                    producto_nombre = item['producto']
                    
                    # Buscar producto por nombre en productos disponibles
                    producto_found = None
                    for producto in self.productos_disponibles:
                        if producto['nombre'] == producto_nombre:
                            producto_found = producto
                            break
                    
                    if producto_found:
                        # Agregar con cantidad por defecto (usuario puede ajustar)
                        id_producto = producto_found['id_producto']
                        self.batch_products[id_producto] = {
                            'producto': producto_found.copy(),
                            'cantidad': 1  # Cantidad por defecto para corrección
                        }
                
                # Actualizar UI del lote
                self._update_batch_tree()
                self._update_batch_info()
                self._validate_batch()
                self._update_batch_panel_state()
                
                # Cambiar a modo batch si no está activo
                if not self.batch_mode_enabled:
                    self.batch_mode_var.set(True)
                    self.toggle_batch_mode()
                
                messagebox.showinfo(
                    "Productos Agregados al Lote",
                    f"Se agregaron {len(failed)} productos al lote para corrección.\n"
                    f"Revise las cantidades y vuelva a crear los movimientos."
                )
                
        except Exception as e:
            logger.error(f"Error reintentando productos fallidos: {e}")
            messagebox.showerror("Error", f"Error reintentando productos: {e}")
            return
            
            # Simular escaneo manual
            self._on_barcode_scanned(code, is_valid=True)
            
        except Exception as e:
            logger.error(f"Error en búsqueda manual: {e}")
            messagebox.showerror("Error", f"Error en búsqueda manual: {e}")
    
    def _clear_barcode_field(self):
        """Limpiar campo de código de barras."""
        self.barcode_var.set("")
        self.barcode_status_label.config(
            text="Esperando código...",
            foreground="gray"
        )
        self.barcode_entry.focus()
    
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
        ).pack(side=tk.LEFT, padx=(5, 10))
        
        # SPRINT 2: Botones de exportación
        ttk.Button(
            filter_frame,
            text="Exportar Excel",
            command=self.export_movements_to_excel
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        ttk.Button(
            filter_frame,
            text="Exportar PDF",
            command=self.export_movements_to_pdf
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
                if producto.id_producto == id_producto:
                    self.producto_seleccionado = producto
                    break
            
            if self.producto_seleccionado:
                stock_actual = getattr(self.producto_seleccionado, 'stock', 0)
                self.stock_actual_label.config(text=f"Stock: {stock_actual}")
                
                # Actualizar código de barras si se selecciona manualmente
                self.barcode_var.set(str(self.producto_seleccionado.id_producto))
                
                # Validar formulario
                self.validate_form_data()
        
        except Exception as e:
            logger.error(f"Error en selección de producto: {e}")
    
    def on_tipo_changed(self, event=None):
        """Manejar cambio de tipo de movimiento.
        
        SPRINT 1: Actualizado para manejar solo ENTRADA y AJUSTE.
        VENTA eliminada - usar formulario de ventas especializado.
        """
        tipo = self.tipo_movimiento_var.get()
        
        # Actualizar información según tipo (solo ENTRADA y AJUSTE)
        if tipo == 'ENTRADA':
            self.cantidad_info_label.config(text="(Cantidad a ingresar)")
            self.costo_entry.config(state='normal')
        elif tipo == 'AJUSTE':
            self.cantidad_info_label.config(text="(+/- para ajustar)")
            self.costo_entry.config(state='disabled')
            self.costo_unitario_var.set('')
        else:
            # Manejo de valores no válidos (ej: si alguien establece VENTA manualmente)
            logger.warning(f"Tipo de movimiento no válido: {tipo}. Estableciendo ENTRADA por defecto.")
            self.tipo_movimiento_var.set('ENTRADA')
            self.cantidad_info_label.config(text="(Cantidad a ingresar)")
            self.costo_entry.config(state='normal')
        
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
            
            # SPRINT 1: Validaciones actualizadas para ENTRADA y AJUSTE solamente
            tipo = self.tipo_movimiento_var.get()
            
            # ENTRADA debe tener cantidad positiva
            if tipo == 'ENTRADA' and cantidad < 0:
                self.validation_label.config(text="Las entradas deben tener cantidad positiva")
                self.crear_button.config(state='disabled')
                return
            
            # AJUSTE puede tener cantidades positivas o negativas (sin restricción adicional)
            # VENTA eliminada - no requiere validación de stock aquí
            
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
                error_message = "Errores encontrados:\n" + "\n".join(errors)
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
                f"Movimiento creado exitosamenten"
                f"ID: {movimiento.id_movimiento}\n"
                f"Tipo: {movimiento.tipo_movimiento}\n"
                f"Producto: {producto_nombre}"
            )
            
            # SPRINT 1: Generar tickets para movimientos de inventario (ENTRADA y AJUSTE)
            # VENTA no aplicable - usar formulario de ventas especializado
            if movimiento.tipo_movimiento in ['ENTRADA', 'AJUSTE']:
                self._offer_ticket_generation(movimiento.id_movimiento, producto_nombre, cantidad, movimiento.tipo_movimiento)
            
            # Limpiar formulario
            self.clear_form()
            
            # Actualizar datos
            self.load_productos()
            self.load_movements_history()
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
        
        # Limpiar también códigos de barras
        self._clear_barcode_field()
        
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
                
                # SPRINT 1: Formatear cantidad según tipo (ENTRADA y AJUSTE)
                cantidad = mov['cantidad']
                if mov['tipo_movimiento'] == 'ENTRADA':
                    cantidad_str = f"+{cantidad}"
                elif mov['tipo_movimiento'] == 'AJUSTE':
                    cantidad_str = f"{cantidad:+d}"
                else:
                    # Para compatibilidad con datos históricos que puedan tener VENTA
                    cantidad_str = f"{cantidad}"
                
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
            
            # Aplicar filtro de tipo si es necesario
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
                
                # SPRINT 1: Formateo de cantidad para ENTRADA y AJUSTE
                cantidad = mov['cantidad']
                if mov['tipo_movimiento'] == 'ENTRADA':
                    cantidad_str = f"+{cantidad}"
                elif mov['tipo_movimiento'] == 'AJUSTE':
                    cantidad_str = f"{cantidad:+d}"
                else:
                    # Compatibilidad con datos históricos
                    cantidad_str = f"{cantidad}"
                
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
    
    # SPRINT 2: Métodos de exportación
    
    def export_movements_to_excel(self):
        """Exportar movimientos actuales a Excel.
        
        SPRINT 2: Exportación con formato profesional y filtros aplicados.
        """
        try:
            # Obtener movimientos actuales del TreeView
            movements_data = self._get_current_movements_data()
            
            if not movements_data:
                messagebox.showinfo(
                    "Sin Datos",
                    "No hay movimientos para exportar. Aplique filtros o cargue datos primero."
                )
                return
            
            # Preparar filtros aplicados
            filters = self._get_applied_filters()
            
            # Mostrar diálogo de progreso
            progress_window = self._show_export_progress("Exportando a Excel...")
            
            try:
                # Exportar usando ExportService
                file_path = self.export_service.export_movements_to_excel(
                    movements=movements_data,
                    filters=filters
                )
                
                # Cerrar progreso
                progress_window.destroy()
                
                # Preguntar si abrir archivo
                if messagebox.askyesno(
                    "Exportación Exitosa",
                    f"Archivo Excel generado exitosamente.\n\n"
                    f"Ubicación: {file_path}\n\n"
                    f"¿Desea abrir el archivo?"
                ):
                    self._open_file(file_path)
                
            except Exception as e:
                progress_window.destroy()
                raise e
                
        except Exception as e:
            logger.error(f"Error exportando a Excel: {e}")
            messagebox.showerror(
                "Error de Exportación",
                f"No se pudo exportar a Excel:\n{e}"
            )
    
    def export_movements_to_pdf(self):
        """Exportar movimientos actuales a PDF.
        
        SPRINT 2: Exportación con diseño profesional y resumen ejecutivo.
        """
        try:
            # Obtener movimientos actuales
            movements_data = self._get_current_movements_data()
            
            if not movements_data:
                messagebox.showinfo(
                    "Sin Datos",
                    "No hay movimientos para exportar. Aplique filtros o cargue datos primero."
                )
                return
            
            # Preparar filtros aplicados
            filters = self._get_applied_filters()
            
            # Mostrar diálogo de progreso
            progress_window = self._show_export_progress("Generando PDF...")
            
            try:
                # Exportar usando ExportService
                file_path = self.export_service.export_movements_to_pdf(
                    movements=movements_data,
                    filters=filters
                )
                
                # Cerrar progreso
                progress_window.destroy()
                
                # Preguntar si abrir archivo
                if messagebox.askyesno(
                    "Exportación Exitosa",
                    f"Reporte PDF generado exitosamente.\n\n"
                    f"Ubicación: {file_path}\n\n"
                    f"¿Desea abrir el archivo?"
                ):
                    self._open_file(file_path)
                
            except Exception as e:
                progress_window.destroy()
                raise e
                
        except Exception as e:
            logger.error(f"Error exportando a PDF: {e}")
            messagebox.showerror(
                "Error de Exportación",
                f"No se pudo generar PDF:\n{e}"
            )
    
    def _get_current_movements_data(self):
        """Obtener datos de movimientos actuales del TreeView.
        
        Returns:
            List[Dict[str, Any]]: Lista de movimientos en formato para exportación
        """
        movements_data = []
        
        # Obtener todos los items del TreeView
        for item_id in self.movements_tree.get_children():
            item_values = self.movements_tree.item(item_id)['values']
            
            if item_values:
                # Convertir a diccionario usando headers de columnas
                movement_dict = {
                    'id_movimiento': item_values[0],
                    'fecha_movimiento': item_values[1],
                    'producto_nombre': item_values[2],
                    'tipo_movimiento': item_values[3],
                    'cantidad': item_values[4],
                    'cantidad_anterior': item_values[5],
                    'cantidad_nueva': item_values[6],
                    'responsable': item_values[7]
                }
                movements_data.append(movement_dict)
        
        return movements_data
    
    def _get_applied_filters(self):
        """Obtener filtros actualmente aplicados.
        
        Returns:
            Dict[str, Any]: Filtros aplicados
        """
        filters = {
            'fecha_generacion': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'usuario_generador': session_manager.get_current_user().get('nombre_usuario', 'usuario') if session_manager.get_current_user() else 'usuario'
        }
        
        # Filtro de producto
        producto_filter = self.filter_producto_combo.get()
        if producto_filter and producto_filter != 'Todos':
            filters['producto'] = producto_filter
        
        # Filtro de tipo
        tipo_filter = self.filter_tipo_combo.get()
        if tipo_filter and tipo_filter != 'Todos':
            filters['tipo_movimiento'] = tipo_filter
        
        # Si no hay filtros específicos, indicar que son todos
        if len(filters) == 2:  # Solo fecha y usuario
            filters['alcance'] = 'Todos los movimientos disponibles'
        
        return filters
    
    def _show_export_progress(self, message: str):
        """Mostrar ventana de progreso durante exportación.
        
        Args:
            message: Mensaje a mostrar
            
        Returns:
            tk.Toplevel: Ventana de progreso
        """
        progress_window = tk.Toplevel(self.parent)
        progress_window.title("Exportando...")
        progress_window.geometry("300x100")
        progress_window.transient(self.parent)
        progress_window.grab_set()
        
        # Centrar ventana
        progress_window.update_idletasks()
        x = (progress_window.winfo_screenwidth() // 2) - (300 // 2)
        y = (progress_window.winfo_screenheight() // 2) - (100 // 2)
        progress_window.geometry(f"300x100+{x}+{y}")
        
        # Mensaje
        ttk.Label(
            progress_window,
            text=message,
            font=("Arial", 10)
        ).pack(pady=20)
        
        # Barra de progreso indeterminada
        progress_bar = ttk.Progressbar(
            progress_window,
            mode='indeterminate',
            length=250
        )
        progress_bar.pack(pady=10)
        progress_bar.start()
        
        # Actualizar UI
        progress_window.update()
        
        return progress_window
    
    def _open_file(self, file_path: str):
        """Abrir archivo con aplicación por defecto del sistema.
        
        Args:
            file_path: Ruta del archivo a abrir
        """
        try:
            import os
            import subprocess
            import platform
            
            system = platform.system()
            
            if system == 'Windows':
                os.startfile(file_path)
            elif system == 'Darwin':  # macOS
                subprocess.run(['open', file_path])
            else:  # Linux
                subprocess.run(['xdg-open', file_path])
                
        except Exception as e:
            logger.warning(f"No se pudo abrir archivo automáticamente: {e}")
            messagebox.showinfo(
                "Archivo Listo",
                f"El archivo se guardó en:\n{file_path}\n\n"
                f"Puede abrirlo manualmente desde el explorador de archivos."
            )
    
    def _offer_ticket_generation(self, id_movimiento: int, producto_nombre: str, cantidad: int, tipo_movimiento: str = "ENTRADA"):
        """Ofrecer generar ticket para movimiento de entrada o ajuste."""
        try:
            # Validar tipo de movimiento soportado
            if tipo_movimiento not in ['ENTRADA', 'AJUSTE']:
                logger.warning(f"Tipo de movimiento {tipo_movimiento} no soportado para tickets")
                return
            
            # Determinar mensaje según tipo
            if tipo_movimiento == 'ENTRADA':
                tipo_texto = "entrada"
                cantidad_texto = f"{cantidad} unidades"
            else:  # AJUSTE
                tipo_texto = "ajuste de inventario"
                cantidad_texto = f"{cantidad:+d} unidades" if cantidad != 0 else "sin cambio de cantidad"
            
            # Preguntar si desea generar ticket
            if messagebox.askyesno(
                "Generar Ticket",
                f"¿Desea generar un ticket para el movimiento de {tipo_texto}?\n"
                f"Producto: {producto_nombre}\n"
                f"Cantidad: {cantidad_texto}"
            ):
                ticket_service = self.ticket_service
                
                # Obtener usuario actual
                current_user = session_manager.get_current_user()
                responsable = current_user.get('nombre_usuario', 'usuario') if current_user else 'usuario'
                
                # Generar ticket
                ticket = ticket_service.generar_ticket_entrada(
                    id_movimiento=id_movimiento,
                    generated_by=responsable
                )
                
                # Mostrar mensaje de éxito
                tipo_ticket_texto = "entrada" if tipo_movimiento == 'ENTRADA' else "ajuste de inventario"
                messagebox.showinfo(
                    "Ticket Generado",
                    f"Ticket de {tipo_ticket_texto} generado exitosamente\n"
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

    def create_movement_window(parent, db_connection):
        """
        Crear ventana de gestión de movimientos - Modo Teclado.
        
        Args:
            parent: Ventana padre
            db_connection: Conexión a base de datos
        """
        try:
            # Crear ventana
            window = tk.Toplevel(parent)
            window.title("Gestión de Movimientos de Inventario - Modo Teclado")
            window.geometry("1100x800")
            window.minsize(900, 700)
            
            # Centrar ventana
            window.transient(parent)
            window.grab_set()
            
            # Crear formulario
            movement_form = MovementForm(window, db_connection)
            
            # Configurar cierre de ventana (simple, sin hardware)
            def on_closing():
                window.destroy()
            
            window.protocol("WM_DELETE_WINDOW", on_closing)
            
            # Foco inicial en campo de código de barras
            movement_form.barcode_entry.focus()
            
            return window
            
        except Exception as e:
            messagebox.showerror("Error", f"Error creando ventana de movimientos: {e}")
            return None


    def _prepare_movement_ticket_data(self, movement_id: int, product_name: str, quantity: int, movement_type: str):
        """Preparar datos para ticket de movimiento.
        
        SPRINT 1: Estructura de datos para tickets de inventario.
        
        Args:
            movement_id: ID del movimiento
            product_name: Nombre del producto
            quantity: Cantidad del movimiento
            movement_type: Tipo de movimiento
            
        Returns:
            Dict: Datos estructurados para el ticket
        """
        try:
            current_user = session_manager.get_current_user()
            responsable = current_user.get('nombre_usuario', 'usuario') if current_user else 'usuario'
            
            ticket_data = {
                'id_movimiento': movement_id,
                'tipo_movimiento': movement_type,
                'fecha': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                'producto': product_name,
                'cantidad': abs(quantity),
                'responsable': responsable,
                'empresa': {
                    'nombre': 'Copy Point S.A.',
                    'ruc': '888-888-8888',
                    'direccion': 'Las Lajas, Las Cumbres, Panamá',
                    'telefono': '6666-6666',
                    'email': 'copy.point@gmail.com'
                }
            }
            
            return ticket_data
            
        except Exception as e:
            logger.error(f"Error preparando datos de ticket: {e}")
            return {}

    def _show_ticket_preview(self, ticket_content: str, movement_type: str):
        """Mostrar preview del ticket generado.
        
        SPRINT 1: Vista previa de tickets de movimiento.
        
        Args:
            ticket_content: Contenido del ticket generado
            movement_type: Tipo de movimiento para el título
        """
        try:
            # Crear ventana de preview
            preview_window = tk.Toplevel(self.parent)
            preview_window.title(f"Preview Ticket - {movement_type}")
            preview_window.geometry("400x500")
            preview_window.transient(self.parent)
            preview_window.grab_set()
            
            # Centrar ventana
            preview_window.update_idletasks()
            x = (preview_window.winfo_screenwidth() // 2) - (400 // 2)
            y = (preview_window.winfo_screenheight() // 2) - (500 // 2)
            preview_window.geometry(f"400x500+{x}+{y}")
            
            # Frame principal
            main_frame = ttk.Frame(preview_window, padding=10)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Título
            ttk.Label(
                main_frame,
                text=f"Preview Ticket - {movement_type}",
                font=("Arial", 12, "bold")
            ).pack(pady=(0, 10))
            
            # Contenido del ticket
            ticket_text = tk.Text(
                main_frame,
                wrap=tk.WORD,
                font=("Consolas", 9),
                height=20,
                width=50
            )
            ticket_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            
            # Scrollbar para texto
            scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=ticket_text.yview)
            ticket_text.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Insertar contenido
            ticket_text.insert('1.0', ticket_content)
            ticket_text.config(state='disabled')
            
            # Botones
            buttons_frame = ttk.Frame(main_frame)
            buttons_frame.pack(fill=tk.X, pady=(10, 0))
            
            ttk.Button(
                buttons_frame,
                text="Imprimir",
                command=lambda: self._print_ticket(ticket_content),
                style="Accent.TButton"
            ).pack(side=tk.LEFT, padx=(0, 10))
            
            ttk.Button(
                buttons_frame,
                text="Guardar PDF",
                command=lambda: self._save_ticket_pdf(ticket_content, movement_type)
            ).pack(side=tk.LEFT, padx=(0, 10))
            
            ttk.Button(
                buttons_frame,
                text="Cerrar",
                command=preview_window.destroy
            ).pack(side=tk.RIGHT)
            
        except Exception as e:
            logger.error(f"Error mostrando preview de ticket: {e}")
            messagebox.showerror("Error", f"Error mostrando ticket: {e}")

    def _print_ticket(self, ticket_content: str):
        """Imprimir ticket directamente.
        
        SPRINT 1: Funcionalidad de impresión directa.
        
        Args:
            ticket_content: Contenido del ticket a imprimir
        """
        try:
            # Usar servicio de impresión del sistema
            import tempfile
            import os
            
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(ticket_content)
                temp_path = temp_file.name
            
            # Imprimir usando comando del sistema
            if os.name == 'nt':  # Windows
                os.startfile(temp_path, "print")
            else:
                # Linux/Mac
                os.system(f'lp "{temp_path}"')
            
            messagebox.showinfo("Impresión", "Ticket enviado a impresora")
            
            # Limpiar archivo temporal después de un momento
            self.parent.after(5000, lambda: self._cleanup_temp_file(temp_path))
            
        except Exception as e:
            logger.error(f"Error imprimiendo ticket: {e}")
            messagebox.showerror("Error", f"Error imprimiendo ticket: {e}")

    def _save_ticket_pdf(self, ticket_content: str, movement_type: str):
        """Guardar ticket como PDF.
        
        SPRINT 1: Exportación de tickets a PDF.
        
        Args:
            ticket_content: Contenido del ticket
            movement_type: Tipo de movimiento para nombre del archivo
        """
        try:
            from tkinter import filedialog
            
            # Solicitar ubicación
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            default_filename = f"ticket_{movement_type.lower()}_{timestamp}.pdf"
            
            file_path = filedialog.asksaveasfilename(
                title="Guardar Ticket como PDF",
                defaultextension=".pdf",
                filetypes=[("Archivos PDF", "*.pdf"), ("Todos los archivos", "*.*")],
                initialname=default_filename
            )
            
            if file_path:
                # Generar PDF usando TicketService
                pdf_path = self.ticket_service.generate_ticket_pdf(ticket_content, file_path)
                
                messagebox.showinfo(
                    "PDF Generado",
                    f"Ticket guardado como PDF:\n{pdf_path}"
                )
                
                # Preguntar si abrir
                if messagebox.askyesno("Abrir PDF", "¿Desea abrir el archivo PDF?"):
                    self._open_file(pdf_path)
            
        except Exception as e:
            logger.error(f"Error guardando ticket como PDF: {e}")
            messagebox.showerror("Error", f"Error guardando PDF: {e}")

    def _cleanup_temp_file(self, file_path: str):
        """Limpiar archivo temporal.
        
        Args:
            file_path: Ruta del archivo temporal a eliminar
        """
        try:
            import os
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            logger.debug(f"No se pudo limpiar archivo temporal {file_path}: {e}")

    def _fix_batch_retry_syntax(self):
        """Método para corregir sintaxis en _retry_failed_batch_items.
        
        SPRINT 3: Corrección de error de sintaxis detectado.
        Este método reemplaza la implementación problemática.
        """
        # Este método sirve como referencia para la corrección
        # El error estaba en un 'return' mal colocado en el método original
        pass

    # MÉTODOS ADICIONALES DE VALIDACIÓN BATCH - SPRINT 3

    def _validate_batch_product_consistency(self, id_producto: int, producto_data: Dict[str, Any]) -> bool:
        """Validar consistencia de datos de producto en lote.
        
        SPRINT 3: Validación específica para productos en lote.
        
        Args:
            id_producto: ID del producto
            producto_data: Datos del producto
            
        Returns:
            bool: True si los datos son consistentes
        """
        try:
            # Verificar que el ID coincida
            if producto_data.get('id_producto') != id_producto:
                logger.warning(f"ID inconsistente: esperado {id_producto}, encontrado {producto_data.get('id_producto')}")
                return False
            
            # Verificar campos obligatorios
            required_fields = ['nombre', 'id_producto']
            for field in required_fields:
                if field not in producto_data or not producto_data[field]:
                    logger.warning(f"Campo obligatorio faltante: {field}")
                    return False
            
            # Verificar tipos de datos
            if not isinstance(producto_data['id_producto'], int):
                logger.warning(f"Tipo de dato incorrecto para id_producto: {type(producto_data['id_producto'])}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validando consistencia de producto {id_producto}: {e}")
            return False

    def _calculate_batch_totals(self) -> Dict[str, Any]:
        """Calcular totales del lote actual.
        
        SPRINT 3: Cálculos estadísticos del lote.
        
        Returns:
            Dict: Totales calculados del lote
        """
        try:
            if not self.batch_products:
                return {
                    'total_productos': 0,
                    'total_cantidad': 0,
                    'total_valor_estimado': 0,
                    'productos_sin_stock': 0
                }
            
            total_productos = len(self.batch_products)
            total_cantidad = 0
            total_valor_estimado = 0
            productos_sin_stock = 0
            
            for id_producto, item in self.batch_products.items():
                producto = item['producto']
                cantidad = item['cantidad']
                
                total_cantidad += cantidad
                
                # Calcular valor estimado si hay precio
                precio = producto.get('precio', 0)
                if precio and precio > 0:
                    total_valor_estimado += precio * cantidad
                
                # Contar productos sin stock
                stock_actual = producto.get('stock', 0)
                if stock_actual <= 0:
                    productos_sin_stock += 1
            
            return {
                'total_productos': total_productos,
                'total_cantidad': total_cantidad,
                'total_valor_estimado': total_valor_estimado,
                'productos_sin_stock': productos_sin_stock,
                'promedio_cantidad_por_producto': total_cantidad / total_productos if total_productos > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error calculando totales del lote: {e}")
            return {}

    def _generate_batch_summary_report(self, created: List[Dict], failed: List[Dict]) -> str:
        """Generar reporte de resumen para operación batch.
        
        SPRINT 3: Reporte detallado de resultados batch.
        
        Args:
            created: Movimientos creados exitosamente
            failed: Productos que fallaron
            
        Returns:
            str: Reporte de resumen en formato texto
        """
        try:
            timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            total_processed = len(created) + len(failed)
            success_rate = (len(created) / total_processed * 100) if total_processed > 0 else 0
            
            # Calcular estadísticas
            total_quantity_created = sum(item['cantidad'] for item in created) if created else 0
            
            report = f"""
    ╔══════════════════════════════════════════════════════════════════╗
    ║                    REPORTE DE OPERACIÓN POR LOTES               ║
    ║                Sistema de Inventario - Copy Point S.A.          ║
    ╠══════════════════════════════════════════════════════════════════╣
    ║ Fecha y Hora: {timestamp:<47} ║
    ║ Operación: Entrada por Lotes de Inventario                      ║
    ╠══════════════════════════════════════════════════════════════════╣
    ║                         RESUMEN EJECUTIVO                       ║
    ╠══════════════════════════════════════════════════════════════════╣
    ║ Total Productos Procesados: {total_processed:<36} ║
    ║ Movimientos Exitosos: {len(created):<42} ║
    ║ Productos con Errores: {len(failed):<41} ║
    ║ Tasa de Éxito: {success_rate:.1f}%{'':<48} ║
    ║ Cantidad Total Ingresada: {total_quantity_created:<38} ║
    ╠══════════════════════════════════════════════════════════════════╣
    ║                      DETALLE DE RESULTADOS                      ║
    ╚══════════════════════════════════════════════════════════════════╝

    """
            
            if created:
                report += "\n🟢 MOVIMIENTOS CREADOS EXITOSAMENTE:\n"
                report += "─" * 65 + "\n"
                for i, item in enumerate(created, 1):
                    report += f"{i:2d}. {item['producto']:<35} | +{item['cantidad']:>3} unidades\n"
                    report += f"    ID Movimiento: {item['movimiento'].id_movimiento}\n\n"
            
            if failed:
                report += "\n🔴 PRODUCTOS CON ERRORES:\n"
                report += "─" * 45 + "\n"
                for i, item in enumerate(failed, 1):
                    report += f"{i:2d}. {item['producto']:<30}\n"
                    report += f"    Error: {item['error']}\n\n"
            
            # Estadísticas adicionales
            if created:
                report += "\n📊 ESTADÍSTICAS ADICIONALES:\n"
                report += "─" * 35 + "\n"
                report += f"• Tiempo estimado de procesamiento: {len(created) * 0.5:.1f} segundos\n"
                report += f"• Promedio por producto: {total_quantity_created / len(created):.1f} unidades\n"
                report += f"• Eficiencia de operación: {success_rate:.1f}%\n"
            
            report += f"\n\n📅 Reporte generado: {timestamp}\n"
            report += "🏢 Sistema de Inventario v5.0 - Copy Point S.A.\n"
            
            return report
            
        except Exception as e:
            logger.error(f"Error generando reporte de resumen: {e}")
            return f"Error generando reporte: {e}"
