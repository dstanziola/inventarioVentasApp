# Instrucciones Claude v2 - Sistema de Inventario

**Fecha de Creación:** 2025-07-17
**Última Actualización:** 2025-07-19
**Versión:** 2.0.0
**Estado:** IMPLEMENTADO COMPLETAMENTE

## Resumen Ejecutivo

Este documento establece las instrucciones específicas para el desarrollo del Sistema de Inventario Copy Point S.A. utilizando Claude Opus 4 bajo metodología atómica con Clean Architecture, TDD y DRY. Define protocolos obligatorios, estilo de código PEP8 y control de calidad >= 95%.

## Metodología de Desarrollo Atómica

### Principios Fundamentales

1. **Una funcionalidad por sesión:** Desarrollo incremental y controlado
2. **Entregables garantizados:** Cada sesión debe producir código funcional
3. **Secuencia obligatoria sin omisiones:** Flujo de trabajo inmutable
4. **Validación antes de integrar:** pytest, flake8, pylint, black, isort
5. **Control de versiones atómico:** Commits descriptivos y granulares

### Configuración de Claude

```yaml
Modelo: Claude Opus 4
Estilo: Formal, técnico, profesional
Pensamiento: Extendido y estructurado
Temperatura: 0.2 (precisión máxima)
Formato: Sin emojis, markdown estándar
```

## Secuencia Obligatoria del Flujo de Trabajo

### **PROHIBIDO MODIFICAR ESTA SECUENCIA**

```
1. Cargar y comprender documentos del contexto
   - D:\inventario_app2\docs\architecture.md
   - D:\inventario_app2\docs\claude_commands.md
   - D:\inventario_app2\docs\claude_development_strategy.md
   - D:\inventario_app2\docs\claude_instructions_v2.md
   - D:\inventario_app2\docs\inventory_system_directory.md
   - D:\inventario_app2\docs\Requerimientos_Sistema_Inventario_v6_0.md

2. Analizar si la funcionalidad ya existe
   - Buscar implementaciones existentes
   - Verificar redundancias (comparar hashes)
   - Identificar conflictos potenciales

3. Validar consistencia y nombres existentes
   - Verificar nomenclatura PEP8
   - Validar estructura Clean Architecture
   - Comprobar patrones establecidos

4. Diseñar y escribir test
   - Test unitario primero (TDD)
   - Cobertura >= 95%
   - Casos de prueba exhaustivos

5. Escribir código solo para cumplir el test
   - Implementación mínima funcional
   - División en pasos pequeños y explícitos
   - Aplicar principios DRY

6. Validar sintaxis y consistencia
   - black (formateo)
   - isort (imports)
   - flake8 (linting)
   - pylint (análisis)
   - mypy (tipos)

7. Guardar cambios con commit atómico
   - Mensaje formato: feat:, fix:, refactor:
   - Descripción breve pero informativa
   - Un solo concepto por commit

8. Actualizar changelog y directorio
   - Formato .md con diff documentado
   - Actualizar inventory_system_directory.md
   - Registrar cambios estructurales

9. Esperar confirmación o nueva instrucción
   - No proceder sin autorización explícita
   - Reportar estado y próximos pasos

10. Gestionar límites de tokens
    - Si excede límite: resumen + prompt continuación
    - Mantener contexto entre sesiones
```

## Arquitectura Clean Architecture

### Estructura de Capas Obligatoria

```
src/
├── ui/                    # Capa de Presentación
│   ├── auth/             # Autenticación UI
│   ├── forms/            # Formularios específicos
│   ├── main/             # Ventana principal
│   ├── utils/            # Utilidades UI
│   └── widgets/          # Widgets reutilizables
├── application/          # Capa de Aplicación
│   └── services/         # Servicios de aplicación
├── domain/              # Capa de Dominio
│   └── services/        # Servicios de dominio
├── infrastructure/      # Capa de Infraestructura
│   ├── exports/         # Exportaciones
│   └── security/        # Seguridad
└── db/                  # Persistencia de datos
```

### Reglas de Dependencia

