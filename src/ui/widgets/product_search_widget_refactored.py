"""
ProductSearchWidget - Widget reutilizable para búsqueda de productos (REFACTORIZADO)
Implementa comunicación vía Event Bus para eliminar dependencias circulares

CAMBIOS ARQUITECTÓNICOS:
- Eliminados callbacks directos (on_product_selected, on_search_completed, on_focus_quantity)
- Implementada comunicación vía Event Bus pattern
- Desacoplamiento completo de componentes padre
- Mantenida funcionalidad optimizada existente
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional
import logging

from utils.logger import get_logger
from patterns.event_bus import get_event_bus, InventoryEvents


class ProductSearchWidget(ttk.Frame):
    """
    Widget reutilizable para búsqueda de productos - REFACTORIZADO con Event Bus
    
    Características:
    - Búsqueda por ID o nombre
    - Soporte código de barras
    - Validación en tiempo real
    - Comunicación vía Event Bus (sin callbacks directos)
    - Auto-selección para resultados únicos
    - Botón "Borrar Código" para flujo optimizado
    """

    def __init__(self, parent: tk.Widget, product_service, **kwargs):
        """
        Inicializar widget de búsqueda de productos
        
        Args:
            parent: Widget padre
            product_service: Servicio de productos
            **kwargs: Argumentos adicionales
        """
        super().__init__(parent, **kwargs)
        
        self.product_service = product_service
        self.logger = get_logger(__name__)
        self.event_bus = get_event_bus()
        
        # Estado del widget
        self.current_results: List[Dict] = []
        self.selected_product: Optional[Dict] = None
        
        # REFACTOR: Eliminados callbacks directos, ahora usa Event Bus
        # self.on_product_selected = None (REMOVIDO)
        # self.on_search_completed = None (REMOVIDO)
        # self.on_focus_quantity = None (REMOVIDO)
        
        # Crear interfaz
        self._create_interface()
        self._setup_bindings()
        
        self.logger.info("ProductSearchWidget refactorizado con Event Bus inicializado")

    def _create_interface(self):
        """Crear interfaz del widget (mantenida igual)"""
        # Configurar grid
        self.grid_columnconfigure(1, weight=1)
        
        # Campo de búsqueda
        ttk.Label(self, text="Buscar:").grid(
            row=0, column=0, sticky="w", padx=5
        )
        
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(
            self,
            textvariable=self.search_var,
            width=40
        )
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=5)
        
        # Botón búsqueda
        self.search_button = ttk.Button(
            self,
            text="Buscar",
            command=self._perform_search
        )
        self.search_button.grid(row=0, column=2, padx=2)
        
        # Botón borrar código - FUNCIONALIDAD MANTENIDA
        self.clear_code_button = ttk.Button(
            self,
            text="Borrar Código",
            command=self._clear_code_and_selection,
            style="Toolbutton"
        )
        self.clear_code_button.grid(row=0, column=3, padx=2)
        
        # Lista de resultados
        self.results_listbox = tk.Listbox(
            self,
            height=6
        )
        self.results_listbox.grid(
            row=1, column=0, columnspan=4, 
            sticky="ew", pady=5
        )
        
        # Label para producto seleccionado
        self.selected_label = ttk.Label(
            self,
            text="Ningún producto seleccionado",
            foreground="gray"
        )
        self.selected_label.grid(
            row=2, column=0, columnspan=4,
            sticky="w", pady=5
        )

    def _setup_bindings(self):
        """Configurar eventos (mantenida igual)"""
        # Enter en búsqueda
        self.search_entry.bind("<Return>", lambda e: self._perform_search())
        
        # Selección en listbox
        self.results_listbox.bind("<<ListboxSelect>>", self._on_selection_change)
        
        # Doble click
        self.results_listbox.bind("<Double-Button-1>", self._on_double_click)
        
        # Validación en tiempo real
        self.search_var.trace("w", self._on_search_change)

    def _perform_search(self):
        """
        Ejecutar búsqueda de productos - REFACTORIZADO con Event Bus
        """
        search_term = self.search_var.get().strip()
        
        if not search_term:
            return
            
        try:
            results = self.product_service.search_products(search_term)
            self._update_results_optimized(results)
            
            # REFACTOR: Usar Event Bus en lugar de callback directo
            self.event_bus.publish(InventoryEvents.PRODUCT_SEARCH_COMPLETED, {
                'search_term': search_term,
                'results': results,
                'widget_id': id(self)
            })
            
            self.logger.info(f"Búsqueda completada: {len(results)} productos")
            
        except Exception as e:
            self.logger.error(f"Error en búsqueda: {e}")
            self._update_results_optimized([])
            
            # Emitir evento de error
            self.event_bus.publish(InventoryEvents.PRODUCT_SEARCH_FAILED, {
                'search_term': search_term,
                'error': str(e),
                'widget_id': id(self)
            })

    def on_enter_code(self, code: str):
        """
        Procesar código introducido (manual o por lector) - REFACTORIZADO
        """
        try:
            # Buscar productos por código
            results = self.product_service.buscar_por_codigo(code)
            
            # Usar flujo optimizado para auto-selección
            self._update_results_optimized(results)
            
            # REFACTOR: Usar Event Bus
            self.event_bus.publish(InventoryEvents.PRODUCT_SEARCH_COMPLETED, {
                'search_term': code,
                'results': results,
                'search_type': 'code_entry',
                'widget_id': id(self)
            })
            
            self.logger.info(f"Código procesado: {code}, resultados: {len(results)}")
                
        except Exception as e:
            self.logger.error(f"Error procesando código {code}: {e}")
            self._update_results_optimized([])
            
            self.event_bus.publish(InventoryEvents.PRODUCT_SEARCH_FAILED, {
                'search_term': code,
                'error': str(e),
                'search_type': 'code_entry',
                'widget_id': id(self)
            })

    def _update_results_optimized(self, results: List[Dict]):
        """
        Actualizar lista de resultados con selección automática optimizada - REFACTORIZADO
        
        MANTIENE: Funcionalidad de auto-selección optimizada
        REFACTOR: Comunicación vía Event Bus
        
        Args:
            results: Lista de productos encontrados
        """
        self.logger.info(f"DEBUGGING _update_results_optimized (Event Bus):")
        self.logger.info(f"  - results count: {len(results)}")
        
        self.current_results = results
        
        # Limpiar listbox
        self.results_listbox.delete(0, tk.END)
        
        if not results:
            # Sin resultados
            self.selected_product = None
            self.selected_label.config(
                text="No se encontraron productos",
                foreground="red"
            )
            self.logger.info(f"  - Sin resultados, selected_product = None")
            return
        
        # Agregar resultados al listbox
        for product in results:
            display_text = f"{product['id']} - {product['nombre']}"
            if 'stock' in product:
                display_text += f" (Stock: {product['stock']})"
            self.results_listbox.insert(tk.END, display_text)
        
        # OPTIMIZACIÓN MANTENIDA: Selección automática para resultado único
        if len(results) == 1:
            self.logger.info(f"  - Un solo resultado: iniciando auto-selección via Event Bus")
            
            # Selección automática INMEDIATA
            self.results_listbox.selection_set(0)
            self.selected_product = results[0]
            
            # Actualizar label
            self.selected_label.config(
                text=f"✓ Auto-seleccionado: {self.selected_product['nombre']}",
                foreground="blue"
            )
            
            # REFACTOR: Emitir via Event Bus en lugar de callbacks directos
            self._emit_product_selection_event(self.selected_product, auto_selected=True)
            self._emit_quantity_focus_event()
            
            self.logger.info(f"Producto auto-seleccionado via Event Bus: {self.selected_product['nombre']}")
        
        else:
            # Múltiples resultados: mostrar para selección manual
            self.selected_product = None
            self.selected_label.config(
                text=f"Encontrados {len(results)} productos - seleccione uno",
                foreground="orange"
            )
            self.logger.info(f"  - Múltiples resultados, selected_product = None")

    def _on_selection_change(self, event):
        """
        Manejar cambio de selección - REFACTORIZADO con Event Bus
        """
        selection = self.results_listbox.curselection()
        
        if selection:
            index = selection[0]
            self.selected_product = self.current_results[index]
            
            # Actualizar label
            self.selected_label.config(
                text=f"Seleccionado: {self.selected_product['nombre']}",
                foreground="black"
            )
            
            # REFACTOR: Emitir evento en lugar de callback directo
            self._emit_product_selection_event(self.selected_product, auto_selected=False)
            
            # OPTIMIZACIÓN MANTENIDA: Pasar foco a cantidad después de selección
            self._emit_quantity_focus_event()
        else:
            self.selected_product = None
            self.selected_label.config(
                text="Ningún producto seleccionado",
                foreground="gray"
            )

    def _on_double_click(self, event):
        """
        Manejar doble click en resultado - REFACTORIZADO
        """
        if self.selected_product:
            # Emitir evento especial para doble click
            self.event_bus.publish(InventoryEvents.PRODUCT_SELECTED, {
                'product': self.selected_product,
                'interaction_type': 'double_click',
                'widget_id': id(self)
            })

    def _on_search_change(self, *args):
        """
        Manejar cambios en campo de búsqueda - FUNCIONALIDAD MANTENIDA
        """
        search_term = self.search_var.get()
        
        # Auto-búsqueda si es código numérico (código de barras/ID)
        if search_term.isdigit() and len(search_term) >= 3:
            self.on_enter_code(search_term)

    def _clear_code_and_selection(self):
        """
        Limpiar código y selección para nueva búsqueda - REFACTORIZADO con Event Bus
        
        MANTIENE: Funcionalidad de limpieza optimizada
        REFACTOR: Emite evento de limpieza
        """
        # Limpiar completamente el estado
        self.search_var.set("")
        self.results_listbox.delete(0, tk.END)
        self.selected_product = None
        self.current_results.clear()
        
        # Resetear label
        self.selected_label.config(
            text="Ningún producto seleccionado",
            foreground="gray"
        )
        
        # Regresar foco al campo de búsqueda
        self.search_entry.focus()
        
        # REFACTOR: Emitir evento de limpieza
        self.event_bus.publish(InventoryEvents.SEARCH_FIELD_FOCUSED, {
            'action': 'search_cleared',
            'widget_id': id(self)
        })
        
        self.logger.info("Código y selección limpiados - evento emitido via Event Bus")

    # NUEVOS MÉTODOS PARA COMUNICACIÓN VIA EVENT BUS
    
    def _emit_product_selection_event(self, product: Dict, auto_selected: bool = False):
        """
        Emitir evento de selección de producto via Event Bus
        
        Args:
            product: Producto seleccionado
            auto_selected: Si fue auto-seleccionado
        """
        event_type = (InventoryEvents.PRODUCT_AUTO_SELECTED if auto_selected 
                     else InventoryEvents.PRODUCT_SELECTED)
        
        self.event_bus.publish(event_type, {
            'product': product,
            'auto_selected': auto_selected,
            'widget_id': id(self),
            'timestamp': self._get_timestamp()
        })
        
        self.logger.debug(f"Evento de selección emitido: {event_type}")
    
    def _emit_quantity_focus_event(self):
        """Emitir evento para solicitar foco en cantidad"""
        self.event_bus.publish(InventoryEvents.QUANTITY_FOCUS_REQUESTED, {
            'product': self.selected_product,
            'widget_id': id(self),
            'timestamp': self._get_timestamp()
        })
        
        self.logger.debug("Evento de foco en cantidad emitido")
    
    def _get_timestamp(self):
        """Obtener timestamp actual"""
        from datetime import datetime
        return datetime.now()

    # MÉTODOS PÚBLICOS MANTENIDOS PARA COMPATIBILIDAD
    
    def get_selected_product(self) -> Optional[Dict]:
        """
        Obtener producto seleccionado (API mantenida)
        
        Returns:
            Dict: Producto seleccionado o None
        """
        return self.selected_product

    def clear_selection(self):
        """Limpiar selección actual (API mantenida)"""
        self._clear_code_and_selection()

    def set_focus(self):
        """Establecer foco en campo de búsqueda (API mantenida)"""
        self.search_entry.focus()
        
        # Emitir evento
        self.event_bus.publish(InventoryEvents.SEARCH_FIELD_FOCUSED, {
            'action': 'focus_requested',
            'widget_id': id(self)
        })

    def set_search_term(self, term: str):
        """
        Establecer término de búsqueda y ejecutar (API mantenida)
        
        Args:
            term: Término a buscar
        """
        self.search_var.set(term)
        self._perform_search()
