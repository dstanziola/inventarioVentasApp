# Directorio del Sistema de Inventario - Funciones y Variables

## UserService (src/services/user_service.py) - OPTIMIZADO FASE 4A

### PATRÓN FASE 3 IMPLEMENTADO - 2025-07-02

#### **NUEVA ARQUITECTURA**
- **DatabaseHelper**: Operaciones BD seguras y optimizadas
- **ValidationHelper**: Validaciones robustas y estandarizadas  
- **LoggingHelper**: Logging estructurado y auditoría automática
- **Compatibilidad**: 100% compatible con LoginWindow existente

```python
# Inicialización optimizada
def __init__(self, db_connection: DatabaseConnection):
    self.db_connection = db_connection
    self.db_helper = DatabaseHelper(db_connection)
    self.validator = ValidationHelper()
    self.logger = LoggingHelper.get_service_logger('user_service')
```

### MÉTODOS OPTIMIZADOS - FASE 4A

#### `authenticate(username: str, password: str) -> Optional[Usuario]`
- **MEJORAS FASE 4A**:
  - Usa DatabaseHelper para consultas seguras
  - Logging automático de intentos de autenticación
  - Protección contra timing attacks (delay mínimo)
  - Validaciones robustas con ValidationHelper
  - Sanitización de entrada automática
- **Compatibilidad**: 100% compatible con LoginWindow
- **Seguridad**: Prevención de inyección SQL, enumeración de usuarios
- **Logging**: `LoggingHelper.log_authentication_attempt(username, success)`

#### `create_user(nombre_usuario: str, password: str, rol: str) -> Usuario`
- **MEJORAS FASE 4A**:
  - Validación avanzada de contraseñas con criterios de seguridad
  - Verificación de duplicados optimizada
  - Transacciones seguras con DatabaseHelper
  - Logging automático de operaciones
- **Validaciones**: Username 3-30 chars alfanuméricos, roles válidos
- **Contraseñas**: Criterios de fortaleza (longitud, caracteres especiales, etc.)

#### `get_user_by_id(user_id: int) -> Optional[Usuario]`
- **OPTIMIZACIÓN**: Usa DatabaseHelper.safe_execute()
- **Logging**: Acceso a datos registrado
- **Manejo de Errores**: Robusto con logging automático

#### `change_password(user_id: int, old_password: str, new_password: str) -> bool`
- **MEJORAS FASE 4A**:
  - Validación de fortaleza de nueva contraseña
  - Protección contra timing attacks
  - Logging detallado de cambios de contraseña
  - Validación robusta de contraseña actual

### NUEVOS MÉTODOS - FASE 4A

#### `get_users_by_role(role: str) -> List[Usuario]`
- **FUNCIÓN**: Obtener usuarios filtrados por rol específico
- **PARÁMETROS**: role ('ADMIN' o 'VENDEDOR')
- **RETORNO**: Lista de usuarios activos del rol especificado
- **OPTIMIZACIÓN**: Consulta SQL optimizada por índice de rol
- **USO**: `admins = user_service.get_users_by_role('ADMIN')`

#### `get_user_statistics() -> Dict[str, Any]`
- **FUNCIÓN**: Estadísticas agregadas del sistema de usuarios
- **RETORNO**: Dict con estadísticas completas
- **CAMPOS**:
  ```python
  {
      'total_users': int,        # Total de usuarios
      'active_users': int,       # Usuarios activos
      'inactive_users': int,     # Usuarios inactivos
      'admin_count': int,        # Conteo administradores
      'vendor_count': int,       # Conteo vendedores
      'generated_at': str        # Timestamp ISO
  }
  ```

### MÉTODOS PRIVADOS OPTIMIZADOS

#### `_user_exists_by_username(username: str, exclude_id: int = None) -> bool`
- **OPTIMIZACIÓN**: Usa DatabaseHelper para consulta optimizada
- **FUNCIONALIDAD**: Soporte para exclusión de ID (útil en updates)
- **PARÁMETROS**: username, exclude_id opcional para updates
- **USO INTERNO**: Validación de duplicados

