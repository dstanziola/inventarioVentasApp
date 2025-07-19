# Instrucciones de Desarrollo para Claude IA - v2.0 (Integración Arquitectónica)

## 1. CONFIGURACIÓN OPERATIVA

### Comportamiento y Estilo
- **Estilo de comunicación**: Formal y técnico, sin emojis
- **Enfoque de respuesta**: Pensamiento extendido y detallado
- **Temperatura sugerida**: 0.2 (precisión y consistencia)
- **Lenguaje de programación**: Python

### Estructura de Directorios Obligatoria
```
D:\inventario_app2\
├── src/                    # Código fuente
├── tests/                  # Todos los tests
├── tests/reports/          # Reportes de tests (*.txt)
├── temp/                   # Archivos temporales
├── logs/                   # Archivos de log
├── backups/               # Respaldos del proyecto
└── docs/                  # Documentación del sistema
    ├── architecture.md               # Arquitectura del sistema
    ├── claude_instructions_v2.md     # Estas instrucciones
    └── inventory_system_directory.md # Directorio de funciones y errores
```

## 2. INTEGRACIÓN CON ARQUITECTURA DEL PROYECTO

### 2.1 Documentos de Referencia Obligatorios
- **Instrucciones Claude AI**: Metodología y proceso de desarrollo
- **Documento de Arquitectura**: Estructura técnica, patrones y principios
- **Jerarquía**: Instrucciones Claude (metodología) → Arquitectura (técnica)

### 2.2 Consultas Arquitectónicas Obligatorias
**ANTES DE CUALQUIER IMPLEMENTACIÓN:**
- ✅ Consultar `docs/architecture.md` para patrones aplicables
- ✅ Verificar capa arquitectónica correspondiente
- ✅ Validar interfaces y contratos definidos
- ✅ Confirmar principios SOLID y Clean Architecture

### 2.3 Mapeo de Componentes por Capa
```
Presentation Layer (src/presentation/):
├── views/          # Formularios Tkinter
├── controllers/    # Controladores de vista
└── components/     # Componentes reutilizables

Application Layer (src/application/):
├── services/       # Servicios de aplicación
├── commands/       # Comandos (escritura)
├── queries/        # Consultas (lectura)
└── validators/     # Validadores de negocio

Domain Layer (src/domain/):
├── entities/       # Entidades del dominio
├── value_objects/  # Objetos de valor
├── repositories/   # Interfaces de repositorio
├── services/       # Servicios de dominio
└── exceptions/     # Excepciones específicas

Infrastructure Layer (src/infrastructure/):
├── database/       # Persistencia
├── external/       # Servicios externos
├── logging/        # Sistema de logging
└── config/         # Configuración

Shared Layer (src/shared/):
├── constants/      # Constantes del sistema
├── utils/          # Utilidades generales
├── exceptions/     # Excepciones base
└── container/      # Contenedor de dependencias
```

## 3. METODOLOGÍA TEST DRIVEN DEVELOPMENT (TDD)

### Reglas Obligatorias
- **No escribir código sin test previo**
- **Cobertura mínima**: 95%
- **Herramientas**: `pytest` o `unittest`
- **Ejecución**: Tests automáticos en cada cambio
- **Reportes**: Guardar resultados en `tests/reports/` formato `.txt`

### Proceso TDD Integrado con Arquitectura
1. **Escribir test que falle** (siguiendo patrones arquitectónicos)
2. **Consultar arquitectura** para patrones aplicables
3. **Escribir código mínimo** respetando separación de capas
4. **Refactorizar** manteniendo principios SOLID
5. **Validar compliance** arquitectónica
6. **Repetir ciclo**

## 4. BUENAS PRÁCTICAS DE CODIFICACIÓN

### Obligatorias
- **Evitar duplicación de lógica** (principio DRY)
- **Código autoexplicativo** con nombres descriptivos
- **Validación de sintaxis** antes de integrar archivos `.py`
- **Commits atómicos** en control de versiones
- **Seguir patrones arquitectónicos** definidos en `docs/architecture.md`

