"""
Capa de interfaz de usuario para el Sistema de Inventario.

Esta capa implementa la interfaz gráfica usando Tkinter siguiendo
principios de Clean Architecture y separación de responsabilidades.

ESTRUCTURA:
- auth/: Sistema de autenticación y gestión de sesiones
- forms/: Formularios CRUD para entidades del sistema
- main/: Ventana principal y navegación
- components/: Componentes reutilizables (grillas, diálogos, etc.)

PRINCIPIOS:
- Separación UI/Business Logic mediante servicios
- Componentes reutilizables y modulares
- Validación en tiempo real
- Integración con códigos de barras
- Diseño responsivo y user-friendly
"""

__version__ = '1.0.0'
