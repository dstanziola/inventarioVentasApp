# Directorio del Sistema de Inventario - Funciones y Variables

## ProductService (src/services/product_service.py)

### MÉTODOS PRINCIPALES - ACTUALIZADOS 2025-05-26

#### `get_product_by_id(id_producto: int) -> Optional[Producto]`
- **CORRECCIÓN CRÍTICA**: Ahora devuelve objeto Producto en lugar de dict
- **Parámetros**: id_producto (int)
- **Retorno**: Objeto Producto o None si no existe
- **Uso**: `product = service.get_product_by_id(1); stock = product.stock`
- **Campos Disponibles**: id_producto, nombre, stock, precio, costo, tasa_impuesto, activo, id_categoria

#### `get_all_products(only_active: bool = True) -> List[Producto]`
- **CORRECCIÓN**: Ahora devuelve lista de objetos Producto
- **Parámetros**: only_active (bool, default=True)
- **Retorno**: Lista de objetos Producto
- **Uso**: `products = service.get_all_products(); for p in products: print(p.nombre)`

#### `update_product(id_producto: int, **kwargs) -> Optional[Producto]`
- **CORRECCIÓN**: Ahora devuelve objeto Producto actualizado
- **Parámetros**: id_producto (int), campos a actualizar como kwargs
- **Retorno**: Objeto Producto actualizado o None si falló
- **Uso**: `updated = service.update_product(1, stock=50, precio=25.0)`

#### `create_product(**kwargs) -> Producto`
- **Estado**: Sin cambios, ya devolvía objeto compatible
- **Parámetros**: nombre, categoria_id, stock_inicial, precio_compra, precio_venta, tasa_impuesto
- **Retorno**: Objeto producto creado
- **Validaciones**: Automáticas para restricciones de negocio

#### `delete_product(id_producto: int) -> bool`
- **Estado**: Sin cambios
- **Parámetros**: id_producto (int)
- **Retorno**: bool (True si exitoso)
- **Función**: Soft delete (marca activo=False)

### MÉTODOS DE VALIDACIÓN

#### `validate_stock_for_category(stock: int, categoria) -> bool`
- **Función**: Validar restricción "Si categoría = SERVICIO entonces stock = 0"
- **Parámetros**: stock (int), categoria (objeto)
- **Retorno**: bool (True si válido)
- **Lógica**: Servicios deben tener stock=0, materiales cualquier stock≥0

#### `_category_exists_safe(id_categoria: int) -> bool`
- **Función**: Verificar existencia de categoría con manejo de errores
- **Parámetros**: id_categoria (int)
- **Retorno**: bool
- **Uso Interno**: Validación antes de crear/actualizar productos

#### `_product_exists_safe(nombre: str) -> bool`
- **Función**: Verificar duplicados de nombre de producto
- **Parámetros**: nombre (str)
- **Retorno**: bool
- **Uso Interno**: Validación de unicidad

## Producto Model (src/models/producto.py)

### ATRIBUTOS PRINCIPALES
```python
id_producto: Optional[int]     # ID único (PK)
nombre: str                    # Nombre del producto
id_categoria: int             # FK a categorías
stock: int                    # Cantidad en inventario
costo: Decimal               # Precio de compra
precio: Decimal              # Precio de venta
tasa_impuesto: Decimal       # % de impuesto (0-100)
activo: bool                 # Estado del producto
```

### MÉTODOS DE CÁLCULO
- `calcular_impuesto(cantidad: int) -> Decimal`
- `calcular_subtotal(cantidad: int) -> Decimal`
- `calcular_total(cantidad: int) -> Decimal`
- `tiene_stock_suficiente(cantidad: int) -> bool`
- `actualizar_stock(cantidad: int) -> None`

### MÉTODOS DE VALIDACIÓN
- `validar_datos() -> list` # Lista de errores
- `es_valido() -> bool`
- `validate_service_stock_restriction(categoria) -> bool`

### MÉTODOS DE UTILIDAD
- `to_dict() -> dict`
- `from_dict(data: dict) -> Producto`
- `crear_material(...)` # Factory method
- `crear_servicio(...)` # Factory method

## SalesForm (src/ui/forms/sales_form.py)

### MÉTODOS PRINCIPALES - COMPATIBLES CON CORRECCIÓN

#### `_add_product_to_sale()`
- **CORRECCIÓN VALIDADA**: Ahora funciona con objetos Producto
- **Uso de ProductService**: `product = self.product_service.get_product_by_id(id)`
- **Acceso a Atributos**: `product.stock`, `product.nombre`, `product.tasa_impuesto`
- **Función**: Agregar producto a venta actual

#### Variables de Instancia Críticas:
```python
self.sale_items: List[Dict]           # Items en venta actual
self.product_service: ProductService  # Servicio de productos
self.barcode_service: BarcodeService   # Servicio códigos (opcional)
```

## ProductForm (src/ui/forms/product_form.py)

### MÉTODOS ACTUALIZADOS - 2025-05-26

#### `_load_initial_data()`
- **CORRECCIÓN**: Actualizado para trabajar con objetos Producto directamente
- **Antes**: Convertía dict a Producto manualmente
- **Ahora**: `self.products = self.product_service.get_all_products()`

#### `_save_product()`
- **CORRECCIÓN**: Maneja retorno de objeto Producto de update_product()
- **Validación**: Verifica que `updated_product` no sea None

## API Routes (src/api/routes/products.py)

### COMPATIBILIDAD MANTENIDA

#### `serialize_product(product) -> dict`
- **Función**: Convertir objetos Producto a dict para JSON
- **Compatibilidad**: Maneja tanto dict como objetos Producto
- **Estado**: Sin cambios necesarios

#### Endpoints Principales:
- `GET /products/` -> Usa get_all_products()
- `GET /products/{id}` -> Usa get_product_by_id()
- `PUT /products/{id}` -> Usa update_product()
- `POST /products/` -> Usa create_product()

## Tests Agregados - 2025-05-26

### test_product_service_object_return.py
- **Clase**: `TestProductServiceObjectReturn`
- **Función**: Validar que métodos devuelven objetos Producto
- **Tests Críticos**:
  - `test_get_product_by_id_returns_producto_object()`
  - `test_sales_form_compatibility()`
  - `test_object_has_all_required_attributes()`

### validate_product_service_fix.py
- **Función**: Script ejecutable para validar corrección
- **Tests**:
  - `test_product_service_object_return()`
  - `test_backwards_compatibility()`

## Variables de Configuración

### Database Connection
```python
# Patrón de uso correcto
db_connection = get_database_connection()
product_service = ProductService(db_connection)
```

### Error Handling Patterns
```python
# Patrón recomendado después de corrección
try:
    product = product_service.get_product_by_id(id)
    if product:
        stock = product.stock  # ✅ FUNCIONA
        name = product.nombre  # ✅ FUNCIONA
    else:
        # Manejar producto no encontrado
except Exception as e:
    # Manejar errores de BD
```

## Restricciones de Negocio

### Stock para Servicios
- **Regla**: Si categoria.tipo == 'SERVICIO' entonces producto.stock == 0
- **Validación**: `validate_stock_for_category()`
- **Aplicación**: En create_product() y update_product()

### Validaciones Automáticas
- Nombres únicos de productos
- Categorías existentes
- Valores numéricos válidos
- Restricciones de stock por tipo

---

**Última Actualización**: 2025-05-26  
**Versión**: v2.0 - Post Corrección ProductService  
**Estado**: Validado y Funcional
