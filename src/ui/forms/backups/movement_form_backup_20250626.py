"""
Formulario para gestión de movimientos de inventario.
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
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal

from services.movement_service import MovementService
from services.product_service import ProductService
from ui.auth.session_manager import session_manager
from ui.widgets.decimal_entry import DecimalEntry


class MovementForm:
    """
    Formulario para gestión de movimientos de inventario.
    
    Funcionalidades:
    - Crear movimientos de entrada, venta y ajuste
    - Visualizar historial de movimientos
    - Validación en tiempo real
    - Búsqueda de productos
    - Cálculo automático de stock
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
        
        # Variables del formulario
        self.producto_var = tk.StringVar()
        self.tipo_movimiento_var = tk.StringVar(value='ENTRADA')
        self.cantidad_var = tk.StringVar()
        self.observaciones_var = tk.StringVar()
        self.costo_unitario_var = tk.StringVar()
        
        # Control de estado
        self.producto_seleccionado = None
        self.productos_disponibles = []
        
        # Crear interfaz
        self.create_widgets()
        self.load_productos()
        self.update_form_state()
    
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
                item = f"{producto['id_producto']} - {producto['nombre']}"
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
                if producto['id_producto'] == id_producto:
                    self.producto_seleccionado = producto
                    break
            
            if self.producto_seleccionado:
                # Actualizar información de stock
                stock_actual = self.producto_seleccionado.get('stock_actual', 
                                                            self.producto_seleccionado.get('stock', 0))
                self.stock_actual_label.config(text=f"Stock: {stock_actual}")
                
                # Validar formulario
                self.validate_form_data()
        
        except Exception as e:
            print(f"Error en selección de producto: {e}")
    
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
                stock_actual = self.producto_seleccionado.get('stock_actual', 
                                                            self.producto_seleccionado.get('stock', 0))
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
            producto_nombre = self.producto_seleccionado['nombre']
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
            
            # FASE 3: Preguntar si desea generar ticket para movimientos de ENTRADA
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
                'id_producto': self.producto_seleccionado['id_producto'],
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
        """Ofrecer generar ticket para movimiento de entrada - FASE 3"""
        try:
            # Preguntar si desea generar ticket
            if messagebox.askyesno(
                "Generar Ticket",
                f"¿Desea generar un ticket para el movimiento de entrada?\n"
                f"Producto: {producto_nombre}\n"
                f"Cantidad: {cantidad} unidades"
            ):
                # Importar servicios de tickets
                from services.ticket_service import TicketService
                
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
            messagebox.showerror("Error", f"Error al generar ticket: {e}")
            # No interrumpir el flujo normal si hay error con el ticket


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
        window.title("Gestión de Movimientos de Inventario")
        window.geometry("1000x700")
        window.minsize(800, 600)
        
        # Centrar ventana
        window.transient(parent)
        window.grab_set()
        
        # Crear formulario
        movement_form = MovementForm(window, db_connection)
        
        # Foco inicial
        window.focus()
        
        return window
        
    except Exception as e:
        messagebox.showerror("Error", f"Error creando ventana de movimientos: {e}")
        return None