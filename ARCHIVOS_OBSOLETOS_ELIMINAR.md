# ARCHIVOS DE PROMPTS OBSOLETOS - LISTA PARA ELIMINACIÓN

## ARCHIVOS OBSOLETOS QUE SE PUEDEN ELIMINAR SEGURAMENTE

### **PROMPTS DE FASES ANTERIORES (YA COMPLETADAS)**
```
✅ ELIMINAR - Fases 1, 2, 3 ya completadas:
- NEXT_CHAT_PROMPT.md                           # Fase 1 obsoleta
- NEXT_CHAT_PROMPT_FASE3_FINAL.md              # Fase 3 completada  
- NEXT_CHAT_PROMPT_FASE3_VALIDATION.md         # Validación ya hecha
- NEXT_CHAT_PROMPT_FASE3_VALIDATION_FINAL.md   # Validación completada
- NEXT_CHAT_PROMPT_FASE4_CONTINUACION.md       # Fase 4 superada
- NEXT_CHAT_PROMPT_FASE4_FINAL.md              # Versión intermedia
- NEXT_CHAT_PROMPT_FASE4_FINALIZACION.md       # Usado en este chat
- NEXT_CHAT_PROMPT_FASE4_INICIO.md             # Fase 4 ya iniciada
```

### **REPORTES Y CHANGELOGS DE DESARROLLO (HISTÓRICOS)**
```
✅ ELIMINAR - Reportes históricos ya incorporados:
- CHANGELOG_FASE1.md                           # Incorporado en documentación
- CHANGELOG_FASE2.md                           # Incorporado en documentación  
- REPORTE_FINAL_FASE3_VALIDACION.md           # Validación ya hecha
- RESUMEN_EJECUTIVO_FASE2.md                  # Histórico
- RESUMEN_EJECUTIVO_FASE3.md                  # Histórico
- RESUMEN_EJECUTIVO_FASE4_INICIO.md           # Superado
```

## ARCHIVOS QUE MANTENER

### **DOCUMENTACIÓN ACTIVA**
```
🔒 MANTENER - Documentación esencial:
- Requerimientos_Sistema_Inventario_v5.0_Optimizado.md  # Documentación base
- inventory_system_directory.md                         # Directorio actualizado
- NEXT_CHAT_PROMPT_FASE4_COMPLETAR_FINAL.md            # Prompt actual activo
```

### **ARCHIVOS DE DESARROLLO TEMPORAL**
```
🔒 MANTENER - Archivos temporales útiles:
- temp/*.py                                    # Scripts de validación activos
- ui/forms/backups/*.py                        # Backups de seguridad
```

## COMANDO DE ELIMINACIÓN SUGERIDO

```bash
# Navegar al directorio del proyecto
cd D:\inventario_app2

# Eliminar archivos obsoletos de prompts
del NEXT_CHAT_PROMPT.md
del NEXT_CHAT_PROMPT_FASE3_FINAL.md  
del NEXT_CHAT_PROMPT_FASE3_VALIDATION.md
del NEXT_CHAT_PROMPT_FASE3_VALIDATION_FINAL.md
del NEXT_CHAT_PROMPT_FASE4_CONTINUACION.md
del NEXT_CHAT_PROMPT_FASE4_FINAL.md
del NEXT_CHAT_PROMPT_FASE4_FINALIZACION.md
del NEXT_CHAT_PROMPT_FASE4_INICIO.md

# Eliminar reportes históricos
del CHANGELOG_FASE1.md
del CHANGELOG_FASE2.md
del REPORTE_FINAL_FASE3_VALIDACION.md
del RESUMEN_EJECUTIVO_FASE2.md
del RESUMEN_EJECUTIVO_FASE3.md
del RESUMEN_EJECUTIVO_FASE4_INICIO.md
```

## LIMPIEZA RECOMENDADA

**TOTAL DE ARCHIVOS A ELIMINAR: 14 archivos**
**ESPACIO LIBERADO ESTIMADO: ~200-300 KB**

**BENEFICIOS DE LA LIMPIEZA:**
- Directorio más organizado y limpio
- Eliminación de confusión por archivos obsoletos
- Foco en documentación actual y relevante
- Mejor navegación del proyecto

**ARCHIVOS CRÍTICOS QUE NUNCA ELIMINAR:**
- inventory_system_directory.md (directorio del sistema)
- Requerimientos_Sistema_Inventario_v5.0_Optimizado.md (especificaciones)
- NEXT_CHAT_PROMPT_FASE4_COMPLETAR_FINAL.md (prompt activo)
- Cualquier archivo .py del código fuente
- requirements.txt
- .gitignore
- Archivos de configuración (.env, config.ini)

**NOTA:** Realizar backup completo antes de eliminar archivos por seguridad.
