"""
Autenticación de usuarios - Módulo de login.

Este módulo contiene la lógica de autenticación y componentes
relacionados con el sistema de login.
"""

from .session_manager import SessionManager, session_manager
from .login_window import LoginWindow

__all__ = ['SessionManager', 'session_manager', 'LoginWindow']