#### `_hash_password(password: str) -> str`
- **CONSISTENCIA**: Mismo algoritmo que versión original
- **SEGURIDAD**: Salt consistente con sistema
- **LOGGING**: Errores registrados automáticamente

### MEJORAS DE SEGURIDAD - FASE 4A

#### **Validación Avanzada de Contraseñas**
```python
# Criterios de validación automática
password_validation = self.validator.validate_password_strength(password)
# Retorna: {'is_valid': bool, 'score': int, 'errors': list, 'recommendations': list}
```

#### **Protección contra Timing Attacks**
- Delay mínimo constante en autenticación
- Tiempo de respuesta consistente para usuarios válidos/inválidos
- Procesamiento independiente de resultado de validación

#### **Logging de Seguridad Automático**
- Intentos de autenticación (exitosos y fallidos)
- Cambios de contraseña
- Creación/modificación de usuarios
- Operaciones administrativas

#### **Prevención de Inyección SQL**
- Todas las consultas usan DatabaseHelper.safe_execute()
- Parámetros sanitizados automáticamente
- Validación de entrada robusta

### COMPATIBILIDAD GARANTIZADA

#### **LoginWindow (src/ui/auth/login_window.py)**
- **MÉTODO CRÍTICO**: `authenticate()` mantiene misma firma
- **RETORNO**: Mismo tipo (Usuario o None)
- **COMPORTAMIENTO**: Idéntico desde perspectiva del cliente
- **MEJORAS**: Transparentes al código cliente

#### **Métodos Deprecated (Compatibilidad)**
```python
# Mantenidos para compatibilidad, redirigen a ValidationHelper
def _validate_username(self, username: str) -> bool
def _validate_password(self, password: str) -> bool  
def _validate_role(self, role: str) -> bool
```

### CONFIGURACIÓN DE LOGGING

#### **Logger Específico de Servicio**
```python
self.logger = LoggingHelper.get_service_logger('user_service')
# Genera logs en: logs/inventory_system.log
# Formato: timestamp - servicio - nivel - función:línea - mensaje
```

#### **Tipos de Log Generados**
- **INFO**: Operaciones exitosas, inicialización
- **WARNING**: Intentos de autenticación fallidos, validaciones fallidas
- **ERROR**: Errores de base de datos, excepciones
- **DEBUG**: Acceso a datos, operaciones internas

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

## Tests Agregados

### test_product_service_fase3_optimization.py - FASE 5A CRÍTICO
- **Ubicación**: `tests/test_product_service_fase3_optimization.py`
- **Clase**: `TestProductServiceFase3Optimization`
- **Función**: Test crítico para migrar ProductService FASE 1 → FASE 3
- **PROBLEMA IDENTIFICADO**: ProductService sin helpers mientras otros servicios están en FASE 3
- **Funcionalidades Testeadas**:
  - Verificación helpers FASE 3 (DatabaseHelper, ValidationHelper, LoggingHelper) (3 tests)
  - Performance optimizada vs FASE 1 (3 tests)
  - Validaciones usando ValidationHelper
  - Logging usando LoggingHelper
  - Operaciones BD con DatabaseHelper
  - Compatibilidad FASE 1 → FASE 3 preservada
  - Integración con servicios ya optimizados
  - Funcionalidad CRUD completa preservada
  - Reglas de negocio mantenidas
- **Total Tests**: 13 tests críticos optimización
- **Performance Benchmarks**:
  - Crear 50 productos: < 2 segundos
  - 50 búsquedas: < 1 segundo
  - 20 listados: < 1 segundo
- **Mock Strategy**: Helpers mock si no disponibles + performance real
- **Cobertura**: ProductService optimization completa
- **Prioridad**: MÁXIMA - Componente más crítico faltante FASE 5A

