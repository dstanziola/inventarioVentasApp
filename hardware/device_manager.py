"""
Gestor de Dispositivos de Hardware
=================================

Módulo para gestionar múltiples dispositivos de códigos de barras
y otros dispositivos de hardware del sistema.

Autor: Sistema de Inventario
Versión: 1.0.0
Fecha: Junio 2025
"""

import logging
import hashlib
from typing import List, Dict, Optional, Any
from threading import Lock

from .barcode_reader import BarcodeReader, BarcodeReaderError


class DeviceManager:
    """
    Gestor de dispositivos de hardware.
    
    Maneja la detección, conexión y comunicación con múltiples
    dispositivos de códigos de barras y otros equipos de hardware.
    """
    
    def __init__(self):
        """
        Inicializa el gestor de dispositivos.
        """
        self.logger = logging.getLogger(__name__)
        self._devices = {}  # device_id -> device_info
        self._readers = {}  # device_id -> BarcodeReader instance
        self._lock = Lock()  # Para thread-safety
        
        self.logger.info("DeviceManager inicializado")
    
    def scan_devices(self) -> List[Dict[str, Any]]:
        """
        Escanea y detecta todos los dispositivos disponibles.
        
        Returns:
            List[Dict]: Lista de dispositivos detectados con IDs únicos
        """
        with self._lock:
            try:
                # Crear un lector temporal para detectar dispositivos
                temp_reader = BarcodeReader()
                detected_devices = temp_reader.detect_devices()
                
                # Agregar IDs únicos y procesar información
                processed_devices = []
                for device in detected_devices:
                    device_id = self._generate_device_id(device)
                    device_info = {
                        'device_id': device_id,
                        'vendor_id': device.get('vendor_id', 0),
                        'product_id': device.get('product_id', 0),
                        'manufacturer': device.get('manufacturer', 'Unknown'),
                        'product': device.get('product', 'Unknown'),
                        'serial': device.get('serial', 'Unknown'),
                        'bus': device.get('bus', 0),
                        'address': device.get('address', 0),
                        'connected': device_id in self._readers,
                        'reader_available': True
                    }
                    
                    # Actualizar registro interno
                    self._devices[device_id] = device_info
                    processed_devices.append(device_info)
                
                self.logger.info(f"Escaneados {len(processed_devices)} dispositivos")
                return processed_devices
                
            except Exception as e:
                self.logger.error(f"Error al escanear dispositivos: {e}")
                return []
    
    def get_connected_devices(self) -> List[Dict[str, Any]]:
        """
        Obtiene la lista de dispositivos actualmente conectados.
        
        Returns:
            List[Dict]: Lista de dispositivos conectados
        """
        with self._lock:
            connected = []
            for device_id, device_info in self._devices.items():
                if device_id in self._readers:
                    # Actualizar estado de conexión
                    device_info_copy = device_info.copy()
                    device_info_copy['connected'] = True
                    connected.append(device_info_copy)
            
            return connected
    
    def connect_device(self, device_id: str) -> bool:
        """
        Conecta con un dispositivo específico.
        
        Args:
            device_id: ID único del dispositivo
            
        Returns:
            bool: True si la conexión fue exitosa
        """
        with self._lock:
            try:
                # Verificar si el dispositivo existe
                if device_id not in self._devices:
                    self.logger.error(f"Dispositivo no encontrado: {device_id}")
                    return False
                
                # Verificar si ya está conectado
                if device_id in self._readers:
                    self.logger.warning(f"Dispositivo ya conectado: {device_id}")
                    return True
                
                # Obtener información del dispositivo
                device_info = self._devices[device_id]
                vendor_id = device_info['vendor_id']
                product_id = device_info['product_id']
                
                # Crear y conectar lector
                reader = BarcodeReader()
                if reader.connect(vendor_id, product_id):
                    self._readers[device_id] = reader
                    self._devices[device_id]['connected'] = True
                    
                    self.logger.info(f"Dispositivo conectado exitosamente: {device_id}")
                    return True
                else:
                    self.logger.error(f"Fallo al conectar dispositivo: {device_id}")
                    return False
                    
            except Exception as e:
                self.logger.error(f"Error al conectar dispositivo {device_id}: {e}")
                return False
    
    def disconnect_device(self, device_id: str) -> bool:
        """
        Desconecta un dispositivo específico.
        
        Args:
            device_id: ID único del dispositivo
            
        Returns:
            bool: True si la desconexión fue exitosa
        """
        with self._lock:
            try:
                # Verificar si el dispositivo está conectado
                if device_id not in self._readers:
                    self.logger.warning(f"Dispositivo no conectado: {device_id}")
                    return False
                
                # Desconectar el lector
                reader = self._readers[device_id]
                reader.disconnect()
                
                # Remover de la lista de conectados
                del self._readers[device_id]
                
                # Actualizar estado si el dispositivo está en el registro
                if device_id in self._devices:
                    self._devices[device_id]['connected'] = False
                
                self.logger.info(f"Dispositivo desconectado: {device_id}")
                return True
                
            except Exception as e:
                self.logger.error(f"Error al desconectar dispositivo {device_id}: {e}")
                return False
    
    def disconnect_all(self) -> None:
        """
        Desconecta todos los dispositivos conectados.
        """
        with self._lock:
            device_ids = list(self._readers.keys())
            for device_id in device_ids:
                try:
                    self.disconnect_device(device_id)
                except Exception as e:
                    self.logger.error(f"Error al desconectar dispositivo {device_id}: {e}")
            
            self.logger.info("Todos los dispositivos desconectados")
    
    def read_from_device(self, device_id: str, timeout: int = 5000) -> Optional[str]:
        """
        Lee un código de barras desde un dispositivo específico.
        
        Args:
            device_id: ID único del dispositivo
            timeout: Tiempo máximo de espera en milisegundos
            
        Returns:
            str: Código de barras leído, None si falla o timeout
        """
        with self._lock:
            try:
                # Verificar si el dispositivo está conectado
                if device_id not in self._readers:
                    self.logger.error(f"Dispositivo no conectado: {device_id}")
                    return None
                
                # Obtener el lector y leer código
                reader = self._readers[device_id]
                
                # Release lock durante la lectura para evitar bloqueo
                # La lectura puede tomar tiempo y no necesita sincronización
                
            except Exception as e:
                self.logger.error(f"Error al preparar lectura desde {device_id}: {e}")
                return None
        
        # Leer fuera del lock para evitar bloqueos prolongados
        try:
            result = reader.read_barcode(timeout)
            if result:
                self.logger.info(f"Código leído desde {device_id}: {result}")
            else:
                self.logger.debug(f"Sin código leído desde {device_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error al leer desde dispositivo {device_id}: {e}")
            return None
    
    def is_device_connected(self, device_id: str) -> bool:
        """
        Verifica si un dispositivo específico está conectado.
        
        Args:
            device_id: ID único del dispositivo
            
        Returns:
            bool: True si está conectado
        """
        with self._lock:
            return device_id in self._readers
    
    def get_device_info(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información detallada de un dispositivo.
        
        Args:
            device_id: ID único del dispositivo
            
        Returns:
            Dict: Información del dispositivo, None si no existe o no está conectado
        """
        with self._lock:
            try:
                # Verificar si el dispositivo está conectado
                if device_id not in self._readers:
                    self.logger.warning(f"Dispositivo no conectado: {device_id}")
                    return None
                
                # Obtener información del lector
                reader = self._readers[device_id]
                reader_info = reader.get_device_info()
                
                if reader_info:
                    # Combinar con información almacenada
                    stored_info = self._devices.get(device_id, {})
                    combined_info = {
                        'device_id': device_id,
                        'connected': True,
                        'reader_available': True,
                        **stored_info,
                        **reader_info
                    }
                    return combined_info
                else:
                    return None
                    
            except Exception as e:
                self.logger.error(f"Error al obtener info del dispositivo {device_id}: {e}")
                return None
    
    def get_available_devices(self) -> List[Dict[str, Any]]:
        """
        Obtiene lista de dispositivos disponibles (detectados pero no necesariamente conectados).
        
        Returns:
            List[Dict]: Lista de dispositivos disponibles
        """
        with self._lock:
            available = []
            for device_id, device_info in self._devices.items():
                info_copy = device_info.copy()
                info_copy['connected'] = device_id in self._readers
                available.append(info_copy)
            
            return available
    
    def get_device_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas generales de dispositivos.
        
        Returns:
            Dict: Estadísticas de dispositivos
        """
        with self._lock:
            total_detected = len(self._devices)
            total_connected = len(self._readers)
            
            # Contar por fabricante
            manufacturers = {}
            for device_info in self._devices.values():
                manufacturer = device_info.get('manufacturer', 'Unknown')
                manufacturers[manufacturer] = manufacturers.get(manufacturer, 0) + 1
            
            return {
                'total_detected': total_detected,
                'total_connected': total_connected,
                'available_for_connection': total_detected - total_connected,
                'manufacturers': manufacturers,
                'readers_active': len([r for r in self._readers.values() if r.is_connected()])
            }
    
    def _generate_device_id(self, device_info: Dict[str, Any]) -> str:
        """
        Genera un ID único para un dispositivo basado en sus características.
        
        Args:
            device_info: Información del dispositivo
            
        Returns:
            str: ID único del dispositivo
        """
        # Crear string único basado en vendor, product y serial
        unique_string = (
            f"{device_info.get('vendor_id', 0):04x}:"
            f"{device_info.get('product_id', 0):04x}:"
            f"{device_info.get('serial', 'unknown')}:"
            f"{device_info.get('bus', 0)}:"
            f"{device_info.get('address', 0)}"
        )
        
        # Generar hash MD5 para ID único pero legible
        device_hash = hashlib.md5(unique_string.encode()).hexdigest()[:12]
        
        return f"dev_{device_hash}"


class DeviceManagerError(Exception):
    """Excepción base para errores del gestor de dispositivos"""
    pass


class DeviceNotFoundError(DeviceManagerError):
    """Excepción para dispositivo no encontrado"""
    pass


class DeviceConnectionError(DeviceManagerError):
    """Excepción para errores de conexión de dispositivos"""
    pass


class DeviceOperationError(DeviceManagerError):
    """Excepción para errores en operaciones de dispositivos"""
    pass
