"""
ProductSearchWidget - Widget reutilizable para búsqueda de productos
Implementa funcionalidad común de búsqueda con código de barras
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Callable, Optional
import logging

from utils.logger import get_logger


class ProductSearchWidget(ttk.Frame):
    """
    Widget reutilizable para búsqueda de productos
    
    Características:
    - Búsqueda por ID o nombre
    - Soporte código de barras
    - Validación en tiempo real
    - Eventos customizables
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
        
        # Estado del widget
        self.current_results: List[Dict] = []
        self.selected_product: Optional[Dict] = None
        
        # Callbacks
        self.on_product_selected: Optional[Callable] = None
        self.on_search_completed: Optional[Callable] = None
        
        # Crear interfaz
        self._create_interface()
        self._setup_bindings()

    def _create_interface(self):
        """Crear interfaz del widget"""
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
        self.search_button.grid(row=0, column=2, padx=5)
        
        # Lista de resultados
        self.results_listbox = tk.Listbox(
            self,
            height=6
        )
        self.results_listbox.grid(
            row=1, column=0, columnspan=3, 
            sticky="ew", pady=5
        )
        
        # Label para producto seleccionado
        self.selected_label = ttk.Label(
            self,
            text="Ningún producto seleccionado",
            foreground="gray"
        )
        self.selected_label.grid(
            row=2, column=0, columnspan=3,
            sticky="w", pady=5
        )

    def _setup_bindings(self):
        """Configurar eventos"""
        # Enter en búsqueda
        self.search_entry.bind("<Return>", lambda e: self._perform_search())
        
        # Selección en listbox
        self.results_listbox.bind("<<ListboxSelect>>", self._on_selection_change)
        
        # Doble click
        self.results_listbox.bind("<Double-Button-1>", self._on_double_click)
        
        # Validación en tiempo real
        self.search_var.trace("w", self._on_search_change)

    def _perform_search(self):
        """Ejecutar búsqueda de productos"""
        search_term = self.search_var.get().strip()
        
        if not search_term:
            return
            
        try:
            results = self.product_service.search_products(search_term)
            self._update_results(results)
            
            if self.on_search_completed:
                self.on_search_completed(results)
                
            self.logger.info(f"Búsqueda completada: {len(results)} productos")
            
        except Exception as e:
            self.logger.error(f"Error en búsqueda: {e}")
            self._update_results([])

    def _update_results(self, results: List[Dict]):
        """
        Actualizar lista de resultados
        
        Args:
            results: Lista de productos encontrados
        """
        self.current_results = results
        
        # Limpiar listbox
        self.results_listbox.delete(0, tk.END)
        
        # Agregar resultados
        for product in results:
            display_text = f"{product['id']} - {product['nombre']}"
            if 'stock' in product:
                display_text += f" (Stock: {product['stock']})"
            self.results_listbox.insert(tk.END, display_text)

    def _on_selection_change(self, event):
        """Manejar cambio de selección"""
        selection = self.results_listbox.curselection()
        
        if selection:
            index = selection[0]
            self.selected_product = self.current_results[index]
            
            # Actualizar label
            self.selected_label.config(
                text=f"Seleccionado: {self.selected_product['nombre']}",
                foreground="black"
            )
            
            # Callback
            if self.on_product_selected:
                self.on_product_selected(self.selected_product)
        else:
            self.selected_product = None
            self.selected_label.config(
                text="Ningún producto seleccionado",
                foreground="gray"
            )

    def _on_double_click(self, event):
        """Manejar doble click en resultado"""
        # Trigger selección adicional si hay callback
        if self.selected_product and self.on_product_selected:
            self.on_product_selected(self.selected_product, double_click=True)

    def _on_search_change(self, *args):
        """Manejar cambios en campo de búsqueda"""
        search_term = self.search_var.get()
        
        # Auto-búsqueda si es código numérico (código de barras/ID)
        if search_term.isdigit() and len(search_term) >= 3:
            self._perform_search()

    def get_selected_product(self) -> Optional[Dict]:
        """
        Obtener producto seleccionado
        
        Returns:
            Dict: Producto seleccionado o None
        """
        return self.selected_product

    def clear_selection(self):
        """Limpiar selección actual"""
        self.search_var.set("")
        self.results_listbox.delete(0, tk.END)
        self.selected_product = None
        self.current_results.clear()
        
        self.selected_label.config(
            text="Ningún producto seleccionado",
            foreground="gray"
        )

    def set_focus(self):
        """Establecer foco en campo de búsqueda"""
        self.search_entry.focus()

    def set_search_term(self, term: str):
        """
        Establecer término de búsqueda y ejecutar
        
        Args:
            term: Término a buscar
        """
        self.search_var.set(term)
        self._perform_search()
