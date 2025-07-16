    def export_movements_to_pdf(self):
        """Exportar movimientos actuales a PDF.
        
        SPRINT 2: Exportación con diseño profesional y resumen ejecutivo.
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
        """Obtener datos de movimientos actualmente mostrados en el TreeView.
        
        SPRINT 2: Extrae los datos del TreeView para exportación.
        
        Returns:
            Lista de diccionarios con datos de movimientos
        """
        try:
            movements_data = []
            
            # Iterar sobre elementos del TreeView
            for item in self.movements_tree.get_children():
                values = self.movements_tree.item(item)['values']
                
                # Extraer valores según columnas definidas
                # Columnas: ('ID', 'Fecha', 'Producto', 'Tipo', 'Cantidad', 'Stock Ant.', 'Stock Nuevo', 'Responsable')
                movement_dict = {
                    'id_movimiento': values[0],
                    'fecha_movimiento': values[1],
                    'producto_nombre': values[2],
                    'tipo_movimiento': values[3],
                    'cantidad': values[4],
                    'cantidad_anterior': values[5] if len(values) > 5 else '',
                    'cantidad_nueva': values[6] if len(values) > 6 else '',
                    'responsable': values[7] if len(values) > 7 else ''
                }
                
                movements_data.append(movement_dict)
            
            logger.debug(f"Datos extraídos del TreeView: {len(movements_data)} movimientos")
            return movements_data
            
        except Exception as e:
            logger.error(f"Error extrayendo datos del TreeView: {e}")
            return []
    
    def _get_applied_filters(self) -> Dict[str, str]:
        """Obtener filtros actualmente aplicados en el formulario.
        
        SPRINT 2: Información de filtros para incluir en la exportación.
        
        Returns:
            Diccionario con filtros aplicados
        """
        try:
            filters = {
                'producto_filter': self.filter_producto_combo.get() if hasattr(self, 'filter_producto_combo') else 'Todos',
                'tipo_filter': self.filter_tipo_combo.get() if hasattr(self, 'filter_tipo_combo') else 'Todos',
                'timestamp': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            }
            
            # Filtros adicionales del contexto
            current_user = session_manager.get_current_user()
            if current_user:
                filters['generated_by'] = current_user.get('nombre_usuario', 'Usuario')
            else:
                filters['generated_by'] = 'Sistema'
            
            return filters
            
        except Exception as e:
            logger.error(f"Error obteniendo filtros aplicados: {e}")
            return {'producto_filter': 'Todos', 'tipo_filter': 'Todos'}
    
    def _show_export_progress(self, message: str) -> tk.Toplevel:
        """Mostrar ventana de progreso durante exportación.
        
        SPRINT 2: Indicador visual durante procesos de exportación.
        
        Args:
            message: Mensaje a mostrar
            
        Returns:
            Ventana de progreso
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
            
            # Deshabilitar redimensionamiento
            progress_window.resizable(False, False)
            
            # Crear contenido
            main_frame = ttk.Frame(progress_window, padding=20)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Etiqueta de mensaje
            message_label = ttk.Label(
                main_frame,
                text=message,
                font=("Arial", 10),
                justify=tk.CENTER
            )
            message_label.pack(pady=(0, 10))
            
            # Barra de progreso indeterminada
            progress_bar = ttk.Progressbar(
                main_frame,
                mode='indeterminate',
                length=200
            )
            progress_bar.pack(pady=(0, 10))
            progress_bar.start(10)
            
            # Etiqueta de estado
            status_label = ttk.Label(
                main_frame,
                text="Generando archivo...",
                font=("Arial", 8),
                foreground="gray"
            )
            status_label.pack()
            
            # Actualizar ventana
            progress_window.update_idletasks()
            
            return progress_window
            
        except Exception as e:
            logger.error(f"Error creando ventana de progreso: {e}")
            # Retornar una ventana simple si hay problemas
            simple_window = tk.Toplevel(self.parent)
            simple_window.title("Procesando...")
            simple_window.geometry("200x80")
            ttk.Label(simple_window, text=message).pack(pady=20)
            return simple_window
    
    def _open_file(self, file_path: str):
        """Abrir archivo con aplicación predeterminada del sistema.
        
        SPRINT 2: Abre archivos exportados para visualización inmediata.
        
        Args:
            file_path: Ruta del archivo a abrir
        """
        try:
            import os
            import platform
            import subprocess
            
            # Verificar que el archivo existe
            if not os.path.exists(file_path):
                messagebox.showerror(
                    "Archivo No Encontrado",
                    f"El archivo no se encuentra en la ruta especificada:\n{file_path}"
                )
                return
            
            # Abrir archivo según el sistema operativo
            system = platform.system()
            
            if system == "Windows":
                os.startfile(file_path)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", file_path])
            else:  # Linux y otros
                subprocess.run(["xdg-open", file_path])
            
            logger.info(f"Archivo abierto exitosamente: {file_path}")
            
        except Exception as e:
            logger.error(f"Error abriendo archivo {file_path}: {e}")
            messagebox.showerror(
                "Error Abriendo Archivo",
                f"No se pudo abrir el archivo:\n{e}\n\n"
                f"Ruta: {file_path}"
            )
    
    def _offer_ticket_generation(self, movement_id: int, product_name: str, quantity: int, movement_type: str):
        """Ofrecer generación de ticket para movimiento creado.
        
        SPRINT 1: Generación opcional de tickets para movimientos de inventario.
        
        Args:
            movement_id: ID del movimiento creado
            product_name: Nombre del producto
            quantity: Cantidad del movimiento
            movement_type: Tipo de movimiento (ENTRADA/AJUSTE)
        """
        try:
            # Solo ofrecer tickets para movimientos de inventario (no VENTA)
            if movement_type not in ['ENTRADA', 'AJUSTE']:
                return
            
            # Preguntar si generar ticket
            generate_ticket = messagebox.askyesno(
                "Generar Ticket",
                f"¿Desea generar un ticket para este movimiento?\n\n"
                f"Tipo: {movement_type}\n"
                f"Producto: {product_name}\n"
                f"Cantidad: {quantity} unidades\n"
                f"ID Movimiento: {movement_id}"
            )
            
            if generate_ticket:
                self._generate_movement_ticket(movement_id, movement_type)
                
        except Exception as e:
            logger.error(f"Error ofreciendo generación de ticket: {e}")
    
    def _generate_movement_ticket(self, movement_id: int, movement_type: str):
        """Generar ticket para movimiento de inventario.
        
        SPRINT 1: Generación de tickets para ENTRADA y AJUSTE.
        
        Args:
            movement_id: ID del movimiento
            movement_type: Tipo de movimiento
        """
        try:
            # Usar TicketService para generar ticket
            if movement_type == 'ENTRADA':
                ticket_data = self.ticket_service.generate_entrada_ticket(movement_id)
            elif movement_type == 'AJUSTE':
                ticket_data = self.ticket_service.generate_ajuste_ticket(movement_id)
            else:
                logger.warning(f"Tipo de movimiento no soportado para tickets: {movement_type}")
                return
            
            # Mostrar ticket generado
            if ticket_data:
                messagebox.showinfo(
                    "Ticket Generado",
                    f"Ticket generado exitosamente\n\n"
                    f"Número de ticket: {ticket_data.get('numero_ticket', 'N/A')}\n"
                    f"Tipo: {movement_type}\n"
                    f"Archivo: {ticket_data.get('file_path', 'N/A')}"
                )
                
                # Preguntar si abrir ticket
                if ticket_data.get('file_path') and messagebox.askyesno(
                    "Abrir Ticket",
                    "¿Desea abrir el ticket generado?"
                ):
                    self._open_file(ticket_data['file_path'])
            else:
                messagebox.showwarning(
                    "Error en Ticket",
                    "No se pudo generar el ticket. Verifique la configuración del sistema."
                )
                
        except Exception as e:
            logger.error(f"Error generando ticket para movimiento {movement_id}: {e}")
            messagebox.showerror(
                "Error de Ticket",
                f"No se pudo generar el ticket:\n{e}"
            )
