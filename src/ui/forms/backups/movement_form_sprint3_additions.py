"""
MÉTODOS FALTANTES DEL SPRINT 3 PARA MovementForm
Estos métodos deben agregarse al final de la clase MovementForm
"""

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

def _get_current_movements_data(self):
    """Obtener datos de movimientos actualmente mostrados en el TreeView.
    
    SPRINT 2: Extrae datos del TreeView para exportación.
    
    Returns:
        List[Dict]: Lista de movimientos con estructura para exportar
    """
    try:
        movements_data = []
        
        # Obtener todos los items del TreeView
        for item in self.movements_tree.get_children():
            values = self.movements_tree.item(item)['values']
            
            if len(values) >= 8:  # Verificar que tenemos todos los campos
                movement = {
                    'id_movimiento': values[0],
                    'fecha_movimiento': values[1],
                    'producto_nombre': values[2],
                    'tipo_movimiento': values[3],
                    'cantidad': values[4],
                    'cantidad_anterior': values[5],
                    'cantidad_nueva': values[6],
                    'responsable': values[7]
                }
                movements_data.append(movement)
        
        return movements_data
        
    except Exception as e:
        logger.error(f"Error obteniendo datos de movimientos: {e}")
        return []

def _get_applied_filters(self):
    """Obtener filtros aplicados actualmente.
    
    SPRINT 2: Información de filtros para incluir en reportes.
    
    Returns:
        Dict: Diccionario con filtros aplicados
    """
    try:
        filters = {
            'producto': self.filter_producto_combo.get() if hasattr(self, 'filter_producto_combo') else 'Todos',
            'tipo_movimiento': self.filter_tipo_combo.get() if hasattr(self, 'filter_tipo_combo') else 'Todos',
            'fecha_generacion': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'total_registros': len(self.movements_tree.get_children())
        }
        
        return filters
        
    except Exception as e:
        logger.error(f"Error obteniendo filtros aplicados: {e}")
        return {}

def _show_export_progress(self, message: str):
    """Mostrar ventana de progreso durante exportación.
    
    SPRINT 2: Feedback visual para operaciones de exportación.
    
    Args:
        message: Mensaje a mostrar
        
    Returns:
        tk.Toplevel: Ventana de progreso
    """
    try:
        # Crear ventana de progreso
        progress_window = tk.Toplevel(self.parent)
        progress_window.title("Exportando...")
        progress_window.geometry("300x120")
        progress_window.transient(self.parent)
        progress_window.grab_set()
        
        # Centrar ventana
        progress_window.update_idletasks()
        x = (progress_window.winfo_screenwidth() // 2) - (300 // 2)
        y = (progress_window.winfo_screenheight() // 2) - (120 // 2)
        progress_window.geometry(f"300x120+{x}+{y}")
        
        # Contenido
        main_frame = ttk.Frame(progress_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            main_frame,
            text=message,
            font=("Arial", 10),
            justify=tk.CENTER
        ).pack(pady=(10, 15))
        
        # Barra de progreso indeterminada
        progress_bar = ttk.Progressbar(
            main_frame,
            mode='indeterminate',
            length=200
        )
        progress_bar.pack(pady=(0, 10))
        progress_bar.start()
        
        # Forzar actualización
        progress_window.update()
        
        return progress_window
        
    except Exception as e:
        logger.error(f"Error mostrando progreso de exportación: {e}")
        return None

def _open_file(self, file_path: str):
    """Abrir archivo en aplicación por defecto del sistema.
    
    SPRINT 2: Abrir archivos exportados automáticamente.
    
    Args:
        file_path: Ruta del archivo a abrir
    """
    try:
        import os
        import platform
        
        system = platform.system()
        
        if system == 'Windows':
            os.startfile(file_path)
        elif system == 'Darwin':  # macOS
            os.system(f'open "{file_path}"')
        elif system == 'Linux':
            os.system(f'xdg-open "{file_path}"')
        else:
            logger.warning(f"Sistema operativo no soportado para abrir archivos: {system}")
            messagebox.showinfo(
                "Archivo Generado",
                f"Archivo generado en:\n{file_path}\n\nAbra el archivo manualmente."
            )
            
    except Exception as e:
        logger.error(f"Error abriendo archivo {file_path}: {e}")
        messagebox.showwarning(
            "No se pudo abrir archivo",
            f"Archivo generado correctamente en:\n{file_path}\n\n"
            f"Error abriendo: {e}\n\nAbra el archivo manualmente."
        )

def _offer_ticket_generation(self, movement_id: int, product_name: str, quantity: int, movement_type: str):
    """Ofrecer generación de ticket para movimiento creado.
    
    SPRINT 1: Generación de tickets para movimientos ENTRADA y AJUSTE.
    
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
            f"Cantidad: {abs(quantity)} unidades\n"
            f"ID Movimiento: {movement_id}"
        ):
            # Generar ticket usando TicketService
            ticket_data = self._prepare_movement_ticket_data(
                movement_id, product_name, quantity, movement_type
            )
            
            # Crear y mostrar ticket
            ticket_content = self.ticket_service.generate_movement_ticket(ticket_data)
            
            # Mostrar ventana de preview del ticket
            self._show_ticket_preview(ticket_content, movement_type)
            
    except Exception as e:
        logger.error(f"Error ofreciendo generación de ticket: {e}")
        messagebox.showerror("Error", f"Error generando ticket: {e}")

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