1. **Solo hacia adentro:** Dependencias apuntan hacia el centro
2. **UI → Application → Domain ← Infrastructure**
3. **Domain sin dependencias externas**
4. **Infrastructure implementa interfaces del Domain**

## Estándares de Código PEP8

### Convenciones de Nomenclatura

```python
# Clases: PascalCase
class ProductService:
    pass

# Funciones y variables: snake_case
def create_product():
    user_name = "example"

# Constantes: UPPER_CASE
MAX_ITEMS_PER_PAGE = 100

# Archivos: snake_case.py
product_service.py
inventory_repository.py

# Directorios: lowercase
src/domain/services/
```

### Formateo y Estilo

```python
# Longitud de línea: 88 caracteres
# Indentación: 4 espacios
# Strings: Comillas dobles preferidas
# Imports: Organizados con isort

# Ejemplo de función bien formateada
def process_inventory_movement(
    product_id: int,
    quantity: Decimal,
    movement_type: MovementType,
    user_id: int,
) -> InventoryMovement:
    """
    Procesa un movimiento de inventario con validaciones completas.
    
    Args:
        product_id: Identificador único del producto
        quantity: Cantidad del movimiento (positiva o negativa)
        movement_type: Tipo de movimiento (entrada/salida)
        user_id: Usuario que ejecuta el movimiento
        
    Returns:
        InventoryMovement: Objeto del movimiento creado
        
    Raises:
        ValidationError: Si los datos son inválidos
        BusinessRuleException: Si viola reglas de negocio
    """
    # Implementación...
    pass
```

## Test-Driven Development (TDD)

### Ciclo Red-Green-Refactor

```python
# 1. RED: Escribir test que falle
def test_create_product_with_valid_data():
    # Given
    product_data = {
        "code": "P001",
        "name": "Laptop HP",
        "price": Decimal("1500.00"),
        "stock_min": 5,
        "stock_max": 100
    }
    
    # When
    product = ProductService.create_product(product_data)
    
    # Then
    assert product.code == "P001"
    assert product.name == "Laptop HP"
    assert product.price == Decimal("1500.00")

# 2. GREEN: Implementación mínima para pasar test
class ProductService:
    @staticmethod
    def create_product(product_data):
        return Product(
            code=product_data["code"],
            name=product_data["name"],
            price=product_data["price"]
        )

# 3. REFACTOR: Mejorar sin romper tests
```

### Estructura de Tests

```
tests/
├── unit/                 # Pruebas unitarias
│   ├── domain/          # Tests de entidades y servicios
│   ├── application/     # Tests de servicios de aplicación
│   └── infrastructure/  # Tests de repositories
├── integration/         # Pruebas de integración
│   ├── api/            # Tests de endpoints
│   ├── database/       # Tests de persistencia
│   └── ui/             # Tests de interfaz
└── e2e/                # Pruebas end-to-end
    └── scenarios/      # Escenarios completos
```

## Principio DRY (Don't Repeat Yourself)

### Detección de Redundancias

```python
# PROHIBIDO: Código duplicado
def validate_product_code_format(code):
    if not code or len(code) < 3:
        raise ValidationError("Invalid code")

def validate_supplier_code_format(code):
    if not code or len(code) < 3:
        raise ValidationError("Invalid code")

# CORRECTO: Código reutilizable
def validate_code_format(code: str, entity_type: str) -> None:
    """Valida formato de código para cualquier entidad."""
    if not code or len(code) < 3:
        raise ValidationError(f"Invalid {entity_type} code format")

# Uso
validate_code_format(product_code, "product")
validate_code_format(supplier_code, "supplier")
```

### Estrategias de Reutilización

1. **Funciones utilitarias:** Operaciones comunes
2. **Clases base:** Comportamiento compartido
3. **Mixins:** Funcionalidad opcional
4. **Decoradores:** Aspectos transversales
5. **Factory patterns:** Creación de objetos

## Control de Calidad

### Herramientas Obligatorias

```bash
# Formateo automático
black src/ tests/ --line-length 88

# Ordenamiento de imports
isort src/ tests/ --profile black

# Análisis estático
flake8 src/ tests/ --max-line-length 88

# Análisis avanzado
pylint src/ tests/ --rcfile=.pylintrc

# Verificación de tipos
mypy src/ --strict

# Ejecutar tests con cobertura
pytest tests/ --cov=src --cov-report=html --cov-fail-under=95
```

