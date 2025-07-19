# Documentación de Dependencias - Sistema de Inventario

**Fecha de Creación:** 2025-07-17
**Última Actualización:** 2025-07-17
**Versión:** 1.0.0
**Estado:** IMPLEMENTADO

## Resumen Ejecutivo

Este documento detalla todas las dependencias del Sistema de Inventario Copy Point S.A., organizadas por categorías funcionales y niveles de importancia crítica. El proyecto implementa Clean Architecture con patrones TDD y DRY.

## Dependencias de Producción

### Core Framework y Base de Datos

| Dependencia | Versión | Propósito | Criticidad |
|-------------|---------|-----------|------------|
| `SQLAlchemy` | >=2.0.20 | ORM principal para gestión de datos | CRÍTICA |
| `aiosqlite` | >=0.19.0 | Driver asíncrono SQLite | CRÍTICA |
| `alembic` | >=1.13.0 | Sistema de migraciones de BD | ALTA |
| `python-dotenv` | 1.0.0 | Gestión de variables de entorno | ALTA |

### Interfaz de Usuario

| Dependencia | Versión | Propósito | Criticidad |
|-------------|---------|-----------|------------|
| `PyQt6` | >=6.4.0 | Framework principal de UI | CRÍTICA |
| `tkcalendar` | >=1.6.1 | Widget calendario para fechas | MEDIA |
| `Pillow` | 10.1.0 | Procesamiento de imágenes | ALTA |

### API y Servicios Web

| Dependencia | Versión | Propósito | Criticidad |
|-------------|---------|-----------|------------|
| `fastapi` | >=0.110.0 | Framework API REST | ALTA |
| `uvicorn[standard]` | >=0.27.0 | Servidor ASGI para FastAPI | ALTA |
| `jinja2` | 3.1.2 | Motor de templates | MEDIA |

### Códigos de Barras y QR

| Dependencia | Versión | Propósito | Criticidad |
|-------------|---------|-----------|------------|
| `python-barcode` | 0.15.1 | Generación códigos de barras | ALTA |
| `qrcode` | 7.4.2 | Generación códigos QR | ALTA |
| `pyzbar` | 0.1.9 | Lectura códigos de barras | ALTA |

### Reportes y Documentos

| Dependencia | Versión | Propósito | Criticidad |
|-------------|---------|-----------|------------|
| `reportlab` | 4.0.4 | Generación de reportes PDF | CRÍTICA |
| `openpyxl` | 3.1.2 | Procesamiento archivos Excel | ALTA |
| `pandas` | 2.1.3 | Análisis y manipulación de datos | ALTA |

### Seguridad y Autenticación

| Dependencia | Versión | Propósito | Criticidad |
|-------------|---------|-----------|------------|
| `bcrypt` | 4.0.1 | Hash de contraseñas | CRÍTICA |

### Utilidades del Sistema

| Dependencia | Versión | Propósito | Criticidad |
|-------------|---------|-----------|------------|
| `psutil` | >=5.9.0 | Información del sistema | MEDIA |
| `colorama` | 0.4.6 | Colores en terminal | BAJA |
| `structlog` | >=23.1.0 | Sistema de logging estructurado | ALTA |

## Dependencias de Desarrollo

### Testing

| Dependencia | Versión | Propósito | Criticidad |
|-------------|---------|-----------|------------|
| `pytest` | >=7.4.0 | Framework de pruebas principal | CRÍTICA |
| `pytest-asyncio` | >=0.21.0 | Soporte pruebas asíncronas | ALTA |
| `pytest-cov` | >=4.1.0 | Cobertura de código | ALTA |
| `html-testRunner` | >=1.2.1 | Reportes HTML de pruebas | MEDIA |

### Análisis de Código

| Dependencia | Versión | Propósito | Criticidad |
|-------------|---------|-----------|------------|
| `mypy` | >=1.8.0 | Verificación de tipos estáticos | ALTA |
| `black` | -- | Formateo automático de código | ALTA |
| `isort` | -- | Ordenamiento de imports | ALTA |
| `flake8` | -- | Linting y análisis estático | ALTA |

### Documentación y Empaquetado

| Dependencia | Versión | Propósito | Criticidad |
|-------------|---------|-----------|------------|
| `pdoc3` | >=0.10.0 | Generación documentación API | MEDIA |
| `pyinstaller` | 5.13.0 | Empaquetado ejecutables | ALTA |

## Dependencias del Sistema (Built-in Python)

### Módulos Estándar Críticos

```python
# Gestión del sistema
import os
import sys
import pathlib
import configparser
import logging

# Interfaz gráfica nativa
import tkinter
from tkinter import messagebox, filedialog, ttk

# Base de datos
import sqlite3

# Utilidades
import json
import csv
import datetime
import decimal
import uuid
import hashlib
import re
import threading
import asyncio

# Testing
import unittest
```

## Arquitectura de Dependencias

### Clean Architecture - Capas y Sus Dependencias

