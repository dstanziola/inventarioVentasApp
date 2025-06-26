"""
Modelo de datos para Usuario.
Representa usuarios del sistema de inventario con autenticación y roles.

Este archivo fue implementado siguiendo TDD:
- Tests escritos primero en tests/unit/test_models.py
- Implementación mínima para pasar tests (GREEN)
- Refactorización manteniendo tests pasando

Autor: Sistema TDD
Fecha: 2025-05-26
"""

from typing import Optional
import hashlib
import secrets
from datetime import datetime


class Usuario:
    """
    Modelo para representar un usuario del sistema.
    
    Los usuarios tienen roles (ADMIN, VENDEDOR) y manejo seguro de contraseñas.
    Incluye funcionalidades de autenticación y gestión de sesiones.
    """
    
    # Roles válidos del sistema
    ROLES_VALIDOS = {'ADMIN', 'VENDEDOR'}
    
    def __init__(
        self,
        nombre_usuario: str,
        password_hash: str,
        rol: str,
        activo: bool = True,
        id_usuario: Optional[int] = None
    ):
        """
        Inicializar un nuevo usuario.
        
        Args:
            nombre_usuario: Nombre único del usuario
            password_hash: Hash de la contraseña (ya hasheada)
            rol: Rol del usuario ('ADMIN' o 'VENDEDOR')
            activo: Si el usuario está activo (default: True)
            id_usuario: ID único (asignado por la base de datos)
            
        Raises:
            ValueError: Si el rol no es válido
        """
        if rol not in self.ROLES_VALIDOS:
            raise ValueError(f"Rol '{rol}' no válido. Debe ser uno de: {', '.join(self.ROLES_VALIDOS)}")
        
        self.id_usuario = id_usuario
        self.nombre_usuario = nombre_usuario.strip() if nombre_usuario else ""
        self.password_hash = password_hash
        self.rol = rol
        self.activo = activo
        self.fecha_creacion = datetime.now()
        self.ultimo_login = None
    
    def set_password(self, password_plain: str) -> None:
        """
        Establecer una nueva contraseña (hasheando el texto plano).
        
        Args:
            password_plain: Contraseña en texto plano
        """
        # Generar salt aleatorio
        salt = secrets.token_hex(16)
        
        # Crear hash con salt
        password_with_salt = f"{password_plain}{salt}"
        hash_object = hashlib.sha256(password_with_salt.encode())
        hash_hex = hash_object.hexdigest()
        
        # Almacenar salt + hash
        self.password_hash = f"{salt}:{hash_hex}"
    
    def verify_password(self, password_plain: str) -> bool:
        """
        Verificar si una contraseña coincide con el hash almacenado.
        
        Args:
            password_plain: Contraseña en texto plano a verificar
            
        Returns:
            True si la contraseña es correcta
        """
        if not self.password_hash or ':' not in self.password_hash:
            return False
        
        try:
            # Separar salt y hash
            salt, stored_hash = self.password_hash.split(':', 1)
            
            # Recrear hash con el salt
            password_with_salt = f"{password_plain}{salt}"
            hash_object = hashlib.sha256(password_with_salt.encode())
            computed_hash = hash_object.hexdigest()
            
            # Comparación segura
            return secrets.compare_digest(stored_hash, computed_hash)
            
        except Exception:
            return False
    
    def es_admin(self) -> bool:
        """
        Verificar si el usuario es administrador.
        
        Returns:
            True si es ADMIN
        """
        return self.rol == 'ADMIN'
    
    def es_vendedor(self) -> bool:
        """
        Verificar si el usuario es vendedor.
        
        Returns:
            True si es VENDEDOR
        """
        return self.rol == 'VENDEDOR'
    
    def es_activo(self) -> bool:
        """
        Verificar si el usuario está activo.
        
        Returns:  
            True si está activo
        """
        return self.activo
    
    def activar(self) -> None:
        """Activar el usuario."""
        self.activo = True
    
    def desactivar(self) -> None:
        """Desactivar el usuario."""
        self.activo = False
    
    def registrar_login(self) -> None:
        """Registrar el momento del último login."""
        self.ultimo_login = datetime.now()
    
    def puede_realizar_accion(self, accion: str) -> bool:
        """
        Verificar si el usuario puede realizar una acción específica.
        
        Args:
            accion: Nombre de la acción a verificar
            
        Returns:
            True si puede realizar la acción
        """
        if not self.activo:
            return False
        
        # Acciones que solo ADMIN puede hacer
        acciones_admin = {
            'crear_usuario', 'eliminar_usuario', 'modificar_usuario',
            'ver_reportes_admin', 'configurar_sistema', 'respaldar_db'
        }
        
        # Acciones que ambos roles pueden hacer
        acciones_comunes = {
            'crear_venta', 'ver_productos', 'buscar_clientes', 
            'generar_factura', 'consultar_stock'
        }
        
        if accion in acciones_comunes:
            return True
        elif accion in acciones_admin:
            return self.es_admin()
        else:
            # Acción desconocida, solo ADMIN por seguridad
            return self.es_admin()
    
    def obtener_permisos(self) -> list:
        """
        Obtener lista de permisos del usuario según su rol.
        
        Returns:
            Lista de acciones permitidas
        """
        permisos_base = [
            'crear_venta', 'ver_productos', 'buscar_clientes',
            'generar_factura', 'consultar_stock', 'ver_movimientos'
        ]
        
        if self.es_admin():
            permisos_admin = [
                'crear_usuario', 'eliminar_usuario', 'modificar_usuario',
                'ver_reportes_admin', 'configurar_sistema', 'respaldar_db',
                'crear_categoria', 'modificar_producto', 'ajustar_stock'
            ]
            return permisos_base + permisos_admin
        
        return permisos_base
    
    def __str__(self) -> str:
        """
        Representación string del usuario.
        
        Returns:
            String descriptivo con nombre y rol
        """
        estado = "activo" if self.activo else "inactivo"
        return f"Usuario(nombre='{self.nombre_usuario}', rol='{self.rol}', {estado})"
    
    def __repr__(self) -> str:
        """
        Representación técnica del usuario.
        
        Returns:
            String con todos los atributos principales
        """
        return (f"Usuario(id_usuario={self.id_usuario}, "
                f"nombre_usuario='{self.nombre_usuario}', rol='{self.rol}', "
                f"activo={self.activo})")
    
    def __eq__(self, other) -> bool:
        """
        Comparar dos usuarios por igualdad.
        
        Args:
            other: Otra instancia de Usuario
            
        Returns:
            True si son el mismo usuario
        """
        if not isinstance(other, Usuario):
            return False
        
        # Si ambos tienen ID, comparar por ID
        if self.id_usuario is not None and other.id_usuario is not None:
            return self.id_usuario == other.id_usuario
        
        # Si no tienen ID, comparar por nombre de usuario
        return self.nombre_usuario == other.nombre_usuario
    
    def __hash__(self) -> int:
        """
        Hash del usuario para usar en conjuntos y diccionarios.
        
        Returns:  
            Hash basado en ID o nombre de usuario
        """
        if self.id_usuario is not None:
            return hash(('Usuario', self.id_usuario))
        
        return hash(('Usuario', self.nombre_usuario))
    
    def to_dict(self, incluir_password: bool = False) -> dict:
        """
        Convertir el usuario a diccionario.
        
        Args:
            incluir_password: Si incluir el hash de password (default: False)
            
        Returns:
            Diccionario con los atributos del usuario
        """
        data = {
            'id_usuario': self.id_usuario,
            'nombre_usuario': self.nombre_usuario,
            'rol': self.rol,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'ultimo_login': self.ultimo_login.isoformat() if self.ultimo_login else None
        }
        
        if incluir_password:
            data['password_hash'] = self.password_hash
            
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Usuario':
        """
        Crear un usuario desde un diccionario.
        
        Args:
            data: Diccionario con los datos del usuario
            
        Returns:
            Nueva instancia de Usuario
        """
        usuario = cls(
            nombre_usuario=data['nombre_usuario'],
            password_hash=data['password_hash'],
            rol=data['rol'],
            activo=data.get('activo', True),
            id_usuario=data.get('id_usuario')
        )
        
        # Restaurar fechas si existen
        if 'fecha_creacion' in data and data['fecha_creacion']:
            usuario.fecha_creacion = datetime.fromisoformat(data['fecha_creacion'])
        
        if 'ultimo_login' in data and data['ultimo_login']:
            usuario.ultimo_login = datetime.fromisoformat(data['ultimo_login'])
            
        return usuario
    
    @classmethod
    def crear_admin(cls, nombre_usuario: str, password_plain: str) -> 'Usuario':
        """
        Crear un usuario con rol ADMIN.
        
        Args:
            nombre_usuario: Nombre del administrador
            password_plain: Contraseña en texto plano
            
        Returns:
            Nueva instancia de Usuario con rol ADMIN
        """
        usuario = cls(
            nombre_usuario=nombre_usuario,
            password_hash="temp",  # Se cambiará con set_password
            rol="ADMIN"
        )
        usuario.set_password(password_plain)
        return usuario
    
    @classmethod
    def crear_vendedor(cls, nombre_usuario: str, password_plain: str) -> 'Usuario':
        """
        Crear un usuario con rol VENDEDOR.
        
        Args:
            nombre_usuario: Nombre del vendedor
            password_plain: Contraseña en texto plano
            
        Returns:
            Nueva instancia de Usuario con rol VENDEDOR
        """
        usuario = cls(
            nombre_usuario=nombre_usuario,
            password_hash="temp",  # Se cambiará con set_password
            rol="VENDEDOR"
        )
        usuario.set_password(password_plain)
        return usuario
    
    def cambiar_password(self, password_actual: str, password_nuevo: str) -> bool:
        """
        Cambiar la contraseña verificando la actual.
        
        Args:
            password_actual: Contraseña actual en texto plano
            password_nuevo: Nueva contraseña en texto plano
            
        Returns:
            True si el cambio fue exitoso
        """
        if not self.verify_password(password_actual):
            return False
        
        self.set_password(password_nuevo)
        return True
    
    def obtener_info_resumida(self) -> dict:
        """
        Obtener información resumida del usuario (sin datos sensibles).
        
        Returns:
            Diccionario con información básica
        """
        return {
            'id_usuario': self.id_usuario,
            'nombre_usuario': self.nombre_usuario,
            'rol': self.rol,
            'activo': self.activo,
            'es_admin': self.es_admin(),
            'ultimo_login': self.ultimo_login.isoformat() if self.ultimo_login else None
        }
    
    def validar_datos(self) -> list:
        """
        Validar los datos del usuario.
        
        Returns:
            Lista de errores encontrados (vacía si todo está bien)
        """
        errores = []
        
        if not self.nombre_usuario or len(self.nombre_usuario.strip()) == 0:
            errores.append("El nombre de usuario es requerido")
        
        if len(self.nombre_usuario) > 30:
            errores.append("El nombre de usuario no puede exceder 30 caracteres")
        
        if not self.password_hash:
            errores.append("El hash de contraseña es requerido")
        
        if self.rol not in self.ROLES_VALIDOS:
            errores.append(f"El rol debe ser uno de: {', '.join(self.ROLES_VALIDOS)}")
        
        # Validar formato de nombre de usuario (solo letras, números, guiones bajos)
        import re
        if not re.match(r'^[a-zA-Z0-9_]+$', self.nombre_usuario):
            errores.append("El nombre de usuario solo puede contener letras, números y guiones bajos")
        
        return errores
    
    def es_valido(self) -> bool:
        """
        Verificar si el usuario tiene datos válidos.
        
        Returns:
            True si todos los datos son válidos
        """
        return len(self.validar_datos()) == 0
    
    def tiempo_desde_ultimo_login(self) -> Optional[str]:
        """
        Calcular tiempo transcurrido desde el último login.
        
        Returns:
            String descriptivo del tiempo transcurrido o None si nunca hizo login
        """
        if not self.ultimo_login:
            return None
        
        ahora = datetime.now()
        diferencia = ahora - self.ultimo_login
        
        if diferencia.days > 0:
            return f"hace {diferencia.days} días"
        elif diferencia.seconds > 3600:
            horas = diferencia.seconds // 3600
            return f"hace {horas} horas"
        elif diferencia.seconds > 60:
            minutos = diferencia.seconds // 60
            return f"hace {minutos} minutos"
        else:
            return "hace menos de un minuto"
    
    @classmethod
    def validar_nombre_usuario_unico(cls, usuarios: list, nombre_usuario: str, excluir_id: Optional[int] = None) -> bool:
        """
        Validar que un nombre de usuario sea único.
        
        Args:
            usuarios: Lista de usuarios existentes
            nombre_usuario: Nombre a validar
            excluir_id: ID de usuario a excluir de la validación (para edición)
            
        Returns:
            True si el nombre es único
        """
        for usuario in usuarios:
            if (isinstance(usuario, cls) and 
                usuario.nombre_usuario == nombre_usuario and
                usuario.id_usuario != excluir_id):
                return False
        
        return True
