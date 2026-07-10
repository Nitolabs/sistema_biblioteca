"""
Vista: UsuarioView

Responsable únicamente de la interacción por consola para la
gestión de usuarios. No contiene reglas de negocio ni
acceso a datos: solo pide datos con input() y muestra resultados
con print(). Toda la lógica real vive en controllers/usuario_controller.py.
"""

from controllers.usuarios_controller import UsuarioController
from utils.excepciones import UsuarioDuplicadoError, UsuarioNoEncontradoError


class UsuarioView:

    def __init__(self, usuario_controller: UsuarioController):
        self.usuario_controller = usuario_controller

    def mostrar_menu(self) -> None:
        opciones = {
            "1": self._registrar,
            "2": self._modificar,
            "3": self._eliminar,
            "4": self._buscar,
            "5": self._listar,
        }

        while True:
            print("\n--- GESTIÓN DE USUARIOS ---")
            print("1. Crear usuario")
            print("2. Editar usuario")
            print("3. Eliminar usuario")
            print("4. Buscar usuario (por ID o DUI)")
            print("5. Listar usuarios")
            print("0. Volver al menú principal")

            opcion = input("Seleccione una opción: ").strip()
            if opcion == "0":
                return

            accion = opciones.get(opcion)
            if accion is None:
                print("Opción inválida.")
                continue

            try:
                accion()
            except (UsuarioDuplicadoError, UsuarioNoEncontradoError, ValueError) as error:
                print(f"\nError: {error}")

    # Acciones individuales
    def _registrar(self) -> None:
        print("\n-- Crear nuevo usuario --")
        nombre_completo = input("Nombre completo: ").strip()
        dui = input("DUI (00000000-0): ").strip()
        correo = input("Correo electrónico: ").strip()
        telefono = input("Teléfono: ").strip()

        usuario = self.usuario_controller.registrar_usuario(nombre_completo, dui, correo, telefono)
        print(f"\nUsuario registrado exitosamente: {usuario}")

    def _modificar(self) -> None:
        print("\n-- Editar usuario --")
        id_usuario = int(input("ID del usuario a editar: ").strip())
        nombre_completo = input("Nuevo nombre completo: ").strip()
        dui = input("Nuevo DUI: ").strip()
        correo = input("Nuevo correo: ").strip()
        telefono = input("Nuevo teléfono: ").strip()

        usuario = self.usuario_controller.modificar_usuario(
            id_usuario, nombre_completo, dui, correo, telefono
        )
        print(f"\nUsuario actualizado exitosamente: {usuario}")

    def _eliminar(self) -> None:
        print("\n-- Eliminar usuario --")
        id_usuario = int(input("ID del usuario a eliminar: ").strip())
        confirmacion = input(f"¿Confirma eliminar al usuario #{id_usuario}? (s/n): ").strip().lower()
        if confirmacion != "s":
            print("Operación cancelada.")
            return
        self.usuario_controller.eliminar_usuario(id_usuario)
        print("\nUsuario eliminado exitosamente.")

    def _buscar(self) -> None:
        print("\n-- Buscar usuario --")
        print("1. Por ID")
        print("2. Por DUI")
        sub_opcion = input("Seleccione: ").strip()

        if sub_opcion == "1":
            id_usuario = int(input("ID: ").strip())
            usuario = self.usuario_controller.buscar_por_id(id_usuario)
        elif sub_opcion == "2":
            dui = input("DUI: ").strip()
            usuario = self.usuario_controller.buscar_por_dui(dui)
        else:
            print("Opción inválida.")
            return

        print(f"\n{usuario}")

    def _listar(self) -> None:
        usuarios = self.usuario_controller.listar_usuarios()
        if not usuarios:
            print("\nNo hay usuarios registrados.")
            return
        print(f"\nSe encontraron {len(usuarios)} usuario(s):")
        for usuario in usuarios:
            print(f"  {usuario}")