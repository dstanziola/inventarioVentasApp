"""
Formulario de configuración de códigos de barras.

Este formulario permite configurar dispositivos de hardware para códigos de barras:
- Detección automática de dispositivos
- Configuración de lectores
- Configuración de impresoras
- Pruebas de conectividad
- Gestión de templates de etiquetas

Autor: Sistema de Inventario Copy Point S.A.
Fecha: Junio 2025
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime

# Importaciones del sistema
from src.utils.hardware_detector import get_hardware_detector, DeviceInfo
from services.label_service import get_label_service
from ui.utils.window_manager import center_window

# Configurar logging
logger = logging.getLogger(__name__)


class BarcodeConfigForm:
    """
    Formulario para configuración de códigos de barras.
    
    Permite gestionar todos los aspectos de configuración de hardware
    y software relacionados con códigos de barras.
    """
    
    def __init__(self, parent=None):
        """
        Inicializar el formulario de configuración.
        
        Args:
            parent: Ventana padre (opcional)
        """
        self.parent = parent
        self.window = None
        self.hardware_detector = get_hardware_detector()
        self.label_service = get_label_service()
        
        # Variables de estado
        self.scanning_devices = False
        self.devices_list = []
        self.selected_scanner = None
        self.selected_printer = None
        
        # Variables del formulario
        self.var_auto_scan = tk.BooleanVar(value=True)
        self.var_scanner_enabled = tk.BooleanVar(value=True)
        self.var_printer_enabled = tk.BooleanVar(value=True)
        self.var_auto_configure = tk.BooleanVar(value=True)
        
        self._create_window()
        self._setup_ui()
        self._bind_events()
        
        # Iniciar escaneo automático
        self._start_device_scan()
        
        logger.info("BarcodeConfigForm inicializado")
    
    def _create_window(self):
        """Crear y configurar la ventana principal."""
        self.window = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.window.title("Configuración de Códigos de Barras - Copy Point S.A.")
        self.window.geometry("900x700")
        self.window.resizable(True, True)
        
        # Configurar icono si existe
        try:
            self.window.iconbitmap("assets/icon.ico")
        except:
            pass
        
        # Centrar ventana
        center_window(self.window, 900, 700)
        
        # Hacer modal si tiene padre
        if self.parent:
            self.window.transient(self.parent)
            self.window.grab_set()
        
        # Manejar cierre de ventana
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _setup_ui(self):
        """Configurar la interfaz de usuario."""
        # Frame principal con scrollbar
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Crear notebook para pestañas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Pestañas
        self._create_devices_tab()
        self._create_scanner_tab()
        self._create_printer_tab()
        self._create_templates_tab()
        self._create_advanced_tab()
        
        # Frame de botones inferior
        self._create_buttons_frame(main_frame)
    
    def _create_devices_tab(self):
        """Crear pestaña de dispositivos."""
        devices_frame = ttk.Frame(self.notebook)
        self.notebook.add(devices_frame, text="Dispositivos")
        
        # Frame de control superior
        control_frame = ttk.Frame(devices_frame)
        control_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(control_frame, text="Dispositivos Detectados", 
                 font=('Arial', 12, 'bold')).pack(side='left')
        
        # Botones de control
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(side='right')
        
        self.btn_scan = ttk.Button(btn_frame, text="Escanear", command=self._scan_devices)
        self.btn_scan.pack(side='left', padx=2)
        
        self.btn_refresh = ttk.Button(btn_frame, text="Actualizar", command=self._refresh_devices)
        self.btn_refresh.pack(side='left', padx=2)
        
        # Checkbox de escaneo automático
        ttk.Checkbutton(control_frame, text="Escaneo Automático", 
                       variable=self.var_auto_scan,
                       command=self._toggle_auto_scan).pack(side='left', padx=20)
        
        # Frame de lista de dispositivos
        list_frame = ttk.Frame(devices_frame)
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Treeview para dispositivos
        columns = ('Tipo', 'Nombre', 'Fabricante', 'Interface', 'Estado')
        self.devices_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings')
        
        # Configurar columnas
        self.devices_tree.heading('#0', text='ID')
        self.devices_tree.column('#0', width=120)
        
        for col in columns:
            self.devices_tree.heading(col, text=col)
            self.devices_tree.column(col, width=100)
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(list_frame, orient='vertical', command=self.devices_tree.yview)
        h_scroll = ttk.Scrollbar(list_frame, orient='horizontal', command=self.devices_tree.xview)
        self.devices_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Pack treeview y scrollbars
        self.devices_tree.pack(side='left', fill='both', expand=True)
        v_scroll.pack(side='right', fill='y')
        h_scroll.pack(side='bottom', fill='x')
        
        # Frame de información del dispositivo
        info_frame = ttk.LabelFrame(devices_frame, text="Información del Dispositivo")
        info_frame.pack(fill='x', padx=5, pady=5)
        
        self.device_info_text = tk.Text(info_frame, height=8, wrap='word', state='disabled')
        info_scroll = ttk.Scrollbar(info_frame, orient='vertical', command=self.device_info_text.yview)
        self.device_info_text.configure(yscrollcommand=info_scroll.set)
        
        self.device_info_text.pack(side='left', fill='both', expand=True)
        info_scroll.pack(side='right', fill='y')
        
        # Bind selección en treeview
        self.devices_tree.bind('<<TreeviewSelect>>', self._on_device_select)
    
    def _create_scanner_tab(self):
        """Crear pestaña de configuración de scanner."""
        scanner_frame = ttk.Frame(self.notebook)
        self.notebook.add(scanner_frame, text="Scanner")
        
        # Frame de selección de scanner
        select_frame = ttk.LabelFrame(scanner_frame, text="Selección de Scanner")
        select_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(select_frame, text="Scanner Activo:").pack(side='left', padx=5)
        
        self.scanner_combo = ttk.Combobox(select_frame, state='readonly', width=40)
        self.scanner_combo.pack(side='left', padx=5, fill='x', expand=True)
        self.scanner_combo.bind('<<ComboboxSelected>>', self._on_scanner_select)
        
        self.btn_test_scanner = ttk.Button(select_frame, text="Probar", 
                                          command=self._test_scanner)
        self.btn_test_scanner.pack(side='right', padx=5)
        
        # Frame de configuración
        config_frame = ttk.LabelFrame(scanner_frame, text="Configuración")
        config_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Opciones de configuración
        ttk.Checkbutton(config_frame, text="Habilitar Scanner", 
                       variable=self.var_scanner_enabled).pack(anchor='w', padx=5, pady=2)
        
        ttk.Checkbutton(config_frame, text="Configuración Automática", 
                       variable=self.var_auto_configure).pack(anchor='w', padx=5, pady=2)
        
        # Frame de formato de códigos
        format_frame = ttk.LabelFrame(config_frame, text="Formatos Soportados")
        format_frame.pack(fill='x', padx=5, pady=5)
        
        # Variables para formatos
        self.format_vars = {}
        formats = ['Code128', 'Code39', 'EAN13', 'EAN8', 'UPC', 'UPCA']
        
        for i, format_name in enumerate(formats):
            var = tk.BooleanVar(value=True)
            self.format_vars[format_name] = var
            
            row = i // 3
            col = i % 3
            
            cb = ttk.Checkbutton(format_frame, text=format_name, variable=var)
            cb.grid(row=row, column=col, sticky='w', padx=5, pady=2)
        
        # Frame de configuración avanzada
        advanced_scanner_frame = ttk.LabelFrame(config_frame, text="Configuración Avanzada")
        advanced_scanner_frame.pack(fill='x', padx=5, pady=5)
        
        # Timeout de lectura
        ttk.Label(advanced_scanner_frame, text="Timeout (ms):").grid(row=0, column=0, sticky='w', padx=5)
        self.scanner_timeout = tk.IntVar(value=5000)
        ttk.Spinbox(advanced_scanner_frame, from_=1000, to=30000, 
                   textvariable=self.scanner_timeout, width=10).grid(row=0, column=1, padx=5)
        
        # Prefijo/Sufijo
        ttk.Label(advanced_scanner_frame, text="Prefijo:").grid(row=1, column=0, sticky='w', padx=5)
        self.scanner_prefix = tk.StringVar()
        ttk.Entry(advanced_scanner_frame, textvariable=self.scanner_prefix, 
                 width=15).grid(row=1, column=1, padx=5)
        
        ttk.Label(advanced_scanner_frame, text="Sufijo:").grid(row=1, column=2, sticky='w', padx=5)
        self.scanner_suffix = tk.StringVar(value="\\r\\n")
        ttk.Entry(advanced_scanner_frame, textvariable=self.scanner_suffix, 
                 width=15).grid(row=1, column=3, padx=5)
    
    def _create_printer_tab(self):
        """Crear pestaña de configuración de impresora."""
        printer_frame = ttk.Frame(self.notebook)
        self.notebook.add(printer_frame, text="Impresora")
        
        # Frame de selección de impresora
        select_frame = ttk.LabelFrame(printer_frame, text="Selección de Impresora")
        select_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(select_frame, text="Impresora Activa:").pack(side='left', padx=5)
        
        self.printer_combo = ttk.Combobox(select_frame, state='readonly', width=40)
        self.printer_combo.pack(side='left', padx=5, fill='x', expand=True)
        self.printer_combo.bind('<<ComboboxSelected>>', self._on_printer_select)
        
        self.btn_test_printer = ttk.Button(select_frame, text="Probar", 
                                          command=self._test_printer)
        self.btn_test_printer.pack(side='right', padx=5)
        
        # Frame de configuración
        config_frame = ttk.LabelFrame(printer_frame, text="Configuración")
        config_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Opciones básicas
        ttk.Checkbutton(config_frame, text="Habilitar Impresora", 
                       variable=self.var_printer_enabled).pack(anchor='w', padx=5, pady=2)
        
        # Frame de configuración de impresión
        print_config_frame = ttk.LabelFrame(config_frame, text="Configuración de Impresión")
        print_config_frame.pack(fill='x', padx=5, pady=5)
        
        # Calidad de impresión
        ttk.Label(print_config_frame, text="Calidad:").grid(row=0, column=0, sticky='w', padx=5)
        self.print_quality = tk.StringVar(value="Normal")
        quality_combo = ttk.Combobox(print_config_frame, textvariable=self.print_quality,
                                   values=["Borrador", "Normal", "Alta"], state='readonly')
        quality_combo.grid(row=0, column=1, padx=5, sticky='w')
        
        # Orientación
        ttk.Label(print_config_frame, text="Orientación:").grid(row=0, column=2, sticky='w', padx=5)
        self.print_orientation = tk.StringVar(value="Vertical")
        orientation_combo = ttk.Combobox(print_config_frame, textvariable=self.print_orientation,
                                       values=["Vertical", "Horizontal"], state='readonly')
        orientation_combo.grid(row=0, column=3, padx=5, sticky='w')
        
        # Tamaño de papel
        ttk.Label(print_config_frame, text="Papel:").grid(row=1, column=0, sticky='w', padx=5)
        self.paper_size = tk.StringVar(value="A4")
        paper_combo = ttk.Combobox(print_config_frame, textvariable=self.paper_size,
                                 values=["A4", "Carta", "Etiqueta"], state='readonly')
        paper_combo.grid(row=1, column=1, padx=5, sticky='w')
        
        # Copias
        ttk.Label(print_config_frame, text="Copias:").grid(row=1, column=2, sticky='w', padx=5)
        self.print_copies = tk.IntVar(value=1)
        ttk.Spinbox(print_config_frame, from_=1, to=10, 
                   textvariable=self.print_copies, width=5).grid(row=1, column=3, padx=5, sticky='w')
    
    def _create_templates_tab(self):
        """Crear pestaña de templates de etiquetas."""
        templates_frame = ttk.Frame(self.notebook)
        self.notebook.add(templates_frame, text="Templates")
        
        # Frame de lista de templates
        list_frame = ttk.LabelFrame(templates_frame, text="Templates Disponibles")
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Treeview para templates
        template_columns = ('Nombre', 'Descripción', 'Etiquetas/Página', 'Tamaño')
        self.templates_tree = ttk.Treeview(list_frame, columns=template_columns, show='tree headings')
        
        self.templates_tree.heading('#0', text='ID')
        self.templates_tree.column('#0', width=100)
        
        for col in template_columns:
            self.templates_tree.heading(col, text=col)
            self.templates_tree.column(col, width=120)
        
        # Scrollbar para templates
        template_scroll = ttk.Scrollbar(list_frame, orient='vertical', 
                                       command=self.templates_tree.yview)
        self.templates_tree.configure(yscrollcommand=template_scroll.set)
        
        self.templates_tree.pack(side='left', fill='both', expand=True)
        template_scroll.pack(side='right', fill='y')
        
        # Frame de botones de templates
        template_buttons_frame = ttk.Frame(templates_frame)
        template_buttons_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(template_buttons_frame, text="Nuevo Template", 
                  command=self._create_custom_template).pack(side='left', padx=2)
        ttk.Button(template_buttons_frame, text="Editar", 
                  command=self._edit_template).pack(side='left', padx=2)
        ttk.Button(template_buttons_frame, text="Eliminar", 
                  command=self._delete_template).pack(side='left', padx=2)
        ttk.Button(template_buttons_frame, text="Exportar", 
                  command=self._export_template).pack(side='left', padx=2)
        ttk.Button(template_buttons_frame, text="Importar", 
                  command=self._import_template).pack(side='left', padx=2)
        
        # Cargar templates iniciales
        self._load_templates()
    
    def _create_advanced_tab(self):
        """Crear pestaña de configuración avanzada."""
        advanced_frame = ttk.Frame(self.notebook)
        self.notebook.add(advanced_frame, text="Avanzado")
        
        # Frame de diagnósticos
        diag_frame = ttk.LabelFrame(advanced_frame, text="Diagnósticos")
        diag_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(diag_frame, text="Probar Todos los Dispositivos", 
                  command=self._test_all_devices).pack(side='left', padx=5, pady=5)
        ttk.Button(diag_frame, text="Generar Reporte", 
                  command=self._generate_report).pack(side='left', padx=5, pady=5)
        ttk.Button(diag_frame, text="Exportar Configuración", 
                  command=self._export_config).pack(side='left', padx=5, pady=5)
        
        # Frame de logs
        logs_frame = ttk.LabelFrame(advanced_frame, text="Registro de Eventos")
        logs_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.logs_text = tk.Text(logs_frame, height=15, wrap='word', state='disabled')
        logs_scroll = ttk.Scrollbar(logs_frame, orient='vertical', command=self.logs_text.yview)
        self.logs_text.configure(yscrollcommand=logs_scroll.set)
        
        self.logs_text.pack(side='left', fill='both', expand=True)
        logs_scroll.pack(side='right', fill='y')
        
        # Frame de configuración del sistema
        system_frame = ttk.LabelFrame(advanced_frame, text="Configuración del Sistema")
        system_frame.pack(fill='x', padx=5, pady=5)
        
        # Intervalo de escaneo
        ttk.Label(system_frame, text="Intervalo de escaneo (seg):").grid(row=0, column=0, sticky='w', padx=5)
        self.scan_interval = tk.DoubleVar(value=5.0)
        ttk.Spinbox(system_frame, from_=1.0, to=60.0, increment=1.0,
                   textvariable=self.scan_interval, width=10).grid(row=0, column=1, padx=5)
        
        # Nivel de logging
        ttk.Label(system_frame, text="Nivel de Log:").grid(row=0, column=2, sticky='w', padx=5)
        self.log_level = tk.StringVar(value="INFO")
        log_combo = ttk.Combobox(system_frame, textvariable=self.log_level,
                               values=["DEBUG", "INFO", "WARNING", "ERROR"], state='readonly')
        log_combo.grid(row=0, column=3, padx=5)
        
        # Agregar algunos logs iniciales
        self._add_log("Sistema iniciado")
        self._add_log("Configuración cargada")
    
    def _create_buttons_frame(self, parent):
        """Crear frame de botones inferior."""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill='x', pady=10)
        
        # Botones principales
        ttk.Button(buttons_frame, text="Aplicar", 
                  command=self._apply_config).pack(side='right', padx=5)
        ttk.Button(buttons_frame, text="Aceptar", 
                  command=self._accept_config).pack(side='right', padx=5)
        ttk.Button(buttons_frame, text="Cancelar", 
                  command=self._cancel_config).pack(side='right', padx=5)
        
        # Botón de ayuda
        ttk.Button(buttons_frame, text="Ayuda", 
                  command=self._show_help).pack(side='left', padx=5)
    
    def _bind_events(self):
        """Configurar eventos del formulario."""
        # Eventos de teclado
        self.window.bind('<F5>', lambda e: self._refresh_devices())
        self.window.bind('<Escape>', lambda e: self._cancel_config())
        self.window.bind('<Control-s>', lambda e: self._apply_config())
    
    def _start_device_scan(self):
        """Iniciar escaneo inicial de dispositivos."""
        if self.var_auto_scan.get():
            self.hardware_detector.start_auto_scan()
        
        # Ejecutar primer escaneo en thread separado
        threading.Thread(target=self._scan_devices, daemon=True).start()
    
    def _scan_devices(self):
        """Escanear dispositivos en thread separado."""
        if self.scanning_devices:
            return
        
        self.scanning_devices = True
        
        try:
            self._update_scan_button_state(False)
            self._add_log("Iniciando escaneo de dispositivos...")
            
            # Escanear dispositivos
            devices = self.hardware_detector.detect_all_devices(force_rescan=True)
            self.devices_list = devices
            
            # Actualizar UI en thread principal
            self.window.after(0, self._update_devices_list, devices)
            self._add_log(f"Escaneo completado: {len(devices)} dispositivos encontrados")
            
        except Exception as e:
            self._add_log(f"Error en escaneo: {e}", "ERROR")
            logger.error(f"Error escaneando dispositivos: {e}")
        finally:
            self.scanning_devices = False
            self.window.after(0, lambda: self._update_scan_button_state(True))
    
    def _refresh_devices(self):
        """Actualizar lista de dispositivos."""
        threading.Thread(target=self._scan_devices, daemon=True).start()
    
    def _update_devices_list(self, devices: List[DeviceInfo]):
        """Actualizar la lista de dispositivos en el UI."""
        # Limpiar tree
        for item in self.devices_tree.get_children():
            self.devices_tree.delete(item)
        
        # Agregar dispositivos
        for device in devices:
            self.devices_tree.insert('', 'end', 
                                   text=device.device_id,
                                   values=(
                                       device.device_type.title(),
                                       device.name,
                                       device.manufacturer,
                                       device.interface.upper(),
                                       device.status.title()
                                   ))
        
        # Actualizar combos
        self._update_scanner_combo(devices)
        self._update_printer_combo(devices)
    
    def _update_scanner_combo(self, devices: List[DeviceInfo]):
        """Actualizar combo de scanners."""
        scanners = [d for d in devices if d.device_type == 'scanner']
        scanner_names = [f"{s.name} ({s.device_id})" for s in scanners]
        
        self.scanner_combo['values'] = scanner_names
        
        # Seleccionar el primer scanner si existe
        if scanners and not self.scanner_combo.get():
            self.scanner_combo.set(scanner_names[0])
            self.selected_scanner = scanners[0]
    
    def _update_printer_combo(self, devices: List[DeviceInfo]):
        """Actualizar combo de impresoras."""
        printers = [d for d in devices if d.device_type == 'printer']
        printer_names = [f"{p.name} ({p.device_id})" for p in printers]
        
        self.printer_combo['values'] = printer_names
        
        # Seleccionar la primera impresora si existe
        if printers and not self.printer_combo.get():
            self.printer_combo.set(printer_names[0])
            self.selected_printer = printers[0]
    
    def _update_scan_button_state(self, enabled: bool):
        """Actualizar estado del botón de escaneo."""
        if enabled:
            self.btn_scan.configure(text="Escanear", state='normal')
        else:
            self.btn_scan.configure(text="Escaneando...", state='disabled')
    
    def _on_device_select(self, event):
        """Manejar selección de dispositivo."""
        selection = self.devices_tree.selection()
        if not selection:
            return
        
        item = self.devices_tree.item(selection[0])
        device_id = item['text']
        
        # Buscar el dispositivo
        device = None
        for d in self.devices_list:
            if d.device_id == device_id:
                device = d
                break
        
        if device:
            self._show_device_info(device)
    
    def _show_device_info(self, device: DeviceInfo):
        """Mostrar información detallada del dispositivo."""
        capabilities = self.hardware_detector.get_device_capabilities(device.device_id)
        
        info_text = f"""Información del Dispositivo:
        
