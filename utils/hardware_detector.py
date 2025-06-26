"""
Detector automático de hardware para códigos de barras.

Este módulo proporciona funcionalidades para:
- Detección automática de dispositivos USB
- Identificación de lectores de códigos de barras
- Detección de impresoras compatibles
- Obtención de capacidades de dispositivos
- Auto-configuración de dispositivos
- Pruebas de conectividad

Autor: Sistema de Inventario Copy Point S.A.
Fecha: Junio 2025
"""

import logging
import platform
import subprocess
import time
import re
from typing import List, Dict, Optional, Tuple, Any
import threading
from dataclasses import dataclass

# Importaciones de hardware
try:
    import usb.core
    import usb.util
    import hid
except ImportError as e:
    logging.warning(f"Dependencias de hardware no disponibles: {e}")
    usb = None
    hid = None

# Configurar logging
logger = logging.getLogger(__name__)


@dataclass
class DeviceInfo:
    """Información de un dispositivo detectado."""
    device_id: str
    name: str
    manufacturer: str
    vendor_id: int
    product_id: int
    device_type: str  # 'scanner', 'printer', 'unknown'
    interface: str    # 'usb', 'serial', 'network'
    status: str       # 'connected', 'disconnected', 'error'
    capabilities: List[str]
    port: Optional[str] = None
    driver: Optional[str] = None
    description: Optional[str] = None


