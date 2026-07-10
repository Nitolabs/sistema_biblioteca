"""
DAO: AdministradorDAO

Se encarga exclusivamente de la comunicación con la tabla
`administradores` en MySQL. No contiene reglas de negocio (ej.
verificar contraseña, decidir cuándo bloquear) — eso vive en
controllers/auth_controller.py. Este DAO solo lee/escribe datos.
"""

import mysql.connector

from database.conexion import dataBase
from models.administradores import Administrador
from utils.excepciones import UsuarioDuplicadoError, UsuarioNoEncontradoError


class AdministradorDAO:

    def __init__(self, db: dataBase):
        self.db = db


    # Registrar un nuevo administrador
    def registrar(self, administrador: Administrador) -> int:
        """Inserta el administrador y retorna el id_admin asignado por MySQL."""
        cursor = self.db.cursor()
        try:
            cursor.execute(
                """INSERT INTO administradores
                   (usuario, contrasena_hash, intentos_fallidos, bloqueado, fecha_creacion)
                   VALUES (%s, %s, %s, %s, %s)""",
                (
                    administrador.usuario, administrador.contrasena_hash,
                    administrador.intentos_fallidos, administrador.bloqueado,
                    administrador.fecha_creacion
                )
            )
            self.db.conexion.commit()
            return cursor.lastrowid
        except mysql.connector.errors.IntegrityError as error:
            self.db.conexion.rollback()
            raise UsuarioDuplicadoError(
                f"Ya existe un administrador con el usuario '{administrador.usuario}'."
            ) from error
        finally:
            cursor.close()

    # Buscar administrador por nombre de usuario (para login)
    def buscar_por_usuario(self, usuario: str) -> Administrador | None:
        cursor = self.db.cursor()
        try:
            cursor.execute(
                "SELECT * FROM administradores WHERE usuario = %s", (usuario,)
            )
            fila = cursor.fetchone()
            return self._fila_a_administrador(fila) if fila else None
        finally:
            cursor.close()

    # Registrar un intento fallido de login
    def incrementar_intentos_fallidos(self, id_admin: int) -> None:
        cursor = self.db.cursor()
        try:
            cursor.execute(
                """UPDATE administradores
                   SET intentos_fallidos = intentos_fallidos + 1
                   WHERE id_admin = %s""",
                (id_admin,)
            )
            if cursor.rowcount == 0:
                raise UsuarioNoEncontradoError(f"No existe un administrador con ID {id_admin}.")
            self.db.conexion.commit()
        except mysql.connector.Error:
            self.db.conexion.rollback()
            raise
        finally:
            cursor.close()

    # Bloquear cuenta tras exceder intentos permitidos
    def bloquear(self, id_admin: int) -> None:
        cursor = self.db.cursor()
        try:
            cursor.execute(
                "UPDATE administradores SET bloqueado = TRUE WHERE id_admin = %s",
                (id_admin,)
            )
            if cursor.rowcount == 0:
                raise UsuarioNoEncontradoError(f"No existe un administrador con ID {id_admin}.")
            self.db.conexion.commit()
        except mysql.connector.Error:
            self.db.conexion.rollback()
            raise
        finally:
            cursor.close()

    # Reiniciar intentos fallidos tras un login exitoso
    def reiniciar_intentos_fallidos(self, id_admin: int) -> None:
        cursor = self.db.cursor()
        try:
            cursor.execute(
                "UPDATE administradores SET intentos_fallidos = 0 WHERE id_admin = %s",
                (id_admin,)
            )
            if cursor.rowcount == 0:
                raise UsuarioNoEncontradoError(f"No existe un administrador con ID {id_admin}.")
            self.db.conexion.commit()
        except mysql.connector.Error:
            self.db.conexion.rollback()
            raise
        finally:
            cursor.close()

    # Helper interno: convierte una fila (dict) en objeto Administrador
    @staticmethod
    def _fila_a_administrador(fila: dict) -> Administrador:
        return Administrador(
            id_admin=fila["id_admin"],
            usuario=fila["usuario"],
            contrasena_hash=fila["contrasena_hash"],
            intentos_fallidos=fila["intentos_fallidos"],
            bloqueado=bool(fila["bloqueado"]),
            fecha_creacion=fila["fecha_creacion"],
        )