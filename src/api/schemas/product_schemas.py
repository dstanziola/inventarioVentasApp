"""
Schemas Pydantic para API de Productos
Sistema de Inventario v2.0 - TDD FASE GREEN

Modelos de validación para endpoints CRUD de productos usando Pydantic.
"""

from pydantic import BaseModel, field_validator, model_validator, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime


class ProductCreate(BaseModel):
    """Schema para crear un nuevo producto."""
    
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del producto")
    descripcion: Optional[str] = Field(None, max_length=500, description="Descripción del producto")
    precio_venta: Decimal = Field(..., gt=0, description="Precio de venta (debe ser mayor a 0)")
    precio_compra: Optional[Decimal] = Field(None, ge=0, description="Precio de compra")
    stock_inicial: int = Field(..., ge=0, description="Stock inicial (debe ser mayor o igual a 0)")
    stock_minimo: int = Field(default=1, ge=0, description="Stock mínimo para alertas")
    id_categoria: int = Field(..., gt=0, description="ID de la categoría")
    
    @field_validator('nombre')
    def validate_nombre(cls, v):
        """Validar que el nombre no esté vacío después de limpiar espacios."""
        if v:
            v = v.strip()
            if not v:
                raise ValueError("El nombre no puede estar vacío")
        return v
    
    @field_validator('descripcion')
    def validate_descripcion(cls, v):
        """Limpiar espacios en la descripción."""
        if v:
            return v.strip()
        return v
    
    @model_validator(mode='after')
    def validate_precio_compra(self):
        """Validar que precio de compra sea menor o igual al precio de venta."""
        if self.precio_compra is not None and self.precio_compra > self.precio_venta:
            raise ValueError("El precio de compra no puede ser mayor al precio de venta")
        return self

    class Config:
        json_schema_extra = {
            "example": {
                "nombre": "Laptop HP EliteBook",
                "descripcion": "Laptop profesional para oficina",
                "precio_venta": 1500.00,
                "precio_compra": 1200.00,
                "stock_inicial": 10,
                "stock_minimo": 2,
                "id_categoria": 1
            }
        }


class ProductUpdate(BaseModel):
    """Schema para actualizar un producto existente."""
    
    nombre: Optional[str] = Field(None, min_length=1, max_length=100, description="Nombre del producto")
    descripcion: Optional[str] = Field(None, max_length=500, description="Descripción del producto")
    precio_venta: Optional[Decimal] = Field(None, gt=0, description="Precio de venta")
    precio_compra: Optional[Decimal] = Field(None, ge=0, description="Precio de compra")
    stock_minimo: Optional[int] = Field(None, ge=0, description="Stock mínimo")
    id_categoria: Optional[int] = Field(None, gt=0, description="ID de la categoría")
    activo: Optional[bool] = Field(None, description="Estado activo/inactivo del producto")
    
    @field_validator('nombre')
    def validate_nombre(cls, v):
        """Validar que el nombre no esté vacío después de limpiar espacios."""
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("El nombre no puede estar vacío")
        return v
    
    @field_validator('descripcion')
    def validate_descripcion(cls, v):
        """Limpiar espacios en la descripción."""
        if v is not None:
            return v.strip()
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "precio_venta": 1450.00,
                "stock_minimo": 3,
                "activo": True
            }
        }


class ProductResponse(BaseModel):
    """Schema para respuesta de un producto."""
    
    id_producto: int
    nombre: str
    descripcion: Optional[str]
    precio_venta: Decimal
    precio_compra: Optional[Decimal]
    stock_actual: int
    stock_minimo: int
    id_categoria: int
    categoria_nombre: Optional[str]
    activo: bool
    fecha_creacion: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "id_producto": 1,
                "nombre": "Laptop HP EliteBook",
                "descripcion": "Laptop profesional para oficina",
                "precio_venta": 1500.00,
                "precio_compra": 1200.00,
                "stock_actual": 8,
                "stock_minimo": 2,
                "id_categoria": 1,
                "categoria_nombre": "Electrónicos",
                "activo": True,
                "fecha_creacion": "2025-05-27T10:00:00"
            }
        }


class ProductListResponse(BaseModel):
    """Schema para respuesta de lista de productos."""
    
    status: str = "success"
    data: List[ProductResponse]
    count: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "data": [
                    {
                        "id_producto": 1,
                        "nombre": "Laptop HP",
                        "descripcion": "Laptop para oficina",
                        "precio_venta": 1500.00,
                        "stock_actual": 8,
                        "categoria_nombre": "Electrónicos",
                        "activo": True
                    }
                ],
                "count": 1
            }
        }


class ProductSingleResponse(BaseModel):
    """Schema para respuesta de un solo producto."""
    
    status: str = "success"
    data: ProductResponse
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "data": {
                    "id_producto": 1,
                    "nombre": "Laptop HP",
                    "precio_venta": 1500.00,
                    "stock_actual": 8,
                    "categoria_nombre": "Electrónicos",
                    "activo": True
                },
                "message": "Producto obtenido exitosamente"
            }
        }


class ProductSearchRequest(BaseModel):
    """Schema para petición de búsqueda."""
    q: str = Field(..., min_length=1, description="Término de búsqueda")


class ProductSearchResponse(BaseModel):
    """Schema para respuesta de búsqueda de productos."""
    
    status: str = "success"
    data: List[ProductResponse]
    count: int
    query: Optional[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "data": [
                    {
                        "id_producto": 1,
                        "nombre": "Laptop HP",
                        "precio_venta": 1500.00,
                        "stock_actual": 8,
                        "activo": True
                    }
                ],
                "count": 1,
                "query": "laptop"
            }
        }


class LowStockProductResponse(BaseModel):
    """Schema para productos con stock bajo."""
    
    id_producto: int
    nombre: str
    stock_actual: int
    stock_minimo: int
    categoria_nombre: Optional[str]
    precio_venta: Decimal
    activo: bool
    
    class Config:
        json_schema_extra = {
            "example": {
                "id_producto": 4,
                "nombre": "Cable USB",
                "stock_actual": 2,
                "stock_minimo": 5,
                "categoria_nombre": "Accesorios",
                "precio_venta": 15.99,
                "activo": True
            }
        }


class LowStockListResponse(BaseModel):
    """Schema para respuesta de productos con stock bajo."""
    
    status: str = "success"
    data: List[LowStockProductResponse]
    count: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "data": [
                    {
                        "id_producto": 4,
                        "nombre": "Cable USB",
                        "stock_actual": 2,
                        "stock_minimo": 5,
                        "categoria_nombre": "Accesorios",
                        "activo": True
                    }
                ],
                "count": 1
            }
        }


class ProductStatsResponse(BaseModel):
    """Schema para estadísticas de productos."""
    
    status: str = "success"
    data: dict
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "data": {
                    "total_products": 25,
                    "active_products": 23,
                    "inactive_products": 2,
                    "low_stock_products": 3,
                    "total_stock_value": 45750.50,
                    "categories_distribution": {
                        "Electrónicos": 12,
                        "Accesorios": 8,
                        "Software": 5
                    }
                }
            }
        }


# Schemas de error reutilizados de categorías
class ErrorResponse(BaseModel):
    """Schema para respuestas de error."""
    
    status: str = "error"
    message: str
    detail: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "message": "Producto no encontrado",
                "detail": "El producto con ID 999 no existe en el sistema"
            }
        }


class SuccessResponse(BaseModel):
    """Schema para respuestas de éxito simples."""
    
    status: str = "success"
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Producto eliminado exitosamente"
            }
        }
