# PROTOCOLO DE RECUPERACIÓN DE CONTEXTO - FUTURAS SESIONES

## INSTRUCCIONES PARA CLAUDE AI - NUEVAS CONVERSACIONES

### FASE 1: DETECCIÓN DE CONTINUACIÓN
Si el usuario menciona cualquiera de estos términos:
- "continuar", "seguir", "sprint", "implementación"
- "inventario_app2", "Copy Point"
- "testing", "reportes", "códigos de barras"

**ACCIÓN INMEDIATA:** Ejecutar Protocolo de Recuperación

### FASE 2: COMANDOS DE RECUPERACIÓN OBLIGATORIOS

#### COMANDO 1: Verificar Directorio Contexto
```
filesystem:list_directory
path: D:\inventario_app2\context\session_state
```

#### COMANDO 2: Leer Estado Actual del Proyecto
```
filesystem:read_file
path: D:\inventario_app2\context\session_state\current_project_status.md
```

#### COMANDO 3: Leer Plan de Sprints
```
filesystem:read_file  
path: D:\inventario_app2\context\session_state\sprint_plan_detailed.md
```

#### COMANDO 4: Leer Decisiones y Contexto
```
filesystem:read_file
path: D:\inventario_app2\context\session_state\session_decisions_context.md
```

#### COMANDO 5: Verificar Última Actualización Change Log
```
filesystem:read_file
path: D:\inventario_app2\docs\change_log.md
```

### FASE 3: ANÁLISIS DE ESTADO ACTUAL

Después de leer los archivos, determinar:

1. **¿Qué sprint está activo?**
   - Sprint 1: Testing y estabilización
   - Sprint 2: Reportes  
   - Sprint 3: Integración final
   - Ninguno: Pendiente autorización

2. **¿Hay trabajo completado desde última sesión?**
   - Verificar change_log.md por entries nuevos
   - Buscar archivos nuevos en tests/, src/
   - Validar completitud según métricas

3. **¿Cuál es la próxima acción esperada?**
   - Autorización pendiente
   - Implementación específica
   - Validación de entregables

### FASE 4: RESPUESTA CONTEXTUALIZADA

Formato de respuesta obligatorio:

```
# CONTEXTO RECUPERADO - SESIÓN CONTINUADA

## ESTADO DEL PROYECTO ACTUAL
- **Decisión Estratégica:** [desde session_decisions_context.md]
- **Sprint Activo:** [desde sprint_plan_detailed.md]  
- **Completitud:** [desde current_project_status.md]
- **Próxima Acción:** [análisis de archivos]

## RESUMEN EJECUTIVO
[2-3 líneas sobre dónde estamos y qué sigue]

## PRÓXIMOS PASOS INMEDIATOS
[Lista de acciones específicas]

¿Confirma que desea continuar desde este punto?
```

### ARCHIVOS DE CONTEXTO CRÍTICOS

#### CONTEXTO MÍNIMO (siempre leer):
1. `context/session_state/current_project_status.md`
2. `context/session_state/sprint_plan_detailed.md`
3. `context/session_state/session_decisions_context.md`

#### CONTEXTO EXTENDIDO (si necesario):
4. `docs/change_log.md` (últimos cambios)
5. `docs/features_backlog.md` (funcionalidades pendientes)
6. `docs/Requerimientos_Sistema_Inventario_v6_0.md` (requerimientos)

### VALIDACIONES ANTES DE CONTINUAR

- ✅ Archivos de estado leídos correctamente
- ✅ Estado actual del proyecto identificado
- ✅ Sprint activo o pendiente determinado
- ✅ Próximas acciones claras
- ✅ Usuario confirma continuación

### ACTUALIZACIONES REQUERIDAS

Al final de cada sesión productiva, actualizar:

1. **current_project_status.md**: Nuevo % completitud
2. **sprint_plan_detailed.md**: Estado sprints  
3. **session_decisions_context.md**: Nuevas decisiones
4. **change_log.md**: Cambios realizados

### EJEMPLOS DE CONTINUACIÓN

#### Escenario 1: Usuario dice "continuar con Sprint 1"
→ Leer contexto → Identificar Sprint 1 → Continuar con testing básico

#### Escenario 2: Usuario dice "¿cómo va el proyecto?"
→ Leer contexto → Reportar estado actual → Mostrar métricas progreso

#### Escenario 3: Usuario dice "implementar reportes"
→ Leer contexto → Verificar si Sprint 2 autorizado → Proceder o solicitar autorización

## ERRORES A EVITAR

- ❌ No asumir contexto sin leer archivos
- ❌ No iniciar implementación sin confirmar estado
- ❌ No actualizar archivos de estado al final de sesión
- ❌ No validar autorización de usuario para continuar

## FECHA DE CREACIÓN
- **Creado:** 2025-07-21
- **Propósito:** Garantizar continuidad entre sesiones Claude AI
- **Validez:** Hasta completar proyecto (Sprint 3)
