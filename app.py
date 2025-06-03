# app.py
from flask import Flask, jsonify
from flask_cors import CORS
from config import config # Importa el diccionario de configuración
# from models import init_db, db # COMENTA o ELIMINA esta línea por ahora para depuración
from models import db # SOLO importa la instancia 'db' si la necesitas, NO la función init_db aquí
from routes.sales_routes import sales_bp # Importa el Blueprint de rutas de ventas
import os
# from sqlalchemy import text # No es necesario aquí si movemos la verificación de DB

# Asegúrate de que 'db' es una instancia global de SQLAlchemy, pero no inicializada con la app aquí.
# Si models/__init__.py tiene db = SQLAlchemy(), eso está bien.
# La inicialización real (db.init_app) debe hacerse dentro de create_app.

def create_app(config_name=None):
    """
    Función de fábrica para crear y configurar la aplicación Flask.
    Permite usar diferentes configuraciones (desarrollo, producción).
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Asegúrate de que Flask-SQLAlchemy se inicialice *después* de cargar la configuración
    # y *antes* de registrar Blueprints si esos Blueprints usan la instancia 'db'.
    db.init_app(app) # <--- Mueve la inicialización de 'db' aquí si no está ya.

    CORS(app, origins=[
        'http://localhost:5173',
        'http://localhost:8080',
        'https://*.lovable.app',
        'https://*.lovableproject.com',
        os.environ.get('RENDER_FRONTEND_URL') # Añade la URL de Render Frontend aquí si quieres, o maneja en frontend
    ])

    app.register_blueprint(sales_bp)

    # Si planeas usar Flask-Migrate, inicialízalo aquí también:
    # from flask_migrate import Migrate
    # migrate = Migrate(app, db)


    # Elimina cualquier bloque de app_context() o db.create_all() de aquí.
    # Esas operaciones se harán *después* del despliegue exitoso.

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

# Esta línea asegura que la instancia 'app' esté disponible
# cuando Gunicorn importe este módulo para iniciar el servicio.
# No queremos que se ejecute la parte de db.create_all() o db.session.execute() en este punto.
app = create_app()

if __name__ == '__main__':
    # Puedes ejecutar app.run() aquí para desarrollo local.
    # Para db.create_all() local, usarías:
    # with app.app_context():
    #    db.create_all()
    #    print("Tablas creadas localmente.")
    app.run(debug=True, host='0.0.0.0', port=5000)
    