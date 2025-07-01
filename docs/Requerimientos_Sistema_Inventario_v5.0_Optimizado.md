# Requerimientos del Sistema de Gestión de Inventario: vers.5.0 - Optimizado

## **1. Arquitectura del Sistema**

- Sistema de escritorio desarrollado en Python con interfaz gráfica en Tkinter
- Base de datos SQLite para almacenamiento local
- Arquitectura modular por capas (UI, Servicios, Base de datos)
- Soporte para lector de códigos de barras USB como dispositivo de entrada opcional

## **2. Gestión de Datos - Estructura Unificada**

### **2.1 Categorías**
- Operaciones CRUD (Crear, leer, actualizar y eliminar)
- Validación para evitar eliminación de categorías con productos asociados
- Campos de categorías:
  - `id_categoria`: INTEGER PRIMARY KEY AUTOINCREMENT
  - `nombre`: VARCHAR(60) NOT NULL
  - `tipo`: VARCHAR(20) NOT NULL ('MATERIAL' o 'SERVICIO')

### **2.2 Productos - Tabla Unificada**
- Operaciones CRUD para productos
- Tabla única para materiales y servicios
- El ID del producto es también su código de barras
- Campos unificados:
  - `id_producto`: INTEGER PRIMARY KEY AUTOINCREMENT
  - `nombre`: VARCHAR(60) NOT NULL
  - `id_categoria`: INTEGER FOREIGN KEY
  - `stock`: INTEGER DEFAULT 0 (solo relevante para materiales)
  - `costo`: DECIMAL(10,4) DEFAULT 0
  - `precio`: DECIMAL(10,2) DEFAULT 0
  - `tasa_impuesto`: DECIMAL(5,2) DEFAULT 0 (porcentaje, 0 = exento)
  - `activo`: BOOLEAN DEFAULT 1

### **2.3 Clientes**
- Operaciones para crear, leer y actualizar clientes
- Creación opcional al momento de generar ventas
- Campos de clientes:
  - `id_cliente`: INTEGER PRIMARY KEY AUTOINCREMENT
  - `nombre`: VARCHAR(60) NOT NULL
  - `ruc`: VARCHAR(20)
  - `activo`: BOOLEAN DEFAULT 1

### **2.4 Sistema de Movimientos Unificado**
- Tabla única para todos los movimientos de inventario
- Tipos de movimiento: 'ENTRADA', 'VENTA', 'AJUSTE'
- Entrada de datos manual o por lector de código de barras
- Campos unificados:
  - `id_movimiento`: INTEGER PRIMARY KEY AUTOINCREMENT
  - `id_producto`: INTEGER FOREIGN KEY
  - `tipo_movimiento`: VARCHAR(20) NOT NULL
  - `cantidad`: INTEGER NOT NULL (positivo para entradas, negativo para salidas)
  - `fecha_movimiento`: DATETIME DEFAULT CURRENT_TIMESTAMP
  - `responsable`: VARCHAR(60) NOT NULL
  - `id_venta`: INTEGER FOREIGN KEY (opcional, para movimientos de venta)
  - `observaciones`: TEXT

### **2.5 Ventas**
- Registro de transacciones de venta
- Campos de ventas:
  - `id_venta`: INTEGER PRIMARY KEY AUTOINCREMENT
  - `fecha_venta`: DATETIME DEFAULT CURRENT_TIMESTAMP
  - `id_cliente`: INTEGER FOREIGN KEY (opcional)
  - `subtotal`: DECIMAL(10,2) DEFAULT 0
  - `impuestos`: DECIMAL(10,2) DEFAULT 0
  - `total`: DECIMAL(10,2) DEFAULT 0
  - `responsable`: VARCHAR(60) NOT NULL

### **2.6 Detalle de Ventas**
- Desglose de productos/servicios por venta
- Campos:
  - `id_detalle`: INTEGER PRIMARY KEY AUTOINCREMENT
  - `id_venta`: INTEGER FOREIGN KEY
  - `id_producto`: INTEGER FOREIGN KEY
  - `cantidad`: INTEGER NOT NULL
  - `precio_unitario`: DECIMAL(10,2) NOT NULL
  - `subtotal_item`: DECIMAL(10,2) NOT NULL
  - `impuesto_item`: DECIMAL(10,2) DEFAULT 0

## **3. Funcionalidades de Códigos de Barras - Simplificadas**

- Lectura de códigos de barras 1D estándar
- Lector USB tipo HID sin configuración adicional
- El ID del producto funciona como código de barras
- Procesamiento directo para movimientos rápidos
- Generación opcional de etiquetas con códigos Code128

## **4. Gestión de Ventas - Optimizada**

- Registro de ventas mediante escaneo o entrada manual
- Soporte para múltiples productos en una venta
- Cálculo automático de impuestos basado en `tasa_impuesto`
- Discriminación automática de ítems gravados y exentos
- Asociación opcional de clientes para facturación
- Si en 'Categoria', `tipo` = 'SERVICIO' entonces 'Stock' = 0 

