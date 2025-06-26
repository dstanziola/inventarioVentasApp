"""
Servicio de Códigos de Barras
============================

Servicio de lógica de negocio para manejo de códigos de barras
en el sistema de inventario.

Autor: Sistema de Inventario
Versión: 1.0.0
Fecha: Junio 2025
"""

import logging
import re
from typing import List, Dict, Optional, Any, Union

from hardware.device_manager import DeviceManager, DeviceManagerError
from services.product_service import ProductService
from models.producto import Producto


class BarcodeService:
    """
    Servicio para gestión de códigos de barras.
    
    Proporciona funcionalidades de alto nivel para:
    - Gestión de dispositivos de códigos de barras
    - Lectura y validación de códigos
    - Búsqueda de productos por código
    - Formateo y normalización de códigos
    """
    
    # Patrón para validación de códigos de barras
    # Permite letras, números y algunos caracteres especiales comunes
    VALID_BARCODE_PATTERN = re.compile(r'^[A-Za-z0-9\-_]+$')
    
    # Longitud máxima para códigos de barras
    MAX_BARCODE_LENGTH = 100
    
    def __init__(self):
        """
        Inicializa el servicio de códigos de barras.
        """
        self.logger = logging.getLogger(__name__)
        self.device_manager = DeviceManager()
        self.product_service = ProductService()
        
        self.logger.info("BarcodeService inicializado")
    
    def scan_barcode_devices(self) -> List[Dict[str, Any]]:
        """
        Escanea y detecta dispositivos de códigos de barras disponibles.
        
        Returns:
            List[Dict]: Lista de dispositivos detectados
        """
        try:
            devices = self.device_manager.scan_devices()
            self.logger.info(f"Detectados {len(devices)} dispositivos de códigos de barras")
            return devices
            
        except Exception as e:
            self.logger.error(f"Error al escanear dispositivos: {e}")
            return []
    
    def connect_barcode_device(self, device_id: str) -> bool:
        """
        Conecta con un dispositivo específico de códigos de barras.
        
        Args:
            device_id: ID único del dispositivo
            
        Returns:
            bool: True si la conexión fue exitosa
        """
        try:
            result = self.device_manager.connect_device(device_id)
            if result:
                self.logger.info(f"Dispositivo conectado exitosamente: {device_id}")
            else:
                self.logger.warning(f"Fallo al conectar dispositivo: {device_id}")
            return result
            
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
        try:
            result = self.device_manager.disconnect_device(device_id)
            if result:
                self.logger.info(f"Dispositivo desconectado: {device_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error al desconectar dispositivo {device_id}: {e}")
            return False
    
    def disconnect_all_devices(self) -> None:
        """
        Desconecta todos los dispositivos conectados.
        """
        try:
            self.device_manager.disconnect_all()
            self.logger.info("Todos los dispositivos desconectados")
            
        except Exception as e:
            self.logger.error(f"Error al desconectar todos los dispositivos: {e}")
    
    def get_connected_devices(self) -> List[Dict[str, Any]]:
        """
        Obtiene la lista de dispositivos actualmente conectados.
        
        Returns:
            List[Dict]: Lista de dispositivos conectados
        """
        try:
            return self.device_manager.get_connected_devices()
            
        except Exception as e:
            self.logger.error(f"Error al obtener dispositivos conectados: {e}")
            return []
    
    def get_device_info(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información detallada de un dispositivo.
        
        Args:
            device_id: ID único del dispositivo
            
        Returns:
            Dict: Información del dispositivo, None si no existe
        """
        try:
            return self.device_manager.get_device_info(device_id)
            
        except Exception as e:
            self.logger.error(f"Error al obtener info del dispositivo {device_id}: {e}")
            return None
    
    def read_barcode(self, device_id: str, timeout: int = 5000) -> Optional[str]:
        """
        Lee un código de barras desde un dispositivo específico.
        
        Args:
            device_id: ID único del dispositivo
            timeout: Tiempo máximo de espera en milisegundos
            
        Returns:
            str: Código de barras leído, None si falla o timeout
        """
        try:
            barcode = self.device_manager.read_from_device(device_id, timeout)
            if barcode:
                formatted_barcode = self.format_barcode(barcode)
                self.logger.info(f"Código leído y formateado: {formatted_barcode}")
                return formatted_barcode
            else:
                self.logger.debug(f"No se pudo leer código desde {device_id}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error al leer código desde {device_id}: {e}")
            return None
    
    def read_barcode_with_validation(self, device_id: str, timeout: int = 5000) -> Optional[str]:
        """
        Lee un código de barras y lo valida antes de retornarlo.
        
        Args:
            device_id: ID único del dispositivo
            timeout: Tiempo máximo de espera en milisegundos
            
        Returns:
            str: Código válido, None si es inválido o falla la lectura
        """
        barcode = self.read_barcode(device_id, timeout)
        if barcode and self.validate_barcode(barcode):
            return barcode
        elif barcode:
            self.logger.warning(f"Código leído pero inválido: {barcode}")
        
        return None
    
    def read_barcode_with_formatting(self, device_id: str, timeout: int = 5000) -> Optional[str]:
        """
        Lee un código de barras y aplica formateo completo.
        
        Args:
            device_id: ID único del dispositivo
            timeout: Tiempo máximo de espera en milisegundos
            
        Returns:
            str: Código formateado, None si falla la lectura
        """
        return self.read_barcode(device_id, timeout)  # Ya incluye formateo
    
    def read_and_lookup_product(self, device_id: str, timeout: int = 5000) -> Optional[Dict[str, Any]]:
        """
        Lee un código de barras y busca el producto correspondiente.
        
        Args:
            device_id: ID único del dispositivo
            timeout: Tiempo máximo de espera en milisegundos
            
        Returns:
            Dict: Diccionario con 'barcode' y 'product', None si falla la lectura
        """
        try:
            barcode = self.read_barcode_with_validation(device_id, timeout)
            if not barcode:
                return None
            
            product = self.lookup_product_by_barcode(barcode)
            
            result = {
                'barcode': barcode,
                'product': product
            }
            
            if product:
                self.logger.info(f"Producto encontrado para código {barcode}: {product.nombre}")
            else:
                self.logger.warning(f"No se encontró producto para código: {barcode}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error al leer y buscar producto: {e}")
            return None
    
    def lookup_product_by_barcode(self, barcode: str) -> Optional[Producto]:
        """
        Busca un producto por su código de barras.
        
        Args:
            barcode: Código de barras a buscar
            
        Returns:
            Producto: Instancia del producto, None si no se encuentra
        """
        try:
            # Formatear el código antes de buscar
            formatted_barcode = self.format_barcode(barcode)
            
            # En nuestro sistema, el ID del producto es su código de barras
            try:
                product_id = int(formatted_barcode)
                product = self.product_service.find_by_id(product_id)
                
                if product:
                    self.logger.debug(f"Producto encontrado: ID {product_id}")
                else:
                    self.logger.debug(f"Producto no encontrado para ID: {product_id}")
                
                return product
                
            except ValueError:
                # El código no es numérico, buscar por otros criterios si es necesario
                self.logger.warning(f"Código de barras no numérico: {formatted_barcode}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error al buscar producto por código {barcode}: {e}")
            return None
    
    def validate_barcode(self, barcode: Union[str, None]) -> bool:
        """
        Valida si un código de barras tiene formato válido.
        
        Args:
            barcode: Código de barras a validar
            
        Returns:
            bool: True si el código es válido
        """
        if not barcode:
            return False
        
        # Convertir a string y limpiar
        barcode_str = str(barcode).strip()
        
        # Verificar que no esté vacío después de limpiar
        if not barcode_str:
            return False
        
        # Verificar longitud máxima
        if len(barcode_str) > self.MAX_BARCODE_LENGTH:
            return False
        
        # Verificar patrón válido (solo letras, números, guiones y guiones bajos)
        if not self.VALID_BARCODE_PATTERN.match(barcode_str):
            return False
        
        return True
    
    def format_barcode(self, barcode: str) -> str:
        """
        Formatea y normaliza un código de barras.
        
        Args:
            barcode: Código de barras a formatear
            
        Returns:
            str: Código formateado
        """
        if not barcode:
            return ""
        
        # Convertir a string, limpiar espacios y convertir a mayúsculas
        formatted = str(barcode).strip().upper()
        
        # Remover caracteres de control (\\n, \\t, etc.)
        formatted = re.sub(r'\\[ntr]', '', formatted)
        
        return formatted
    
    def get_barcode_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de uso de códigos de barras.
        
        Returns:
            Dict: Estadísticas de códigos de barras
        """
        try:
            device_stats = self.device_manager.get_device_statistics()
            
            # Agregar estadísticas específicas del servicio
            service_stats = {
                'devices': device_stats,
                'service_version': '1.0.0',
                'validation_pattern': self.VALID_BARCODE_PATTERN.pattern,
                'max_barcode_length': self.MAX_BARCODE_LENGTH
            }
            
            return service_stats
            
        except Exception as e:
            self.logger.error(f"Error al obtener estadísticas: {e}")
            return {}
    
    def is_device_connected(self, device_id: str) -> bool:
        """
        Verifica si un dispositivo específico está conectado.
        
        Args:
            device_id: ID único del dispositivo
            
        Returns:
            bool: True si está conectado
        """
        try:
            return self.device_manager.is_device_connected(device_id)
            
        except Exception as e:
            self.logger.error(f"Error al verificar conexión del dispositivo {device_id}: {e}")
            return False
    
    def get_available_devices(self) -> List[Dict[str, Any]]:
        """
        Obtiene lista de todos los dispositivos disponibles.
        
        Returns:
            List[Dict]: Lista de dispositivos disponibles
        """
        try:
            return self.device_manager.get_available_devices()
            
        except Exception as e:
            self.logger.error(f"Error al obtener dispositivos disponibles: {e}")
            return []
    
    def auto_connect_first_device(self) -> Optional[str]:
        """
        Conecta automáticamente al primer dispositivo disponible.
        
        Returns:
            str: ID del dispositivo conectado, None si no hay dispositivos
        """
        try:
            devices = self.scan_barcode_devices()
            if devices:
                device_id = devices[0]['device_id']
                if self.connect_barcode_device(device_id):
                    self.logger.info(f"Auto-conectado al dispositivo: {device_id}")
                    return device_id
            
            self.logger.warning("No hay dispositivos disponibles para auto-conexión")
            return None
            
        except Exception as e:
            self.logger.error(f"Error en auto-conexión: {e}")
            return None


class BarcodeServiceError(Exception):
    """Excepción base para errores del servicio de códigos de barras"""
    pass


class BarcodeValidationError(BarcodeServiceError):
    """Excepción para errores de validación de códigos"""
    pass


class BarcodeDeviceError(BarcodeServiceError):
    """Excepción para errores de dispositivos de códigos de barras"""
    pass


class BarcodeReadError(BarcodeServiceError):
    """Excepción para errores de lectura de códigos"""
    pass
