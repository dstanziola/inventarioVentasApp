# src/ui/forms/movement_history_form.py
"""
MovementHistoryForm - Formulario de Historial de Movimientos
Implementación Clean Architecture + MVP Pattern + CQRS

Propósito: Consulta y visualización de movimientos históricos
Restricción: Solo lectura, no modificación de registros
Acceso: Solo administradores

Autor: Sistema de Gestión de Inventario v5.0
Fecha: 2025-07-16
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import re
from typing import List, Dict, Optional, Any
import logging

# Configurar logger
logger = logging.getLogger(__name__)

class MovementHistoryForm:
    """
    Formulario de historial de movimientos
    
    Implementa:
    - Clean Architecture: Capa Presentación
    - MVP Pattern: Presenter
    - CQRS: Solo consultas (lectura)
    - Service Layer: Lazy loading de servicios
    - Observer Pattern: Callbacks para eventos
    """
    
    def __init__(self, parent: tk.Tk, db_connection: Any):
        """
        Inicializar formulario de historial de movimientos
        
        Args:
            parent: Ventana padre
            db_connection: Conexión a base de datos
        """
        self.parent = parent
        self.db = db_connection
        self.window = None
        
        # Servicios (lazy loading)
        self._movement_service = None
        self._product_service = None
        self._export_service = None
        self._session_manager = None
        self._container = None
        
        # Estado del formulario
        self.current_movements = []
        self.selected_movement = None
        
        # Validar permisos antes de crear UI
        if not self._validate_permissions():
            return
            
        self._setup_window()
        self._create_ui_components()
        self._setup_bindings()
        self._setup_styles()
        
        logger.info("MovementHistoryForm inicializado correctamente")
    
    def _validate_permissions(self) -> bool:
        """
        Validar que el usuario tenga permisos de administrador
        
        Returns:
            bool: True si tiene permisos, False caso contrario
        """
        try:
            if not self.session_manager.has_permission('admin'):
                messagebox.showerror(
                    "Acceso Denegado",
                    "Solo los administradores pueden acceder al historial de movimientos"
                )
                return False
            return True
            
        except Exception as e:
            logger.error(f"Error validando permisos: {e}")
            messagebox.showerror("Error", "Error validando permisos de usuario")
            return False
    
    def _setup_window(self):
        """Configurar ventana principal"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Historial de Movimientos - Copy Point S.A.")
        self.window.geometry("1200x700")
        self.window.resizable(True, True)
        self.window.grab_set()  # Modal
        
        # Centrar ventana
        self.window.transient(self.parent)
        self.window.protocol("WM_DELETE_WINDOW", self._close_form)
    
    def _create_ui_components(self):
        """Crear todos los componentes de la interfaz"""
        
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar peso de filas y columnas
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # 1. Panel de título
        self._create_title_panel(main_frame)
        
        # 2. Panel de búsqueda y filtros
        self._create_search_panel(main_frame)
        
        # 3. Panel de botones de acción
        self._create_action_panel(main_frame)
        
        # 4. Panel de resultados
        self._create_results_panel(main_frame)
        
        # 5. Panel de detalles (inferior)
        self._create_details_panel(main_frame)
    
    def _create_title_panel(self, parent):
        """Crear panel de título"""
        title_frame = ttk.LabelFrame(parent, text="", padding="5")
        title_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        title_label = ttk.Label(
            title_frame,
            text="HISTORIAL DE MOVIMIENTOS",
            font=('Arial', 14, 'bold')
        )
        title_label.pack()
    
    def _create_search_panel(self, parent):
        """Crear panel de búsqueda y filtros"""
        search_frame = ttk.LabelFrame(parent, text="Filtros de Búsqueda", padding="10")
        search_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)
        search_frame.columnconfigure(3, weight=1)
        
        # Fila 1: Rango de fechas
        ttk.Label(search_frame, text="Fecha Inicio:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.date_start_entry = ttk.Entry(search_frame, width=12)
        self.date_start_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 20))
        self.date_start_entry.insert(0, (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        
        ttk.Label(search_frame, text="Fecha Fin:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.date_end_entry = ttk.Entry(search_frame, width=12)
        self.date_end_entry.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=(0, 20))
        self.date_end_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        # Fila 2: Tipo de transacción y ticket
        ttk.Label(search_frame, text="Tipo Transacción:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        self.transaction_type_combo = ttk.Combobox(
            search_frame, 
            values=['TODOS', 'ENTRADA', 'AJUSTE', 'VENTA'],
            state='readonly',
            width=15
        )
        self.transaction_type_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 20), pady=(10, 0))
        self.transaction_type_combo.set('TODOS')
        
        ttk.Label(search_frame, text="Número Ticket:").grid(row=1, column=2, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        self.ticket_search_entry = ttk.Entry(search_frame, width=15)
        self.ticket_search_entry.grid(row=1, column=3, sticky=(tk.W, tk.E), padx=(0, 20), pady=(10, 0))
    
    def _create_action_panel(self, parent):
        """Crear panel de botones de acción"""
        action_frame = ttk.Frame(parent, padding="5")
        action_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Botones principales
        ttk.Button(
            action_frame,
            text="BUSCAR",
            command=self._search_movements,
            width=12
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            action_frame,
            text="LIMPIAR",
            command=self._clear_form,
            width=12
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            action_frame,
            text="EXPORTAR PDF",
            command=self._export_to_pdf,
            width=15
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            action_frame,
            text="EXPORTAR EXCEL",
            command=self._export_to_excel,
            width=15
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        # Botón cerrar a la derecha
        ttk.Button(
            action_frame,
            text="CERRAR",
            command=self._close_form,
            width=12
        ).pack(side=tk.RIGHT)
    
    def _create_results_panel(self, parent):
        """Crear panel de resultados con tabla"""
        results_frame = ttk.LabelFrame(parent, text="Resultados de Búsqueda", padding="10")
        results_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Crear Treeview con scrollbars
        tree_frame = ttk.Frame(results_frame)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Configurar columnas
        columns = ('ID', 'Fecha/Hora', 'Tipo', 'Ticket', 'Producto', 'Cantidad', 'Responsable', 'Observaciones')
        self.results_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Configurar encabezados
        self.results_tree.heading('ID', text='ID')
        self.results_tree.heading('Fecha/Hora', text='Fecha/Hora')
        self.results_tree.heading('Tipo', text='Tipo')
        self.results_tree.heading('Ticket', text='Ticket')
        self.results_tree.heading('Producto', text='Producto')
        self.results_tree.heading('Cantidad', text='Cantidad')
        self.results_tree.heading('Responsable', text='Responsable')
        self.results_tree.heading('Observaciones', text='Observaciones')
        
        # Configurar anchos de columna
        self.results_tree.column('ID', width=60, minwidth=50)
        self.results_tree.column('Fecha/Hora', width=130, minwidth=100)
        self.results_tree.column('Tipo', width=80, minwidth=70)
        self.results_tree.column('Ticket', width=100, minwidth=80)
        self.results_tree.column('Producto', width=200, minwidth=150)
        self.results_tree.column('Cantidad', width=80, minwidth=70)
        self.results_tree.column('Responsable', width=100, minwidth=80)
        self.results_tree.column('Observaciones', width=200, minwidth=150)
        
        # Posicionar Treeview
        self.results_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.results_tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.results_tree.xview)
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.results_tree.configure(xscrollcommand=h_scrollbar.set)
    
    def _create_details_panel(self, parent):
        """Crear panel de detalles del movimiento seleccionado"""
        details_frame = ttk.LabelFrame(parent, text="Detalles del Movimiento Seleccionado", padding="10")
        details_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        details_frame.columnconfigure(1, weight=1)
        details_frame.columnconfigure(3, weight=1)
        
        # Campos de detalles (readonly)
        ttk.Label(details_frame, text="ID Movimiento:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.detail_id_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.detail_id_var, state='readonly', width=15).grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 20))
        
        ttk.Label(details_frame, text="Producto ID:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.detail_product_id_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.detail_product_id_var, state='readonly', width=15).grid(
            row=0, column=3, sticky=(tk.W, tk.E))
        
        ttk.Label(details_frame, text="Observaciones:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        self.detail_obs_var = tk.StringVar()
        ttk.Entry(details_frame, textvariable=self.detail_obs_var, state='readonly').grid(
            row=1, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def _setup_bindings(self):
        """Configurar eventos y bindings"""
        # Evento selección en Treeview
        self.results_tree.bind('<<TreeviewSelect>>', self._on_tree_select)
        
        # Eventos de teclado para búsqueda rápida
        self.ticket_search_entry.bind('<Return>', lambda e: self._search_movements())
        
        # Bind para cerrar con Escape
        self.window.bind('<Escape>', lambda e: self._close_form())
    
    def _setup_styles(self):
        """Configurar estilos visuales"""
        style = ttk.Style()
        
        # Estilo para Treeview alternado
        style.configure('Treeview', rowheight=25)
        style.configure('Treeview.Heading', font=('Arial', 9, 'bold'))
    
    # ===============================
    # LAZY LOADING DE SERVICIOS
    # ===============================
    
    @property
    def container(self):
        """Lazy loading ServiceContainer"""
        if self._container is None:
            try:
                from services.service_container import get_container
                self._container = get_container()
            except Exception as e:
                logger.error(f"Error cargando ServiceContainer: {e}")
                raise
        return self._container
    
    @property
    def session_manager(self):
        """Lazy loading SessionManager"""
        if self._session_manager is None:
            try:
                self._session_manager = self.container.get('session_manager')
            except Exception as e:
                logger.error(f"Error cargando SessionManager: {e}")
                raise
        return self._session_manager
    
    @property
    def movement_service(self):
        """Lazy loading MovementService"""
        if self._movement_service is None:
            try:
                self._movement_service = self.container.get('movement_service')
            except Exception as e:
                logger.error(f"Error cargando MovementService: {e}")
                raise
        return self._movement_service
    
    @property
    def product_service(self):
        """Lazy loading ProductService"""
        if self._product_service is None:
            try:
                self._product_service = self.container.get('product_service')
            except Exception as e:
                logger.error(f"Error cargando ProductService: {e}")
                raise
        return self._product_service
    
    @property
    def export_service(self):
        """Lazy loading ExportService"""
        if self._export_service is None:
            try:
                self._export_service = self.container.get('export_service')
            except Exception as e:
                logger.error(f"Error cargando ExportService: {e}")
                raise
        return self._export_service
    
    # ===============================
    # MÉTODOS DE BÚSQUEDA Y FILTROS
    # ===============================
    
    def _search_movements(self):
        """Ejecutar búsqueda de movimientos con filtros aplicados"""
        try:
            # Limpiar resultados anteriores
            self._clear_results()
            
            # Obtener filtros
            filters = self._get_search_filters()
            
            # Validar filtros
            self._validate_filters(filters)
            
            # Ejecutar búsqueda
            if filters.get('ticket_number'):
                # Búsqueda específica por ticket
                movements = self._search_by_ticket(filters['ticket_number'])
            else:
                # Búsqueda general por filtros
                movements = self._search_by_filters(filters)
            
            # Mostrar resultados
            self._display_search_results(movements)
            
            logger.info(f"Búsqueda ejecutada: {len(movements)} movimientos encontrados")
            
        except ValueError as e:
            messagebox.showerror("Error de Validación", str(e))
        except Exception as e:
            logger.error(f"Error en búsqueda de movimientos: {e}")
            messagebox.showerror("Error", f"Error ejecutando búsqueda: {str(e)}")
    
    def _get_search_filters(self) -> Dict[str, Any]:
        """Obtener filtros de búsqueda desde la UI"""
        filters = {}
        
        # Fechas
        start_date_str = self.date_start_entry.get().strip()
        end_date_str = self.date_end_entry.get().strip()
        
        if start_date_str:
            filters['start_date'] = datetime.strptime(start_date_str, '%Y-%m-%d')
        if end_date_str:
            filters['end_date'] = datetime.strptime(end_date_str + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
        
        # Tipo de transacción
        transaction_type = self.transaction_type_combo.get()
        if transaction_type and transaction_type != 'TODOS':
            filters['transaction_type'] = transaction_type
        
        # Número de ticket
        ticket_number = self.ticket_search_entry.get().strip()
        if ticket_number:
            filters['ticket_number'] = self._sanitize_ticket_input(ticket_number)
        
        return filters
    
    def _validate_filters(self, filters: Dict[str, Any]):
        """Validar filtros de búsqueda"""
        # Validar rango de fechas
        if 'start_date' in filters and 'end_date' in filters:
            self._validate_date_range(filters['start_date'], filters['end_date'])
    
    def _validate_date_range(self, start_date: datetime, end_date: datetime):
        """Validar rango de fechas"""
        if start_date > end_date:
            raise ValueError("La fecha de inicio debe ser menor o igual a la fecha fin")
        
        # Validar rango máximo (1 año)
        if (end_date - start_date).days > 365:
            raise ValueError("El rango de fechas no puede exceder 1 año")
    
    def _sanitize_ticket_input(self, ticket_input: str) -> str:
        """Sanitizar entrada de búsqueda de ticket"""
        # Remover caracteres especiales, solo alfanuméricos
        return re.sub(r'[^a-zA-Z0-9]', '', ticket_input.upper())
    
    def _search_by_filters(self, filters: Dict[str, Any]) -> List[Any]:
        """Buscar movimientos por filtros generales"""
        try:
            return self.movement_service.get_movements_by_filters(filters)
        except Exception as e:
            logger.error(f"Error buscando por filtros: {e}")
            raise
    
    def _search_by_ticket(self, ticket_number: str) -> List[Any]:
        """Buscar movimiento por número de ticket específico"""
        try:
            movement = self.movement_service.get_movement_by_ticket(ticket_number)
            return [movement] if movement else []
        except Exception as e:
            logger.error(f"Error buscando por ticket: {e}")
            raise
    
    def _search_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Any]:
        """Buscar movimientos por rango de fechas"""
        filters = {'start_date': start_date, 'end_date': end_date}
        return self._search_by_filters(filters)
    
    def _search_by_transaction_type(self, transaction_type: str) -> List[Any]:
        """Buscar movimientos por tipo de transacción"""
        filters = {'transaction_type': transaction_type}
        return self._search_by_filters(filters)
    
    def _apply_combined_filters(self, filters: Dict[str, Any]) -> List[Any]:
        """Aplicar filtros combinados"""
        return self._search_by_filters(filters)
    
    # ===============================
    # MÉTODOS DE VISUALIZACIÓN
    # ===============================
    
    def _display_search_results(self, movements: List[Any]):
        """Mostrar resultados de búsqueda en la tabla"""
        # Limpiar tabla
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Guardar movimientos actuales
        self.current_movements = movements
        
        if not movements:
            # Mostrar mensaje de no resultados
            self.results_tree.insert('', 'end', values=(
                '', '', '', 'No se encontraron movimientos', '', '', '', ''
            ))
            return
        
        # Insertar movimientos
        for movement in movements:
            self.results_tree.insert('', 'end', values=(
                getattr(movement, 'id', ''),
                getattr(movement, 'movement_date', ''),
                getattr(movement, 'movement_type', ''),
                getattr(movement, 'ticket_number', ''),
                getattr(movement, 'product_name', ''),
                getattr(movement, 'quantity', ''),
                getattr(movement, 'responsible', ''),
                getattr(movement, 'observations', '')[:50] + '...' if len(getattr(movement, 'observations', '')) > 50 else getattr(movement, 'observations', '')
            ))
        
        # Mostrar contador de resultados
        self.window.title(f"Historial de Movimientos - {len(movements)} resultados encontrados")
    
    def _clear_results(self):
        """Limpiar resultados de búsqueda"""
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.current_movements = []
        self._clear_details()
    
    def _clear_details(self):
        """Limpiar panel de detalles"""
        self.detail_id_var.set('')
        self.detail_product_id_var.set('')
        self.detail_obs_var.set('')
        self.selected_movement = None
    
    def _on_tree_select(self, event):
        """Manejar selección en Treeview"""
        selection = self.results_tree.selection()
        if not selection:
            return
        
        # Obtener item seleccionado
        item = self.results_tree.item(selection[0])
        values = item['values']
        
        if not values or not values[0]:  # No hay datos válidos
            return
        
        # Buscar movimiento correspondiente
        movement_id = values[0]
        movement = self._find_movement_by_id(movement_id)
        
        if movement:
            self._on_movement_selected(movement)
    
    def _find_movement_by_id(self, movement_id: Any) -> Optional[Any]:
        """Buscar movimiento por ID en resultados actuales"""
        for movement in self.current_movements:
            if str(getattr(movement, 'id', '')) == str(movement_id):
                return movement
        return None
    
    def _on_movement_selected(self, movement: Any):
        """Mostrar detalles del movimiento seleccionado"""
        self.selected_movement = movement
        
        # Actualizar panel de detalles
        self.detail_id_var.set(getattr(movement, 'id', ''))
        self.detail_product_id_var.set(getattr(movement, 'product_id', ''))
        self.detail_obs_var.set(getattr(movement, 'observations', ''))
        
        logger.info(f"Movimiento seleccionado: ID {getattr(movement, 'id', '')}")
    
    # ===============================
    # MÉTODOS DE EXPORTACIÓN
    # ===============================
    
    def _export_to_pdf(self):
        """Exportar resultados actuales a PDF"""
        if not self.current_movements:
            messagebox.showwarning("Sin Datos", "No hay movimientos para exportar")
            return
        
        try:
            # Generar nombre de archivo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"historial_movimientos_{timestamp}.pdf"
            
            # Solicitar ubicación de guardado
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                initialname=filename,
                title="Guardar reporte PDF"
            )
            
            if not file_path:
                return
            
            # Exportar usando servicio
            pdf_data = self.export_service.export_movements_to_pdf(self.current_movements)
            
            # Guardar archivo
            with open(file_path, 'wb') as f:
                f.write(pdf_data)
            
            messagebox.showinfo("Exportación Exitosa", f"Reporte PDF guardado en:\n{file_path}")
            logger.info(f"Exportación PDF exitosa: {file_path}")
            
        except Exception as e:
            logger.error(f"Error exportando PDF: {e}")
            messagebox.showerror("Error de Exportación", f"Error exportando PDF: {str(e)}")
    
    def _export_to_excel(self):
        """Exportar resultados actuales a Excel"""
        if not self.current_movements:
            messagebox.showwarning("Sin Datos", "No hay movimientos para exportar")
            return
        
        try:
            # Generar nombre de archivo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"historial_movimientos_{timestamp}.xlsx"
            
            # Solicitar ubicación de guardado
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialname=filename,
                title="Guardar reporte Excel"
            )
            
            if not file_path:
                return
            
            # Exportar usando servicio
            excel_data = self.export_service.export_movements_to_excel(self.current_movements)
            
            # Guardar archivo
            with open(file_path, 'wb') as f:
                f.write(excel_data)
            
            messagebox.showinfo("Exportación Exitosa", f"Reporte Excel guardado en:\n{file_path}")
            logger.info(f"Exportación Excel exitosa: {file_path}")
            
        except Exception as e:
            logger.error(f"Error exportando Excel: {e}")
            messagebox.showerror("Error de Exportación", f"Error exportando Excel: {str(e)}")
    
    # ===============================
    # MÉTODOS DE FORMULARIO
    # ===============================
    
    def _clear_form(self):
        """Limpiar todos los campos del formulario"""
        # Limpiar filtros
        self.date_start_entry.delete(0, tk.END)
        self.date_start_entry.insert(0, (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        
        self.date_end_entry.delete(0, tk.END)
        self.date_end_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        self.transaction_type_combo.set('TODOS')
        self.ticket_search_entry.delete(0, tk.END)
        
        # Limpiar resultados y detalles
        self._clear_results()
        
        # Restaurar título
        self.window.title("Historial de Movimientos - Copy Point S.A.")
        
        logger.info("Formulario limpiado")
    
    def _close_form(self):
        """Cerrar formulario con limpieza"""
        try:
            # Limpiar estado
            self.current_movements = None
            self.selected_movement = None
            
            # Cerrar ventana
            if self.window:
                self.window.destroy()
                
            logger.info("MovementHistoryForm cerrado correctamente")
            
        except Exception as e:
            logger.error(f"Error cerrando formulario: {e}")
    
    def show(self):
        """Mostrar el formulario"""
        if self.window:
            self.window.deiconify()
            self.window.lift()
            self.window.focus_set()
    
    def destroy(self):
        """Destruir el formulario"""
        self._close_form()


# Funciones de utilidad para compatibilidad con tests
def create_movement_history_form(parent, db_connection):
    """Factory function para crear MovementHistoryForm"""
    return MovementHistoryForm(parent, db_connection)


if __name__ == "__main__":
    # Test básico del formulario
    root = tk.Tk()
    root.withdraw()
    
    # Mock database connection
    mock_db = type('MockDB', (), {})()
    
    try:
        form = MovementHistoryForm(root, mock_db)
        if form.window:
            form.show()
            root.mainloop()
    except Exception as e:
        print(f"Error en test: {e}")
    finally:
        root.destroy()
