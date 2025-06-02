import os
from dotenv import load_dotenv

load_dotenv() # Carga las variables de entorno del archivo .env

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Una clave secreta para la seguridad de Flask (cambiar en producción)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-2024'

    # Configuración de conexión a PostgreSQL
    # Preferimos leer de variables de entorno (DB_HOST, DB_PORT, etc.)
    # Si no están presentes, usamos valores por defecto (localhost, 5432, etc.)
    DB_HOST = os.environ.get('DB_HOST') or 'localhost'
    DB_PORT = os.environ.get('DB_PORT') or '5432'
    DB_NAME = os.environ.get('DB_NAME') or 'sales_dashboard'
    DB_USER = os.environ.get('DB_USER') or 'postgres' # ¡Asegúrate de que este sea el usuario correcto de tu DB!
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or '69512310Anacleta' # ¡Asegúrate de que esta sea la contraseña correcta!

    # URL completa de conexión a la base de datos para SQLAlchemy
    # Usa DATABASE_URL de entorno si existe, de lo contrario, construye una con los valores anteriores
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

    # Deshabilita el seguimiento de modificaciones de SQLAlchemy (ahorra memoria)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # URL del archivo CSV que cargaremos en la base de datos
    CSV_URL = 'https://raw.githubusercontent.com/rudyluis/DashboardJS/refs/heads/main/superstore_data.csv'

class DevelopmentConfig(Config):
    # En desarrollo, Flask mostrará información de depuración detallada
    DEBUG = True

class ProductionConfig(Config):
    # En producción, DEBUG debe ser False por seguridad y rendimiento
    DEBUG = False
    # En producción, la URL de la base de datos debe venir estrictamente de variables de entorno
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

# Define qué configuración se usará por defecto (development en este caso)
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}