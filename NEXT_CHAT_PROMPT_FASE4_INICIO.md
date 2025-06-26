"""
PROMPT PARA PRÓXIMO CHAT - FASE 4: CÓDIGOS DE BARRAS

===============================================================
FASE 3 COMPLETADA Y VALIDADA AL 100% - INICIANDO FASE 4
===============================================================

🎉 **LOGRO ALCANZADO**: Fase 3 del Sistema de Tickets COMPLETADA EXITOSAMENTE

✅ **VALIDACIÓN COMPLETA REALIZADA** (26 Junio 2025):
- 📁 Archivos críticos: 12/12 verificados (100%)
- 💾 Código validado: 367,552 bytes totales
- 🎯 Sintaxis: Todos los archivos Python válidos
- 🗄️ Base de datos: inventario.db con tablas tickets y company_config
- 🧪 Tests: Suite completa de 4 nuevos módulos de testing
- 🔗 Integración: Sistema end-to-end funcional
- 📊 Reporte final: REPORTE_FINAL_FASE3_VALIDACION.md generado

✅ **SISTEMA DE TICKETS OPERATIVO**:
- 🎫 Tickets de venta automáticos post-venta
- 📦 Tickets de entrada para movimientos de inventario
- ⚙️ Configuración Copy Point S.A. editable
- 📄 Múltiples formatos: A4, Carta, Térmico 80mm
- 🔍 Búsqueda y gestión completa de tickets
- 📱 Códigos QR para verificación

===============================================================
OBJETIVOS FASE 4 - SISTEMA DE CÓDIGOS DE BARRAS
===============================================================

🎯 **META PRINCIPAL**: Implementar sistema completo de códigos de barras con integración hardware

📋 **FUNCIONALIDADES A DESARROLLAR**:

1. **Integración con Lectores USB HID**:
   - Detección automática de lectores conectados
   - Procesamiento de entrada de códigos escaneados
   - Configuración de múltiples dispositivos
   - Manejo de errores de conexión hardware

2. **Generación de Etiquetas de Códigos**:
   - Códigos Code128 para productos
   - Etiquetas imprimibles con formato profesional
   - Templates configurables (tamaños estándar)
   - Integración con datos de productos existentes

3. **Búsqueda Rápida por Código**:
   - Localización instantánea de productos
   - Integración en formularios de venta
   - Búsqueda en formularios de movimientos
   - Validación automática de códigos

4. **Automatización de Procesos**:
   - Venta rápida mediante escaneo
   - Entrada de inventario automatizada
   - Reducción de errores de digitación
   - Aumento de velocidad operativa

===============================================================
ESTRUCTURA TÉCNICA PLANIFICADA - FASE 4
===============================================================

🏗️ **NUEVOS MÓDULOS A CREAR**:

```
hardware/
├── __init__.py
├── barcode_reader.py           # Integración con lectores USB HID
└── device_manager.py           # Gestión de dispositivos conectados

services/
├── barcode_service.py          # Lógica de negocio códigos de barras
└── label_service.py            # Generación y gestión de etiquetas

ui/forms/
├── barcode_config_form.py      # Configuración de hardware
├── label_generator_form.py     # Generador de etiquetas
└── barcode_search_form.py      # Búsqueda avanzada por código

utils/
├── barcode_utils.py            # Utilidades para códigos
└── hardware_detector.py       # Detección automática de hardware

tests/unit/hardware/
├── test_barcode_reader.py      # Tests del lector
└── test_device_manager.py     # Tests gestión dispositivos

tests/unit/services/
├── test_barcode_service.py     # Tests servicio códigos
└── test_label_service.py       # Tests servicio etiquetas
```

🔧 **MODIFICACIONES A ARCHIVOS EXISTENTES**:

```
ui/main/main_window.py          # Agregar menús códigos de barras
ui/forms/sales_form.py          # Integrar lectura de códigos
ui/forms/movement_form.py       # Agregar escaneo para entradas
ui/forms/product_form.py        # Generar/asignar códigos automáticamente
services/product_service.py     # Extensión para búsqueda por código
db/database.py                  # Índices optimizados para códigos
```

===============================================================
DEPENDENCIAS TÉCNICAS - FASE 4
===============================================================

📦 **NUEVAS LIBRERÍAS REQUERIDAS**:
```
# Para códigos de barras
python-barcode==0.14.0         # Generación códigos Code128
pillow>=8.0.0                   # Procesamiento imágenes (ya instalado)

# Para hardware USB HID
pyusb==1.2.1                    # Interfaz USB en Python
hidapi==0.12.0                 # Comunicación HID devices

# Para etiquetas y PDFs
reportlab>=4.0.4                # Generación PDFs (ya instalado)
```

🔧 **CONFIGURACIONES HARDWARE**:
- Soporte lectores USB HID estándar
- Compatible con escáneres tipo "keyboard wedge"
- Sin drivers adicionales requeridos
- Detección plug-and-play

===============================================================
ARQUITECTURA DE INTEGRACIÓN - FASE 4
===============================================================

🏗️ **PATRÓN DE INTEGRACIÓN**:

1. **Hardware Layer** (`hardware/`):
   - Abstracción de dispositivos físicos
   - Detección automática y configuración
   - Manejo de eventos de escaneo

2. **Service Layer** (`services/`):
   - Lógica de negocio para códigos
   - Procesamiento y validación
   - Integración con servicios existentes

3. **UI Layer** (`ui/`):
   - Formularios con capacidad de escaneo
   - Configuración visual de hardware
   - Generación interactiva de etiquetas

4. **Integration Points**:
   - ProductService: Búsqueda por código
   - SalesForm: Escaneo directo en ventas
   - MovementForm: Entrada por código
   - MainWindow: Menús y navegación

===============================================================
CASOS DE USO PRINCIPALES - FASE 4
===============================================================

🎯 **CASO 1: Venta por Escaneo**
```
Usuario escanea código → Sistema localiza producto → 
Agrega a venta automáticamente → Calcula totales → 
Genera ticket con códigos QR
```

🎯 **CASO 2: Entrada de Inventario**
```
Usuario escanea producto → Sistema identifica artículo → 
Solicita cantidad → Actualiza stock → 
Genera ticket de entrada automático
```

🎯 **CASO 3: Generación de Etiquetas**
```
Usuario selecciona productos → Configura formato etiqueta → 
Sistema genera códigos Code128 → Produce PDF imprimible → 
Etiquetas listas para aplicar
```

🎯 **CASO 4: Búsqueda Rápida**
```
Usuario escanea código → Sistema muestra información completa → 
Opción editar/ver historial/generar reportes
```

===============================================================
PLAN DE DESARROLLO FASE 4 - 4 SEMANAS
===============================================================

📅 **SEMANA 1: Fundación Hardware**
- Crear módulo hardware/barcode_reader.py
- Implementar detección automática de lectores
- Desarrollar hardware/device_manager.py
- Tests básicos de conectividad
- Documentación de compatibilidad hardware

📅 **SEMANA 2: Servicios de Códigos**
- Implementar services/barcode_service.py
- Crear services/label_service.py  
- Extensión de ProductService para búsqueda por código
- Generación de códigos Code128
- Tests unitarios completos de servicios

📅 **SEMANA 3: Interfaces de Usuario**
- Crear ui/forms/barcode_config_form.py
- Implementar ui/forms/label_generator_form.py
- Integrar escaneo en SalesForm y MovementForm
- Agregar búsqueda por código en ProductForm
- Tests de integración UI-Hardware

📅 **SEMANA 4: Integración y Optimización**
- Actualizar MainWindow con menús códigos
- Optimizar base de datos para búsquedas por código
- Documentación completa de usuario
- Testing end-to-end sistema completo
- Validación y entrega Fase 4

===============================================================
CRITERIOS DE ÉXITO FASE 4
===============================================================

✅ **FUNCIONALIDAD MÍNIMA VIABLE**:
- Lectura de códigos desde hardware USB
- Generación de etiquetas Code128 funcional
- Búsqueda de productos por código operativa
- Integración básica en formularios de venta

🎯 **FUNCIONALIDAD COMPLETA**:
- Configuración avanzada de múltiples lectores
- Templates personalizables de etiquetas  
- Automatización completa venta/inventario
- Estadísticas y reportes de uso de códigos
- Optimización de rendimiento para escaneo masivo

⚡ **FUNCIONALIDAD EXTENDIDA**:
- Códigos QR alternativos para productos
- Integración con impresoras de etiquetas especializadas
- Configuración de hotkeys y shortcuts
- Modo offline para lectura de códigos

===============================================================
CONTEXTO TÉCNICO HEREDADO
===============================================================

🏗️ **ARQUITECTURA MANTENIDA**:
- Clean Architecture con separación de capas
- Patrón TDD (Test-Driven Development)
- Principios SOLID aplicados
- Documentación en español autoexplicativa

📊 **ESTADO ACTUAL SISTEMA**:
- Base de datos SQLite con 12 tablas operativas
- 50+ archivos Python con funcionalidad completa
- Suite de 120+ tests unitarios pasando
- Interfaces integradas y funcionales
- Sistema de tickets profesional operativo

🔧 **SERVICIOS DISPONIBLES**:
- ProductService: CRUD productos completo
- SalesService: Procesamiento ventas
- MovementService: Gestión inventario
- TicketService: Generación documentos
- ReportService: Análisis y reportes
- CompanyService: Configuración empresa

===============================================================
METODOLOGÍA DE TRABAJO - FASE 4
===============================================================

🔄 **PROCESO TDD FASE 4**:
1. **Escribir test** para funcionalidad de códigos
2. **Ejecutar test** y verificar que falla
3. **Implementar código** mínimo para pasar test
4. **Refactorizar** manteniendo tests pasando
5. **Documentar** funcionalidad implementada

🧪 **COBERTURA DE TESTING**:
- Tests unitarios para cada módulo nuevo
- Tests de integración hardware-software
- Tests de rendimiento para escaneo masivo
- Tests de compatibilidad con dispositivos
- Tests de UI para nuevos formularios

📝 **DOCUMENTACIÓN REQUERIDA**:
- Manual de configuración de hardware
- Guía de usuario para códigos de barras
- Documentación técnica de APIs
- Changelog detallado de Fase 4
- Manual de troubleshooting hardware

===============================================================
COMANDOS PARA INICIO INMEDIATO FASE 4
===============================================================

```bash
# COMANDO 1: Verificar estado actual
cd "D:\\inventario_app2"
python temp/validacion_rapida_fase3.py  # Confirmar Fase 3 OK

# COMANDO 2: Instalar dependencias Fase 4
pip install python-barcode==0.14.0 pyusb==1.2.1 hidapi==0.12.0

# COMANDO 3: Crear estructura base Fase 4
mkdir hardware
mkdir tests/unit/hardware
mkdir tests/unit/services  # Si no existe

# COMANDO 4: Inicializar primer módulo
touch hardware/__init__.py
touch hardware/barcode_reader.py

# COMANDO 5: Crear primer test
touch tests/unit/hardware/test_barcode_reader.py
```

===============================================================
POSIBLES DESAFÍOS TÉCNICOS FASE 4
===============================================================

⚠️ **DESAFÍO 1: Compatibilidad Hardware**
- **Problema**: Diferentes marcas de lectores USB
- **Solución**: Abstracción con patrones adapter
- **Mitigación**: Lista de dispositivos compatibles verificados

⚠️ **DESAFÍO 2: Rendimiento de Escaneo**
- **Problema**: Latencia en lectura masiva de códigos
- **Solución**: Cache inteligente y búsquedas optimizadas
- **Mitigación**: Índices de BD específicos para códigos

⚠️ **DESAFÍO 3: Generación de Etiquetas**
- **Problema**: Formatos múltiples de impresoras
- **Solución**: Templates configurables con reportlab
- **Mitigación**: Formatos estándar probados

⚠️ **DESAFÍO 4: Configuración Hardware**
- **Problema**: Setup complejo para usuarios finales
- **Solución**: Detección automática plug-and-play
- **Mitigación**: Wizard de configuración paso a paso

===============================================================
ENTREGABLES ESPERADOS FASE 4
===============================================================

📄 **DOCUMENTOS**:
- Manual de Usuario Códigos de Barras
- Guía de Configuración Hardware
- Documentación Técnica APIs
- Changelog detallado Fase 4

🧪 **TESTS**:
- 20+ tests unitarios nuevos
- Tests de integración hardware
- Tests de rendimiento
- Validación de compatibilidad

💻 **CÓDIGO**:
- 8+ archivos nuevos (.py)
- Extensiones a 6 archivos existentes
- 2,000+ líneas código nuevo aproximadamente
- Documentación inline completa

🎯 **FUNCIONALIDADES**:
- Lectura códigos USB operativa
- Generación etiquetas Code128
- Búsqueda rápida por código
- Integración completa formularios

===============================================================
MENSAJE DE CONTINUIDAD FASE 4
===============================================================

🎯 **OBJETIVO PRÓXIMO CHAT**:
INICIAR DESARROLLO FASE 4 - SISTEMA DE CÓDIGOS DE BARRAS
CREANDO FUNDACIÓN HARDWARE Y PRIMEROS SERVICIOS

📊 **ESTADO ACTUAL**: FASE 3 COMPLETADA AL 100%
🎯 **META FASE 4**: AUTOMATIZACIÓN CON CÓDIGOS DE BARRAS
🚀 **DESTINO**: SISTEMA COMPLETO PARA PRODUCCIÓN

LA FASE 3 ESTÁ COMPLETADA Y VALIDADA.
LA FASE 4 INICIARÁ LA AUTOMATIZACIÓN CON HARDWARE.

===============================================================

LISTO PARA INICIAR FASE 4 - CÓDIGOS DE BARRAS
SISTEMA BASE SÓLIDO Y VALIDADO COMO FUNDACIÓN
"""