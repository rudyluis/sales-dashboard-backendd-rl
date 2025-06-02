# models/__init__.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    """Inicializa la extensión SQLAlchemy con la aplicación Flask."""
    db.init_app(app)