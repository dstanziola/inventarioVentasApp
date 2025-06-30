"""
Capa de servicios del sistema de inventario.

Esta capa contiene la lógica de negocio pura, implementando casos de uso
específicos del dominio sin depender de frameworks externos.

ARQUITECTURA LIMPIA:
- Services: Contiene la lógica de aplicación y orquesta operaciones complejas
- Models: Entidades de dominio (ya implementadas)
- Database: Capa de persistencia (ya implementada)

SERVICIOS DISPONIBLES:
- CategoryService: Gestión de categorías MATERIAL/SERVICIO
- ProductService: Gestión de productos con cálculos financieros
- ClientService: Gestión de clientes con validación de RUC
- SalesService: Procesamiento completo de ventas con inventario
- InventoryService: Movimientos de stock y auditoría
- UserService: Gestión de usuarios y autenticación
- ReportService: Generación de reportes y exportación a PDF (FASE 2)
"""

from .category_service import CategoryService
from .product_service import ProductService
from .client_service import ClientService
from .sales_service import SalesService
from .inventory_service import InventoryService
from .user_service import UserService
from .report_service import ReportService

__all__ = [
    'CategoryService',
    'ProductService', 
    'ClientService',
    'SalesService',
    'InventoryService',
    'UserService',
    'ReportService'
]

# Versión de la capa de servicios
__version__ = '1.1.0'  # Incrementada por FASE 2
