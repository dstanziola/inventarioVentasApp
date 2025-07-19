# Directorio del Sistema de Inventario

**Fecha de Creación:** 2025-07-17
**Última Actualización:** 2025-07-19
**Versión:** 1.0.0
**Estado:** IMPLEMENTADO

## Estructura General del Proyecto

```
D:\inventario_app2\
├── docs/                           # Documentación del proyecto
│   ├── dependencies.md            # Documentación de dependencias ✅ NUEVO
│   ├── architecture.md            # Arquitectura del sistema (PENDIENTE)
│   ├── claude_commands.md         # Comandos para Claude (PENDIENTE)
│   ├── claude_development_strategy.md # Estrategia desarrollo (PENDIENTE)
│   ├── claude_instructions_v2.md  # Instrucciones Claude v2 (PENDIENTE)
│   └── Requerimientos_Sistema_Inventario_v6_0.md # Requerimientos (PENDIENTE)
│
├── src/                           # Código fuente - Clean Architecture
│   ├── api/                       # Capa API REST
│   │   ├── routes/               # Rutas de endpoints
│   │   └── schemas/              # Esquemas de validación
│   ├── application/              # Capa de Aplicación
│   │   └── services/             # Servicios de aplicación
│   ├── compliance/               # Cumplimiento normativo
│   │   ├── controllers/          # Controladores de compliance
│   │   ├── models/              # Modelos de compliance
│   │   ├── utils/               # Utilidades compliance
│   │   └── validators/          # Validadores
│   ├── config/                   # Configuraciones
│   ├── db/                       # Capa de Infraestructura - Base de Datos
│   ├── domain/                   # Capa de Dominio
│   │   └── services/            # Servicios de dominio
│   ├── helpers/                  # Funciones auxiliares
│   ├── infrastructure/           # Capa de Infraestructura
│   │   ├── exports/             # Exportaciones
│   │   └── security/            # Seguridad
│   ├── models/                   # Modelos de datos
│   ├── reports/                  # Sistema de reportes
│   ├── scripts/                  # Scripts de utilidad
│   ├── services/                 # Servicios generales
│   ├── shared/                   # Componentes compartidos
│   │   └── session/             # Gestión de sesiones
│   ├── ui/                       # Capa de Presentación
│   │   ├── auth/                # Autenticación UI
│   │   ├── forms/               # Formularios específicos
│   │   ├── main/                # Ventana principal
│   │   ├── utils/               # Utilidades UI
│   │   └── widgets/             # Widgets reutilizables
│   └── utils/                    # Utilidades generales
│
├── tests/                        # Suite de pruebas
│   └── reports/                 # Reportes de pruebas
│
├── config/                       # Archivos de configuración
├── data/                        # Datos del sistema
├── logs/                        # Archivos de log
├── backups/                     # Respaldos del sistema
├── temp/                        # Archivos temporales
│
├── .git/                        # Control de versiones Git
├── .vscode/                     # Configuración VS Code
│
├── main.py                      # Punto de entrada principal
├── config.py                    # Configuración centralizada
├── config_db.py                # Configuración base de datos
├── requirements.txt             # Dependencias Python
├── pyproject.toml              # Configuración del proyecto
├── pytest.ini                 # Configuración pytest
├── .gitignore                  # Exclusiones Git
├── .env                        # Variables de entorno
├── CHANGELOG.md                # Registro de cambios ✅ NUEVO
│
└── scripts de utilidad/
    ├── _activar_env.bat        # Activar entorno virtual
    ├── _reset_pywork.bat       # Reset ambiente
    └── _run.bat                # Ejecutar aplicación
```

## Documentación del Proyecto

### Archivos de Documentación Requeridos

