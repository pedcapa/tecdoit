import mysql.connector
from db_config import db_config  # Importamos las credenciales

def connect_to_db():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except mysql.connector.Error as err:
        print(f"Error: '{err}'")
        return None