## Configuración de Herramientas

### Configuración pyproject.toml

```toml
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["src"]
known_third_party = ["pytest", "pyqt6", "sqlalchemy"]

[tool.coverage.run]
source = ["src"]
branch = true
omit = [
    "*/tests/*",
    "*/venv/*",
    "*/migrations/*",
    "*/scripts/*",
    "*/__init__.py",
    "*/config.py"
]

[tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:",
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod"
]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true
```

### Configuración .pylintrc

```ini
[MASTER]
extension-pkg-whitelist=pydantic
load-plugins=pylint.extensions.docparams

[MESSAGES CONTROL]
disable=
    missing-docstring,
    too-few-public-methods,
    import-error,
    no-name-in-module

[FORMAT]
max-line-length=88
max-module-lines=1000
indent-string='    '

[DESIGN]
max-args=7
max-locals=15
max-returns=6
max-branches=12
max-statements=50

[SIMILARITIES]
min-similarity-lines=4
ignore-comments=yes
ignore-docstrings=yes
ignore-imports=no
```

### Configuración pytest.ini

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --strict-config
    --verbose
    --tb=short
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=95
    --junitxml=tests/reports/junit.xml
markers =
    unit: Pruebas unitarias
    integration: Pruebas de integración
    e2e: Pruebas end-to-end
    slow: Pruebas que tardan más de 5 segundos
filterwarnings =
    ignore::UserWarning
    ignore::DeprecationWarning
```

### Configuración .flake8

```ini
[flake8]
max-line-length = 88
select = E,W,F
ignore = 
    E203,  # whitespace before ':'
    E501,  # line too long (handled by black)
    W503,  # line break before binary operator
exclude = 
    .git,
    __pycache__,
    .venv,
    .eggs,
    *.egg,
    build,
    dist
max-complexity = 10
max-cognitive-complexity = 12
```

### Configuración .gitignore

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
PYTHONPATH

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
.pybuilder/
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
Pipfile.lock

# poetry
poetry.lock

# pdm
.pdm.toml

# PEP 582
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static type analyzer
.pytype/

# Cython debug symbols
cython_debug/

# PyCharm
.idea/

# VSCode
.vscode/

# Sistema de Inventario específico
data/backups/
logs/*.log
temp/*
!temp/.gitkeep
config/local_settings.py
*.db
!schema.sql

# Reportes y archivos temporales
tests/reports/
*.tmp
*.backup
```

## Prohibiciones Específicas

### Prohibiciones Metodológicas

**PROHIBIDO MODIFICAR:**
- La secuencia obligatoria del flujo de trabajo
- Los nombres de archivos sin autorización previa
- La estructura de Clean Architecture establecida
- Los patrones de nomenclatura PEP8 definidos

**PROHIBIDO EJECUTAR:**
- Saltarse pasos o fases de la metodología
- Implementar código sin tests previos
- Commits sin validación de herramientas
- Cambios silenciosos sin documentación

**PROHIBIDO CREAR:**
- Estructuras duplicadas o redundantes
- Dependencias circulares entre capas
- Código sin documentación apropiada
- Funcionalidades sin casos de prueba

### Detección de Violaciones

```python
# Ejemplo: Validación automática de prohibiciones
def validate_methodology_compliance(change_request):
    """Validar cumplimiento de metodología antes de implementar."""
    violations = []
    
    # Verificar secuencia de trabajo
    if not change_request.follows_required_sequence:
        violations.append("Violación: Secuencia obligatoria no seguida")
    
    # Verificar tests primero
    if not change_request.has_tests_before_code:
        violations.append("Violación: Código implementado sin tests")
    
    # Verificar nombres consistentes
    if not change_request.follows_naming_conventions:
        violations.append("Violación: Nomenclatura PEP8 no respetada")
    
    # Verificar documentación
    if not change_request.has_documentation:
        violations.append("Violación: Cambios sin documentar")
    
    if violations:
        raise MethodologyViolationException(violations)
    
    return True
```