### Prohibiciones Estrictas
- Variables mágicas (números/strings sin constantes)
- Nombres ambiguos o abreviados
- Funciones/clases sin documentación
- Código duplicado o redundante
- **Violación de separación de capas**
- **Incumplimiento de principios SOLID**

## 5. FLUJO DE TRABAJO INTEGRADO (OBLIGATORIO)

**ESTE FLUJO NO PUEDE SER MODIFICADO Y DEBE SEGUIRSE EN ORDEN:**

### 5.1 Análisis Inicial Integrado
- Cargar y comprender contexto completo (estructura, archivos, requerimientos)
- **CONSULTAR `docs/architecture.md`** para entender componentes afectados
- Analizar si la funcionalidad ya existe (nombres y lógica)
- **VALIDAR capa arquitectónica** correspondiente al cambio
- Validar consistencia de nombres y estructuras existentes
- **IDENTIFICAR patrones de diseño** aplicables

### 5.2 Planificación Arquitectónica
- **ANTES de modificar o escribir código**: presentar lista completa de archivos
- **VALIDAR contra estructura modular** definida en arquitectura
- **VERIFICAR interfaces y contratos** especificados
- **CONFIRMAR principios SOLID** aplicables
- **ESPERAR autorización explícita** antes de proceder

### 5.3 Implementación TDD con Compliance Arquitectónica
- Diseñar y escribir tests primero
- **APLICAR patrones Repository/Service** según arquitectura
- **RESPETAR separación de capas** estrictamente
- Escribir código mínimo necesario para cumplir el test
- **IMPLEMENTAR interfaces** definidas en arquitectura
- **USAR ServiceContainer** para inyección de dependencias
- Dividir implementación en pasos pequeños y explícitos
- Validar sintaxis, formato y consistencia lógica
- **EJECUTAR checklist de compliance** arquitectónica

### 5.4 Validación Cruzada
- **Validar compliance TDD**: Tests pasan, cobertura ≥95%
- **Validar compliance arquitectónica**: Patrones, capas, principios
- **Verificar nomenclatura** según estándares arquitectónicos
- Guardar todos los cambios
- Actualizar `changelog` (formato mínimo)
- Actualizar `inventory_system_directory.md`

### 5.5 Confirmación Integrada
- **Confirmar TDD**: Tests ejecutados exitosamente
- **Confirmar arquitectura**: Principios y patrones aplicados
- **ESPERAR confirmación** antes de continuar con siguiente sección
- No proceder a nuevas funcionalidades sin autorización

### 5.6 Manejo de Límites de Tokens
Si la respuesta excede límites, proporcionar:
- Resumen de máximo 500 palabras incluyendo:
  - Qué se ha completado (TDD + arquitectura)
  - Estado actual del desarrollo
  - Compliance arquitectónica alcanzada
  - Qué falta por implementar
  - Siguiente paso recomendado

## 6. CHECKLIST DE COMPLIANCE ARQUITECTÓNICA

### Validación Obligatoria Antes de Proceder
- [ ] **Separación de capas**: ¿Se respeta la arquitectura por capas?
- [ ] **Principios SOLID**: ¿Se aplican correctamente?
- [ ] **Patrón Repository**: ¿Se usa para acceso a datos?
- [ ] **Service Layer**: ¿Se encapsula lógica de aplicación?
- [ ] **Dependency Injection**: ¿Se usa ServiceContainer?
- [ ] **CQRS**: ¿Se separan comandos y consultas?
- [ ] **Nomenclatura**: ¿Sigue estándares arquitectónicos?
- [ ] **Interfaces**: ¿Se definen e implementan correctamente?
- [ ] **Value Objects**: ¿Se usan cuando es apropiado?
- [ ] **Exception Handling**: ¿Sigue jerarquía definida?

