# Comandos Internos Claude IA (claude_commands.md)

Este documento resume los módulos de operación para el desarrollo con Claude IA en el proyecto `inventario_app2`. Cada módulo puede ser llamado por su código (`P01` a `P06`) para reducir el uso de tokens y estandarizar tareas.

---

## 🧩 P01 - Análisis Inicial
**Objetivo:** Comprender el contexto completo antes de realizar cambios.

**Acciones:**
- Leer requerimientos, arquitectura y estructura de carpetas
- Verificar si la funcionalidad ya existe
- Validar consistencia de nombres y estructura
- Confirmar la capa afectada según Clean Architecture

**Resultado esperado:** Diagnóstico completo del área a trabajar.

---

## 📝 P02 - Planificación
**Objetivo:** Definir claramente el impacto y la ruta del cambio antes de codificar.

**Acciones:**
- Listar todos los archivos a modificar o crear
- Validar ubicación en capas correctas (según arquitectura)
- Confirmar interfaces o contratos existentes
- Esperar autorización explícita antes de implementar

**Resultado esperado:** Plan de acción validado y autorizado.

---

## 🛠 P03 - Implementación TDD
**Objetivo:** Codificar con base en pruebas bajo el marco arquitectónico.

**Acciones:**
- Escribir test que falle
- Implementar código mínimo para pasar el test
- Aplicar separación de capas y patrones (Repository, Service, CQRS)
- Refactorizar respetando principios SOLID

**Resultado esperado:** Código funcional y alineado con TDD + arquitectura.

---

## ✅ P04 - Validación y Documentación
**Objetivo:** Verificar cumplimiento técnico y actualizar documentación.

**Acciones:**
- Validar que todos los tests pasen (≥95% cobertura)
- Verificar cumplimiento arquitectónico (checklist)
- Actualizar `changelog`, `inventory_system_directory.md` y patrones aplicados
- Guardar y respaldar archivos

**Resultado esperado:** Entregable completo, validado y documentado.

---

## 🔁 P05 - Confirmación
**Objetivo:** Presentar resumen técnico y esperar nueva autorización.

**Acciones:**
- Resumir tareas realizadas, archivos modificados y estado de tests
- Indicar próximos pasos sugeridos
- Detenerse hasta recibir confirmación

**Resultado esperado:** Confirmación del cierre de etapa y autorización para continuar.

---

## 🔍 P06 - Detección de Redundancias
**Objetivo:** Prevenir duplicación innecesaria de lógica o estructuras.

**Acciones:**
- Buscar funciones similares existentes
- Validar si se puede reutilizar lógica o estructuras
- Comparar con interfaces y servicios previos
- Documentar decisión de reutilizar o crear nuevo

**Resultado esperado:** Cambio implementado sin duplicar funcionalidad existente.

---

**Uso recomendado:** En cada tarea, indicar los módulos aplicables: por ejemplo,
> "Implementar nueva función para control de stock: P01 + P02 + P03"

**Mantenimiento:** Actualizar este archivo si se agregan nuevos módulos o se modifica el flujo de trabajo.

