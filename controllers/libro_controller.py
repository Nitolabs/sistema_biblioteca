"""
Controlador: LibroController

Orquesta las operaciones de gestión de libros y las
validaciones asociadas. No conoce nada de consola
(input/print) — eso vive en views/libro_view.py. No conoce SQL
directamente — usa LibroDAO para leer/escribir datos.
"""

from dao.libro_dao import LibroDAO
from models.libros import Libro
from utils.excepciones import ISBNDuplicadoError, LibroNoEncontradoError


class LibroController:

    def __init__(self, libro_dao: LibroDAO):
        self.libro_dao = libro_dao

    # Registrar libro

    # La construcción de Libro(...) ya dispara las validaciones de
    # formato (título vacío, año futuro, etc. — ver __post_init__
    # en models/libro.py). Aquí solo se agrega la validación que
    # SÍ depende de la base de datos: ISBN duplicado.
    def registrar_libro(
        self,
        isbn: str,
        titulo: str,
        autor: str,
        editorial: str,
        anio_publicacion: int,
        categoria: str,
        cantidad_disponible: int,
    ) -> Libro:
        if self.libro_dao.buscar_por_isbn(isbn) is not None:
            raise ISBNDuplicadoError(f"Ya existe un libro registrado con el ISBN '{isbn}'.")

        estado = "Disponible" if cantidad_disponible > 0 else "No disponible"

        libro = Libro(
            isbn=isbn,
            titulo=titulo,
            autor=autor,
            editorial=editorial,
            anio_publicacion=anio_publicacion,
            categoria=categoria,
            cantidad_disponible=cantidad_disponible,
            estado=estado,
        )

        self.libro_dao.registrar(libro)
        return libro

    # Modificar libro
    def modificar_libro(
        self,
        isbn: str,
        titulo: str,
        autor: str,
        editorial: str,
        anio_publicacion: int,
        categoria: str,
        cantidad_disponible: int,
    ) -> Libro:
        libro_actual = self.libro_dao.buscar_por_isbn(isbn)
        if libro_actual is None:
            raise LibroNoEncontradoError(f"No existe un libro con el ISBN '{isbn}'.")

        estado = "Disponible" if cantidad_disponible > 0 else "No disponible"

        libro_actualizado = Libro(
            isbn=isbn,
            titulo=titulo,
            autor=autor,
            editorial=editorial,
            anio_publicacion=anio_publicacion,
            categoria=categoria,
            cantidad_disponible=cantidad_disponible,
            estado=estado,
        )

        self.libro_dao.modificar(libro_actualizado)
        return libro_actualizado

    # Eliminar libro
    def eliminar_libro(self, isbn: str) -> None:
        if self.libro_dao.buscar_por_isbn(isbn) is None:
            raise LibroNoEncontradoError(f"No existe un libro con el ISBN '{isbn}'.")
        self.libro_dao.eliminar(isbn)


    # Consultar un libro
    def consultar_libro(self, isbn: str) -> Libro:
        libro = self.libro_dao.buscar_por_isbn(isbn)
        if libro is None:
            raise LibroNoEncontradoError(f"No existe un libro con el ISBN '{isbn}'.")
        return libro


    # Buscar por título / autor / categoría
    def buscar_libros(self, criterio: str, texto: str) -> list[Libro]:
        criterios_validos = {
            "isbn": lambda t: [self.libro_dao.buscar_por_isbn(t)] if self.libro_dao.buscar_por_isbn(t) else [],
            "titulo": self.libro_dao.buscar_por_titulo,
            "autor": self.libro_dao.buscar_por_autor,
            "categoria": self.libro_dao.buscar_por_categoria,
        }

        buscar = criterios_validos.get(criterio.lower())
        if buscar is None:
            raise ValueError(
                f"Criterio de búsqueda inválido: '{criterio}'. "
                "Use 'isbn', 'titulo', 'autor' o 'categoria'."
            )
        return buscar(texto)

    # Reportes relacionados a libros
    def listar_todos(self) -> list[Libro]:
        return self.libro_dao.listar_todos()

    def listar_disponibles(self) -> list[Libro]:
        return self.libro_dao.listar_disponibles()

    def listar_sin_existencias(self) -> list[Libro]:
        return self.libro_dao.listar_sin_existencias()