### test_category_form_basic.py - FASE 5A
- **Ubicación**: `tests/test_category_form_basic.py`
- **Clase**: `TestCategoryFormBasic`
- **Función**: Suite completa de tests para CategoryForm UI
- **Funcionalidades Testeadas**:
  - Inicialización correcta de ventana (4 tests)
  - Elementos UI críticos presentes
  - Estados iniciales de botones/campos
  - Carga de datos desde CategoryService
  - Búsqueda y filtros en tiempo real
  - Selección y manejo de eventos TreeView
  - Modos nuevo/editar/cancelar
  - Validaciones de formulario
  - Integración CRUD con servicios
  - Manejo de errores y casos edge
  - Protocolo de cierre de ventana
- **Total Tests**: 15 tests críticos
- **Mock Strategy**: Database temporal + ServiceMocking
- **Cobertura**: UI functionality completa

### test_client_form_basic.py - FASE 5A
- **Ubicación**: `tests/test_client_form_basic.py`
- **Clase**: `TestClientFormBasic`
- **Función**: Suite completa de tests para ClientForm UI
- **Funcionalidades Testeadas**:
  - Inicialización ventana y servicios (4 tests)
  - Presencia elementos UI y estados iniciales
  - Carga datos ClientService con/sin RUC
  - Búsqueda en tiempo real por nombre
  - Selección clientes en TreeView
  - Modos nuevo/editar cliente
  - Validaciones campo nombre requerido
  - RUC opcional vs obligatorio
  - Integración CRUD con ClientService
  - Operaciones crear/actualizar/desactivar
  - Manejo errores y casos edge
  - Casos específicos clientes sin RUC
- **Total Tests**: 20 tests críticos
- **Mock Strategy**: Database temporal + Service integration
- **Cobertura**: ClientForm functionality completa

### test_models_validation.py - FASE 5A CRÍTICO NUEVO
- **Ubicación**: `tests/test_models_validation.py`
- **Clase**: `TestModelsValidation`
- **Función**: Test crítico para validación completa de modelos de datos
- **Objetivo**: Completar gap crítico #1 - Validación de integridad de modelos
- **Funcionalidades Testeadas**:
  - Validación Categoria: creación, tipos, nombres, integridad BD (4 tests)
  - Validación Producto: creación, decimales, stock, FK categoría (4 tests)
  - Validación Cliente: creación, RUC, email (3 tests)
  - Validación Usuario: creación, roles, constraints únicos (3 tests)
  - Validación Venta: creación, cálculos, FK cliente (3 tests)
  - Validación Movimiento: creación, tipos, signos cantidad (3 tests)
  - Integridad Relacional: cascade delete, tipos de datos (2 tests)
- **Total Tests**: 22 tests críticos de validación
- **Mock Strategy**: Database temporal + validaciones reales
- **Cobertura**: Modelos de datos completa
- **Prioridad**: MÁXIMA - Gap crítico #1 completado
- **Estado**: CREADO - Listo para ejecución

### test_user_service_optimization.py - FASE 4A
- **Ubicación**: `tests/optimization/test_user_service_optimization.py`
- **Clases**: 
  - `TestUserServiceOptimization`: Tests principales de patrón FASE 3
  - `TestUserServiceSecurityEnhancements`: Tests específicos de seguridad
- **Tests Críticos**:
  - `test_fase3_pattern_implementation()`: Validar patrón FASE 3
  - `test_authenticate_compatibility_maintained()`: Compatibilidad LoginWindow
  - `test_enhanced_password_validation()`: Validaciones robustas
  - `test_logging_implementation()`: Logging automático
  - `test_security_validations_robust()`: Prevención vulnerabilidades
  - `test_get_users_by_role_new_method()`: Nuevo método por rol
  - `test_get_user_statistics_new_method()`: Estadísticas de usuarios

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
user_service = UserService(db_connection)  # FASE 4A optimizado
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

## Helpers FASE 3 (src/helpers/)