### Validación TDD Integrada
- [ ] **Test First**: ¿Se escribieron tests antes que código?
- [ ] **Cobertura**: ¿Se alcanza mínimo 95%?
- [ ] **Tests arquitectónicos**: ¿Validan patrones aplicados?
- [ ] **Mocks apropiados**: ¿Se usan según arquitectura?
- [ ] **Integration tests**: ¿Validan capas integradas?

## 7. DETECCIÓN DE REDUNDANCIAS ARQUITECTÓNICAS

### Proceso Obligatorio Antes de Escribir Código
1. **Buscar funciones similares** por nombre y propósito
2. **Consultar arquitectura** para patrones existentes
3. **Validar capa correcta** según responsabilidad
4. **Comparar lógica existente** para evitar duplicación
5. **Verificar interfaces** ya definidas
6. **Validar consistencia** con patrones establecidos
7. **Documentar decisiones** de reutilización vs nueva implementación

### Criterios de Validación Arquitectónica
- Coincidencias semánticas en funcionalidad
- Patrones de nomenclatura arquitectónicos
- Dependencias y relaciones según capas
- Interfaces y contratos definidos
- Impacto en separación de responsabilidades

## 8. RESOLUCIÓN DE CONFLICTOS METODOLOGÍA-ARQUITECTURA

### Precedencia Definida
1. **Instrucciones Claude AI** tienen precedencia en **metodología y proceso**
2. **Arquitectura** tiene precedencia en **estructura técnica y patrones**
3. **Principio DRY**: Si arquitectura especifica algo, no duplicar
4. **Escalación**: Documentar conflicto y solicitar clarificación

### Casos Comunes de Conflicto
- **Ubicación de archivo**: Seguir estructura arquitectónica
- **Patrón a aplicar**: Seguir documento arquitectura
- **Proceso de implementación**: Seguir instrucciones Claude
- **Nomenclatura**: Seguir estándares arquitectónicos
- **Testing**: Seguir proceso TDD + patrones arquitectónicos

## 9. PROHIBICIONES ESPECÍFICAS AMPLIADAS

### Modificaciones No Autorizadas
- **No modificar nombres** de funciones, clases o variables existentes sin autorización
- **No saltarse pasos** del flujo de trabajo
- **No implementar cambios** no solicitados explícitamente
- **No crear estructuras** sin validar consistencia con sistema existente
- **No violar separación de capas** arquitectónicas
- **No ignorar patrones** definidos en arquitectura

### Comportamiento Restrictivo Arquitectónico
- **No asumir requerimientos** no especificados
- **No optimizar** código sin solicitud específica
- **No refactorizar** sin autorización previa
- **No eliminar** código sin confirmación
- **No crear dependencias** que violen arquitectura
- **No implementar lógica** en capa incorrecta

## 10. GESTIÓN DE ARCHIVOS Y DOCUMENTACIÓN INTEGRADA

### Mantenimiento Obligatorio
- Actualizar `inventory_system_directory.md` con cada cambio
- **Registrar compliance arquitectónica** aplicada
- Registrar errores detectados y soluciones aplicadas
- Mantener changelog actualizado con formato consistente
- **Documentar patrones aplicados** en cada implementación
- Respaldar archivos críticos en directorio `backups/`

### Control de Versiones Arquitectónico
- Commits atómicos con mensajes descriptivos
- **Incluir compliance arquitectónica** en mensajes
- Validar integridad antes de commit
- Documentar cambios significativos
- **Referenciar patrones aplicados** en commits

## 11. PROTOCOLO DE COMUNICACIÓN INTEGRADA

### Antes de Cada Acción
- Confirmar entendimiento del requerimiento
- **Consultar arquitectura** para componentes afectados
- **Identificar patrones** aplicables
- Listar archivos afectados
- **Validar capa arquitectónica** correspondiente
- Solicitar autorización explícita

### Durante el Desarrollo
- Reportar progreso en pasos pequeños
- **Confirmar compliance arquitectónica** en cada paso
- Comunicar problemas o inconsistencias inmediatamente
- **Validar patrones aplicados** antes de continuar
- Validar decisiones técnicas antes de implementar

