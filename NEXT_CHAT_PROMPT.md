"""
PROMPT PARA PRÓXIMO CHAT - CONTINUAR FASE 3: SISTEMA DE TICKETS

===============================================================
ESTADO ACTUAL - FASE 3 EN PROGRESO
===============================================================

✅ **COMPLETADO**:
1. Base de datos actualizada con tablas de tickets (v3)
2. Modelo Ticket completo y validado
3. Modelo CompanyConfig completo y validado  
4. Dependencias agregadas (qrcode)

🔄 **EN PROGRESO - SIGUIENTE PASO INMEDIATO**:
Crear y ejecutar tests unitarios TDD para los nuevos modelos

❌ **PENDIENTE**:
- Tests unitarios para Ticket y CompanyConfig
- TicketService (lógica de negocio)
- CompanyService (configuración de empresa)
- TicketGenerator (generación de PDFs)
- Interfaces de usuario (forms)
- Integración con sistema existente

===============================================================
CONTEXTO DEL PROYECTO
===============================================================

**EMPRESA**: Copy Point S.A.
- RUC: 888-888-8888
- Dirección: Las Lajas, Las Cumbres, Panamá
- Teléfono: 6666-6666
- Email: copy.point@gmail.com
- ITBMS: 7%

**ARQUITECTURA**: Clean Architecture + TDD estricto
**ESTADO GENERAL**: FASE 1 y FASE 2 completadas (70% del proyecto)
**BD ACTUAL**: SQLite v3 con sistema de tickets preparado

===============================================================
PRIMERA TAREA - CREAR TESTS UNITARIOS
===============================================================

**OBJETIVO INMEDIATO**: Completar los tests unitarios siguiendo TDD

**ARCHIVOS A CREAR**:

1. **Crear directorio faltante**:
```
tests/unit/models/
├── __init__.py
└── test_ticket.py          # ⚠️ ARCHIVO PARCIALMENTE INICIADO
└── test_company_config.py  # ❌ PENDIENTE CREAR
```

2. **tests/unit/models/test_ticket.py**:
- ✅ YA INICIADO - Continuar desde donde se quedó
- Tests para modelo Ticket (27 tests aprox.)
- Tests para TicketNumberGenerator
- Cobertura 95%+ requerida

3. **tests/unit/models/test_company_config.py**:
- ❌ CREAR COMPLETO
- Tests para validaciones de empresa
- Tests para cálculos de ITBMS
- Tests para formateo de datos
- Tests para métodos de configuración

**COMANDO PARA EJECUTAR TESTS**:
```bash
cd D:\inventario_app2
python -m pytest tests/unit/models/ -v --tb=short
```

===============================================================
SEGUNDA TAREA - SERVICIOS DE NEGOCIO
===============================================================

**DESPUÉS DE COMPLETAR TESTS**, crear servicios siguiendo TDD:

1. **services/ticket_service.py**:
- Generar tickets de venta y entrada
- Numeración automática consecutiva
- Registro en base de datos
- Búsqueda y reimpresión
- Integración con SalesService/MovementService

2. **services/company_service.py**:
- CRUD de configuración de empresa
- Singleton pattern (solo 1 configuración)
- Validaciones de datos corporativos
- Cálculos de impuestos centralizados

3. **Tests correspondientes**:
- tests/unit/services/test_ticket_service.py
- tests/unit/services/test_company_service.py

===============================================================
TERCERA TAREA - GENERACIÓN DE PDFs
===============================================================

1. **reports/ticket_generator.py**:
- Templates especializados para tickets
- Formato compacto (80mm térmicas)
- Formato A4 (impresoras normales)
- Integración con reportlab
- Códigos QR opcionales

2. **reports/templates/**:
- venta_ticket_template.py
- entrada_ticket_template.py
- base_ticket_template.py

===============================================================
CUARTA TAREA - INTERFACES DE USUARIO
===============================================================

1. **ui/forms/ticket_preview_form.py**:
- Preview de tickets antes de imprimir
- Configuración de impresora
- Opciones de formato

2. **ui/forms/company_config_form.py**:
- Edición de datos de empresa
- Validación en tiempo real
- Configuración de impuestos

3. **Integración con formularios existentes**:
- Agregar botón "Generar Ticket" en SalesForm
- Agregar botón "Ticket Entrada" en MovementForm
- Menú "Tickets" en MainWindow

===============================================================
ESTRUCTURA DE ARCHIVOS OBJETIVO FASE 3
===============================================================

```
models/                     # ✅ COMPLETADO
├── ticket.py              # ✅ Modelo Ticket
└── company_config.py      # ✅ Modelo CompanyConfig

tests/unit/models/          # 🔄 EN PROGRESO
├── test_ticket.py         # ⚠️ INICIADO
└── test_company_config.py # ❌ PENDIENTE

services/                   # ❌ PENDIENTE
├── ticket_service.py      # ❌ CREAR
└── company_service.py     # ❌ CREAR

tests/unit/services/        # ❌ PENDIENTE
├── test_ticket_service.py # ❌ CREAR
└── test_company_service.py# ❌ CREAR

reports/                    # ❌ PENDIENTE
├── ticket_generator.py    # ❌ CREAR
└── templates/             # ❌ CREAR DIRECTORIO
    ├── base_ticket_template.py
    ├── venta_ticket_template.py
    └── entrada_ticket_template.py

ui/forms/                   # ❌ PENDIENTE
├── ticket_preview_form.py # ❌ CREAR
└── company_config_form.py # ❌ CREAR
```

===============================================================
COMANDO INICIAL PARA PRÓXIMO CHAT
===============================================================

```bash
# 1. Crear directorios faltantes
mkdir -p "D:\\inventario_app2\\tests\\unit\\models"
cd "D:\\inventario_app2"

# 2. Verificar estado actual
python temp/quick_validate_syntax.py

# 3. Continuar con tests unitarios
```

===============================================================
ARCHIVOS CRÍTICOS CREADOS EN ESTA SESIÓN
===============================================================

**MODIFICADOS**:
- `db/database.py` - Tablas de tickets agregadas
- `requirements.txt` - qrcode agregado

**NUEVOS**:
- `models/ticket.py` - ✅ COMPLETO Y VALIDADO
- `models/company_config.py` - ✅ COMPLETO Y VALIDADO

**PARCIALES**:
- `tests/unit/models/test_ticket.py` - ⚠️ INICIADO, FALTA COMPLETAR

**VALIDACIÓN**:
- `temp/quick_validate_syntax.py` - Script para verificar sintaxis

===============================================================
METODOLOGÍA A SEGUIR
===============================================================

1. **TDD ESTRICTO**: Tests antes que implementación
2. **COBERTURA 95%+**: Para todos los servicios críticos
3. **VALIDACIÓN CONSTANTE**: python -m py_compile para cada archivo
4. **DOCUMENTACIÓN**: Español, formato Google, autoexplicativo
5. **ARQUITECTURA LIMPIA**: Separación UI/Services/Models
6. **SIN EMOJIS**: Código y documentación formal

===============================================================
CRITERIOS DE ÉXITO FASE 3
===============================================================

✅ Tests unitarios pasando al 100%
✅ TicketService funcional con numeración automática
✅ CompanyService con configuración editable
✅ Generación de PDFs profesionales
✅ Integración con SalesForm y MovementForm
✅ Preview e impresión de tickets
✅ Documentación técnica completa

**DURACIÓN ESTIMADA RESTANTE**: 2-3 semanas
**COMPLEJIDAD**: Media-Alta (por generación PDFs e integración)
**RIESGO**: Bajo (base sólida establecida)

===============================================================
NOTAS IMPORTANTES
===============================================================

1. **NO ROMPER FUNCIONALIDAD EXISTENTE**
   - Sistema de reportes (Fase 2) debe seguir funcionando
   - Ventas y movimientos no deben afectarse

2. **MANTENER ESTÁNDARES**
   - Mismo estilo de código que fases anteriores
   - Arquitectura limpia preservada
   - Tests obligatorios para todo

3. **DATOS DE EMPRESA**
   - Copy Point S.A. por defecto
   - Permitir personalización completa
   - ITBMS 7% configurable

**LISTO PARA CONTINUAR DESARROLLO FASE 3**
**PRÓXIMO OBJETIVO**: Completar tests unitarios de modelos
"""