### Consecuencias de Violaciones

1. **Violación Menor:** Advertencia y corrección inmediata
2. **Violación Mayor:** Rollback obligatorio del cambio
3. **Violación Crítica:** Suspensión del desarrollo hasta revisión
4. **Violación Sistémica:** Reevaluación completa de la metodología

## Manejo de Errores y Excepciones

### Jerarquía de Excepciones

```python
# Jerarquía de excepciones del sistema
class InventorySystemException(Exception):
    """Excepción base del sistema de inventario."""
    pass

class ValidationException(InventorySystemException):
    """Excepción para errores de validación."""
    pass

class BusinessRuleException(InventorySystemException):
    """Excepción para violaciones de reglas de negocio."""
    pass

class InfrastructureException(InventorySystemException):
    """Excepción para errores de infraestructura."""
    pass

class SecurityException(InventorySystemException):
    """Excepción para violaciones de seguridad."""
    pass

class MethodologyViolationException(InventorySystemException):
    """Excepción para violaciones de metodología."""
    pass
```

### Manejo de Errores por Capa

**Capa de Presentación (UI):**
```python
def handle_ui_errors(func):
    """Decorador para manejo de errores en UI."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationException as e:
            show_validation_error_dialog(str(e))
        except BusinessRuleException as e:
            show_business_error_dialog(str(e))
        except Exception as e:
            log_unexpected_error(e)
            show_generic_error_dialog()
    return wrapper
```

**Capa de Aplicación:**
```python
def handle_service_errors(func):
    """Decorador para manejo de errores en servicios."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationException:
            raise  # Re-lanzar para manejo en UI
        except InfrastructureException as e:
            logger.error(f"Infrastructure error: {e}")
            raise BusinessRuleException("Servicio temporalmente no disponible")
        except Exception as e:
            logger.error(f"Unexpected error in service: {e}")
            raise BusinessRuleException("Error interno del sistema")
    return wrapper
```

### Logging de Errores

```python
# Configuración de logging para errores
import logging
from pathlib import Path

def setup_error_logging():
    """Configurar logging específico para errores."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    error_logger = logging.getLogger("inventory.errors")
    error_logger.setLevel(logging.ERROR)
    
    # Handler para archivo de errores
    error_handler = logging.FileHandler(log_dir / "errors.log")
    error_handler.setLevel(logging.ERROR)
    
    # Formato detallado para errores
    error_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - '
        '%(filename)s:%(lineno)d - %(funcName)s - %(message)s'
    )
    error_handler.setFormatter(error_formatter)
    
    error_logger.addHandler(error_handler)
    return error_logger
```

## Commits Atómicos

### Estructura de Commits

**Formato Obligatorio:**
```
<tipo>(<ámbito>): <descripción>

<cuerpo opcional>

<pie opcional>
```

**Tipos Permitidos:**
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Cambios en documentación
- `style`: Cambios de formato (no afectan lógica)
- `refactor`: Refactorización sin cambio funcional
- `test`: Agregar o modificar tests
- `chore`: Cambios en build, dependencias, etc.

### Ejemplos de Commits Válidos

```bash
# Commit de nueva funcionalidad
feat(products): agregar validación de código de barras

Implementa validación de formato Code128 para códigos de barras
de productos, incluyendo verificación de dígito de control.

Resolves: #123

# Commit de corrección
fix(inventory): corregir cálculo de stock disponible

El cálculo no consideraba productos reservados en ventas pendientes.
Ahora se descuentan correctamente las reservas.

# Commit de refactorización
refactor(services): extraer lógica común de validación

Mueve validaciones repetidas a helper centralizado para
seguir principio DRY y facilitar mantenimiento.
```

### Validación Pre-commit

