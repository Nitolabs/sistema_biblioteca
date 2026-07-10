"""
Vista: AuthView

Responsable únicamente de la interacción por consola para el
login. No contiene reglas de negocio ni acceso a datos:
solo pide datos con input() y muestra resultados con print().
Toda la lógica real vive en controllers/auth_controller.py.
"""

import getpass

from controllers.auth_controller import AuthController
from models.administradores import Administrador
from utils.excepciones import CredencialesInvalidasError, CuentaBloqueadaError

MAX_INTENTOS_VISTA = 3


class AuthView:

    def __init__(self, auth_controller: AuthController):
        self.auth_controller = auth_controller

    def mostrar_login(self) -> Administrador | None:
        """
        Muestra el formulario de login y reintenta hasta 3 veces.
        Retorna el Administrador autenticado, o None si se agotaron
        los intentos o la cuenta quedó bloqueada.
        """
        print("=" * 40)
        print("  SISTEMA DE GESTIÓN DE BIBLIOTECA")
        print("           Inicio de sesión")
        print("=" * 40)

        for intento in range(1, MAX_INTENTOS_VISTA + 1):
            usuario = input("Usuario: ").strip()
            contrasena = getpass.getpass("Contraseña: ")

            try:
                admin = self.auth_controller.iniciar_sesion(usuario, contrasena)
                print(f"\nBienvenido, {admin.usuario}.\n")
                return admin

            except CuentaBloqueadaError as error:
                print(f"\n{error}\n")
                return None

            except CredencialesInvalidasError as error:
                restantes = MAX_INTENTOS_VISTA - intento
                if restantes > 0:
                    print(f"{error} Intentos restantes: {restantes}\n")
                else:
                    print(f"\n{error}")
                    print("Ha excedido el número máximo de intentos.\n")

        return None