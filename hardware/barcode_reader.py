"""
Lector de Códigos de Barras USB HID
==================================

Módulo para integración con lectores de códigos de barras USB HID.
Proporciona funcionalidades para detectar, conectar y leer códigos
desde dispositivos hardware.

Autor: Sistema de Inventario
Versión: 1.0.0
Fecha: Junio 2025
"""

import logging
import time
from typing import List, Dict, Optional, Any

try:
    import usb.core
    import usb.util
    USB_AVAILABLE = True
except ImportError:
    USB_AVAILABLE = False
    logging.warning("PyUSB no está instalado. Funcionalidad de hardware limitada.")

try:
    import hid
    HID_AVAILABLE = True
except ImportError:
    HID_AVAILABLE = False
    logging.warning("hidapi no está instalado. Funcionalidad HID limitada.")


class BarcodeReader:
    """
    Lector de códigos de barras USB HID.
    
    Proporciona métodos para detectar, conectar y leer códigos de barras
    desde dispositivos USB estándar tipo "keyboard wedge".
    """
    
    # Códigos de teclas comunes para conversión HID a ASCII
    HID_KEYCODE_MAP = {
        30: '1', 31: '2', 32: '3', 33: '4', 34: '5',
        35: '6', 36: '7', 37: '8', 38: '9', 39: '0',
        4: 'a', 5: 'b', 6: 'c', 7: 'd', 8: 'e',
        9: 'f', 10: 'g', 11: 'h', 12: 'i', 13: 'j',
        14: 'k', 15: 'l', 16: 'm', 17: 'n', 18: 'o',
        19: 'p', 20: 'q', 21: 'r', 22: 's', 23: 't',
        24: 'u', 25: 'v', 26: 'w', 27: 'x', 28: 'y', 29: 'z',
        40: '\n',  # Enter key
        44: ' ',   # Space
        45: '-',   # Minus
        46: '=',   # Equal
    }
    
    # Vendor IDs comunes de lectores de códigos de barras
    COMMON_BARCODE_VENDORS = [
        0x05e0,  # Symbol Technologies
        0x0c2e,  # Metrologic/Honeywell
        0x1a86,  # QinHeng Electronics
        0x0483,  # STMicroelectronics
        0x1eab,  # Skanwear
        0x08ff,  # AuthenTec
        0x0536,  # Hand Held Products (Honeywell)
    ]
    
    def __init__(self):
        """
        Inicializa el lector de códigos de barras.
        """
        self.logger = logging.getLogger(__name__)
        self.device = None
        self.endpoint_in = None
        self.endpoint_out = None
        self._connected = False
        
        # Verificar disponibilidad de librerías
        if not USB_AVAILABLE:
            self.logger.warning("PyUSB no disponible. Funcionalidad USB limitada.")
        if not HID_AVAILABLE:
            self.logger.warning("hidapi no disponible. Funcionalidad HID limitada.")
    
    def detect_devices(self) -> List[Dict[str, Any]]:
        """
        Detecta dispositivos de códigos de barras conectados.
        
        Returns:
            List[Dict]: Lista de dispositivos detectados con información básica
        """
        devices = []
        
        if not USB_AVAILABLE:
            self.logger.warning("USB no disponible para detección de dispositivos")
            return devices
        
        try:
            # Buscar dispositivos USB HID
            usb_devices = usb.core.find(find_all=True)
            
            for device in usb_devices:
                try:
                    # Verificar si es un dispositivo HID
                    if self._is_hid_device(device):
                        device_info = {
                            'vendor_id': device.idVendor,
                            'product_id': device.idProduct,
                            'manufacturer': self._get_string_descriptor(device, device.iManufacturer),
                            'product': self._get_string_descriptor(device, device.iProduct),
                            'serial': self._get_string_descriptor(device, device.iSerialNumber),
                            'bus': device.bus,
                            'address': device.address
                        }
                        devices.append(device_info)
                        self.logger.debug(f"Dispositivo HID detectado: {device_info}")
                
                except Exception as e:
                    self.logger.debug(f"Error al obtener info del dispositivo: {e}")
                    continue
        
        except Exception as e:
            self.logger.error(f"Error al detectar dispositivos USB: {e}")
        
        self.logger.info(f"Detectados {len(devices)} dispositivos HID")
        return devices
    
    def connect(self, vendor_id: int, product_id: int) -> bool:
        """
        Conecta con un dispositivo específico.
        
        Args:
            vendor_id: ID del fabricante
            product_id: ID del producto
            
        Returns:
            bool: True si la conexión fue exitosa
        """
        if not USB_AVAILABLE:
            self.logger.error("PyUSB no disponible para conexión")
            return False
        
        try:
            # Buscar el dispositivo específico
            self.device = usb.core.find(idVendor=vendor_id, idProduct=product_id)
            
            if self.device is None:
                self.logger.error(f"Dispositivo no encontrado: {vendor_id:04x}:{product_id:04x}")
                return False
            
            # Verificar si necesita desconectar driver del kernel
            if self.device.is_kernel_driver_active(0):
                try:
                    self.device.detach_kernel_driver(0)
                    self.logger.debug("Driver del kernel desconectado")
                except usb.core.USBError as e:
                    self.logger.warning(f"No se pudo desconectar driver del kernel: {e}")
            
            # Configurar el dispositivo
            self.device.set_configuration()
            self.device.reset()
            
            # Encontrar endpoints
            cfg = self.device.get_active_configuration()
            interface = cfg[(0, 0)]
            
            self.endpoint_in = usb.util.find_descriptor(
                interface,
                custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN
            )
            
            self.endpoint_out = usb.util.find_descriptor(
                interface,
                custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT
            )
            
            if self.endpoint_in is None:
                self.logger.error("No se encontró endpoint de entrada")
                return False
            
            self._connected = True
            self.logger.info(f"Conectado exitosamente a {vendor_id:04x}:{product_id:04x}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error al conectar con dispositivo: {e}")
            self.device = None
            self._connected = False
            return False
    
    def is_connected(self) -> bool:
        """
        Verifica si hay una conexión activa.
        
        Returns:
            bool: True si está conectado
        """
        return self._connected and self.device is not None
    
    def read_barcode(self, timeout: int = 5000) -> Optional[str]:
        """
        Lee un código de barras del dispositivo.
        
        Args:
            timeout: Tiempo máximo de espera en milisegundos
            
        Returns:
            str: Código de barras leído, None si falla o timeout
        """
        if not self.is_connected():
            self.logger.error("Dispositivo no conectado")
            return None
        
        if self.endpoint_in is None:
            self.logger.error("Endpoint de entrada no disponible")
            return None
        
        try:
            barcode_data = []
            start_time = time.time()
            
            while (time.time() - start_time) * 1000 < timeout:
                try:
                    # Leer datos del dispositivo
                    data = self.device.read(self.endpoint_in.bEndpointAddress, 
                                          self.endpoint_in.wMaxPacketSize, 
                                          timeout=100)
                    
                    if data and len(data) > 0:
                        # Procesar datos HID
                        processed = self._process_hid_data(data)
                        if processed:
                            barcode_data.extend(processed)
                            
                            # Verificar si es fin de línea (Enter)
                            if '\n' in processed:
                                break
                
                except usb.core.USBError as e:
                    if e.errno == 110:  # Timeout
                        continue
                    else:
                        self.logger.error(f"Error USB al leer: {e}")
                        break
                except Exception as e:
                    self.logger.error(f"Error inesperado al leer: {e}")
                    break
            
            if barcode_data:
                # Convertir a string y limpiar
                barcode_string = ''.join(barcode_data).strip()
                if barcode_string:
                    self.logger.info(f"Código leído: {barcode_string}")
                    return barcode_string
            
            self.logger.debug("Timeout o sin datos en lectura")
            return None
            
        except Exception as e:
            self.logger.error(f"Error al leer código de barras: {e}")
            return None
    
    def disconnect(self) -> None:
        """
        Desconecta del dispositivo.
        """
        if self.device is not None:
            try:
                # Liberar la interfaz
                usb.util.dispose_resources(self.device)
                self.logger.info("Dispositivo desconectado")
            except Exception as e:
                self.logger.warning(f"Error al desconectar: {e}")
            finally:
                self.device = None
                self.endpoint_in = None
                self.endpoint_out = None
                self._connected = False
        else:
            self.logger.debug("No hay dispositivo para desconectar")
    
    def get_device_info(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene información del dispositivo conectado.
        
        Returns:
            Dict: Información del dispositivo, None si no está conectado
        """
        if not self.is_connected():
            return None
        
        try:
            return {
                'vendor_id': self.device.idVendor,
                'product_id': self.device.idProduct,
                'manufacturer': self._get_string_descriptor(self.device, self.device.iManufacturer),
                'product': self._get_string_descriptor(self.device, self.device.iProduct),
                'serial': self._get_string_descriptor(self.device, self.device.iSerialNumber),
                'bus': self.device.bus,
                'address': self.device.address
            }
        except Exception as e:
            self.logger.error(f"Error al obtener info del dispositivo: {e}")
            return None
    
    def _is_hid_device(self, device) -> bool:
        """
        Verifica si un dispositivo es HID.
        
        Args:
            device: Dispositivo USB a verificar
            
        Returns:
            bool: True si es dispositivo HID
        """
        try:
            # Verificar clase HID (clase 3)
            for cfg in device:
                for interface in cfg:
                    if interface.bInterfaceClass == 3:  # HID class
                        return True
            return False
        except Exception:
            return False
    
    def _get_string_descriptor(self, device, index: int) -> str:
        """
        Obtiene descriptor de string del dispositivo.
        
        Args:
            device: Dispositivo USB
            index: Índice del descriptor
            
        Returns:
            str: Descriptor de string o "Unknown"
        """
        try:
            if index == 0:
                return "Unknown"
            return usb.util.get_string(device, index)
        except Exception:
            return "Unknown"
    
    def _process_hid_data(self, data) -> List[str]:
        """
        Procesa datos HID y convierte a caracteres legibles.
        
        Args:
            data: Datos HID recibidos
            
        Returns:
            List[str]: Lista de caracteres procesados
        """
        processed = []
        
        try:
            # Los datos HID suelen venir en formato [modifier, reserved, keycode1, keycode2, ...]
            if len(data) >= 3:
                # Procesar códigos de tecla (ignorar modificadores por ahora)
                for i in range(2, len(data), 2):  # Saltar de 2 en 2 para datos de teclado
                    if i < len(data):
                        keycode = data[i]
                        if keycode in self.HID_KEYCODE_MAP:
                            processed.append(self.HID_KEYCODE_MAP[keycode])
                        elif keycode == 0:
                            # Código 0 significa que no hay tecla presionada
                            continue
                        else:
                            # Código desconocido, registrar para debug
                            self.logger.debug(f"Código HID desconocido: {keycode}")
            
        except Exception as e:
            self.logger.error(f"Error al procesar datos HID: {e}")
        
        return processed


class BarcodeReaderError(Exception):
    """Excepción específica para errores del lector de códigos de barras"""
    pass


class BarcodeReaderTimeoutError(BarcodeReaderError):
    """Excepción para timeouts en lectura"""
    pass


class BarcodeReaderConnectionError(BarcodeReaderError):
    """Excepción para errores de conexión"""
    pass