```python
# Script de validación pre-commit
def validate_commit_message(message):
    """Validar formato de mensaje de commit."""
    pattern = r'^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .{1,50}'
    
    if not re.match(pattern, message):
        raise CommitValidationException(
            f"Formato de commit inválido: {message}\n"
            f"Usar: <tipo>(<ámbito>): <descripción>"
        )
    
    return True

def validate_commit_atomicity(changed_files):
    """Validar que el commit sea atómico."""
    # Un commit debe abordar un solo concepto
    if len(changed_files) > 10:
        raise CommitValidationException(
            "Commit muy grande. Dividir en commits más pequeños."
        )
    
    # Verificar que los archivos estén relacionados
    file_categories = categorize_files(changed_files)
    if len(file_categories) > 2:
        raise CommitValidationException(
            "Commit aborda múltiples conceptos. Crear commits separados."
        )
    
    return True
```

## Detección de Redundancias

### Algoritmos de Detección

```python
import hashlib
import ast
from typing import Dict, List, Set

class RedundancyDetector:
    """Detector de código duplicado y redundancias."""
    
    def __init__(self):
        self.function_hashes: Dict[str, List[str]] = {}
        self.class_hashes: Dict[str, List[str]] = {}
    
    def analyze_file(self, file_path: str) -> Dict[str, List[str]]:
        """Analizar archivo para detectar redundancias."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        redundancies = {
            'duplicate_functions': [],
            'duplicate_classes': [],
            'similar_logic': []
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_hash = self._hash_function(node)
                if func_hash in self.function_hashes:
                    redundancies['duplicate_functions'].append(node.name)
                else:
                    self.function_hashes[func_hash] = [node.name]
            
            elif isinstance(node, ast.ClassDef):
                class_hash = self._hash_class(node)
                if class_hash in self.class_hashes:
                    redundancies['duplicate_classes'].append(node.name)
                else:
                    self.class_hashes[class_hash] = [node.name]
        
        return redundancies
    
    def _hash_function(self, func_node: ast.FunctionDef) -> str:
        """Generar hash de función para comparación."""
        # Extraer estructura de la función sin nombres específicos
        structure = self._extract_function_structure(func_node)
        return hashlib.md5(structure.encode()).hexdigest()
    
    def _extract_function_structure(self, func_node: ast.FunctionDef) -> str:
        """Extraer estructura de función para comparación."""
        structure_parts = []
        
        # Argumentos (tipos, no nombres)
        args_types = []
        for arg in func_node.args.args:
            if arg.annotation:
                args_types.append(ast.dump(arg.annotation))
        structure_parts.append("args:" + ",".join(args_types))
        
        # Estructura del cuerpo (sin literales específicos)
        body_structure = []
        for stmt in func_node.body:
            body_structure.append(type(stmt).__name__)
        structure_parts.append("body:" + ",".join(body_structure))
        
        return "|".join(structure_parts)
    
    def suggest_refactoring(self, redundancies: Dict[str, List[str]]) -> List[str]:
        """Sugerir refactorizaciones para eliminar redundancias."""
        suggestions = []
        
        if redundancies['duplicate_functions']:
            suggestions.append(
                f"Funciones duplicadas detectadas: {redundancies['duplicate_functions']}. "
                f"Considerar extraer a función común."
            )
        
        if redundancies['duplicate_classes']:
            suggestions.append(
                f"Clases duplicadas detectadas: {redundancies['duplicate_classes']}. "
                f"Considerar herencia o composición."
            )
        
        return suggestions
```

### Integración en Workflow

```python
def check_redundancies_before_commit():
    """Verificar redundancias antes de hacer commit."""
    detector = RedundancyDetector()
    changed_files = get_changed_files_from_git()
    
    total_redundancies = 0
    for file_path in changed_files:
        if file_path.endswith('.py'):
            redundancies = detector.analyze_file(file_path)
            total_redundancies += sum(len(v) for v in redundancies.values())
            
            if any(redundancies.values()):
                suggestions = detector.suggest_refactoring(redundancies)
                print(f"⚠️  Redundancias en {file_path}:")
                for suggestion in suggestions:
                    print(f"   - {suggestion}")
    
    if total_redundancies > 0:
        response = input("¿Continuar con commit a pesar de redundancias? (y/N): ")
        if response.lower() != 'y':
            raise RedundancyException("Commit cancelado por redundancias detectadas")
```

## Metodología de Sesiones

### Estructura de Sesión de Desarrollo

**Fase 1: Inicialización (5 minutos)**
1. Cargar contexto de documentos obligatorios
2. Verificar estado del repositorio
3. Confirmar objetivo específico de la sesión
4. Establecer criterios de éxito

