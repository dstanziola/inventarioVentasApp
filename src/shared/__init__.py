# src/shared/__init__.py
"""
Componentes compartidos - Shared Layer
Fecha: 2025-07-16
"""

# Importaciones de submódulos disponibles
try:
    from .session import SessionManager, create_session_manager
    __all__ = ['SessionManager', 'create_session_manager']
except ImportError:
    __all__ = []
