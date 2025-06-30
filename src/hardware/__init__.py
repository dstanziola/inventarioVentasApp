"""
Módulo Hardware para Sistema de Códigos de Barras
=================================================

Este módulo maneja la integración con dispositivos de hardware,
especialmente lectores de códigos de barras USB HID.

Autor: Sistema de Inventario
Versión: 1.0.0
Fecha: Junio 2025
"""

from .barcode_reader import BarcodeReader
from .device_manager import DeviceManager

__all__ = [
    'BarcodeReader',
    'DeviceManager'
]
