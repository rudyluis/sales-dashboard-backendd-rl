# app.py
from flask import Flask, jsonify
from flask_cors import CORS
from config import config # Importa el diccionario de configuración
from models import init_db, db # Importa la función de inicialización de DB y la instancia de DB
from routes.sales_routes import sales_bp # Importa el Blueprint de rutas de ventas
import os
from sqlalchemy import text # Necesario para ejecutar la consulta de prueba de la base de datos

def create_app(config_name=None):
    """
    Función de fábrica para crear y configurar la aplicación Flask.
    Permite usar diferentes configuraciones (desarrollo, producción).
    """
    # Si no se especifica un nombre de configuración, usa la variable de entorno FLASK_CONFIG o 'default'
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')

    app = Flask(__name__) # Inicializa la aplicación Flask
    app.config.from_object(config[config_name]) # Carga la configuración desde config.py

    # Configura CORS para permitir solicitudes desde tu frontend de Node.js
    # Es crucial que 'http://localhost:5173' coincida con la URL de tu frontend
    CORS(app, origins=[
        'http://localhost:5173',
        'http://localhost:8080', # <--- ¡AGREGA ESTA LÍNEA!
        'https://*.lovable.app',
        'https://*.lovableproject.com'
    ])

    # Inicializa la base de datos con la aplicación Flask
    init_db(app)

    # Registra el Blueprint con las rutas de ventas
    app.register_blueprint(sales_bp)

    # Ruta principal de la API que devuelve información general
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Sales Dashboard API con PostgreSQL',
            'version': '1.0.0',
            'database': 'PostgreSQL',
            'endpoints': [
                '/api/health',
                '/api/test/connection', # Puedes usar /api/database/info para info más detallada
                '/api/data/load (POST)',
                '/api/data/all',
                '/api/analytics/summary',
                '/api/database/info'
            ]
        })

    return app

# Punto de entrada principal cuando se ejecuta el script directamente
if __name__ == '__main__':
    app = create_app() # Crea la aplicación con la configuración por defecto
    print("🚀 Iniciando servidor Flask con PostgreSQL...")
    print("📊 Sales Dashboard API")
    print("🐘 Base de datos: PostgreSQL")
    print("🌐 Servidor: http://localhost:5000")
    # Inicia el servidor Flask en modo depuración (útil para desarrollo)
    # host='0.0.0.0' permite que la app sea accesible desde otras máquinas en la red local
    app.run(debug=True, host='0.0.0.0', port=5000)
else:
    # Esta línea asegura que la instancia 'app' esté disponible
    # cuando Gunicorn importe este módulo para iniciar el servicio.
    app = create_app()