**Fase 2: Análisis (10 minutos)**
1. Ejecutar detección de redundancias
2. Verificar funcionalidad existente
3. Validar consistencia arquitectónica
4. Identificar dependencias y conflictos

**Fase 3: Diseño TDD (15 minutos)**
1. Escribir tests que fallen (RED)
2. Definir interfaz mínima necesaria
3. Establecer criterios de aceptación
4. Verificar cobertura planificada

**Fase 4: Implementación (Variable)**
1. Código mínimo para pasar tests (GREEN)
2. Validación incremental cada 50 líneas
3. Refactoring continuo (REFACTOR)
4. Documentación en línea

**Fase 5: Validación (10 minutos)**
1. Ejecutar suite completa de tests
2. Validar herramientas de calidad
3. Verificar cobertura >= 95%
4. Confirmar cumplimiento arquitectónico

**Fase 6: Integración (5 minutos)**
1. Commit atómico con mensaje descriptivo
2. Actualizar documentación de cambios
3. Registrar en inventory_system_directory.md
4. Confirmar estado para próxima sesión

### Protocolo de Continuidad

```python
class SessionManager:
    """Gestor de continuidad entre sesiones de desarrollo."""
    
    def save_session_state(self, session_data: dict) -> str:
        """Guardar estado de sesión para continuidad."""
        state = {
            'timestamp': datetime.now().isoformat(),
            'completed_phase': session_data['current_phase'],
            'objective': session_data['objective'],
            'files_modified': session_data['files_modified'],
            'tests_status': session_data['tests_status'],
            'next_steps': session_data['next_steps'],
            'context_hash': self._generate_context_hash()
        }
        
        state_file = f"session_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(f"temp/{state_file}", 'w') as f:
            json.dump(state, f, indent=2)
        
        return self._generate_continuation_prompt(state)
    
    def _generate_continuation_prompt(self, state: dict) -> str:
        """Generar prompt para continuar en nueva sesión."""
        return f"""
Continuar desarrollo del Sistema de Inventario desde sesión anterior.

ESTADO ANTERIOR:
- Fase completada: {state['completed_phase']}
- Objetivo: {state['objective']}
- Archivos modificados: {', '.join(state['files_modified'])}
- Estado de tests: {state['tests_status']}

PRÓXIMOS PASOS:
{chr(10).join('- ' + step for step in state['next_steps'])}

INSTRUCCIÓN: 
Cargar contexto de documentos, validar estado actual y continuar 
desde la fase {state['completed_phase']} siguiendo la secuencia 
obligatoria del flujo de trabajo. Mantener metodología TDD y 
cumplimiento de Clean Architecture.
"""
    
    def load_session_state(self, state_file: str) -> dict:
        """Cargar estado de sesión anterior."""
        with open(f"temp/{state_file}", 'r') as f:
            return json.load(f)
```

## Gestión de Límites de Tokens

### Estrategias de Optimización

**Priorización de Información:**
1. **Crítica:** Secuencia obligatoria, prohibiciones, objetivo actual
2. **Alta:** Arquitectura Clean, estándares PEP8, estado de tests
3. **Media:** Documentación completa, contexto histórico
4. **Baja:** Detalles de implementación, logs extensos

