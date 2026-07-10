import mysql.connector
from mysql.connector.constants import ClientFlag


class dataBase:

    def __init__(self):
        self.conexion = None

    # Metodo connectionDb, inicializa la conexion a la db biblioteca
    def connectionDb(self):
        if self.conexion is None or not self.conexion.is_connected():
            self.conexion = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="biblioteca",
                # Sin esta bandera, cursor.rowcount después de un UPDATE
                # refleja filas CAMBIADAS (no las que coincidieron con el
                # WHERE). Con ella, refleja filas COINCIDENTES, que es lo
                # que los DAOs necesitan para detectar "registro no
                # encontrado" de forma confiable.
                client_flags=[ClientFlag.FOUND_ROWS]
            )
        return self.conexion

    # Metodo cursor, generara el cursor que utilizara el sistema universalmente
    def cursor(self):
        return self.connectionDb().cursor(dictionary=True)

    def cerrarConexion(self):
        if self.conexion is not None and self.conexion.is_connected():
            self.conexion.close()