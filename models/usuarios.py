"""
Modelo: Usuario

Representa un usuario en el sistema.
No contiene lógica de ningún tipo más que la de formato permitido para las variables.
"""

# Imports
import re
from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Usuario:
    nombre_completo: str
    dui: str
    correo: str
    telefono: str
    fecha_registro: date
    id_usuario: Optional[int] = None  # lo asigna SQL (AUTO_INCREMENT) al insertar

    # Validaciones básicas de formato
    def __post_init__(self):
        if self.id_usuario is not None and self.id_usuario <= 0:
            raise ValueError("El ID del usuario debe ser un número positivo.")

        if not self.nombre_completo or not self.nombre_completo.strip():
            raise ValueError("El nombre del usuario no puede estar vacío.")

        if not self.dui or not self.dui.strip() or len(self.dui) != 10:
            raise ValueError("El DUI debe tener el formato 00000000-0 (10 caracteres).")

        if not self.correo or not re.match(r"[^@]+@[^@]+\.[^@]+", self.correo):
            raise ValueError("El correo electrónico no tiene un formato válido.")

        if not self.telefono or not self.telefono.strip():
            raise ValueError("El teléfono del usuario no puede estar vacío.")

        if not self.fecha_registro or self.fecha_registro > date.today():
            raise ValueError("La fecha de registro no puede ser del futuro.")

    def __str__(self) -> str:
        id_str = self.id_usuario if self.id_usuario is not None else "sin asignar"
        return f"[{id_str}] {self.nombre_completo} - DUI: {self.dui} - {self.correo}"


if __name__ == "__main__":
    # Test rápido del modelo, sin DB

    # Caso: usuario nuevo, aún sin ID (antes de insertarse en la BD)
    usuario_nuevo = Usuario(
        nombre_completo="Dominic Alejandro Castillo González",
        dui="00000000-0",  # DUI de muestra
        correo="correo@gmail.com",
        telefono="78787878",
        fecha_registro=date(2026, 1, 22)
    )
    print(usuario_nuevo)

    # Caso: usuario ya existente
    usuario_existente = Usuario(
        id_usuario=1,
        nombre_completo="Dominic Alejandro Castillo González",
        dui="00000000-0",
        correo="correo@gmail.com",
        telefono="78787878",
        fecha_registro=date(2026, 1, 22)
    )
    print(usuario_existente)