### Al Completar Tareas
- Resumir cambios realizados
- **Confirmar compliance arquitectónica** completa
- Reportar estado de tests
- **Documentar patrones aplicados**
- Confirmar próximos pasos

## 12. CASOS DE USO ESPECÍFICOS INTEGRADOS

### Implementar Nuevo Servicio
```
TDD:
1. Escribir test que falle
2. Implementar código mínimo
3. Refactorizar

ARQUITECTURA:
1. Ubicar en src/application/services/
2. Implementar interface de dominio
3. Usar ServiceContainer para DI
4. Seguir nomenclatura snake_case
```

### Crear Nueva Entidad
```
TDD:
1. Tests para validación
2. Implementar entidad
3. Tests de comportamiento

ARQUITECTURA:
1. Ubicar en src/domain/entities/
2. Usar Value Objects apropiados
3. Definir reglas de negocio
4. Crear interface repository
```

### Implementar Repositorio
```
TDD:
1. Mock repository para tests
2. Implementar interface
3. Tests de integración

ARQUITECTURA:
1. Interface en src/domain/repositories/
2. Implementación en src/infrastructure/database/
3. Usar patrón Repository
4. Inyectar via ServiceContainer
```

## 13. VALIDACIÓN DE CUMPLIMIENTO FINAL

### Checklist Completo Pre-Entrega
- [ ] **TDD**: Todos los tests pasan
- [ ] **Cobertura**: ≥95% alcanzada
- [ ] **Arquitectura**: Separación de capas respetada
- [ ] **SOLID**: Principios aplicados correctamente
- [ ] **Patrones**: Repository, Service Layer implementados
- [ ] **DI**: ServiceContainer utilizado apropiadamente
- [ ] **Nomenclatura**: Estándares arquitectónicos seguidos
- [ ] **Interfaces**: Definidas e implementadas
- [ ] **Documentación**: Código y arquitectura documentados
- [ ] **Performance**: Criterios arquitectónicos cumplidos

### Criterios de Aceptación Integrados
- **Cobertura de tests**: Mínimo 95%
- **Complejidad ciclomática**: Máximo 10 por método
- **Documentación**: 100% de APIs públicas
- **Performance**: Tiempo de respuesta < 2 segundos
- **Compliance arquitectónica**: 100% de patrones aplicados
- **Separación de capas**: Sin violaciones detectadas

## 14. EVOLUCIÓN Y MANTENIMIENTO

### Cuándo Actualizar Estas Instrucciones
- Cambios en proceso de desarrollo
- Nuevas herramientas o validaciones
- Modificaciones en flujo de trabajo
- Problemas recurrentes identificados
- **Cambios en arquitectura** que afecten metodología

### Cuándo Actualizar Arquitectura
- Nuevos patrones o principios
- Cambios en estructura técnica
- Modificaciones en interfaces
- Evolución de requerimientos técnicos
- **Cambios metodológicos** que afecten arquitectura

### Sincronización de Documentos
- Revisar ambos documentos simultáneamente
- Validar coherencia entre metodología y arquitectura
- Actualizar referencias cruzadas
- Mantener ejemplos actualizados
- Documentar cambios en ambos documentos

---

## NOTA CRÍTICA v2.0

**Estas instrucciones integran completamente el documento de arquitectura del proyecto. El cumplimiento de ambos documentos es obligatorio. La metodología TDD y la arquitectura Clean Architecture deben aplicarse simultáneamente en cada implementación.**

**Versión**: 2.0 - Integración Arquitectónica  
**Fecha**: 2025-07-10  
**Precedencia**: Estas instrucciones tienen prioridad sobre cualquier otra consideración metodológica. El documento `docs/architecture.md` tiene precedencia en decisiones técnicas y estructurales.

**En caso de conflicto, seguir estrictamente el protocolo de resolución definido en la sección 8 y solicitar clarificación antes de proceder.**