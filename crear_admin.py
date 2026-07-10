"""
Script: crear_admin.py

Utilidad de línea de comandos para crear administradores del
sistema. Se usa principalmente para crear el PRIMER administrador,
ya que el sistema no permite crear cuentas desde el menú principal
sin haber iniciado sesión antes.

Uso:
    python crear_admin.py
"""

import getpass

from database.conexion import dataBase
from dao.administrador_dao import AdministradorDAO
from controllers.auth_controller import AuthController
from utils.excepciones import UsuarioDuplicadoError


def solicitar_contrasena() -> str:
    while True:
        contrasena = getpass.getpass("Contraseña: ")
        confirmacion = getpass.getpass("Confirme la contraseña: ")

        if contrasena != confirmacion:
            print("Las contraseñas no coinciden. Intente de nuevo.\n")
            continue

        if len(contrasena) < 8:
            print("La contraseña debe tener al menos 8 caracteres.\n")
            continue

        return contrasena


def main() -> None:
    print("=" * 40)
    print("  CREAR ADMINISTRADOR DEL SISTEMA")
    print("=" * 40)

    usuario = input("Nombre de usuario: ").strip()
    if not usuario:
        print("El nombre de usuario no puede estar vacío.")
        return

    contrasena = solicitar_contrasena()

    db = dataBase()
    try:
        auth_controller = AuthController(AdministradorDAO(db))
        auth_controller.crear_administrador(usuario, contrasena)
        print(f"\nAdministrador '{usuario}' creado exitosamente.")

    except UsuarioDuplicadoError as error:
        print(f"\nError: {error}")

    finally:
        db.cerrarConexion()


if __name__ == "__main__":
    main()