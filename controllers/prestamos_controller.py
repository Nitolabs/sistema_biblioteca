"""
Controlador: PrestamoController

Contiene las reglas de negocio del RF-04 (préstamos) y RF-05
(devoluciones). Es el controlador más complejo porque coordina
tres DAOs distintos: PrestamoDAO, LibroDAO y UsuarioDAO.

No conoce nada de consola (input/print) — eso vive en
views/prestamo_view.py.
"""

from datetime import date, timedelta

from dao.prestamo_dao import PrestamoDAO
from dao.libro_dao import LibroDAO
from dao.usuario_dao import UsuarioDAO
from models.prestamos import Prestamo
from utils.excepciones import *

MAX_PRESTAMOS_ACTIVOS = 3
DIAS_PRESTAMO_DEFECTO = 14


class PrestamoController:

    def __init__(self, prestamo_dao: PrestamoDAO, libro_dao: LibroDAO, usuario_dao: UsuarioDAO):
        self.prestamo_dao = prestamo_dao
        self.libro_dao = libro_dao
        self.usuario_dao = usuario_dao

    # -----------------------------------------------------------
    # RF-04: Registrar préstamo
    #
    # Orden de validaciones (todas ANTES de tocar la base de datos,
    # para no dejar cambios a medias si algo falla):
    #   1. El usuario existe
    #   2. El usuario no supera el máximo de préstamos activos
    #   3. Cada libro existe y tiene existencias
    #   4. El usuario no tiene ya un préstamo activo de ese libro
    # -----------------------------------------------------------
    def registrar_prestamo(
        self,
        id_usuario: int,
        isbns: list[str],
        dias_prestamo: int = DIAS_PRESTAMO_DEFECTO,
    ) -> Prestamo:
        if not isbns:
            raise ValueError("Debe indicar al menos un libro para el préstamo.")

        if self.usuario_dao.buscar_por_id(id_usuario) is None:
            raise UsuarioNoEncontradoError(f"No existe un usuario con el ID {id_usuario}.")

        if self.prestamo_dao.contar_prestamos_activos(id_usuario) >= MAX_PRESTAMOS_ACTIVOS:
            raise PrestamoMaximoExcedidoError(
                f"El usuario ya tiene {MAX_PRESTAMOS_ACTIVOS} préstamos activos. "
                "Debe devolver alguno antes de solicitar uno nuevo."
            )

        for isbn in isbns:
            libro = self.libro_dao.buscar_por_isbn(isbn)
            if libro is None:
                raise LibroNoEncontradoError(f"No existe un libro con el ISBN '{isbn}'.")
            if libro.cantidad_disponible <= 0:
                raise LibroSinExistenciasError(f"El libro '{libro.titulo}' no tiene existencias disponibles.")
            if self.prestamo_dao.tiene_prestamo_activo_de_libro(id_usuario, isbn):
                raise PrestamoDuplicadoError(
                    f"El usuario ya tiene un préstamo activo del libro '{libro.titulo}'."
                )

        prestamo = Prestamo(
            id_usuario=id_usuario,
            fecha_prestamo=date.today(),
            fecha_limite=date.today() + timedelta(days=dias_prestamo),
        )

        codigo_prestamo = self.prestamo_dao.registrar(prestamo, isbns)
        prestamo.codigo_prestamo = codigo_prestamo

        # Descuenta inventario de cada libro prestado
        for isbn in isbns:
            libro = self.libro_dao.buscar_por_isbn(isbn)
            self.libro_dao.actualizar_cantidad(isbn, libro.cantidad_disponible - 1)

        return prestamo

    # -----------------------------------------------------------
    # RF-05: Registrar devolución
    #
    # Actualiza el detalle del préstamo y devuelve el libro al
    # inventario. Si era el último libro pendiente del préstamo,
    # PrestamoDAO ya se encarga de marcar el préstamo como
    # "Devuelto" automáticamente.
    # -----------------------------------------------------------
    def registrar_devolucion(self, codigo_prestamo: int, isbn: str) -> None:
        self.prestamo_dao.registrar_devolucion(codigo_prestamo, isbn)

        libro = self.libro_dao.buscar_por_isbn(isbn)
        if libro is None:
            raise LibroNoEncontradoError(f"No existe un libro con el ISBN '{isbn}'.")

        self.libro_dao.actualizar_cantidad(isbn, libro.cantidad_disponible + 1)

    # -----------------------------------------------------------
    # RF-06: Reportes relacionados a préstamos
    # -----------------------------------------------------------
    def listar_prestamos_activos(self) -> list[Prestamo]:
        return self.prestamo_dao.listar_activos()

    def listar_prestamos_vencidos(self) -> list[Prestamo]:
        # Primero actualiza en bloque cualquier préstamo activo cuya
        # fecha límite ya pasó, para que el reporte esté al día.
        self.prestamo_dao.marcar_vencidos()
        return self.prestamo_dao.listar_vencidos()

    def libros_mas_prestados(self, limite: int = 10) -> list[dict]:
        return self.prestamo_dao.libros_mas_prestados(limite)

    def usuarios_mayor_prestamos(self, limite: int = 10) -> list[dict]:
        return self.prestamo_dao.usuarios_mayor_prestamos(limite)