## **5. Reportes - Configurables**

### **5.1 Reporte de Movimientos**
- Configurable por tipo de movimiento, fechas y categorías
- Incluye entradas, ventas y ajustes de inventario
- Exportación a PDF

### **5.2 Reporte de Inventario Actual**
- Estado actual del inventario por fecha especificada
- Valor total y costo del inventario
- Desglose por categorías
- Solo aplica para productos tipo MATERIAL

### **5.3 Reporte de Ventas**
- Ventas por período con desglose de impuestos
- Detallado por producto o resumido por categoría
- Agrupación por días, meses o años
- Exportación a PDF

### **5.4 Reporte de Rentabilidad**
- Resumen de ingresos, costos y ganancias por período
- Análisis de productos más vendidos
- Exportación a PDF

## **6. Gestión de Tickets - Simplificada**

### **6.1 Configuración de Empresa**
- Copy Point S.A.
- RUC: 888-888-8888
- Dirección: Las Lajas, Las Cumbres, Panamá
- Teléfono: 6666-6666
- E-mail: copy.point@gmail.com

### **6.2 Tipos de Tickets**
- **Ticket de Entrada**: fecha, productos, cantidades, responsable, valor total
- **Ticket de Venta**: fecha, productos, cantidades, cliente (opcional), subtotal, impuestos, total, responsable

### **6.3 Funcionalidades**
- Visualización en pantalla
- Generación en formato PDF
- Impresión directa

## **7. Interfaz de Usuario - Simplificada**

- Ventana principal con menú de navegación claro
- Formularios unificados para crear/editar
- Validación de campos en tiempo real
- Gestión de errores con mensajes claros
- Autenticación básica con roles de usuario

## **8. Control de Usuarios**

### **8.1 Tipos de Usuario**
- **Administrador**: acceso completo al sistema
- **Vendedor**: acceso solo al módulo de ventas y consultas básicas

### **8.2 Tabla de Usuarios**
- `id_usuario`: INTEGER PRIMARY KEY AUTOINCREMENT
- `nombre_usuario`: VARCHAR(30) UNIQUE NOT NULL
- `password_hash`: VARCHAR(255) NOT NULL
- `rol`: VARCHAR(20) NOT NULL ('ADMIN' o 'VENDEDOR')
- `activo`: BOOLEAN DEFAULT 1

## **9. Orden de Desarrollo - Optimizado**

### **Fase 1: Base del Sistema**
1. Configuración de base de datos unificada
2. Modelo de datos y conexión SQLite
3. Autenticación básica de usuarios

### **Fase 2: Funcionalidades Core**
4. CRUD de categorías
5. CRUD de productos (tabla unificada)
6. CRUD de clientes
7. Sistema de movimientos unificado

### **Fase 3: Operaciones de Negocio**
8. Módulo de ventas
9. Cálculo automático de inventario
10. Generación de tickets

### **Fase 4: Reportes y Optimizaciones**
11. Reportes configurables
12. Interfaz pulida y validaciones
13. Integración de códigos de barras

### **Fase 5: Funcionalidades Avanzadas**
14. Importación/exportación de datos
15. Funcionalidades adicionales según necesidades

## **10. Requerimientos Técnicos**

- **Plataforma**: Windows (primario)
- **Lenguaje**: Python 3.8+
- **GUI**: Tkinter (estándar)
- **Base de datos**: SQLite3
- **Herramientas de desarrollo**:
  - Black (formateo de código)
  - isort (ordenamiento de imports)
  - mypy (verificación de tipos)
- **Documentación**: PEP 8 y formato Google
- **Pruebas**: unittest para casos críticos
- **Logging**: registro de errores y operaciones importantes

## **11. Funcionalidades Opcionales - Fase Posterior**

- Importación masiva desde Excel
- Múltiples formatos de exportación
- Integración con impresoras de etiquetas especializadas
- Backup automático de base de datos
- Reportes avanzados de análisis de tendencias

## **12. Beneficios de esta Optimización**

- **Desarrollo más rápido**: Reducción estimada del 35% en tiempo
- **Mantenimiento simplificado**: Menos código duplicado
- **Escalabilidad**: Base sólida para futuras expansiones
- **Usabilidad**: Interfaz más intuitiva y consistente
- **Confiabilidad**: Menos puntos de falla potencial

## **13. Consideraciones de Implementación**

- Implementar validaciones robustas en la capa de servicios
- Usar transacciones de base de datos para operaciones críticas
- Implementar sistema de logging detallado
- Crear datos de prueba para desarrollo y testing
- Documentar APIs internas para facilitar mantenimiento

---

**Versión**: 5.0 - Optimizado  
**Fecha**: Mayo 2025  
**Estado**: Aprobado para desarrollo  
**Próxima revisión**: Al completar Fase 2