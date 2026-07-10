"""
Punto de entrada del sistema de gestión de biblioteca.

Se encarga de:
  1. Armar todas las dependencias (conexión, DAOs, controladores, vistas)
  2. Ejecutar el login
  3. Mostrar el menú principal con acceso a cada módulo
"""

from database.conexion import dataBase

from dao.administrador_dao import AdministradorDAO
from dao.libro_dao import LibroDAO
from dao.usuario_dao import UsuarioDAO
from dao.prestamo_dao import PrestamoDAO

from controllers.auth_controller import AuthController
from controllers.libro_controller import LibroController
from controllers.usuarios_controller import UsuarioController
from controllers.prestamos_controller import PrestamoController

from views.auth_view import AuthView
from views.libros_view import LibroView
from views.usuarios_view import UsuarioView
from views.prestamo_view import PrestamoView


def construir_aplicacion(db: dataBase) -> dict:
    """
    Arma todas las dependencias del sistema (inyección manual de
    dependencias) y las retorna listas para usar. Centralizar esto
    aquí evita que cada módulo tenga que saber cómo crear sus
    propias dependencias.
    """
    # DAOs (capa de acceso a datos)
    administrador_dao = AdministradorDAO(db)
    libro_dao = LibroDAO(db)
    usuario_dao = UsuarioDAO(db)
    prestamo_dao = PrestamoDAO(db)

    # Controladores (capa de lógica de negocio)
    auth_controller = AuthController(administrador_dao)
    libro_controller = LibroController(libro_dao)
    usuario_controller = UsuarioController(usuario_dao)
    prestamo_controller = PrestamoController(prestamo_dao, libro_dao, usuario_dao)

    # Vistas (capa de presentación en consola)
    return {
        "auth_view": AuthView(auth_controller),
        "libro_view": LibroView(libro_controller),
        "usuario_view": UsuarioView(usuario_controller),
        "prestamo_view": PrestamoView(prestamo_controller),
    }


def mostrar_menu_principal(app: dict) -> None:
    opciones = {
        "1": app["libro_view"].mostrar_menu,
        "2": app["usuario_view"].mostrar_menu,
        "3": app["prestamo_view"].mostrar_menu,
    }

    while True:
        print("\n===== MENÚ PRINCIPAL =====")
        print("1. Gestión de Libros")
        print("2. Gestión de Usuarios")
        print("3. Gestión de Préstamos")
        print("0. Cerrar sesión y salir")

        opcion = input("Seleccione una opción: ").strip()
        if opcion == "0":
            print("\nCerrando el sistema...")
            return

        accion = opciones.get(opcion)
        if accion is None:
            print("Opción inválida.")
            continue

        accion()


def main() -> None:
    db = dataBase()

    try:
        app = construir_aplicacion(db)

        admin = app["auth_view"].mostrar_login()
        if admin is None:
            print("Acceso denegado. Cerrando el sistema.")
            return

        mostrar_menu_principal(app)

    finally:
        # Se garantiza el cierre de la conexión sin importar cómo
        # termine el programa (salida normal, error no controlado, etc.)
        db.cerrarConexion()


if __name__ == "__main__":
    main()