```
┌─────────────────────────────────────┐
│           UI Layer (PyQt6)          │
├─────────────────────────────────────┤
│     Application Layer (Services)    │
├─────────────────────────────────────┤
│      Domain Layer (Pure Python)     │
├─────────────────────────────────────┤
│  Infrastructure Layer (SQLAlchemy)  │
└─────────────────────────────────────┘
```

### Inyección de Dependencias

- **Service Container:** Implementación propia
- **Repository Pattern:** SQLAlchemy + Repositorios abstractos
- **Factory Pattern:** Creación de servicios y componentes

## Configuración del Entorno

### Archivo pyproject.toml

```toml
[tool.black]
line-length = 88
target-version = ['py39']

[tool.isort]
profile = "black"
line_length = 88

[tool.flake8]
max-line-length = 88
exclude = .git,__pycache__,env
```

### Archivo pytest.ini

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --strict-markers --strict-config
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
```

## Dependencias por Funcionalidad

### Gestión de Inventario
- SQLAlchemy (persistencia)
- pandas (análisis)
- structlog (auditoría)

### Interface de Usuario
- PyQt6 (ventanas principales)
- tkcalendar (widgets fecha)
- Pillow (imágenes)

### Generación de Reportes
- reportlab (PDFs)
- openpyxl (Excel)
- python-barcode (códigos)
- qrcode (códigos QR)

### API y Integraciones
- fastapi (endpoints)
- uvicorn (servidor)
- jinja2 (templates)

### Seguridad
- bcrypt (passwords)
- python-dotenv (configuración)

## Versionado y Compatibilidad

### Versiones de Python Soportadas
- **Mínima:** Python 3.9
- **Recomendada:** Python 3.11
- **Máxima Probada:** Python 3.12

### Política de Actualización
- **Dependencias Críticas:** Actualizaciones menores automáticas
- **Dependencias Mayores:** Revisión manual obligatoria
- **Vulnerabilidades:** Actualización inmediata

## Instalación y Gestión

### Instalación de Dependencias de Producción

```bash
pip install -r requirements.txt
```

### Instalación Completa (Desarrollo)

```bash
pip install -r requirements.txt
pip install black isort flake8 pylint
```

### Verificación de Dependencias

```bash
# Verificar instalación
python -c "import pkg_resources; pkg_resources.require(open('requirements.txt').readlines())"

# Auditoría de seguridad
pip audit

# Lista de dependencias instaladas
pip freeze > installed_requirements.txt
```

## Dependencias Opcionales

### Desarrollo Avanzado
- `pylint` - Análisis avanzado de código
- `bandit` - Análisis de seguridad
- `memory_profiler` - Profiling de memoria

### Producción Empresarial
- `psycopg2` - Driver PostgreSQL
- `redis` - Cache distribuido
- `celery` - Cola de tareas asíncronas

## Notas de Compatibilidad

### Conflictos Conocidos
- **PyQt6 vs tkinter:** Utilizados en capas separadas
- **SQLAlchemy 2.0:** Sintaxis actualizada requerida
- **Python 3.12:** Algunas dependencias pueden requerir actualización

### Recomendaciones de Entorno
- **Entorno Virtual:** Obligatorio
- **Sistema Operativo:** Windows 10/11, Linux Ubuntu 20.04+
- **Memoria RAM:** Mínimo 4GB, Recomendado 8GB
- **Espacio en Disco:** Mínimo 500MB para dependencias

## Licencias

### Licencias de Dependencias Principales
- **SQLAlchemy:** MIT License
- **PyQt6:** GPL v3 / Commercial
- **FastAPI:** MIT License
- **reportlab:** BSD License
- **pytest:** MIT License

### Consideraciones Legales
- **PyQt6:** Requiere licencia comercial para distribución comercial
- **GPL Dependencies:** Verificar compatibilidad con licencia del proyecto

## Métricas de Dependencias

### Estadísticas Actuales
- **Total Dependencias:** 25 directas
- **Dependencias Críticas:** 7
- **Dependencias de Desarrollo:** 8
- **Tamaño Total Instalado:** ~150MB
- **Tiempo de Instalación:** ~5 minutos

### Evolución del Proyecto
- **v1.0.0:** 15 dependencias base
- **v1.5.0:** +5 dependencias (reportes)
- **v2.0.0:** +5 dependencias (API y testing)

## Gestión de Riesgos

### Dependencias Críticas Sin Alternativa
- **PyQt6:** Framework UI principal
- **SQLAlchemy:** ORM principal
- **reportlab:** Generación PDF

### Plan de Contingencia
- **PyQt6 → tkinter:** Migración completa UI
- **SQLAlchemy → Raw SQL:** Reimplementación DAL
- **reportlab → Alternativas:** weasyprint, xhtml2pdf

## Changelog de Dependencias

### v1.0.0 (2025-07-17)
- Documentación inicial de dependencias
- Análisis completo del proyecto existente
- Clasificación por criticidad y funcionalidad

---

**Mantenido por:** Sistema de Inventario Copy Point S.A.
**Contacto:** soporte-tecnico@copypoint.pa
**Próxima Revisión:** 2025-08-17