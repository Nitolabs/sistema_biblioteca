"""
Controlador: AuthController

Contiene las reglas de negocio del inicio de sesión:
  - máximo 3 intentos
  - bloqueo de acceso tras exceder los intentos
  - hash seguro de contraseñas (nunca texto plano)

No conoce nada de consola (input/print) — eso vive en
views/auth_view.py. No conoce SQL directamente — usa
AdministradorDAO para leer/escribir datos.
"""

import bcrypt

from dao.administrador_dao import AdministradorDAO
from models.administradores import Administrador, MAX_INTENTOS_FALLIDOS
from utils.excepciones import CredencialesInvalidasError, CuentaBloqueadaError


class AuthController:

    def __init__(self, administrador_dao: AdministradorDAO):
        self.administrador_dao = administrador_dao

    # -----------------------------------------------------------
    # RF-01: Iniciar sesión
    # -----------------------------------------------------------
    def iniciar_sesion(self, usuario: str, contrasena: str) -> Administrador:
        admin = self.administrador_dao.buscar_por_usuario(usuario)

        # No revelamos si el problema fue el usuario o la contraseña,
        # por seguridad (evita que alguien "adivine" usuarios válidos).
        if admin is None:
            raise CredencialesInvalidasError("Usuario o contraseña incorrectos.")

        if admin.bloqueado:
            raise CuentaBloqueadaError(
                "Esta cuenta está bloqueada por exceder el número de intentos. "
                "Contacte al administrador del sistema."
            )

        if not self._verificar_contrasena(contrasena, admin.contrasena_hash):
            self._registrar_intento_fallido(admin)
            raise CredencialesInvalidasError("Usuario o contraseña incorrectos.")

        # Login exitoso: reinicia el contador de intentos fallidos
        self.administrador_dao.reiniciar_intentos_fallidos(admin.id_admin)
        admin.intentos_fallidos = 0
        return admin

    # -----------------------------------------------------------
    # Crear un nuevo administrador (hashea la contraseña antes de guardar)
    # -----------------------------------------------------------
    def crear_administrador(self, usuario: str, contrasena_plana: str) -> int:
        contrasena_hash = self._hashear_contrasena(contrasena_plana)
        nuevo_admin = Administrador(
            usuario=usuario,
            contrasena_hash=contrasena_hash,
        )
        return self.administrador_dao.registrar(nuevo_admin)

    # -----------------------------------------------------------
    # Internos
    # -----------------------------------------------------------
    def _registrar_intento_fallido(self, admin: Administrador) -> None:
        self.administrador_dao.incrementar_intentos_fallidos(admin.id_admin)
        intentos_totales = admin.intentos_fallidos + 1

        if intentos_totales >= MAX_INTENTOS_FALLIDOS:
            self.administrador_dao.bloquear(admin.id_admin)

    @staticmethod
    def _hashear_contrasena(contrasena_plana: str) -> str:
        hash_bytes = bcrypt.hashpw(contrasena_plana.encode("utf-8"), bcrypt.gensalt())
        return hash_bytes.decode("utf-8")

    @staticmethod
    def _verificar_contrasena(contrasena_plana: str, contrasena_hash: str) -> bool:
        return bcrypt.checkpw(
            contrasena_plana.encode("utf-8"),
            contrasena_hash.encode("utf-8")
        )