class HardwareDetector:
    """
    Detector automático de hardware para códigos de barras.
    
    Proporciona funcionalidades para detectar y configurar automáticamente
    dispositivos de hardware como lectores de códigos y impresoras.
    """
    
    # Vendors conocidos de lectores de códigos de barras
    BARCODE_SCANNER_VENDORS = {
        0x05E0: "Symbol Technologies",
        0x0536: "Hand Held Products",
        0x0C2E: "Metrologic Instruments",
        0x1234: "Datalogic",
        0x04B4: "Cypress Semiconductor",
        0x0801: "Mag-Tek",
        0x0519: "Datamax",
        0x093A: "Pixart Imaging",
        0x1A86: "QinHeng Electronics",
        0x1CBE: "Luminary Micro",
        0x045E: "Microsoft Corporation",
        0x046D: "Logitech",
        0x05F3: "PI Engineering",
        0x0666: "Chips and Technologies",
        0x0763: "Midiman",
        0x08F7: "Guillemot Corporation",
        0x0A5C: "Broadcom Corp",
        0x0B05: "ASUSTek Computer",
        0x13BA: "PCPlay",
        0x1532: "Razer USA",
        0x16C0: "Van Ooijen Technische Informatica",
    }
    
    # Palabras clave para identificar lectores
    SCANNER_KEYWORDS = [
        'barcode', 'scanner', 'reader', 'imager', 'symbol', 'datalogic',
        'honeywell', 'zebra', 'metrologic', 'intermec', 'hand held',
        'code reader', 'scan', 'pos', 'point of sale'
    ]
    
    # Vendors conocidos de impresoras
    PRINTER_VENDORS = {
        0x04F9: "Brother Industries",
        0x03F0: "Hewlett-Packard",
        0x04A9: "Canon",
        0x04B8: "Seiko Epson",
        0x0924: "Xerox",
        0x1504: "Konica Minolta",
        0x04E8: "Samsung Electronics",
        0x067B: "Prolific Technology",
        0x0483: "STMicroelectronics",
        0x04DA: "Panasonic",
        0x0A5F: "Zebra Technologies",
    }
    
    # Palabras clave para identificar impresoras
    PRINTER_KEYWORDS = [
        'printer', 'print', 'laserjet', 'inkjet', 'deskjet', 'officejet',
        'pixma', 'stylus', 'workforce', 'brother', 'zebra', 'thermal',
        'label printer', 'receipt printer'
    ]
    
    def __init__(self):
        """Inicializar el detector de hardware."""
        self.detected_devices = {}
        self.last_scan_time = 0
        self.scan_interval = 5.0  # segundos
        self._scan_lock = threading.Lock()
        self.auto_scan_enabled = False
        self._scan_thread = None
        
        logger.info("HardwareDetector inicializado")
    
    def detect_all_devices(self, force_rescan: bool = False) -> List[DeviceInfo]:
        """
        Detectar todos los dispositivos disponibles.
        
        Args:
            force_rescan: Forzar nuevo escaneo
            
        Returns:
            List[DeviceInfo]: Lista de dispositivos detectados
        """
        with self._scan_lock:
            current_time = time.time()
            
            # Usar cache si no ha pasado suficiente tiempo
            if not force_rescan and (current_time - self.last_scan_time) < self.scan_interval:
                return list(self.detected_devices.values())
            
            logger.info("Iniciando detección de dispositivos...")
            
            all_devices = []
            
            # Detectar dispositivos USB
            usb_devices = self._detect_usb_devices()
            all_devices.extend(usb_devices)
            
            # Detectar dispositivos serie (en plataformas soportadas)
            serial_devices = self._detect_serial_devices()
            all_devices.extend(serial_devices)
            
            # Detectar impresoras del sistema
            system_printers = self._detect_system_printers()
            all_devices.extend(system_printers)
            
            # Actualizar cache
            self.detected_devices = {dev.device_id: dev for dev in all_devices}
            self.last_scan_time = current_time
            
            logger.info(f"Detectados {len(all_devices)} dispositivos")
            return all_devices
    
    def detect_barcode_scanners(self) -> List[DeviceInfo]:
        """
        Detectar específicamente lectores de códigos de barras.
        
        Returns:
            List[DeviceInfo]: Lista de lectores detectados
        """
        all_devices = self.detect_all_devices()
        scanners = [dev for dev in all_devices if dev.device_type == 'scanner']
        
        logger.info(f"Detectados {len(scanners)} lectores de códigos de barras")
        return scanners
    
    def detect_printers(self) -> List[DeviceInfo]:
        """
        Detectar impresoras disponibles.
        
        Returns:
            List[DeviceInfo]: Lista de impresoras detectadas
        """
        all_devices = self.detect_all_devices()
        printers = [dev for dev in all_devices if dev.device_type == 'printer']
        
        logger.info(f"Detectadas {len(printers)} impresoras")
        return printers
    
    def get_device_capabilities(self, device_id: str) -> Dict[str, Any]:
        """
        Obtener capacidades detalladas de un dispositivo.
        
        Args:
            device_id: ID del dispositivo
            
        Returns:
            Dict: Capacidades del dispositivo
        """
        device = self.detected_devices.get(device_id)
        if not device:
            return {}
        
        capabilities = {
            'basic_info': {
                'name': device.name,
                'manufacturer': device.manufacturer,
                'type': device.device_type,
                'interface': device.interface,
                'status': device.status
            },
            'features': device.capabilities,
            'connection': {
                'vendor_id': f"0x{device.vendor_id:04X}",
                'product_id': f"0x{device.product_id:04X}",
                'port': device.port,
                'driver': device.driver
            }
        }
        
        # Capacidades específicas por tipo
        if device.device_type == 'scanner':
            capabilities.update(self._get_scanner_capabilities(device))
        elif device.device_type == 'printer':
            capabilities.update(self._get_printer_capabilities(device))
        
        return capabilities
    
    def auto_configure_device(self, device_id: str) -> bool:
        """
        Configurar automáticamente un dispositivo.
        
        Args:
            device_id: ID del dispositivo
            
        Returns:
            bool: True si se configuró exitosamente
        """
        device = self.detected_devices.get(device_id)
        if not device:
            logger.error(f"Dispositivo {device_id} no encontrado")
            return False
        
        try:
            logger.info(f"Auto-configurando dispositivo: {device.name}")
            
            if device.device_type == 'scanner':
                return self._configure_scanner(device)
            elif device.device_type == 'printer':
                return self._configure_printer(device)
            else:
                logger.warning(f"Tipo de dispositivo no soportado: {device.device_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error configurando dispositivo {device_id}: {e}")
            return False
    
    def test_device_connection(self, device_id: str) -> bool:
        """
        Probar la conexión con un dispositivo.
        
        Args:
            device_id: ID del dispositivo
            
        Returns:
            bool: True si la conexión es exitosa
        """
        device = self.detected_devices.get(device_id)
        if not device:
            return False
        
        try:
            if device.device_type == 'scanner':
                return self._test_scanner_connection(device)
            elif device.device_type == 'printer':
                return self._test_printer_connection(device)
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error probando conexión con {device_id}: {e}")
            return False
    
    def start_auto_scan(self):
        """Iniciar escaneo automático de dispositivos."""
        if self.auto_scan_enabled:
            return
        
        self.auto_scan_enabled = True
        self._scan_thread = threading.Thread(target=self._auto_scan_worker, daemon=True)
        self._scan_thread.start()
        
        logger.info("Escaneo automático iniciado")
    
    def stop_auto_scan(self):
        """Detener escaneo automático de dispositivos."""
        self.auto_scan_enabled = False
        if self._scan_thread:
            self._scan_thread.join(timeout=2.0)
        
        logger.info("Escaneo automático detenido")
    
    def _detect_usb_devices(self) -> List[DeviceInfo]:
        """Detectar dispositivos USB."""
        devices = []
        
        if not usb:
            logger.warning("PyUSB no disponible, omitiendo detección USB")
            return devices
        
        try:
            # Encontrar todos los dispositivos USB
            usb_devices = usb.core.find(find_all=True)
            
            for device in usb_devices:
                try:
                    # Obtener información básica
                    vendor_id = device.idVendor
                    product_id = device.idProduct
                    
                    # Intentar obtener strings descriptivos
                    try:
                        manufacturer = usb.util.get_string(device, device.iManufacturer) if device.iManufacturer else "Unknown"
                        product_name = usb.util.get_string(device, device.iProduct) if device.iProduct else f"USB Device {product_id:04X}"
                    except:
                        manufacturer = self.BARCODE_SCANNER_VENDORS.get(vendor_id, "Unknown")
                        product_name = f"USB Device {product_id:04X}"
                    
                    # Determinar tipo de dispositivo
                    device_type = self._identify_device_type(vendor_id, product_name, manufacturer)
                    
                    # Crear DeviceInfo
                    device_info = DeviceInfo(
                        device_id=f"usb_{vendor_id:04X}_{product_id:04X}",
                        name=product_name,
                        manufacturer=manufacturer,
                        vendor_id=vendor_id,
                        product_id=product_id,
                        device_type=device_type,
                        interface='usb',
                        status='connected',
                        capabilities=self._get_basic_capabilities(device_type),
                        port=f"USB:{device.address}",
                        description=f"USB {device_type.title()}"
                    )
                    
                    devices.append(device_info)
                    
                except Exception as e:
                    logger.debug(f"Error procesando dispositivo USB: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error detectando dispositivos USB: {e}")
        
        return devices
    
    def _detect_serial_devices(self) -> List[DeviceInfo]:
        """Detectar dispositivos serie."""
        devices = []
        
        try:
            import serial.tools.list_ports
            
            ports = serial.tools.list_ports.comports()
            
            for port in ports:
                # Identificar tipo basado en descripción
                description = (port.description or "").lower()
                manufacturer = (port.manufacturer or "Unknown").lower()
                
                device_type = 'unknown'
                if any(keyword in description for keyword in self.SCANNER_KEYWORDS):
                    device_type = 'scanner'
                elif any(keyword in description for keyword in self.PRINTER_KEYWORDS):
                    device_type = 'printer'
                
                device_info = DeviceInfo(
                    device_id=f"serial_{port.device.replace('/', '_').replace('\\', '_')}",
                    name=port.description or f"Serial Device {port.device}",
                    manufacturer=port.manufacturer or "Unknown",
                    vendor_id=port.vid or 0,
                    product_id=port.pid or 0,
                    device_type=device_type,
                    interface='serial',
                    status='connected',
                    capabilities=self._get_basic_capabilities(device_type),
                    port=port.device,
                    description=f"Serial {device_type.title()}"
                )
                
                devices.append(device_info)
                
        except ImportError:
            logger.debug("pyserial no disponible, omitiendo detección serie")
        except Exception as e:
            logger.error(f"Error detectando dispositivos serie: {e}")
        
        return devices
    
    def _detect_system_printers(self) -> List[DeviceInfo]:
        """Detectar impresoras del sistema."""
        devices = []
        
        try:
            system = platform.system()
            
            if system == "Windows":
                devices.extend(self._detect_windows_printers())
            elif system == "Linux":
                devices.extend(self._detect_linux_printers())
            elif system == "Darwin":  # macOS
                devices.extend(self._detect_macos_printers())
                
        except Exception as e:
            logger.error(f"Error detectando impresoras del sistema: {e}")
        
        return devices
    
    def _detect_windows_printers(self) -> List[DeviceInfo]:
        """Detectar impresoras en Windows."""
        devices = []
        
        try:
            import winreg
            
            # Enumerar impresoras instaladas
            printer_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                       r"SYSTEM\CurrentControlSet\Control\Print\Printers")
            
            i = 0
            while True:
                try:
                    printer_name = winreg.EnumKey(printer_key, i)
                    
                    device_info = DeviceInfo(
                        device_id=f"printer_windows_{printer_name}",
                        name=printer_name,
                        manufacturer="Windows System",
                        vendor_id=0,
                        product_id=0,
                        device_type='printer',
                        interface='system',
                        status='connected',
                        capabilities=['print', 'system_printer'],
                        port=f"Windows:{printer_name}",
                        description="Windows System Printer"
                    )
                    
                    devices.append(device_info)
                    i += 1
                    
                except OSError:
                    break
                    
            winreg.CloseKey(printer_key)
            
        except Exception as e:
            logger.debug(f"Error detectando impresoras Windows: {e}")
        
        return devices
    
    def _detect_linux_printers(self) -> List[DeviceInfo]:
        """Detectar impresoras en Linux."""
        devices = []
        
        try:
            # Usar lpstat para enumerar impresoras
            result = subprocess.run(['lpstat', '-p'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.startswith('printer'):
                        # Extraer nombre de impresora
                        match = re.search(r'printer (\S+)', line)
                        if match:
                            printer_name = match.group(1)
                            
                            device_info = DeviceInfo(
                                device_id=f"printer_linux_{printer_name}",
                                name=printer_name,
                                manufacturer="Linux System",
                                vendor_id=0,
                                product_id=0,
                                device_type='printer',
                                interface='system',
                                status='connected',
                                capabilities=['print', 'system_printer'],
                                port=f"Linux:{printer_name}",
                                description="Linux System Printer"
                            )
                            
                            devices.append(device_info)
                            
        except Exception as e:
            logger.debug(f"Error detectando impresoras Linux: {e}")
        
        return devices
    
    def _detect_macos_printers(self) -> List[DeviceInfo]:
        """Detectar impresoras en macOS."""
        devices = []
        
        try:
            # Usar lpstat para enumerar impresoras en macOS
            result = subprocess.run(['lpstat', '-p'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.startswith('printer'):
                        # Extraer nombre de impresora
                        match = re.search(r'printer (\S+)', line)
                        if match:
                            printer_name = match.group(1)
                            
                            device_info = DeviceInfo(
                                device_id=f"printer_macos_{printer_name}",
                                name=printer_name,
                                manufacturer="macOS System",
                                vendor_id=0,
                                product_id=0,
                                device_type='printer',
                                interface='system',
                                status='connected',
                                capabilities=['print', 'system_printer'],
                                port=f"macOS:{printer_name}",
                                description="macOS System Printer"
                            )
                            
                            devices.append(device_info)
                            
        except Exception as e:
            logger.debug(f"Error detectando impresoras macOS: {e}")
        
        return devices
    
    def _identify_device_type(self, vendor_id: int, product_name: str, manufacturer: str) -> str:
        """Identificar tipo de dispositivo basado en vendor ID y nombres."""
        # Verificar vendors conocidos
        if vendor_id in self.BARCODE_SCANNER_VENDORS:
            return 'scanner'
        
        if vendor_id in self.PRINTER_VENDORS:
            return 'printer'
        
        # Verificar palabras clave en nombres
        combined_text = f"{product_name} {manufacturer}".lower()
        
        if any(keyword in combined_text for keyword in self.SCANNER_KEYWORDS):
            return 'scanner'
        
        if any(keyword in combined_text for keyword in self.PRINTER_KEYWORDS):
            return 'printer'
        
        return 'unknown'
    
    def _get_basic_capabilities(self, device_type: str) -> List[str]:
        """Obtener capacidades básicas por tipo de dispositivo."""
        if device_type == 'scanner':
            return ['scan_barcode', 'hid_input', 'code128', 'ean13']
        elif device_type == 'printer':
            return ['print', 'pdf_print']
        else:
            return []
    
    def _get_scanner_capabilities(self, device: DeviceInfo) -> Dict[str, Any]:
        """Obtener capacidades específicas de scanner."""
        return {
            'scanner_features': {
                'supported_formats': ['Code128', 'EAN13', 'UPC', 'Code39'],
                'interface_type': 'HID Keyboard',
                'auto_enter': True,
                'configurable': False,
                'trigger_modes': ['automatic', 'manual']
            }
        }
    
    def _get_printer_capabilities(self, device: DeviceInfo) -> Dict[str, Any]:
        """Obtener capacidades específicas de impresora."""
        return {
            'printer_features': {
                'supported_formats': ['PDF', 'Text'],
                'paper_sizes': ['A4', 'Letter', 'Label'],
                'color': False,  # Asumir B/N por defecto
                'duplex': False,
                'label_printing': True if 'label' in device.name.lower() else False
            }
        }
    
    def _configure_scanner(self, device: DeviceInfo) -> bool:
        """Configurar scanner automáticamente."""
        try:
            logger.info(f"Configurando scanner: {device.name}")
            
            # Para la mayoría de scanners USB HID, no necesitan configuración especial
            # Solo verificar que esté accesible
            
            # TODO: Implementar configuración específica si es necesaria
            # Esto podría incluir:
            # - Configurar formato de salida
            # - Establecer prefijos/sufijos
            # - Configurar timing
            
            return True
            
        except Exception as e:
            logger.error(f"Error configurando scanner: {e}")
            return False
    
    def _configure_printer(self, device: DeviceInfo) -> bool:
        """Configurar impresora automáticamente."""
        try:
            logger.info(f"Configurando impresora: {device.name}")
            
            # Para impresoras del sistema, generalmente no necesitan configuración
            # Para impresoras de etiquetas, podría necesitar configuración específica
            
            return True
            
        except Exception as e:
            logger.error(f"Error configurando impresora: {e}")
            return False
    
    def _test_scanner_connection(self, device: DeviceInfo) -> bool:
        """Probar conexión con scanner."""
        try:
            if device.interface == 'usb' and hid:
                # Intentar abrir dispositivo HID
                devices = hid.enumerate(device.vendor_id, device.product_id)
                return len(devices) > 0
            else:
                # Para otros interfaces, asumir que está conectado si se detectó
                return True
                
        except Exception as e:
            logger.debug(f"Error probando scanner: {e}")
            return False
    
    def _test_printer_connection(self, device: DeviceInfo) -> bool:
        """Probar conexión con impresora."""
        try:
            if device.interface == 'system':
                # Para impresoras del sistema, verificar que esté disponible
                system = platform.system()
                
                if system == "Windows":
                    # Verificar con wmic o PowerShell
                    result = subprocess.run([
                        'powershell', '-Command', 
                        f'Get-Printer -Name "{device.name}" -ErrorAction SilentlyContinue'
                    ], capture_output=True, timeout=5)
                    return result.returncode == 0
                    
                elif system in ["Linux", "Darwin"]:
                    # Verificar con lpstat
                    result = subprocess.run([
                        'lpstat', '-p', device.name
                    ], capture_output=True, timeout=5)
                    return result.returncode == 0
                    
            return True
            
        except Exception as e:
            logger.debug(f"Error probando impresora: {e}")
            return False
    
    def _auto_scan_worker(self):
        """Worker thread para escaneo automático."""
        while self.auto_scan_enabled:
            try:
                # Escanear dispositivos
                self.detect_all_devices(force_rescan=True)
                
                # Esperar antes del siguiente escaneo
                for _ in range(int(self.scan_interval * 10)):
                    if not self.auto_scan_enabled:
                        break
                    time.sleep(0.1)
                    
            except Exception as e:
                logger.error(f"Error en escaneo automático: {e}")
                time.sleep(1.0)


# Instancia singleton
_hardware_detector_instance = None

def get_hardware_detector() -> HardwareDetector:
    """
    Obtener instancia singleton del detector de hardware.
    
    Returns:
        HardwareDetector: Instancia del detector
    """
    global _hardware_detector_instance
    if _hardware_detector_instance is None:
        _hardware_detector_instance = HardwareDetector()
    return _hardware_detector_instance


# Funciones de conveniencia
def quick_scan_scanners() -> List[DeviceInfo]:
    """
    Escaneo rápido de lectores de códigos de barras.
    
    Returns:
        List[DeviceInfo]: Lectores detectados
    """
    detector = get_hardware_detector()
    return detector.detect_barcode_scanners()


def quick_scan_printers() -> List[DeviceInfo]:
    """
    Escaneo rápido de impresoras.
    
    Returns:
        List[DeviceInfo]: Impresoras detectadas
    """
    detector = get_hardware_detector()
    return detector.detect_printers()


def find_best_scanner() -> Optional[DeviceInfo]:
    """
    Encontrar el mejor scanner disponible.
    
    Returns:
        Optional[DeviceInfo]: Mejor scanner o None
    """
    scanners = quick_scan_scanners()
    
    if not scanners:
        return None
    
    # Priorizar por vendor conocido y tipo USB
    for scanner in scanners:
        if scanner.vendor_id in HardwareDetector.BARCODE_SCANNER_VENDORS and scanner.interface == 'usb':
            return scanner
    
    # Si no hay preferencia clara, devolver el primero
    return scanners[0]


def find_best_printer() -> Optional[DeviceInfo]:
    """
    Encontrar la mejor impresora disponible.
    
    Returns:
        Optional[DeviceInfo]: Mejor impresora o None
    """
    printers = quick_scan_printers()
    
    if not printers:
        return None
    
    # Priorizar impresoras de etiquetas
    for printer in printers:
        if 'label' in printer.name.lower() or 'zebra' in printer.name.lower():
            return printer
    
    # Si no hay impresora de etiquetas, devolver la primera
    return printers[0]