**Técnicas de Compresión:**
```python
def compress_context_for_tokens(full_context: dict) -> dict:
    """Comprimir contexto para optimizar uso de tokens."""
    compressed = {
        'sequence': full_context['obligatory_sequence'],  # Siempre incluir
        'prohibitions': full_context['specific_prohibitions'],  # Crítico
        'current_objective': full_context['session_objective'],  # Esencial
        'architecture_summary': summarize_clean_architecture(),
        'test_status': get_test_status_summary(),
        'modified_files': full_context['recent_changes'][-10:],  # Solo recientes
    }
    
    # Incluir documentación crítica solo por referencia
    compressed['doc_references'] = {
        'instructions': 'claude_instructions_v2.md',
        'architecture': 'architecture.md', 
        'requirements': 'Requerimientos_Sistema_Inventario_v6_0.md'
    }
    
    return compressed

def generate_continuation_summary(session_progress: dict) -> str:
    """Generar resumen para continuación en nueva sesión."""
    return f"""
## RESUMEN DE PROGRESO

**Completado:**
{chr(10).join('✅ ' + item for item in session_progress['completed'])}

**En Progreso:**
{chr(10).join('🔄 ' + item for item in session_progress['in_progress'])}

**Pendiente:**
{chr(10).join('⏳ ' + item for item in session_progress['pending'][:5])}  # Solo top 5

**Estado de Tests:** {session_progress['test_coverage']}% cobertura
**Cumplimiento:** {session_progress['compliance_status']}

**PROMPT PARA CONTINUAR:**
Implementar siguiente item: {session_progress['next_item']}
Seguir secuencia obligatoria desde paso {session_progress['current_step']}
Mantener metodología TDD + Clean Architecture
"""
```

### Protocolo de División de Sesiones

**Cuando dividir:**
- Respuesta alcanza ~4000 tokens
- Implementación requiere >20 archivos modificados
- Sesión excede 2 horas de desarrollo
- Funcionalidad compleja necesita múltiples iteraciones

**Cómo dividir:**
1. Completar fase actual antes de dividir
2. Hacer commit atómico del progreso
3. Generar resumen de continuación
4. Actualizar documentación de estado
5. Proporcionar prompt específico para nueva sesión

---

## Cumplimiento y Validación Final

### Checklist de Cumplimiento por Sesión

**Metodología:**
- ✅ Secuencia obligatoria seguida sin omisiones
- ✅ TDD aplicado (RED → GREEN → REFACTOR)
- ✅ Principio DRY respetado
- ✅ Clean Architecture mantenida
- ✅ Prohibiciones específicas respetadas

**Calidad de Código:**
- ✅ PEP8 cumplido (black, isort, flake8)
- ✅ Análisis estático pasado (pylint, mypy)
- ✅ Cobertura de tests >= 95%
- ✅ Documentación actualizada
- ✅ Tests de integración ejecutados

**Gestión de Cambios:**
- ✅ Commit atómico realizado
- ✅ Mensaje de commit siguiendo convenciones
- ✅ Changelog actualizado
- ✅ Inventory_system_directory.md actualizado
- ✅ Conflictos resueltos

### Criterios de Aceptación

**Para Considerar Sesión Exitosa:**
1. Funcionalidad implementada completamente
2. Todos los tests pasan
3. Cobertura no disminuye
4. Documentación refleja cambios
5. No hay violaciones de metodología
6. Código pasa todas las validaciones

**Para Autorizar Continuación:**
1. Estado documentado apropiadamente
2. Próximos pasos claramente definidos
3. Sin issues críticos pendientes
4. Repositorio en estado consistente

---

## Información de Mantenimiento

**Documento:** Instrucciones Claude v2 - Sistema de Inventario  
**Versión:** 2.0.0  
**Estado:** IMPLEMENTADO COMPLETAMENTE  
**Fecha de Creación:** 2025-07-17  
**Última Actualización:** 2025-07-19  
**Mantenido por:** Equipo de Desarrollo + Claude Assistant  
**Próxima Revisión:** 2025-08-19  

**Archivos Relacionados:**
- `docs/architecture.md` - Arquitectura Clean del sistema
- `docs/claude_commands.md` - Comandos P01-P06 para Claude
- `docs/claude_development_strategy.md` - Estrategia de desarrollo
- `docs/inventory_system_directory.md` - Directorio del proyecto
- `docs/Requerimientos_Sistema_Inventario_v6_0.md` - Especificaciones
- `docs/app_test_plan.md` - Plan de pruebas TDD
- `docs/security_policy.md` - Políticas de seguridad

**Herramientas Configuradas:**
- `pyproject.toml` - Configuración de herramientas Python
- `.pylintrc` - Configuración de análisis estático
- `pytest.ini` - Configuración de tests
- `.flake8` - Configuración de linting
- `.gitignore` - Exclusiones de Git

---

**FIN DEL DOCUMENTO**  
**ESTADO: COMPLETO Y OPERATIVO**