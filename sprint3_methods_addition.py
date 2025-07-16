"""
MÉTODOS ADICIONALES PARA SPRINT 3 - PANEL PRODUCTOS MÚLTIPLES
Agregar estos métodos a la clase MovementForm en movement_form.py
"""

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

def _clear_barcode_field(self):
    """Limpiar campo de código de barras - SPRINT 3."""
    self.barcode_var.set("")
    self.barcode_status_label.config(
        text="Esperando código...",
        foreground="gray"
    )
    self.barcode_entry.focus()
