"""
Modelo: Prestamo

Representa el encabezado de un préstamo (quién, cuándo, estado
general). Los libros específicos prestados viven en DetallePrestamo.

No contiene lógica de negocio (ej. "máximo 3 préstamos activos")
ni de base de datos — solo estructura y validaciones de formato.
Las reglas de negocio van en controllers/prestamo_controller.py.
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional

ESTADOS_VALIDOS = ("Activo", "Devuelto", "Vencido")


@dataclass
class Prestamo:
    id_usuario: int
    fecha_limite: date
    fecha_prestamo: date = None
    estado: str = "Activo"
    codigo_prestamo: Optional[int] = None  # lo asigna MySQL (AUTO_INCREMENT)

    def __post_init__(self):
        if self.fecha_prestamo is None:
            self.fecha_prestamo = date.today()

        if self.codigo_prestamo is not None and self.codigo_prestamo <= 0:
            raise ValueError("El código de préstamo debe ser un número positivo.")

        if self.id_usuario is None or self.id_usuario <= 0:
            raise ValueError("Debe indicar un usuario válido para el préstamo.")

        if self.fecha_limite < self.fecha_prestamo:
            raise ValueError("La fecha límite no puede ser anterior a la fecha del préstamo.")

        if self.estado not in ESTADOS_VALIDOS:
            raise ValueError(
                f"Estado inválido: '{self.estado}'. Debe ser uno de {ESTADOS_VALIDOS}."
            )

    @property
    def esta_activo(self) -> bool:
        return self.estado == "Activo"

    @property
    def esta_vencido(self) -> bool:
        return self.esta_activo and self.fecha_limite < date.today()

    def __str__(self) -> str:
        codigo = self.codigo_prestamo if self.codigo_prestamo is not None else "sin asignar"
        return (
            f"[{codigo}] Usuario #{self.id_usuario} - "
            f"Préstamo: {self.fecha_prestamo} - Límite: {self.fecha_limite} - "
            f"Estado: {self.estado}"
        )


if __name__ == "__main__":
    prestamo = Prestamo(
        id_usuario=1,
        fecha_limite=date(2026, 7, 23),
    )
    print(prestamo)
    print("¿Activo?", prestamo.esta_activo)
    print("¿Vencido?", prestamo.esta_vencido)