import mysql.connector

class dataBase:

    # Metodo connectionDb, inicializa la conexion a la db biblioteca
    def connectionDb():
        database = mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = "",
            database = "biblioteca"
        )