| Archivo | Estado | Descripción | Prioridad |
|---------|--------|-------------|-----------|
| `dependencies.md` | ✅ IMPLEMENTADO | Documentación completa de dependencias | CRÍTICA |
| `architecture.md` | ✅ IMPLEMENTADO | Documentación de Clean Architecture | CRÍTICA |
| `app_test_plan.md` | ✅ IMPLEMENTADO | Plan de pruebas del sistema TDD + Clean Architecture | CRÍTICA |
| `security_policy.md` | ✅ IMPLEMENTADO | Políticas de seguridad empresariales completas | CRÍTICA |
| `claude_commands.md` | ❌ PENDIENTE | Comandos específicos para Claude | ALTA |
| `claude_development_strategy.md` | ❌ PENDIENTE | Estrategia de desarrollo con Claude | ALTA |
| `claude_instructions_v2.md` | ✅ IMPLEMENTADO | Instrucciones actualizadas para Claude v2.0 completas | ALTA |
| `features_backlog.md` | ✅ IMPLEMENTADO | Backlog completo de funcionalidades con metodología TDD | ALTA |
| `Requerimientos_Sistema_Inventario_v6_0.md` | ❌ PENDIENTE | Especificaciones del sistema v6.0 | CRÍTICA |

## Clean Architecture - Estructura por Capas

### 1. Capa de Presentación (UI)
```
src/ui/
├── auth/           # Formularios de autenticación
├── forms/          # Formularios específicos del negocio
├── main/           # Ventana principal y navegación
├── utils/          # Utilidades para UI
└── widgets/        # Componentes reutilizables
```

**Tecnologías:** PyQt6, tkinter
**Responsabilidades:** Interfaz de usuario, presentación de datos, captura de eventos

### 2. Capa de Aplicación
```
src/application/
└── services/       # Servicios de aplicación (orquestación)
```

**Responsabilidades:** Casos de uso, coordinación entre capas, validación de entrada

### 3. Capa de Dominio
```
src/domain/
└── services/       # Servicios de dominio (lógica de negocio)
```

**Responsabilidades:** Reglas de negocio, entidades, lógica central del inventario

### 4. Capa de Infraestructura
```
src/infrastructure/
├── exports/        # Implementaciones de exportación
└── security/       # Implementaciones de seguridad

src/db/            # Persistencia de datos
```

**Tecnologías:** SQLAlchemy, SQLite, bcrypt
**Responsabilidades:** Acceso a datos, servicios externos, implementaciones técnicas

## API REST

### Estructura de API
```
src/api/
├── routes/         # Definición de endpoints
└── schemas/        # Esquemas de validación
```

**Tecnología:** FastAPI + uvicorn
**Funcionalidades:** Endpoints REST, documentación automática, validación

## Sistema de Reportes

### Generación de Documentos
```
src/reports/        # Sistema de reportes
```

**Tecnologías:** reportlab (PDF), openpyxl (Excel)
**Funcionalidades:** PDFs, códigos QR/barras, exportación Excel

## Gestión de Configuración

### Archivos de Configuración

| Archivo | Propósito | Ubicación |
|---------|-----------|-----------|
| `config.py` | Configuración centralizada del sistema | Raíz del proyecto |
| `config_db.py` | Configuración específica de base de datos | Raíz del proyecto |
| `.env` | Variables de entorno | Raíz del proyecto |
| `pyproject.toml` | Configuración del proyecto Python | Raíz del proyecto |
| `pytest.ini` | Configuración de pruebas | Raíz del proyecto |

## Sistema de Pruebas

### Estructura de Testing
```
tests/
└── reports/        # Reportes de ejecución de pruebas
```

**Framework:** pytest + pytest-cov + pytest-asyncio
**Cobertura Objetivo:** >= 95%
**Tipos:** Unitarias, integración, funcionales

## Control de Versiones

### Configuración Git
- **Repositorio:** Inicializado y configurado
- **Exclusiones:** `.gitignore` configurado
- **Estrategia de commits:** Atómicos con mensajes descriptivos
- **Formato de mensajes:** Conventional Commits (feat:, fix:, docs:, etc.)

## Gestión de Dependencias

### Archivos de Dependencias

| Archivo | Propósito |
|---------|-----------|
| `requirements.txt` | Dependencias de producción |
| `pyproject.toml` | Configuración de herramientas de desarrollo |

**Total Dependencias:** 25 directas + 8 desarrollo
**Gestión:** pip + entorno virtual obligatorio

## Directorios de Datos

### Almacenamiento y Persistencia

