"""
DAO: UsuarioDAO

Se encarga exclusivamente de la comunicación con la tabla `usuarios`
en MySQL. No contiene reglas de negocio (eso vive en
controllers/usuario_controller.py) — solo consultas parametrizadas.
"""

import mysql.connector

from database.conexion import dataBase
from models.usuarios import Usuario
from utils.excepciones import UsuarioDuplicadoError, UsuarioNoEncontradoError


class UsuarioDAO:

    def __init__(self, db: dataBase):
        self.db = db

    # Crear usuario
    def registrar(self, usuario: Usuario) -> int:
        """Inserta el usuario y retorna el id_usuario asignado por MySQL."""
        cursor = self.db.cursor()
        try:
            cursor.execute(
                """INSERT INTO usuarios
                   (nombre_completo, dui, correo, telefono, fecha_registro)
                   VALUES (%s, %s, %s, %s, %s)""",
                (
                    usuario.nombre_completo, usuario.dui, usuario.correo,
                    usuario.telefono, usuario.fecha_registro
                )
            )
            self.db.conexion.commit()
            return cursor.lastrowid
        except mysql.connector.errors.IntegrityError as error:
            self.db.conexion.rollback()
            raise UsuarioDuplicadoError(
                f"Ya existe un usuario registrado con el DUI '{usuario.dui}' "
                f"o el correo '{usuario.correo}'."
            ) from error
        finally:
            cursor.close()

    # Editar usuario
    def modificar(self, usuario: Usuario) -> None:
        if usuario.id_usuario is None:
            raise ValueError("No se puede modificar un usuario sin id_usuario.")

        cursor = self.db.cursor()
        try:
            cursor.execute(
                """UPDATE usuarios
                   SET nombre_completo = %s, dui = %s, correo = %s, telefono = %s
                   WHERE id_usuario = %s""",
                (
                    usuario.nombre_completo, usuario.dui, usuario.correo,
                    usuario.telefono, usuario.id_usuario
                )
            )
            if cursor.rowcount == 0:
                raise UsuarioNoEncontradoError(
                    f"No existe un usuario con el ID {usuario.id_usuario}."
                )
            self.db.conexion.commit()
        except mysql.connector.errors.IntegrityError as error:
            self.db.conexion.rollback()
            raise UsuarioDuplicadoError(
                f"El DUI '{usuario.dui}' o el correo '{usuario.correo}' "
                "ya pertenecen a otro usuario."
            ) from error
        except mysql.connector.Error:
            self.db.conexion.rollback()
            raise
        finally:
            cursor.close()

    # Eliminar usuario
    def eliminar(self, id_usuario: int) -> None:
        cursor = self.db.cursor()
        try:
            cursor.execute("DELETE FROM usuarios WHERE id_usuario = %s", (id_usuario,))
            if cursor.rowcount == 0:
                raise UsuarioNoEncontradoError(f"No existe un usuario con el ID {id_usuario}.")
            self.db.conexion.commit()
        except mysql.connector.errors.IntegrityError as error:
            self.db.conexion.rollback()
            # Ocurre si el usuario tiene préstamos asociados (ON DELETE RESTRICT)
            raise ValueError(
                "No se puede eliminar el usuario porque tiene préstamos registrados."
            ) from error
        except mysql.connector.Error:
            self.db.conexion.rollback()
            raise
        finally:
            cursor.close()

    # Buscar usuario (por ID o por DUI)
    def buscar_por_id(self, id_usuario: int) -> Usuario | None:
        cursor = self.db.cursor()
        try:
            cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (id_usuario,))
            fila = cursor.fetchone()
            return self._fila_a_usuario(fila) if fila else None
        finally:
            cursor.close()

    def buscar_por_dui(self, dui: str) -> Usuario | None:
        cursor = self.db.cursor()
        try:
            cursor.execute("SELECT * FROM usuarios WHERE dui = %s", (dui,))
            fila = cursor.fetchone()
            return self._fila_a_usuario(fila) if fila else None
        finally:
            cursor.close()

    # Listar usuarios
    def listar_todos(self) -> list[Usuario]:
        cursor = self.db.cursor()
        try:
            cursor.execute("SELECT * FROM usuarios ORDER BY nombre_completo")
            return [self._fila_a_usuario(fila) for fila in cursor.fetchall()]
        finally:
            cursor.close()

    # Helper interno: convierte una fila (dict) en objeto Usuario
    @staticmethod
    def _fila_a_usuario(fila: dict) -> Usuario:
        return Usuario(
            id_usuario=fila["id_usuario"],
            nombre_completo=fila["nombre_completo"],
            dui=fila["dui"],
            correo=fila["correo"],
            telefono=fila["telefono"],
            fecha_registro=fila["fecha_registro"],
        )