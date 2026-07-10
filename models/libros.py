"""
Modelo: Libro

Representa un libro en el sistema.
No contiene logica de ningun tipo más que la de formato permitido para las variables.
"""

#Imports

from dataclasses import dataclass, field
from datetime import date

@dataclass
class Libro:
    isbn: str
    titulo: str
    autor: str
    editorial: str
    anio_publicacion: int
    categoria: str
    cantidad_disponible: int = 0
    estado: str = field(default = "Disponible")

# Validaciones básicas de formato

    def __post_init__(self):
        if not self.isbn or not self.isbn.strip():
            raise ValueError("El ISBN no puede estar vacío.")
        
        if not self.titulo or not self.titulo.strip():
            raise ValueError("El Título no puede estar vacío.")
        
        if not self.autor or not self.autor.strip():
            raise ValueError("El Autor no puede estar vacío.")
        
        if self.anio_publicacion > date.today().year:
            raise ValueError("El año de publicación no puede ser futuro.")
        
        if self.cantidad_disponible < 0:
            raise ValueError("La cantidad disponible no puede ser negativa.")
        
        if self.estado not in ("Disponible", "No disponible"):
            raise ValueError(f"Estado invalido '{self.estado}'. Debe ser 'Disponible' o 'No disponible'.")

# Propiedad calculada, evito el uso de booleano que podria olvidarme en actualizar.

    @property
    def tiene_existencias(self) -> bool:
        return self.cantidad_disponible > 0
 
    def __str__(self) -> str:
        return f"[{self.isbn}] {self.titulo} - {self.autor} ({self.cantidad_disponible} disp.)"


if __name__ == "__main__":
    # Test rápido del modelo, sin DB

    libro = Libro(
        isbn="978-3-16-148410-0",
        titulo="Cien Años de Soledad",
        autor="Gabriel García Márquez",
        editorial="Sudamericana",
        anio_publicacion=1967,
        categoria="Novela",
        cantidad_disponible=3,
    )

    print(libro)
    print("Tiene existencias ?", libro.tiene_existencias)