ID: {device.device_id}
Nombre: {device.name}
Fabricante: {device.manufacturer}
Tipo: {device.device_type.title()}
Interface: {device.interface.upper()}
Estado: {device.status.title()}

Conexión:
Vendor ID: 0x{device.vendor_id:04X}
Product ID: 0x{device.product_id:04X}
Puerto: {device.port or 'N/A'}
Driver: {device.driver or 'N/A'}

Capacidades:
{', '.join(device.capabilities) if device.capabilities else 'Ninguna especificada'}

Información Adicional:
{device.description or 'No disponible'}
"""
        
        # Agregar capacidades específicas si existen
        if 'scanner_features' in capabilities:
            features = capabilities['scanner_features']
            info_text += f"""

Características del Scanner:
Formatos soportados: {', '.join(features.get('supported_formats', []))}
Tipo de interface: {features.get('interface_type', 'N/A')}
Auto-enter: {'Sí' if features.get('auto_enter', False) else 'No'}
Configurable: {'Sí' if features.get('configurable', False) else 'No'}
"""
        
        if 'printer_features' in capabilities:
            features = capabilities['printer_features']
            info_text += f"""

Características de la Impresora:
Formatos soportados: {', '.join(features.get('supported_formats', []))}
Tamaños de papel: {', '.join(features.get('paper_sizes', []))}
Color: {'Sí' if features.get('color', False) else 'No'}
Dúplex: {'Sí' if features.get('duplex', False) else 'No'}
Etiquetas: {'Sí' if features.get('label_printing', False) else 'No'}
"""
        
        # Actualizar texto
        self.device_info_text.configure(state='normal')
        self.device_info_text.delete(1.0, tk.END)
        self.device_info_text.insert(1.0, info_text)
        self.device_info_text.configure(state='disabled')
    
    def _toggle_auto_scan(self):
        """Activar/desactivar escaneo automático."""
        if self.var_auto_scan.get():
            self.hardware_detector.start_auto_scan()
            self._add_log("Escaneo automático activado")
        else:
            self.hardware_detector.stop_auto_scan()
            self._add_log("Escaneo automático desactivado")
    
    def _on_scanner_select(self, event):
        """Manejar selección de scanner."""
        selection = self.scanner_combo.get()
        if not selection:
            return
        
        # Extraer device_id del string
        device_id = selection.split('(')[-1].replace(')', '')
        
        # Buscar el scanner
        for device in self.devices_list:
            if device.device_id == device_id:
                self.selected_scanner = device
                self._add_log(f"Scanner seleccionado: {device.name}")
                break
    
    def _on_printer_select(self, event):
        """Manejar selección de impresora."""
        selection = self.printer_combo.get()
        if not selection:
            return
        
        # Extraer device_id del string
        device_id = selection.split('(')[-1].replace(')', '')
        
        # Buscar la impresora
        for device in self.devices_list:
            if device.device_id == device_id:
                self.selected_printer = device
                self._add_log(f"Impresora seleccionada: {device.name}")
                break
    
    def _test_scanner(self):
        """Probar conexión con scanner."""
        if not self.selected_scanner:
            messagebox.showwarning("Advertencia", "Seleccione un scanner primero")
            return
        
        def test_thread():
            try:
                self._add_log(f"Probando scanner: {self.selected_scanner.name}")
                success = self.hardware_detector.test_device_connection(self.selected_scanner.device_id)
                
                if success:
                    self._add_log("✓ Scanner funciona correctamente")
                    self.window.after(0, lambda: messagebox.showinfo("Éxito", "El scanner funciona correctamente"))
                else:
                    self._add_log("✗ Error en conexión del scanner")
                    self.window.after(0, lambda: messagebox.showerror("Error", "No se pudo conectar con el scanner"))
                    
            except Exception as e:
                self._add_log(f"Error probando scanner: {e}", "ERROR")
                self.window.after(0, lambda: messagebox.showerror("Error", f"Error probando scanner: {e}"))
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def _test_printer(self):
        """Probar conexión con impresora."""
        if not self.selected_printer:
            messagebox.showwarning("Advertencia", "Seleccione una impresora primero")
            return
        
        def test_thread():
            try:
                self._add_log(f"Probando impresora: {self.selected_printer.name}")
                success = self.hardware_detector.test_device_connection(self.selected_printer.device_id)
                
                if success:
                    self._add_log("✓ Impresora funciona correctamente")
                    self.window.after(0, lambda: messagebox.showinfo("Éxito", "La impresora funciona correctamente"))
                else:
                    self._add_log("✗ Error en conexión de la impresora")
                    self.window.after(0, lambda: messagebox.showerror("Error", "No se pudo conectar con la impresora"))
                    
            except Exception as e:
                self._add_log(f"Error probando impresora: {e}", "ERROR")
                self.window.after(0, lambda: messagebox.showerror("Error", f"Error probando impresora: {e}"))
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def _load_templates(self):
        """Cargar templates de etiquetas."""
        templates = self.label_service.get_available_templates()
        
        # Limpiar tree
        for item in self.templates_tree.get_children():
            self.templates_tree.delete(item)
        
        # Agregar templates
        for template in templates:
            self.templates_tree.insert('', 'end',
                                     text=template['id'],
                                     values=(
                                         template['name'],
                                         template['description'],
                                         template['labels_per_page'],
                                         template['page_size']
                                     ))
    
    def _create_custom_template(self):
        """Crear template personalizado."""
        # TODO: Implementar diálogo para crear template personalizado
        messagebox.showinfo("Información", "Función de template personalizado en desarrollo")
    
    def _edit_template(self):
        """Editar template seleccionado."""
        selection = self.templates_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un template para editar")
            return
        
        # TODO: Implementar edición de template
        messagebox.showinfo("Información", "Edición de templates en desarrollo")
    
    def _delete_template(self):
        """Eliminar template seleccionado."""
        selection = self.templates_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un template para eliminar")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este template?"):
            # TODO: Implementar eliminación de template
            messagebox.showinfo("Información", "Eliminación de templates en desarrollo")
    
    def _export_template(self):
        """Exportar template a archivo."""
        selection = self.templates_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un template para exportar")
            return
        
        # TODO: Implementar exportación
        messagebox.showinfo("Información", "Exportación de templates en desarrollo")
    
    def _import_template(self):
        """Importar template desde archivo."""
        # TODO: Implementar importación
        messagebox.showinfo("Información", "Importación de templates en desarrollo")
    
    def _test_all_devices(self):
        """Probar todos los dispositivos."""
        def test_thread():
            self._add_log("Iniciando pruebas de todos los dispositivos...")
            
            for device in self.devices_list:
                try:
                    self._add_log(f"Probando: {device.name}")
                    success = self.hardware_detector.test_device_connection(device.device_id)
                    
                    if success:
                        self._add_log(f"✓ {device.name}: OK")
                    else:
                        self._add_log(f"✗ {device.name}: Error")
                        
                except Exception as e:
                    self._add_log(f"✗ {device.name}: {e}", "ERROR")
            
            self._add_log("Pruebas completadas")
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def _generate_report(self):
        """Generar reporte de configuración."""
        # TODO: Implementar generación de reporte
        messagebox.showinfo("Información", "Generación de reportes en desarrollo")
    
    def _export_config(self):
        """Exportar configuración actual."""
        # TODO: Implementar exportación de configuración
        messagebox.showinfo("Información", "Exportación de configuración en desarrollo")
    
    def _add_log(self, message: str, level: str = "INFO"):
        """Agregar mensaje al log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {level}: {message}\n"
        
        self.logs_text.configure(state='normal')
        self.logs_text.insert(tk.END, log_message)
        self.logs_text.see(tk.END)
        self.logs_text.configure(state='disabled')
        
        # Log también al logger del sistema
        if level == "ERROR":
            logger.error(message)
        elif level == "WARNING":
            logger.warning(message)
        else:
            logger.info(message)
    
    def _apply_config(self):
        """Aplicar configuración."""
        try:
            # Aplicar configuración del scanner
            if self.selected_scanner and self.var_scanner_enabled.get():
                success = self.hardware_detector.auto_configure_device(self.selected_scanner.device_id)
                if success:
                    self._add_log("Configuración de scanner aplicada")
                else:
                    self._add_log("Error aplicando configuración de scanner", "ERROR")
            
            # Aplicar configuración de impresora
            if self.selected_printer and self.var_printer_enabled.get():
                success = self.hardware_detector.auto_configure_device(self.selected_printer.device_id)
                if success:
                    self._add_log("Configuración de impresora aplicada")
                else:
                    self._add_log("Error aplicando configuración de impresora", "ERROR")
            
            # Actualizar intervalo de escaneo
            self.hardware_detector.scan_interval = self.scan_interval.get()
            
            self._add_log("Configuración aplicada exitosamente")
            messagebox.showinfo("Éxito", "Configuración aplicada correctamente")
            
        except Exception as e:
            self._add_log(f"Error aplicando configuración: {e}", "ERROR")
            messagebox.showerror("Error", f"Error aplicando configuración: {e}")
    
    def _accept_config(self):
        """Aceptar y cerrar."""
        self._apply_config()
        self._close()
    
    def _cancel_config(self):
        """Cancelar y cerrar."""
        if messagebox.askyesno("Confirmar", "¿Descartar cambios y cerrar?"):
            self._close()
    
    def _show_help(self):
        """Mostrar ayuda."""
        help_text = """Configuración de Códigos de Barras - Ayuda

Pestañas:
• Dispositivos: Ver y escanear dispositivos conectados
• Scanner: Configurar lector de códigos de barras
• Impresora: Configurar impresora para etiquetas
• Templates: Gestionar plantillas de etiquetas
• Avanzado: Configuración del sistema y diagnósticos

Funciones principales:
• Escaneo automático de dispositivos USB
• Configuración automática de lectores
• Generación de etiquetas profesionales
• Pruebas de conectividad
• Templates personalizables

Atajos de teclado:
• F5: Actualizar dispositivos
• Ctrl+S: Aplicar configuración
• Escape: Cancelar
"""
        messagebox.showinfo("Ayuda", help_text)
    
    def _on_closing(self):
        """Manejar cierre de ventana."""
        self._cancel_config()
    
    def _close(self):
        """Cerrar formulario."""
        try:
            # Detener escaneo automático
            self.hardware_detector.stop_auto_scan()
            self._add_log("Sistema detenido")
            
            # Cerrar ventana
            if self.parent:
                self.window.grab_release()
            self.window.destroy()
            
        except Exception as e:
            logger.error(f"Error cerrando formulario: {e}")
    
    def show(self):
        """Mostrar el formulario."""
        self.window.deiconify()
        self.window.lift()
        self.window.focus_set()
        return self.window


def show_barcode_config(parent=None):
    """
    Función de conveniencia para mostrar configuración de códigos de barras.
    
    Args:
        parent: Ventana padre (opcional)
        
    Returns:
        BarcodeConfigForm: Instancia del formulario
    """
    form = BarcodeConfigForm(parent)
    return form.show()


if __name__ == "__main__":
    # Test independiente
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal
    
    form = show_barcode_config()
    root.mainloop()
