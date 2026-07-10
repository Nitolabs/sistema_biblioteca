"""
DAO: LibroDAO

Se encarga exclusivamente de la comunicación con la tabla `libros`
en MySQL. No contiene reglas de negocio (eso vive en
controllers/libro_controller.py) — solo consultas parametrizadas.
"""

import mysql.connector

from database.conexion import dataBase
from models.libros import Libro
from utils.excepciones import ISBNDuplicadoError, LibroNoEncontradoError


class LibroDAO:

    def __init__(self, db: dataBase):
        self.db = db

    # Registrar libro
    def registrar(self, libro: Libro) -> None:
        cursor = self.db.cursor()
        try:
            cursor.execute(
                """INSERT INTO libros
                   (isbn, titulo, autor, editorial, anio_publicacion,
                    categoria, cantidad_disponible, estado)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    libro.isbn, libro.titulo, libro.autor, libro.editorial,
                    libro.anio_publicacion, libro.categoria,
                    libro.cantidad_disponible, libro.estado
                )
            )
            self.db.conexion.commit()
        except mysql.connector.errors.IntegrityError as error:
            self.db.conexion.rollback()
            raise ISBNDuplicadoError(
                f"Ya existe un libro registrado con el ISBN '{libro.isbn}'."
            ) from error
        finally:
            cursor.close()


    # Modificar libro
    def modificar(self, libro: Libro) -> None:
        cursor = self.db.cursor()
        try:
            cursor.execute(
                """UPDATE libros
                   SET titulo = %s, autor = %s, editorial = %s,
                       anio_publicacion = %s, categoria = %s,
                       cantidad_disponible = %s, estado = %s
                   WHERE isbn = %s""",
                (
                    libro.titulo, libro.autor, libro.editorial,
                    libro.anio_publicacion, libro.categoria,
                    libro.cantidad_disponible, libro.estado, libro.isbn
                )
            )
            if cursor.rowcount == 0:
                raise LibroNoEncontradoError(
                    f"No existe un libro con el ISBN '{libro.isbn}'."
                )
            self.db.conexion.commit()
        except mysql.connector.Error:
            self.db.conexion.rollback()
            raise
        finally:
            cursor.close()


    # Eliminar libro
    def eliminar(self, isbn: str) -> None:
        cursor = self.db.cursor()
        try:
            cursor.execute("DELETE FROM libros WHERE isbn = %s", (isbn,))
            if cursor.rowcount == 0:
                raise LibroNoEncontradoError(f"No existe un libro con el ISBN '{isbn}'.")
            self.db.conexion.commit()
        except mysql.connector.Error:
            self.db.conexion.rollback()
            raise
        finally:
            cursor.close()


    # Consultar un libro por ISBN
    def buscar_por_isbn(self, isbn: str) -> Libro | None:
        cursor = self.db.cursor()
        try:
            cursor.execute("SELECT * FROM libros WHERE isbn = %s", (isbn,))
            fila = cursor.fetchone()
            return self._fila_a_libro(fila) if fila else None
        finally:
            cursor.close()


    # Buscar por título, autor o categoría (coincidencia parcial)
    def buscar_por_titulo(self, texto: str) -> list[Libro]:
        return self._buscar_por_campo("titulo", texto)

    def buscar_por_autor(self, texto: str) -> list[Libro]:
        return self._buscar_por_campo("autor", texto)

    def buscar_por_categoria(self, texto: str) -> list[Libro]:
        return self._buscar_por_campo("categoria", texto)

    def _buscar_por_campo(self, campo: str, texto: str) -> list[Libro]:
        # campo siempre es un valor fijo definido internamente (no viene
        # del usuario), por lo que no representa riesgo de inyección SQL
        cursor = self.db.cursor()
        try:
            consulta = f"SELECT * FROM libros WHERE {campo} LIKE %s"
            cursor.execute(consulta, (f"%{texto}%",))
            filas = cursor.fetchall()
            return [self._fila_a_libro(fila) for fila in filas]
        finally:
            cursor.close()

    # Listados (usados también por reportes)
    def listar_todos(self) -> list[Libro]:
        cursor = self.db.cursor()
        try:
            cursor.execute("SELECT * FROM libros")
            return [self._fila_a_libro(fila) for fila in cursor.fetchall()]
        finally:
            cursor.close()

    def listar_disponibles(self) -> list[Libro]:
        cursor = self.db.cursor()
        try:
            cursor.execute(
                "SELECT * FROM libros WHERE cantidad_disponible > 0"
            )
            return [self._fila_a_libro(fila) for fila in cursor.fetchall()]
        finally:
            cursor.close()

    def listar_sin_existencias(self) -> list[Libro]:
        cursor = self.db.cursor()
        try:
            cursor.execute(
                "SELECT * FROM libros WHERE cantidad_disponible = 0"
            )
            return [self._fila_a_libro(fila) for fila in cursor.fetchall()]
        finally:
            cursor.close()


    # Usado por el controlador de préstamos al prestar/devolver
    def actualizar_cantidad(self, isbn: str, nueva_cantidad: int) -> None:
        cursor = self.db.cursor()
        try:
            nuevo_estado = "Disponible" if nueva_cantidad > 0 else "No disponible"
            cursor.execute(
                """UPDATE libros
                   SET cantidad_disponible = %s, estado = %s
                   WHERE isbn = %s""",
                (nueva_cantidad, nuevo_estado, isbn)
            )
            if cursor.rowcount == 0:
                raise LibroNoEncontradoError(f"No existe un libro con el ISBN '{isbn}'.")
            self.db.conexion.commit()
        except mysql.connector.Error:
            self.db.conexion.rollback()
            raise
        finally:
            cursor.close()

    # Helper interno: convierte una fila (dict) en objeto Libro
    @staticmethod
    def _fila_a_libro(fila: dict) -> Libro:
        return Libro(
            isbn=fila["isbn"],
            titulo=fila["titulo"],
            autor=fila["autor"],
            editorial=fila["editorial"],
            anio_publicacion=fila["anio_publicacion"],
            categoria=fila["categoria"],
            cantidad_disponible=fila["cantidad_disponible"],
            estado=fila["estado"],
        )