import mysql.connector

class dataBase:

    # Metodo __init__ de la clase
    def __init__(self):
        self.conexion = None

    # Metodo connectionDb, inicializa la conexion a la db biblioteca
    def conexionDb(self):

        if self.conexion is None or not self.conexion.is_connected():
            self.conexion = mysql.connector.connect(
                host = "localhost",
                user = "root",
                password = "",
                database = "biblioteca"
            )

        return self.conexion

    # Metodo cursor, generara el cursor que utilizara el sistema universalmente
    def cursor(self):

        return self.conexionDb().cursor()

    # Metodo para cerrar conexión de la DB

    def cerrarConexion(self):

        if self.conexion is not None and self.conexion.is_connected():
            self.conexion.close()