### DatabaseHelper (database_helper.py)
- **FUNCIÓN**: Operaciones de BD seguras y optimizadas
- **MÉTODOS PRINCIPALES**:
  - `safe_execute(query, params, fetch_mode)`: Ejecución segura
  - `safe_execute_with_commit(query, params)`: Con commit automático
  - `transaction()`: Context manager para transacciones
  - `record_exists(table, where, params)`: Verificación de existencia
- **VENTAJAS**: Manejo de errores, logging, transacciones robustas

### ValidationHelper (validation_helper.py)
- **FUNCIÓN**: Validaciones robustas y estandarizadas
- **MÉTODOS PRINCIPALES**:
  - `validate_username(username)`: Formato de username
  - `validate_password_strength(password)`: Fortaleza de contraseña
  - `validate_role(role)`: Roles válidos del sistema
  - `validate_email(email)`: Formato de email
  - `sanitize_string(value, max_length)`: Limpieza de cadenas
- **VENTAJAS**: Criterios consistentes, mensajes estandarizados

### LoggingHelper (logging_helper.py)
- **FUNCIÓN**: Logging estructurado y configuración centralizada
- **MÉTODOS PRINCIPALES**:
  - `get_service_logger(service_name)`: Logger específico de servicio
  - `log_authentication_attempt(username, success)`: Intentos de login
  - `log_user_action(user_id, action, details)`: Acciones de usuario
  - `log_database_operation(table, operation, record_id)`: Operaciones BD
- **CONFIGURACIÓN**: Rotación automática, formato estructurado

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

## CORRECCIONES DE BUGS UI - 2025-07-02

### Bug 1 Corregido: MovementForm - Acceso a Objetos Producto
**Problema**: Error "'productos' object is not subscriptable" en movement_form.py
**Causa**: MovementForm usaba `producto['key']` cuando ProductService devuelve objetos Producto
**Solución**: Cambiar a `producto.key` (acceso por atributo)

**Métodos Corregidos**:
- `load_productos()`: `producto['id_producto']` → `producto.id_producto`
- `on_producto_selected()`: `producto['id_producto']` → `producto.id_producto`
- `validate_form_data()`: `getattr(producto, 'stock', 0)` para acceso seguro
- `get_form_data()`: `producto.id_producto` consistente

### Bug 2 Corregido: SalesForm - Procesamiento Real de Ventas
**Problema**: Ventas no restaban del stock, solo mostraban mensaje "en desarrollo"
**Causa**: `_process_sale()` no usaba SalesService para procesar ventas reales
**Solución**: Implementar procesamiento real con SalesService

**Cambios Implementados**:
- Configuración correcta de SalesService con dependencias
- `_process_sale()` ahora usa `sales_service.create_sale()`
- Agregar productos con `sales_service.add_product_to_sale()`
- Stock se actualiza automáticamente
- Movimientos de inventario se registran automáticamente

### Estado Post-Correcciones
✅ MovementForm carga productos sin errores de subscript
✅ SalesForm procesa ventas reales y actualiza stock
✅ Ambas correcciones son compatibles
✅ Sistema funcional para gestión de inventario

## PLAN DE DESARROLLO RESTANTE

### FASE 4B (Próxima): Sistema de Reportes PDF Completo
- Reportes de movimientos configurables
- Reporte de inventario actual
- Reportes de ventas con impuestos
- Reporte de rentabilidad

### FASE 4C: Códigos de Barras y Hardware
- Integración lectores USB HID
- Generación de etiquetas
- Búsqueda optimizada por código

### FASE 5A: Testing Final y Performance
- Cobertura ≥95%
- Tests de performance
- Validación completa

### FASE 5B: Deployment y Documentación
- Scripts de instalación
- Documentación de usuario
- Backup automático

---

**Última Actualización**: 2025-07-02  
**Versión**: v3.0 - UserService Optimizado FASE 4A  
**Estado**: Patrón FASE 3 Implementado - Sistema Base Completo
