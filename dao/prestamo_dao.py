"""
DAO: PrestamoDAO

Se encarga de la comunicación con las tablas `prestamos` y
`detalle_prestamo`. No contiene las reglas de negocio del
máximo 3 préstamos activos, no repetir libro activo — esas viven
en controllers/prestamo_controller.py. Este DAO expone las
consultas que el controlador necesita para poder validarlas.
"""

import mysql.connector

from database.conexion import dataBase
from models.prestamos import Prestamo
from models.detalle_prestamo import DetallePrestamo
from utils.excepciones import LibroNoEncontradoError


class PrestamoDAO:

    def __init__(self, db: dataBase):
        self.db = db

    # Registrar préstamo (encabezado + uno o más libros)

    # Ambas tablas se escriben dentro de la MISMA transacción:
    # solo se hace commit al final, si todo salió bien. Si algo
    # falla a mitad de camino, se revierte todo (rollback).
    def registrar(self, prestamo: Prestamo, isbns: list[str]) -> int:
        cursor = self.db.cursor()
        try:
            cursor.execute(
                """INSERT INTO prestamos
                   (id_usuario, fecha_prestamo, fecha_limite, estado)
                   VALUES (%s, %s, %s, %s)""",
                (
                    prestamo.id_usuario, prestamo.fecha_prestamo,
                    prestamo.fecha_limite, prestamo.estado
                )
            )
            codigo_prestamo = cursor.lastrowid

            for isbn in isbns:
                cursor.execute(
                    """INSERT INTO detalle_prestamo (codigo_prestamo, isbn_libro)
                       VALUES (%s, %s)""",
                    (codigo_prestamo, isbn)
                )

            self.db.conexion.commit()
            return codigo_prestamo
        except mysql.connector.Error:
            self.db.conexion.rollback()
            raise
        finally:
            cursor.close()


    # Validaciones que necesita el controlador ANTES de prestar
    def contar_prestamos_activos(self, id_usuario: int) -> int:
        cursor = self.db.cursor()
        try:
            cursor.execute(
                """SELECT COUNT(*) AS total FROM prestamos
                   WHERE id_usuario = %s AND estado = 'Activo'""",
                (id_usuario,)
            )
            return cursor.fetchone()["total"]
        finally:
            cursor.close()

    def tiene_prestamo_activo_de_libro(self, id_usuario: int, isbn: str) -> bool:
        cursor = self.db.cursor()
        try:
            cursor.execute(
                """SELECT COUNT(*) AS total
                   FROM prestamos p
                   JOIN detalle_prestamo dp ON dp.codigo_prestamo = p.codigo_prestamo
                   WHERE p.id_usuario = %s AND dp.isbn_libro = %s
                     AND p.estado = 'Activo' AND dp.fecha_devolucion IS NULL""",
                (id_usuario, isbn)
            )
            return cursor.fetchone()["total"] > 0
        finally:
            cursor.close()

    # Registrar devolución

    # Marca la fecha de devolución del detalle correspondiente y,
    # si TODOS los libros del préstamo ya fueron devueltos, marca
    # el préstamo completo como "Devuelto".
    def registrar_devolucion(self, codigo_prestamo: int, isbn: str) -> None:
        cursor = self.db.cursor()
        try:
            cursor.execute(
                """UPDATE detalle_prestamo
                   SET fecha_devolucion = CURDATE()
                   WHERE codigo_prestamo = %s AND isbn_libro = %s
                     AND fecha_devolucion IS NULL""",
                (codigo_prestamo, isbn)
            )
            if cursor.rowcount == 0:
                raise LibroNoEncontradoError(
                    f"El libro '{isbn}' no está pendiente de devolución "
                    f"en el préstamo #{codigo_prestamo}."
                )

            cursor.execute(
                """SELECT COUNT(*) AS pendientes FROM detalle_prestamo
                   WHERE codigo_prestamo = %s AND fecha_devolucion IS NULL""",
                (codigo_prestamo,)
            )
            pendientes = cursor.fetchone()["pendientes"]

            if pendientes == 0:
                cursor.execute(
                    "UPDATE prestamos SET estado = 'Devuelto' WHERE codigo_prestamo = %s",
                    (codigo_prestamo,)
                )

            self.db.conexion.commit()
        except mysql.connector.Error:
            self.db.conexion.rollback()
            raise
        finally:
            cursor.close()

    # Consultas / RF-06: Reportes
    def buscar_por_codigo(self, codigo_prestamo: int) -> Prestamo | None:
        cursor = self.db.cursor()
        try:
            cursor.execute(
                "SELECT * FROM prestamos WHERE codigo_prestamo = %s", (codigo_prestamo,)
            )
            fila = cursor.fetchone()
            return self._fila_a_prestamo(fila) if fila else None
        finally:
            cursor.close()

    def listar_detalle(self, codigo_prestamo: int) -> list[DetallePrestamo]:
        cursor = self.db.cursor()
        try:
            cursor.execute(
                "SELECT * FROM detalle_prestamo WHERE codigo_prestamo = %s",
                (codigo_prestamo,)
            )
            return [self._fila_a_detalle(fila) for fila in cursor.fetchall()]
        finally:
            cursor.close()

    def listar_activos(self) -> list[Prestamo]:
        cursor = self.db.cursor()
        try:
            cursor.execute("SELECT * FROM prestamos WHERE estado = 'Activo'")
            return [self._fila_a_prestamo(fila) for fila in cursor.fetchall()]
        finally:
            cursor.close()

    def listar_vencidos(self) -> list[Prestamo]:
        cursor = self.db.cursor()
        try:
            cursor.execute(
                """SELECT * FROM prestamos
                   WHERE estado = 'Activo' AND fecha_limite < CURDATE()"""
            )
            return [self._fila_a_prestamo(fila) for fila in cursor.fetchall()]
        finally:
            cursor.close()

    def marcar_vencidos(self) -> int:
        """Actualiza en bloque los préstamos activos cuya fecha límite ya pasó."""
        cursor = self.db.cursor()
        try:
            cursor.execute(
                """UPDATE prestamos SET estado = 'Vencido'
                   WHERE estado = 'Activo' AND fecha_limite < CURDATE()"""
            )
            self.db.conexion.commit()
            return cursor.rowcount
        except mysql.connector.Error:
            self.db.conexion.rollback()
            raise
        finally:
            cursor.close()

    def libros_mas_prestados(self, limite: int = 10) -> list[dict]:
        cursor = self.db.cursor()
        try:
            cursor.execute(
                """SELECT l.isbn, l.titulo, COUNT(*) AS veces_prestado
                   FROM detalle_prestamo dp
                   JOIN libros l ON l.isbn = dp.isbn_libro
                   GROUP BY l.isbn, l.titulo
                   ORDER BY veces_prestado DESC
                   LIMIT %s""",
                (limite,)
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    def usuarios_mayor_prestamos(self, limite: int = 10) -> list[dict]:
        cursor = self.db.cursor()
        try:
            cursor.execute(
                """SELECT u.id_usuario, u.nombre_completo, COUNT(*) AS total_prestamos
                   FROM prestamos p
                   JOIN usuarios u ON u.id_usuario = p.id_usuario
                   GROUP BY u.id_usuario, u.nombre_completo
                   ORDER BY total_prestamos DESC
                   LIMIT %s""",
                (limite,)
            )
            return cursor.fetchall()
        finally:
            cursor.close()

    # Helpers internos
    @staticmethod
    def _fila_a_prestamo(fila: dict) -> Prestamo:
        return Prestamo(
            codigo_prestamo=fila["codigo_prestamo"],
            id_usuario=fila["id_usuario"],
            fecha_prestamo=fila["fecha_prestamo"],
            fecha_limite=fila["fecha_limite"],
            estado=fila["estado"],
        )

    @staticmethod
    def _fila_a_detalle(fila: dict) -> DetallePrestamo:
        return DetallePrestamo(
            id_detalle=fila["id_detalle"],
            codigo_prestamo=fila["codigo_prestamo"],
            isbn_libro=fila["isbn_libro"],
            fecha_devolucion=fila["fecha_devolucion"],
        )