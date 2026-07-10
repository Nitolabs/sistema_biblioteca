"""
Controlador: UsuarioController

Orquesta las operaciones de gestión de usuarios (RF-03) y las
validaciones asociadas (RF-07). No conoce nada de consola
(input/print) — eso vive en views/usuario_view.py. No conoce SQL
directamente — usa UsuarioDAO para leer/escribir datos.
"""

from datetime import date

from dao.usuario_dao import UsuarioDAO
from models.usuarios import Usuario
from utils.excepciones import UsuarioDuplicadoError, UsuarioNoEncontradoError


class UsuarioController:

    def __init__(self, usuario_dao: UsuarioDAO):
        self.usuario_dao = usuario_dao

    # Crear usuario

    # La construcción de Usuario(...) ya valida formato (nombre
    # vacío, correo inválido, DUI con longitud incorrecta — ver
    # __post_init__ en models/usuario.py). Aquí se agrega la
    # validación que SÍ depende de la base de datos: DUI duplicado.
    def registrar_usuario(
        self,
        nombre_completo: str,
        dui: str,
        correo: str,
        telefono: str,
    ) -> Usuario:
        if self.usuario_dao.buscar_por_dui(dui) is not None:
            raise UsuarioDuplicadoError(f"Ya existe un usuario registrado con el DUI '{dui}'.")

        usuario = Usuario(
            nombre_completo=nombre_completo,
            dui=dui,
            correo=correo,
            telefono=telefono,
            fecha_registro=date.today(),
        )

        id_usuario = self.usuario_dao.registrar(usuario)
        usuario.id_usuario = id_usuario
        return usuario


    # Editar usuario
    def modificar_usuario(
        self,
        id_usuario: int,
        nombre_completo: str,
        dui: str,
        correo: str,
        telefono: str,
    ) -> Usuario:
        usuario_actual = self.usuario_dao.buscar_por_id(id_usuario)
        if usuario_actual is None:
            raise UsuarioNoEncontradoError(f"No existe un usuario con el ID {id_usuario}.")

        # Si cambió el DUI, verificar que el nuevo no pertenezca a otro usuario
        if dui != usuario_actual.dui:
            otro = self.usuario_dao.buscar_por_dui(dui)
            if otro is not None and otro.id_usuario != id_usuario:
                raise UsuarioDuplicadoError(f"El DUI '{dui}' ya pertenece a otro usuario.")

        usuario_actualizado = Usuario(
            id_usuario=id_usuario,
            nombre_completo=nombre_completo,
            dui=dui,
            correo=correo,
            telefono=telefono,
            fecha_registro=usuario_actual.fecha_registro,
        )

        self.usuario_dao.modificar(usuario_actualizado)
        return usuario_actualizado

    # Eliminar usuario
    def eliminar_usuario(self, id_usuario: int) -> None:
        if self.usuario_dao.buscar_por_id(id_usuario) is None:
            raise UsuarioNoEncontradoError(f"No existe un usuario con el ID {id_usuario}.")
        # Si el usuario tiene préstamos asociados, el DAO lanza ValueError
        # (por la restricción ON DELETE RESTRICT de la base de datos).
        self.usuario_dao.eliminar(id_usuario)

    # Buscar usuario (por ID o por DUI)
    def buscar_por_id(self, id_usuario: int) -> Usuario:
        usuario = self.usuario_dao.buscar_por_id(id_usuario)
        if usuario is None:
            raise UsuarioNoEncontradoError(f"No existe un usuario con el ID {id_usuario}.")
        return usuario

    def buscar_por_dui(self, dui: str) -> Usuario:
        usuario = self.usuario_dao.buscar_por_dui(dui)
        if usuario is None:
            raise UsuarioNoEncontradoError(f"No existe un usuario con el DUI '{dui}'.")
        return usuario


    # Listar usuarios
    def listar_usuarios(self) -> list[Usuario]:
        return self.usuario_dao.listar_todos()