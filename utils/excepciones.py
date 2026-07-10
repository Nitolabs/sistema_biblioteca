"""
Excepciones personalizadas del sistema de biblioteca.

Permiten que los controladores capturen errores de negocio
específicos, en vez de depender de las excepciones genéricas
de mysql.connector.
"""


class ISBNDuplicadoError(Exception):
    """Se lanza al intentar registrar un libro con un ISBN que ya existe."""
    pass


class LibroNoEncontradoError(Exception):
    """Se lanza cuando se busca un libro por ISBN y no existe."""
    pass


class LibroSinExistenciasError(Exception):
    """Se lanza al intentar prestar un libro sin cantidad disponible."""
    pass


class UsuarioDuplicadoError(Exception):
    """Se lanza al intentar registrar un usuario con un DUI ya existente."""
    pass


class UsuarioNoEncontradoError(Exception):
    """Se lanza cuando se busca un usuario por ID/DUI y no existe."""
    pass


class PrestamoMaximoExcedidoError(Exception):
    """Se lanza cuando un usuario ya tiene 3 préstamos activos (RF-04)."""
    pass


class PrestamoDuplicadoError(Exception):
    """Se lanza al intentar prestar el mismo libro dos veces mientras hay un préstamo activo."""
    pass


class CredencialesInvalidasError(Exception):
    """Se lanza cuando el usuario o la contraseña de login son incorrectos."""
    pass


class CuentaBloqueadaError(Exception):
    """Se lanza cuando se intenta iniciar sesión con una cuenta bloqueada (RF-01)."""
    pass