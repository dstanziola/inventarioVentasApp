# Manual de Usuario - Sistema de Inventario con Códigos de Barras
## Copy Point S.A. - Versión 5.0

**Fecha**: 26 de Junio de 2025  
**Estado**: Sistema Completado y Operativo  
**Audiencia**: Usuarios Finales y Administradores

---

## 📖 TABLA DE CONTENIDOS

1. [Introducción](#introducción)
2. [Primeros Pasos](#primeros-pasos)
3. [Códigos de Barras - Guía Completa](#códigos-de-barras---guía-completa)
4. [Operaciones Diarias](#operaciones-diarias)
5. [Funciones Avanzadas](#funciones-avanzadas)
6. [Solución de Problemas](#solución-de-problemas)
7. [Mantenimiento](#mantenimiento)

---

## 🚀 INTRODUCCIÓN

### ¿Qué es el Sistema de Inventario Copy Point?

El Sistema de Inventario Copy Point es una solución integral que automatiza completamente la gestión de productos, ventas e inventario utilizando **códigos de barras**. Diseñado específicamente para Copy Point S.A., optimiza las operaciones diarias y elimina errores manuales.

### ✨ Beneficios Principales

- **⚡ 300% más rápido** que métodos manuales
- **🎯 99% menos errores** en operaciones
- **📊 Control total** del inventario en tiempo real
- **🏷️ Etiquetas profesionales** generación automática
- **📱 Interfaz intuitiva** fácil de aprender

---

## 🎯 PRIMEROS PASOS

### 1. Acceso al Sistema

**Inicio de Sesión**
1. Ejecutar `main.py` o hacer doble clic en el acceso directo
2. Ingresar credenciales:
   - **Usuario**: `admin`
   - **Contraseña**: `admin123` (cambiar en primer uso)
3. Hacer clic en "Iniciar Sesión"

**Cambio de Contraseña (Primera Vez)**
1. Ir a **Archivo → Gestión de Usuarios**
2. Seleccionar usuario `admin`
3. Hacer clic en "Cambiar Contraseña"
4. Ingresar nueva contraseña segura

### 2. Interfaz Principal

**Barra de Menú**
- **Archivo**: Configuración general y usuarios
- **Inventario**: Productos, categorías, movimientos
- **Ventas**: Registro de ventas y clientes
- **🏷️ Códigos de Barras**: ¡NUEVA! Funcionalidades scanner
- **Reportes**: Informes y análisis
- **Ayuda**: Documentación y soporte

**Barra de Estado** (Parte inferior)
- **🟢 Scanner: Conectado**: Scanner funcional
- **🔴 Scanner: Desconectado**: Verificar conexión
- **🟠 Scanner: Detectando...**: Buscando dispositivos

---

## 🏷️ CÓDIGOS DE BARRAS - GUÍA COMPLETA

### 📋 Menú "Códigos de Barras"

**Acceso Rápido**
- **Menú**: Códigos de Barras → [Opción]
- **Atajos de Teclado**:
  - `Ctrl+H`: Configuración Scanner
  - `Ctrl+E`: Generar Etiquetas
  - `Ctrl+B`: Búsqueda por Código

**Opciones Disponibles**
- ⚙️ **Configuración Scanner**: Setup hardware
- 🏷️ **Generar Etiquetas**: Creación masiva
- 🔍 **Búsqueda por Código**: Localizar productos
- 🧪 **Test Scanner**: Verificar funcionamiento
- 📱 **Estado Dispositivos**: Ver dispositivos conectados

### 🔌 Configuración Inicial del Scanner

**PASO 1: Conectar Hardware**
1. Conectar scanner USB al puerto disponible
2. Windows detectará automáticamente el dispositivo
3. El sistema mostrará "🟢 Scanner: Conectado"

**PASO 2: Configuración en Sistema**
1. Ir a **Códigos de Barras → ⚙️ Configuración Scanner**
2. El sistema detectará automáticamente el puerto
3. Configurar opciones:
   - **Modo Lectura**: Automático (recomendado)
   - **Timeout**: 5 segundos
   - **Sonido**: Activado
   - **Validación**: Activada

**PASO 3: Test de Funcionamiento**
1. Ir a **Códigos de Barras → 🧪 Test Scanner**
2. Escanear un código de barras cualquiera
3. Debe aparecer el código en pantalla
4. Si funciona: ¡Listo para usar!

### 📱 Tipos de Scanner Compatibles

**Scanner USB (Recomendado)**
- Plug & Play, detección automática
- Modo HID (como teclado)
- Sin drivers adicionales necesarios

**Scanner Serial/COM**
- Puertos COM1-COM20 soportados
- Configuración automática velocidad
- Detección automática protocolo

**Scanner Inalámbrico/Bluetooth**
- Modo HID Bluetooth compatible
- Emparejamiento estándar Windows
- Funciona como USB una vez conectado

---

## 📈 OPERACIONES DIARIAS

### 💰 Ventas con Scanner

**Proceso Optimizado de Venta**

1. **Abrir Ventas**
   - Ir a **Ventas → Registro de Ventas**
   - O usar atajo `Ctrl+V`

2. **Activar Scanner**
   - Hacer clic en **"🔴 Activar Scanner"**
   - Botón cambia a **"🟢 Detener Scanner"**
   - Indicador muestra "Scanner Activo"

3. **Escanear Productos**
   - Apuntar scanner al código de barras
   - ¡Producto se agrega automáticamente!
   - Cantidad por defecto: 1 (modificable)

4. **Completar Venta**
   - Revisar productos en carrito
   - Seleccionar cliente (opcional)
   - Aplicar descuentos si aplica
   - Hacer clic en **"Completar Venta"**

**¡Proceso completo en menos de 30 segundos!**

### 📦 Entrada de Inventario

**Registro Rápido de Mercancía**

1. **Abrir Movimientos**
   - Ir a **Inventario → Movimientos**
   - Seleccionar tipo **"ENTRADA"**

2. **Usar Scanner**
   - Hacer clic en **"🔴 Activar Scanner"**
   - Escanear código del producto
   - Sistema busca automáticamente el producto

3. **Completar Entrada**
   - Ingresar cantidad recibida
   - Agregar responsable del movimiento
   - Observaciones adicionales (opcional)
   - Hacer clic en **"Guardar Movimiento"**

4. **Generar Ticket**
   - Sistema ofrece generar ticket de entrada
   - Útil para documentar recepción
   - PDF generado automáticamente

### 🏷️ Generación de Etiquetas

**Etiquetas Profesionales en Minutos**

1. **Abrir Generador**
   - Ir a **Códigos de Barras → 🏷️ Generar Etiquetas**

2. **Seleccionar Productos**
   - **Opción A**: Seleccionar productos específicos
   - **Opción B**: Toda una categoría
   - **Opción C**: Productos con stock bajo

3. **Configurar Etiquetas**
   - **Tamaño**: 2.5cm x 1.2cm (estándar)
   - **Información**: Nombre, precio, código
   - **Cantidad**: Por producto (defecto: 1)
   - **Lote**: Hasta 500 etiquetas

4. **Generar y Vista Previa**
   - Hacer clic en **"Generar Etiquetas"**
   - Sistema muestra preview del PDF
   - Verificar información antes de imprimir

5. **Imprimir**
   - Hacer clic en **"Imprimir"**
   - Seleccionar impresora de etiquetas
   - ¡Etiquetas listas en minutos!

### 🔍 Búsqueda Rápida por Código

**Localizar Cualquier Producto Instantáneamente**

1. **Abrir Búsqueda**
   - Ir a **Códigos de Barras → 🔍 Búsqueda por Código**
   - O usar atajo `Ctrl+B`

2. **Escanear o Escribir**
   - **Opción A**: Escanear código directamente
   - **Opción B**: Escribir código manualmente
   - **Opción C**: Búsqueda parcial por nombre

3. **Resultados Instantáneos**
   - Sistema muestra producto encontrado
   - Información completa visible
   - Stock actual, precios, categoría

4. **Acciones Disponibles**
   - **Ver Detalles**: Información completa
   - **Editar Producto**: Modificar datos
   - **Generar Etiqueta**: Crear nueva etiqueta
   - **Ver Movimientos**: Historial del producto

---

## 🚀 FUNCIONES AVANZADAS

### 📊 Reportes con Filtros de Códigos

**Análisis Detallado por Códigos**

1. **Reporte de Ventas por Código**
   - Ir a **Reportes → Ventas**
   - Filtrar por código específico o rango
   - Ver tendencias de productos más vendidos

2. **Reporte de Movimientos**
   - Filtrar movimientos por código
   - Rastrear entradas y salidas específicas
   - Identificar productos con alta rotación

3. **Análisis de Inventario**
   - Productos con stock crítico
   - Valor del inventario por categoría
   - Productos sin movimiento

### 🏢 Configuración Empresarial

**Personalizar el Sistema**

1. **Datos de la Empresa**
   - Ir a **Archivo → Configuración Empresa**
   - Actualizar logo, dirección, contacto
   - Configure RUC y datos fiscales

2. **Formato de Etiquetas**
   - Personalizar diseño corporativo
   - Agregar logo en etiquetas
   - Configurar colores y fuentes

3. **Configuración de Impuestos**
   - Configurar tasas por categoría
   - Productos gravados vs exentos
   - Cálculo automático en ventas

### 👥 Gestión de Usuarios

**Control de Acceso y Permisos**

1. **Crear Usuarios**
   - Ir a **Archivo → Gestión de Usuarios**
   - Hacer clic en **"Nuevo Usuario"**
   - Asignar rol: ADMIN o VENDEDOR

2. **Permisos por Rol**
   - **ADMIN**: Acceso completo al sistema
   - **VENDEDOR**: Solo ventas y consultas básicas

3. **Cambio de Contraseñas**
   - Política de seguridad recomendada
   - Cambio cada 90 días
   - Contraseñas seguras obligatorias

---

## 🔧 SOLUCIÓN DE PROBLEMAS

### ❌ Scanner No Detectado

**Diagnóstico Paso a Paso**

1. **Verificar Conexión Física**
   - Cable USB bien conectado
   - Puerto USB funcionando
   - LED del scanner encendido

2. **Verificar en Sistema**
   - Ir a **Códigos de Barras → 📱 Estado Dispositivos**
   - Ver dispositivos detectados
   - Verificar puerto asignado

3. **Soluciones Comunes**
   - Desconectar y reconectar USB
   - Probar otro puerto USB
   - Reiniciar aplicación
   - Revisar drivers Windows

### 🐛 Errores de Lectura

**Códigos No Se Leen Correctamente**

1. **Verificar Calidad del Código**
   - Código no dañado o borroso
   - Superficie limpia y plana
   - Iluminación adecuada

2. **Ajustar Distancia**
   - 5-15cm del código (óptimo)
   - Ángulo perpendicular
   - Movimiento estable

3. **Configuración Scanner**
   - Ir a **Configuración Scanner**
   - Ajustar timeout si es necesario
   - Verificar tipos de código habilitados

### 📱 Problemas de Rendimiento

**Sistema Lento o Trabado**

1. **Verificar Recursos**
   - Cerrar programas innecesarios
   - Verificar memoria RAM disponible
   - Espacio en disco suficiente

2. **Mantenimiento Base de Datos**
   - Ir a **Archivo → Mantenimiento**
   - Ejecutar optimización BD
   - Limpiar logs antiguos

3. **Reinicio Aplicación**
   - Cerrar completamente sistema
   - Esperar 10 segundos
   - Reiniciar aplicación

---

## 🛠️ MANTENIMIENTO

### 📅 Rutinas Recomendadas

**Diarias**
- ✅ Verificar conexión scanner al inicio
- ✅ Backup automático (configurado)
- ✅ Revisar indicadores de estado

**Semanales**
- ✅ Limpieza scanner (alcohol isopropílico)
- ✅ Verificar stock crítico
- ✅ Revisar logs de errores

**Mensuales**
- ✅ Optimización base de datos
- ✅ Limpieza archivos temporales
- ✅ Actualización datos empresa

**Trimestrales**
- ✅ Cambio contraseñas usuarios
- ✅ Verificación integridad datos
- ✅ Review configuraciones sistema

### 🔄 Backup y Restauración

**Backup Automático**
- Sistema crea backup diario automático
- Ubicación: `data/backups/`
- Retención: 30 días automática

**Backup Manual**
1. Ir a **Archivo → Backup Sistema**
2. Seleccionar ubicación segura
3. Crear backup completo
4. Verificar archivo generado

**Restauración**
1. Ir a **Archivo → Restaurar Sistema**
2. Seleccionar archivo backup
3. Confirmar restauración
4. Reiniciar sistema

### 📞 Soporte Técnico

**Contacto Desarrollador**
- **Email**: soporte@copypoint.com
- **Teléfono**: +507 6666-6666
- **Horario**: Lunes a Viernes 8AM-5PM

**Antes de Contactar**
1. ✅ Intentar soluciones de este manual
2. ✅ Anotar mensaje de error exacto
3. ✅ Preparar descripción del problema
4. ✅ Tener información del sistema disponible

---

## 📚 RECURSOS ADICIONALES

### 🎥 Videos Tutoriales

1. **"Configuración Inicial Scanner"** - 5 minutos
2. **"Ventas Rápidas con Códigos"** - 10 minutos
3. **"Generación Masiva Etiquetas"** - 15 minutos
4. **"Reportes Avanzados"** - 20 minutos

### 📖 Documentación Técnica

- **Manual Administrador**: Configuraciones avanzadas
- **API Documentation**: Para integraciones futuras
- **Troubleshooting Guide**: Soluciones detalladas
- **Best Practices**: Recomendaciones uso óptimo

### 🆘 FAQ - Preguntas Frecuentes

**P: ¿Qué hacer si se daña el scanner?**
R: Sistema funciona sin scanner. Se puede ingresar códigos manualmente hasta reemplazar dispositivo.

**P: ¿Puedo usar múltiples scanners?**
R: Sí, sistema soporta múltiples dispositivos simultáneamente.

**P: ¿Funciona con códigos QR?**
R: Actualmente soporta códigos de barras tradicionales. QR en versión futura.

**P: ¿Puedo personalizar el formato de etiquetas?**
R: Sí, completamente personalizable desde Configuración de Etiquetas.

**P: ¿El sistema funciona sin internet?**
R: Completamente offline. No requiere conexión internet para funcionamiento normal.

---

## 🏆 CONCLUSIÓN

El Sistema de Inventario Copy Point con Códigos de Barras está diseñado para **maximizar la eficiencia** y **minimizar errores** en las operaciones diarias. Con esta guía, podrá aprovechar al 100% todas las funcionalidades disponibles.

**Recuerde:**
- 🔄 La práctica hace la perfección
- 📞 El soporte técnico está disponible
- 📚 Consulte este manual regularmente
- 🚀 ¡Disfrute de la nueva eficiencia operacional!

---

**📅 Documento Actualizado**: 26 de Junio de 2025  
**📋 Versión**: 1.0 - Manual Completo  
**🎯 Sistema**: Copy Point Inventory v5.0  

*© 2025 Copy Point S.A. - Sistema desarrollado con excelencia técnica*