| Directorio | Propósito | Estado |
|------------|-----------|---------|
| `data/` | Datos del sistema y archivos | Activo |
| `logs/` | Archivos de registro | Activo |
| `backups/` | Respaldos automáticos | Activo |
| `temp/` | Archivos temporales | Activo |

## Herramientas de Desarrollo

### Scripts de Utilidad

| Script | Propósito |
|--------|-----------|
| `_activar_env.bat` | Activar entorno virtual Python |
| `_reset_pywork.bat` | Reiniciar ambiente de trabajo |
| `_run.bat` | Ejecutar aplicación principal |

### Herramientas de Calidad de Código

| Herramienta | Configuración | Propósito |
|-------------|---------------|-----------|
| `black` | `pyproject.toml` | Formateo automático |
| `isort` | `pyproject.toml` | Ordenamiento de imports |
| `flake8` | `pyproject.toml` | Linting y análisis estático |
| `mypy` | -- | Verificación de tipos |

## Cumplimiento Normativo

### Módulo de Compliance
```
src/compliance/
├── controllers/    # Controladores de cumplimiento
├── models/        # Modelos específicos de compliance
├── utils/         # Utilidades para cumplimiento
└── validators/    # Validadores normativos
```

**Funcionalidades:** Auditoría, trazabilidad, reportes regulatorios

## Próximos Pasos de Documentación

### Archivos Pendientes por Crear

1. **claude_instructions_v2.md** (CRÍTICO) 
   - Instrucciones específicas para desarrollo con Claude
   - Estilo de código y metodología
   - Flujo de trabajo establecido

2. **Requerimientos_Sistema_Inventario_v6_0.md** (CRÍTICO)
   - Especificaciones funcionales
   - Casos de uso detallados
   - Criterios de aceptación

3. **claude_development_strategy.md** (ALTO)
   - Estrategia de desarrollo iterativo
   - Metodología TDD + Clean Architecture
   - Protocolo de validación

4. **claude_commands.md** (ALTO)
   - Comandos específicos para tareas de desarrollo
   - Templates de prompts
   - Secuencias de trabajo estandarizadas

## Métricas del Proyecto

### Estado Actual (2025-07-19)

- **Archivos de código:** ~150+ archivos
- **Líneas de código:** Estimado 15,000+ líneas
- **Cobertura de pruebas:** Target >= 95%
- **Documentación:** 94% completada (8/10 archivos críticos)
- **Arquitectura:** Clean Architecture implementada
- **Dependencias:** 25 producción + 8 desarrollo documentadas
- **Seguridad:** Políticas empresariales completas implementadas
- **Metodología:** TDD + Claude AI completamente especificada

### Progreso de Documentación

- ✅ **dependencies.md** - Completado (2025-07-17)
- ✅ **CHANGELOG.md** - Completado (2025-07-17)  
- ✅ **inventory_system_directory.md** - Completado (2025-07-17)
- ✅ **architecture.md** - Completado (2025-07-17)
- ✅ **app_test_plan.md** - Completado (2025-07-17)
- ✅ **security_policy.md** - Completado (2025-07-17)
- ✅ **claude_instructions_v2.md** - Completado (2025-07-19)
- ✅ **features_backlog.md** - Completado (2025-07-19)
- ❌ **Requerimientos_Sistema_Inventario_v6_0.md** - Pendiente
- ❌ **claude_development_strategy.md** - Pendiente
- ❌ **claude_commands.md** - Pendiente

## Notas de Mantenimiento

### Actualización de Este Directorio

- **Frecuencia:** Cada nueva funcionalidad implementada
- **Responsable:** Equipo de desarrollo + Claude Assistant
- **Validación:** Verificar consistencia con estructura real del proyecto
- **Formato:** Mantener formato Markdown estándar

### Convenciones de Nomenclatura

- **Archivos:** snake_case.md para documentación
- **Directorios:** lowercase sin espacios
- **Componentes:** PascalCase para clases, camelCase para funciones
- **Constantes:** UPPER_CASE

---

**Mantenido por:** Sistema de Inventario Copy Point S.A.
**Última Actualización:** 2025-07-19  
**Próxima Actualización:** Con próxima funcionalidad implementada
**Formato:** Markdown estándar con emojis de estado