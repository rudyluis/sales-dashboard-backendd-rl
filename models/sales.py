# models/sales.py
from . import db # Importa 'db' desde models/__init__.py
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID # Importar el tipo de dato UUID específico de PostgreSQL
import uuid # Para generar UUIDs únicos

class Sales(db.Model):
    __tablename__ = 'sales' # Nombre de la tabla en la base de datos

    # Usar UUID como primary key (mejor práctica para PostgreSQL)
    # uuid.uuid4 genera un UUID aleatorio por defecto
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    no = db.Column(db.Integer)
    row_id = db.Column(db.Integer, unique=True)  # Se añade un índice único para RowID
    order_id = db.Column(db.String(20), nullable=False, index=True) # order_id no puede ser nulo y tendrá un índice
    order_date = db.Column(db.Date, index=True)  # Fechas con índice para búsquedas por fecha
    ship_date = db.Column(db.Date)
    ship_mode = db.Column(db.String(50))
    customer_id = db.Column(db.String(20), index=True) # Índice para customer_id
    customer_name = db.Column(db.String(100))
    segment = db.Column(db.String(50), index=True) # Índice para segment
    country = db.Column(db.String(50))
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    postal_code = db.Column(db.String(20))
    region = db.Column(db.String(50), index=True) # Índice para region
    product_id = db.Column(db.String(50), index=True) # Índice para product_id
    category = db.Column(db.String(50), index=True) # Índice para category
    sub_category = db.Column(db.String(50))
    product_name = db.Column(db.Text)  # Usar Text para nombres largos
    sales = db.Column(db.Numeric(10, 2))  # Usar Numeric para precisión decimal (10 dígitos en total, 2 después del punto)
    quantity = db.Column(db.Integer)
    discount = db.Column(db.Numeric(5, 4))  # Precisión para descuentos (5 dígitos en total, 4 después del punto)
    profit = db.Column(db.Numeric(10, 2))  # Usar Numeric para precisión decimal
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True) # Marca de tiempo de creación
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) # Marca de tiempo de actualización

    def to_dict(self):
        """Convierte el objeto Sales a un diccionario para respuestas JSON."""
        return {
            'No': self.no,
            'RowID': self.row_id,
            'OrderID': self.order_id,
            'OrderDate': self.order_date.strftime('%m/%d/%Y') if self.order_date else None,
            'ShipDate': self.ship_date.strftime('%m/%d/%Y') if self.ship_date else None,
            'ShipMode': self.ship_mode,
            'CustomerID': self.customer_id,
            'CustomerName': self.customer_name,
            'Segment': self.segment,
            'Country': self.country,
            'City': self.city,
            'State': self.state,
            'PostalCode': self.postal_code,
            'Region': self.region,
            'ProductID': self.product_id,
            'Category': self.category,
            'SubCategory': self.sub_category,
            'ProductName': self.product_name,
            'Sales': float(self.sales) if self.sales else 0, # Convertir a float para JSON
            'Quantity': self.quantity,
            'Discount': float(self.discount) if self.discount else 0, # Convertir a float para JSON
            'Profit': float(self.profit) if self.profit else 0 # Convertir a float para JSON
        }

    def __repr__(self):
        """Representación amigable del objeto Sales."""
        return f'<Sales {self.order_id}>'