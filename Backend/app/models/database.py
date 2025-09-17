import psycopg2
import os
from dotenv import load_dotenv

#Cargar variables de entorno
load_dotenv()

def get_db_connection():
    """
    Establece y devuelve conexion al PostGresSQL
    :return:
    """
    return psycopg2.connect(
        host=os.getenv("BD_HOST"),
        port=os.getenv("BD_PORT"),
        database=os.getenv("BD_NAME"),
        user=os.getenv("BD_USER"),
        password=os.getenv("BD_PASSWORD")
    )