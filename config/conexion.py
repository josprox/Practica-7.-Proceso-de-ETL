import os
import pyodbc
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

SERVIDOR = os.getenv('DB_HOST')
USUARIO = os.getenv('DB_USER')
CONTRASENA = os.getenv('DB_PASSWORD')
BASE_DATOS_DEFAULT = os.getenv('DB_NAME')
DRIVER = os.getenv('DB_DRIVER')

CADENA_CONEXION_MASTER = (
    f'DRIVER={{{DRIVER}}};'
    f'SERVER={SERVIDOR};'
    'DATABASE=master;'
    f'UID={USUARIO};'
    f'PWD={CONTRASENA};'
    'Encrypt=no;'
    'TrustServerCertificate=yes;'
)

CADENA_CONEXION_ETL = (
    f'DRIVER={{{DRIVER}}};'
    f'SERVER={SERVIDOR};'
    f'DATABASE={BASE_DATOS_DEFAULT};'
    f'UID={USUARIO};'
    f'PWD={CONTRASENA};'
    'Encrypt=no;'
    'TrustServerCertificate=yes;'
)

def obtener_conexion(base_datos=BASE_DATOS_DEFAULT):
    """
    Retorna una conexión activa a SQL Server utilizando las credenciales del archivo .env.
    """
    cadena = CADENA_CONEXION_ETL if base_datos == BASE_DATOS_DEFAULT else CADENA_CONEXION_MASTER
    return pyodbc.connect(cadena, autocommit=True)
