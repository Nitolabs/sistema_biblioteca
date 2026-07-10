"""
Modelo: DetallePrestamo

Representa un libro específico dentro de un préstamo. Permite que
un préstamo (Prestamo) incluya varios libros distintos.

No contiene lógica de negocio ni de base de datos.
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class DetallePrestamo:
    codigo_prestamo: int
    isbn_libro: str
    fecha_devolucion: Optional[date] = None
    id_detalle: Optional[int] = None  # lo asigna MySQL (AUTO_INCREMENT)

    def __post_init__(self):
        if self.codigo_prestamo is None or self.codigo_prestamo <= 0:
            raise ValueError("Debe indicar un código de préstamo válido.")

        if not self.isbn_libro or not self.isbn_libro.strip():
            raise ValueError("El ISBN del libro no puede estar vacío.")

        if self.id_detalle is not None and self.id_detalle <= 0:
            raise ValueError("El ID de detalle debe ser un número positivo.")

    @property
    def ya_devuelto(self) -> bool:
        return self.fecha_devolucion is not None

    def __str__(self) -> str:
        estado = f"devuelto el {self.fecha_devolucion}" if self.ya_devuelto else "pendiente de devolución"
        return f"Préstamo #{self.codigo_prestamo} - ISBN {self.isbn_libro} ({estado})"


if __name__ == "__main__":
    detalle = DetallePrestamo(
        codigo_prestamo=1,
        isbn_libro="978-3-16-148410-0",
    )
    print(detalle)
    print("¿Ya devuelto?", detalle.ya_devuelto)