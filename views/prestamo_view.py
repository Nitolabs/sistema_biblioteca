"""
Vista: PrestamoView

Responsable únicamente de la interacción por consola para
préstamos (RF-04) y devoluciones (RF-05). No contiene reglas de
negocio ni acceso a datos: solo pide datos con input() y muestra
resultados con print(). Toda la lógica real vive en
controllers/prestamo_controller.py.
"""

from controllers.prestamos_controller import PrestamoController
from utils.excepciones import (
    LibroNoEncontradoError,
    LibroSinExistenciasError,
    UsuarioNoEncontradoError,
    PrestamoMaximoExcedidoError,
    PrestamoDuplicadoError,
)

ERRORES_NEGOCIO = (
    LibroNoEncontradoError,
    LibroSinExistenciasError,
    UsuarioNoEncontradoError,
    PrestamoMaximoExcedidoError,
    PrestamoDuplicadoError,
    ValueError,
)


class PrestamoView:

    def __init__(self, prestamo_controller: PrestamoController):
        self.prestamo_controller = prestamo_controller

    def mostrar_menu(self) -> None:
        opciones = {
            "1": self._registrar_prestamo,
            "2": self._registrar_devolucion,
            "3": self._listar_activos,
            "4": self._listar_vencidos,
            "5": self._reporte_libros_mas_prestados,
            "6": self._reporte_usuarios_mayor_prestamos,
        }

        while True:
            print("\n--- GESTIÓN DE PRÉSTAMOS ---")
            print("1. Registrar préstamo")
            print("2. Registrar devolución")
            print("3. Listar préstamos activos")
            print("4. Listar préstamos vencidos")
            print("5. Reporte: libros más prestados")
            print("6. Reporte: usuarios con más préstamos")
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
            except ERRORES_NEGOCIO as error:
                print(f"\nError: {error}")


    # Acciones individuales
    def _registrar_prestamo(self) -> None:
        print("\n-- Registrar préstamo --")
        id_usuario = int(input("ID del usuario: ").strip())

        isbns = []
        print("Ingrese los ISBN de los libros a prestar (deje vacío para terminar):")
        while True:
            isbn = input(f"  ISBN #{len(isbns) + 1}: ").strip()
            if not isbn:
                break
            isbns.append(isbn)

        if not isbns:
            print("No se ingresó ningún libro. Operación cancelada.")
            return

        prestamo = self.prestamo_controller.registrar_prestamo(id_usuario, isbns)
        print(f"\nPréstamo registrado exitosamente: {prestamo}")
        print(f"Libros incluidos: {', '.join(isbns)}")

    def _registrar_devolucion(self) -> None:
        print("\n-- Registrar devolución --")
        codigo_prestamo = int(input("Código de préstamo: ").strip())
        isbn = input("ISBN del libro devuelto: ").strip()

        self.prestamo_controller.registrar_devolucion(codigo_prestamo, isbn)
        print("\nDevolución registrada exitosamente.")

    def _listar_activos(self) -> None:
        prestamos = self.prestamo_controller.listar_prestamos_activos()
        self._imprimir_prestamos(prestamos, "No hay préstamos activos.")

    def _listar_vencidos(self) -> None:
        prestamos = self.prestamo_controller.listar_prestamos_vencidos()
        self._imprimir_prestamos(prestamos, "No hay préstamos vencidos.")

    def _reporte_libros_mas_prestados(self) -> None:
        resultados = self.prestamo_controller.libros_mas_prestados()
        if not resultados:
            print("\nAún no hay préstamos registrados.")
            return
        print("\n-- Libros más prestados --")
        for fila in resultados:
            print(f"  {fila['titulo']} (ISBN {fila['isbn']}) - {fila['veces_prestado']} préstamo(s)")

    def _reporte_usuarios_mayor_prestamos(self) -> None:
        resultados = self.prestamo_controller.usuarios_mayor_prestamos()
        if not resultados:
            print("\nAún no hay préstamos registrados.")
            return
        print("\n-- Usuarios con más préstamos --")
        for fila in resultados:
            print(f"  {fila['nombre_completo']} (ID {fila['id_usuario']}) - {fila['total_prestamos']} préstamo(s)")

    # Helpers de presentación
    @staticmethod
    def _imprimir_prestamos(prestamos: list, mensaje_vacio: str) -> None:
        if not prestamos:
            print(f"\n{mensaje_vacio}")
            return
        print(f"\nSe encontraron {len(prestamos)} préstamo(s):")
        for prestamo in prestamos:
            print(f"  {prestamo}")