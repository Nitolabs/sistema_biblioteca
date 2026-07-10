"""
Modelo: Administrador

Representa una cuenta con acceso al sistema (RF-01: inicio de sesión).
Este modelo nunca maneja contraseñas en texto plano — solo el hash,
que se calcula en la capa de servicio/controlador antes de llegar aquí.

No contiene lógica de negocio (ej. "bloquear tras 3 intentos") ni de
base de datos — solo estructura y validaciones de formato.
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional

MAX_INTENTOS_FALLIDOS = 3


@dataclass
class Administrador:
    usuario: str
    contrasena_hash: str
    intentos_fallidos: int = 0
    bloqueado: bool = False
    fecha_creacion: date = None
    id_admin: Optional[int] = None  # lo asigna SQL (AUTO_INCREMENT)

    def __post_init__(self):
        if self.fecha_creacion is None:
            self.fecha_creacion = date.today()

        if self.id_admin is not None and self.id_admin <= 0:
            raise ValueError("El ID del administrador debe ser un número positivo.")

        if not self.usuario or not self.usuario.strip():
            raise ValueError("El nombre de usuario no puede estar vacío.")

        if not self.contrasena_hash or not self.contrasena_hash.strip():
            raise ValueError("El hash de la contraseña no puede estar vacío.")

        if self.intentos_fallidos < 0:
            raise ValueError("Los intentos fallidos no pueden ser negativos.")

    @property
    def intentos_restantes(self) -> int:
        return max(0, MAX_INTENTOS_FALLIDOS - self.intentos_fallidos)

    def __str__(self) -> str:
        estado = "bloqueado" if self.bloqueado else "activo"
        return f"Administrador: {self.usuario} ({estado}, intentos fallidos: {self.intentos_fallidos})"


if __name__ == "__main__":
    admin = Administrador(
        usuario="admin",
        contrasena_hash="$2b$12$ejemplode.hash.no.real",
    )
    print(admin)
    print("Intentos restantes:", admin.intentos_restantes)