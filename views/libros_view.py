"""
Vista: LibroView

Responsable únicamente de la interacción por consola para la
gestión de libros. No contiene reglas de negocio ni
acceso a datos: solo pide datos con input() y muestra resultados
con print(). Toda la lógica real vive en controllers/libro_controller.py.
"""

from controllers.libro_controller import LibroController
from utils.excepciones import ISBNDuplicadoError, LibroNoEncontradoError


class LibroView:

    def __init__(self, libro_controller: LibroController):
        self.libro_controller = libro_controller

    def mostrar_menu(self) -> None:
        opciones = {
            "1": self._registrar,
            "2": self._modificar,
            "3": self._eliminar,
            "4": self._consultar,
            "5": self._buscar,
            "6": self._listar_todos,
            "7": self._listar_disponibles,
            "8": self._listar_sin_existencias,
        }

        while True:
            print("\n--- GESTIÓN DE LIBROS ---")
            print("1. Registrar libro")
            print("2. Modificar libro")
            print("3. Eliminar libro")
            print("4. Consultar libro por ISBN")
            print("5. Buscar libros (título/autor/categoría)")
            print("6. Listar todos los libros")
            print("7. Listar libros disponibles")
            print("8. Listar libros sin existencias")
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
            except (ISBNDuplicadoError, LibroNoEncontradoError, ValueError) as error:
                print(f"\nError: {error}")

    # Acciones individuales
    def _registrar(self) -> None:
        print("\n-- Registrar nuevo libro --")
        isbn = input("ISBN: ").strip()
        titulo = input("Título: ").strip()
        autor = input("Autor: ").strip()
        editorial = input("Editorial: ").strip()
        anio_publicacion = int(input("Año de publicación: ").strip())
        categoria = input("Categoría: ").strip()
        cantidad_disponible = int(input("Cantidad disponible: ").strip())

        libro = self.libro_controller.registrar_libro(
            isbn, titulo, autor, editorial, anio_publicacion, categoria, cantidad_disponible
        )
        print(f"\nLibro registrado exitosamente: {libro}")

    def _modificar(self) -> None:
        print("\n-- Modificar libro --")
        isbn = input("ISBN del libro a modificar: ").strip()
        titulo = input("Nuevo título: ").strip()
        autor = input("Nuevo autor: ").strip()
        editorial = input("Nueva editorial: ").strip()
        anio_publicacion = int(input("Nuevo año de publicación: ").strip())
        categoria = input("Nueva categoría: ").strip()
        cantidad_disponible = int(input("Nueva cantidad disponible: ").strip())

        libro = self.libro_controller.modificar_libro(
            isbn, titulo, autor, editorial, anio_publicacion, categoria, cantidad_disponible
        )
        print(f"\nLibro actualizado exitosamente: {libro}")

    def _eliminar(self) -> None:
        print("\n-- Eliminar libro --")
        isbn = input("ISBN del libro a eliminar: ").strip()
        confirmacion = input(f"¿Confirma eliminar el libro '{isbn}'? (s/n): ").strip().lower()
        if confirmacion != "s":
            print("Operación cancelada.")
            return
        self.libro_controller.eliminar_libro(isbn)
        print("\nLibro eliminado exitosamente.")

    def _consultar(self) -> None:
        print("\n-- Consultar libro --")
        isbn = input("ISBN: ").strip()
        libro = self.libro_controller.consultar_libro(isbn)
        self._imprimir_libro(libro)

    def _buscar(self) -> None:
        print("\n-- Buscar libros --")
        print("Criterios disponibles: titulo, autor, categoria")
        criterio = input("Criterio de búsqueda: ").strip()
        texto = input("Texto a buscar: ").strip()

        resultados = self.libro_controller.buscar_libros(criterio, texto)
        self._imprimir_lista(resultados, "No se encontraron libros con ese criterio.")

    def _listar_todos(self) -> None:
        libros = self.libro_controller.listar_todos()
        self._imprimir_lista(libros, "No hay libros registrados.")

    def _listar_disponibles(self) -> None:
        libros = self.libro_controller.listar_disponibles()
        self._imprimir_lista(libros, "No hay libros disponibles.")

    def _listar_sin_existencias(self) -> None:
        libros = self.libro_controller.listar_sin_existencias()
        self._imprimir_lista(libros, "No hay libros sin existencias.")

    # Helpers de presentación
    @staticmethod
    def _imprimir_libro(libro) -> None:
        print(f"\n{libro}")

    @staticmethod
    def _imprimir_lista(libros: list, mensaje_vacio: str) -> None:
        if not libros:
            print(f"\n{mensaje_vacio}")
            return
        print(f"\nSe encontraron {len(libros)} libro(s):")
        for libro in libros:
            print(f"  {libro}")