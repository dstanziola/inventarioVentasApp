"""
Servicio de gestión de usuarios - VERSIÓN CORREGIDA.

Esta corrección resuelve el error de conexión que impedía la autenticación.
El problema era que UserService intentaba usar métodos que no existen en DatabaseConnection.

CORRECCIÓN APLICADA:
- Usar self.db.get_connection().cursor() en lugar de self.db.fetchone()
- Usar cursor.execute() en lugar de self.db.execute()
- Usar cursor.lastrowid en lugar de self.db.lastrowid
- Manejo consistente con el patrón usado en CategoryService

Fecha de corrección: 30/05/2025
"""

import hashlib
import re
from typing import Optional, List
from db.database import DatabaseConnection

from models.usuario import Usuario


class UserService:
    """Servicio para gestión de usuarios del sistema - VERSIÓN CORREGIDA."""
    
    def __init__(self, db_connection: DatabaseConnection):
        """
        Inicializa el servicio de usuarios.
        
        Args:
            db_connection: Conexión a la base de datos
        """
        self.db = db_connection
        
    def authenticate(self, username: str, password: str) -> Optional[Usuario]:
        """
        Autentica un usuario con sus credenciales.
        
        Args:
            username: Nombre de usuario
            password: Contraseña en texto plano
            
        Returns:
            Usuario autenticado si las credenciales son válidas, None en caso contrario
        """
        # Validar entrada
        if not username or not password:
            return None
            
        # Hash de la contraseña para comparación
        password_hash = self._hash_password(password)
        
        # Buscar usuario en base de datos - PATRÓN CORREGIDO
        query = """
            SELECT id_usuario, nombre_usuario, password_hash, rol, activo
            FROM usuarios 
            WHERE nombre_usuario = ? AND password_hash = ? AND activo = 1
        """
        
        cursor = self.db.get_connection().cursor()
        cursor.execute(query, (username, password_hash))
        result = cursor.fetchone()
        
        if result:
            # Manejar tanto Row como tupla para compatibilidad
            if hasattr(result, 'keys') and callable(getattr(result, 'keys', None)):
                # Es un Row de SQLite con método keys()
                data = dict(result)
            else:
                # Es una tupla - usar indexación posicional
                data = {
                    'id_usuario': result[0],
                    'nombre_usuario': result[1],
                    'password_hash': result[2],
                    'rol': result[3],
                    'activo': result[4]
                }
            
            # Crear objeto Usuario con los datos encontrados
            return Usuario(**data)
            
        return None
        
    def create_user(self, nombre_usuario: str, password: str, rol: str) -> Usuario:
        """
        Crea un nuevo usuario en el sistema.
        
        Args:
            nombre_usuario: Nombre único del usuario
            password: Contraseña en texto plano
            rol: Rol del usuario ('ADMIN' o 'VENDEDOR')
            
        Returns:
            Usuario creado exitosamente
            
        Raises:
            ValueError: Si los datos son inválidos o el usuario ya existe
        """
        # Validar datos de entrada
        if not self._validate_username(nombre_usuario):
            raise ValueError("Nombre de usuario inválido")
            
        if not self._validate_password(password):
            raise ValueError("Contraseña debe tener al menos 6 caracteres")
            
        if not self._validate_role(rol):
            raise ValueError("Rol debe ser 'ADMIN' o 'VENDEDOR'")
            
        # Verificar que el usuario no exista
        existing_user = self._get_user_by_username(nombre_usuario)
        if existing_user:
            raise ValueError(f"Usuario '{nombre_usuario}' ya existe")
            
        # Hash de la contraseña
        password_hash = self._hash_password(password)
        
        # Insertar nuevo usuario - PATRÓN CORREGIDO
        query = """
            INSERT INTO usuarios (nombre_usuario, password_hash, rol, activo)
            VALUES (?, ?, ?, 1)
        """
        
        cursor = self.db.get_connection().cursor()
        cursor.execute(query, (nombre_usuario, password_hash, rol))
        self.db.get_connection().commit()
        user_id = cursor.lastrowid
        
        # Retornar usuario creado
        return Usuario(
            id_usuario=user_id,
            nombre_usuario=nombre_usuario,
            password_hash=password_hash,
            rol=rol,
            activo=True
        )
        
    def get_user_by_id(self, user_id: int) -> Optional[Usuario]:
        """
        Busca un usuario por su ID.
        
        Args:
            user_id: ID del usuario a buscar
            
        Returns:
            Usuario encontrado o None si no existe
        """
        query = """
            SELECT id_usuario, nombre_usuario, password_hash, rol, activo
            FROM usuarios 
            WHERE id_usuario = ?
        """
        
        cursor = self.db.get_connection().cursor()
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        
        if result:
            # Manejar tanto Row como tupla para compatibilidad
            if hasattr(result, 'keys') and callable(getattr(result, 'keys', None)):
                # Es un Row de SQLite con método keys()
                data = dict(result)
            else:
                # Es una tupla - usar indexación posicional
                data = {
                    'id_usuario': result[0],
                    'nombre_usuario': result[1],
                    'password_hash': result[2],
                    'rol': result[3],
                    'activo': result[4]
                }
            
            return Usuario(**data)
            
        return None
        
    def update_user(self, id_usuario: int, nombre_usuario: str = None, 
                   rol: str = None) -> Optional[Usuario]:
        """
        Actualiza información de un usuario existente.
        
        Args:
            id_usuario: ID del usuario a actualizar
            nombre_usuario: Nuevo nombre de usuario (opcional)
            rol: Nuevo rol (opcional)
            
        Returns:
            Usuario actualizado o None si no existe
            
        Raises:
            ValueError: Si los datos son inválidos
        """
        # Verificar que el usuario existe
        existing_user = self.get_user_by_id(id_usuario)
        if not existing_user:
            return None
            
        # Preparar campos a actualizar
        updates = []
        params = []
        
        if nombre_usuario is not None:
            if not self._validate_username(nombre_usuario):
                raise ValueError("Nombre de usuario inválido")
            updates.append("nombre_usuario = ?")
            params.append(nombre_usuario)
            
        if rol is not None:
            if not self._validate_role(rol):
                raise ValueError("Rol debe ser 'ADMIN' o 'VENDEDOR'")
            updates.append("rol = ?")
            params.append(rol)
            
        if not updates:
            return existing_user  # No hay cambios
            
        # Ejecutar actualización - PATRÓN CORREGIDO
        params.append(id_usuario)
        query = f"UPDATE usuarios SET {', '.join(updates)} WHERE id_usuario = ?"
        
        cursor = self.db.get_connection().cursor()
        cursor.execute(query, params)
        self.db.get_connection().commit()
        
        # Retornar usuario actualizado
        return self.get_user_by_id(id_usuario)
        
    def change_password(self, user_id: int, old_password: str, 
                       new_password: str) -> bool:
        """
        Cambia la contraseña de un usuario.
        
        Args:
            user_id: ID del usuario
            old_password: Contraseña actual
            new_password: Nueva contraseña
            
        Returns:
            True si el cambio fue exitoso, False en caso contrario
        """
        # Verificar contraseña actual
        user = self.get_user_by_id(user_id)
        if not user:
            return False
            
        old_password_hash = self._hash_password(old_password)
        if user.password_hash != old_password_hash:
            return False
            
        # Validar nueva contraseña
        if not self._validate_password(new_password):
            return False
            
        # Actualizar contraseña - PATRÓN CORREGIDO
        new_password_hash = self._hash_password(new_password)
        query = "UPDATE usuarios SET password_hash = ? WHERE id_usuario = ?"
        
        cursor = self.db.get_connection().cursor()
        cursor.execute(query, (new_password_hash, user_id))
        self.db.get_connection().commit()
        return True
        
    def deactivate_user(self, user_id: int) -> bool:
        """
        Desactiva un usuario del sistema.
        
        Args:
            user_id: ID del usuario a desactivar
            
        Returns:
            True si la desactivación fue exitosa, False en caso contrario
        """
        query = "UPDATE usuarios SET activo = 0 WHERE id_usuario = ?"
        cursor = self.db.get_connection().cursor()
        cursor.execute(query, (user_id,))
        self.db.get_connection().commit()
        return True
        
    def get_all_users(self) -> List[Usuario]:
        """
        Obtiene todos los usuarios del sistema.
        
        Returns:
            Lista de usuarios
        """
        query = """
            SELECT id_usuario, nombre_usuario, password_hash, rol, activo
            FROM usuarios 
            ORDER BY nombre_usuario
        """
        
        cursor = self.db.get_connection().cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        
        users = []
        for row in results:
            # Manejar tanto Row como tupla para compatibilidad
            if hasattr(row, 'keys') and callable(getattr(row, 'keys', None)):
                # Es un Row de SQLite con método keys()
                data = dict(row)
            else:
                # Es una tupla - usar indexación posicional
                data = {
                    'id_usuario': row[0],
                    'nombre_usuario': row[1],
                    'password_hash': row[2],
                    'rol': row[3],
                    'activo': row[4]
                }
            
            users.append(Usuario(**data))
        
        return users
        
    def _get_user_by_username(self, username: str) -> Optional[dict]:
        """
        Busca un usuario por nombre de usuario (método privado).
        
        Args:
            username: Nombre de usuario a buscar
            
        Returns:
            Datos del usuario o None si no existe
        """
        query = "SELECT id_usuario FROM usuarios WHERE nombre_usuario = ?"
        cursor = self.db.get_connection().cursor()
        cursor.execute(query, (username,))
        return cursor.fetchone()
        
    def _hash_password(self, password: str) -> str:
        """
        Genera hash seguro de contraseña.
        
        Args:
            password: Contraseña en texto plano
            
        Returns:
            Hash de la contraseña
        """
        # Usar el mismo salt que DatabaseConnection para consistencia
        salt = "inventory_system_salt_2024"
        return hashlib.sha256((password + salt).encode()).hexdigest()
        
    def _validate_username(self, username: str) -> bool:
        """
        Valida formato de nombre de usuario.
        
        Args:
            username: Nombre de usuario a validar
            
        Returns:
            True si es válido, False en caso contrario
        """
        if not username or len(username) < 3 or len(username) > 30:
            return False
            
        # Solo letras, números y guiones bajos
        pattern = r'^[a-zA-Z0-9_]+$'
        return bool(re.match(pattern, username))
        
    def _validate_password(self, password: str) -> bool:
        """
        Valida fortaleza de contraseña.
        
        Args:
            password: Contraseña a validar
            
        Returns:
            True si es válida, False en caso contrario
        """
        if not password or len(password) < 6:
            return False
            
        return True
        
    def _validate_role(self, role: str) -> bool:
        """
        Valida que el rol sea válido.
        
        Args:
            role: Rol a validar
            
        Returns:
            True si es válido, False en caso contrario
        """
        return role in ['ADMIN', 'VENDEDOR']