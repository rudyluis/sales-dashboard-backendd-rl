# routes/sales_routes.py

from flask import Blueprint, jsonify, request
from models import db # Importa la instancia de SQLAlchemy
from models.sales import Sales # Importa el modelo Sales
from utils.data_loader import DataLoader
from config import Config
from sqlalchemy import text, func, distinct # Asegúrate de importar func y distinct

# Crea un Blueprint para las rutas de ventas
sales_bp = Blueprint('sales_bp', __name__)

@sales_bp.route('/api/health', methods=['GET'])
def health_check():
    """
    Endpoint simple para verificar si la API está funcionando.
    """
    return jsonify({
        'status': 'ok',
        'message': 'API is healthy and running!'
    }), 200

@sales_bp.route('/api/data/load', methods=['POST'])
def load_data():
    """
    Endpoint para cargar datos desde el CSV remoto a la base de datos PostgreSQL.
    Se usa un método POST para indicar una acción que modifica el estado del servidor.
    """
    data_loader = DataLoader(Config.CSV_URL)
    success, records_inserted = data_loader.load_csv_to_database()

    if success:
        return jsonify({
            'status': 'success',
            'message': f'Datos cargados exitosamente. {records_inserted} registros insertados.',
            'records_inserted': records_inserted
        }), 200
    else:
        return jsonify({
            'status': 'error',
            'message': 'Error al cargar los datos en la base de datos. Consulta los logs del servidor.'
        }), 500

@sales_bp.route('/api/data/all', methods=['GET'])
def get_all_sales_data():
    """
    Endpoint para obtener todos los registros de ventas desde la base de datos.
    """
    try:
        all_sales = Sales.query.all()
        sales_list = [sale.to_dict() for sale in all_sales]

        return jsonify({
            'status': 'success',
            'count': len(sales_list),
            'data': sales_list
        }), 200
    except Exception as e:
        print(f"Error al obtener todos los datos de ventas: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error al obtener los datos de ventas: {str(e)}'
        }), 500

@sales_bp.route('/api/analytics/summary', methods=['GET'])
def get_sales_summary():
    """
    Endpoint para obtener un resumen de ventas (ej. total de ventas, total de ganancias).
    """
    try:
        total_sales = db.session.query(func.sum(Sales.sales)).scalar()
        total_profit = db.session.query(func.sum(Sales.profit)).scalar()
        total_quantity = db.session.query(func.sum(Sales.quantity)).scalar()
        total_orders = db.session.query(func.count(distinct(Sales.order_id))).scalar()
        total_customers = db.session.query(func.count(distinct(Sales.customer_id))).scalar()

        return jsonify({
            'status': 'success',
            'summary': {
                'total_sales': float(total_sales) if total_sales is not None else 0.0,
                'total_profit': float(total_profit) if total_profit is not None else 0.0,
                'total_quantity_sold': int(total_quantity) if total_quantity is not None else 0,
                'total_unique_orders': int(total_orders) if total_orders is not None else 0,
                'total_unique_customers': int(total_customers) if total_customers is not None else 0,
            }
        }), 200
    except Exception as e:
        print(f"Error al generar el resumen de ventas: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error al generar el resumen de ventas: {str(e)}'
        }), 500

@sales_bp.route('/api/analytics/categories', methods=['GET'])
def get_sales_by_category():
    """
    Endpoint para obtener las ventas, ganancias y cantidad vendida por categoría de producto.
    """
    try:
        # Usando 'Sales.category' que es el nombre de la columna en tu modelo Sales
        category_sales = db.session.query(
            Sales.category, # ¡CORREGIDO!
            func.sum(Sales.sales).label('total_sales'),
            func.sum(Sales.profit).label('total_profit'),
            func.sum(Sales.quantity).label('total_quantity_sold')
        ).group_by(Sales.category) \
        .order_by(func.sum(Sales.sales).desc()) \
        .all()

        results = []
        for category_row in category_sales:
            results.append({
                "category": category_row.category, # ¡CORREGIDO!
                "total_sales": float(category_row.total_sales) if category_row.total_sales is not None else 0.0,
                "total_profit": float(category_row.total_profit) if category_row.total_profit is not None else 0.0,
                "total_quantity_sold": int(category_row.total_quantity_sold) if category_row.total_quantity_sold is not None else 0
            })

        return jsonify({
            "status": "success",
            "categories": results
        }), 200

    except Exception as e:
        print(f"Error al obtener ventas por categoría: {e}")
        return jsonify({
            "status": "error",
            "message": "Error interno del servidor al obtener ventas por categoría."
        }), 500

@sales_bp.route('/api/analytics/regions', methods=['GET'])
def get_regional_performance():
    """
    Endpoint para obtener el rendimiento (ventas y ganancias) por región.
    """
    try:
        # Usando 'Sales.region' que es el nombre de la columna en tu modelo Sales
        regional_performance = db.session.query(
            Sales.region, # ¡CORREGIDO!
            func.sum(Sales.sales).label('total_sales'),
            func.sum(Sales.profit).label('total_profit')
        ).group_by(Sales.region) \
        .order_by(func.sum(Sales.sales).desc()) \
        .all()

        results = []
        for region_row in regional_performance: # Renombrado para claridad
            results.append({
                "region": region_row.region, # ¡CORREGIDO!
                "total_sales": float(region_row.total_sales) if region_row.total_sales is not None else 0.0,
                "total_profit": float(region_row.total_profit) if region_row.total_profit is not None else 0.0
            })

        return jsonify({
            "status": "success",
            "regions": results
        }), 200

    except Exception as e:
        print(f"Error al obtener rendimiento regional: {e}")
        return jsonify({
            "status": "error",
            "message": "Error interno del servidor al obtener rendimiento regional."
        }), 500

@sales_bp.route('/api/analytics/customers', methods=['GET'])
def get_top_customers():
    """
    Endpoint para obtener los principales clientes por total gastado, con un límite opcional.
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        
        # Usando 'Sales.customer_id' y 'Sales.customer_name' de tu modelo Sales
        top_customers = db.session.query(
            Sales.customer_id,
            Sales.customer_name, # Incluido según tu modelo
            func.sum(Sales.sales).label('total_spent'),
            func.count(distinct(Sales.order_id)).label('total_orders')
        ).group_by(Sales.customer_id, Sales.customer_name) \
        .order_by(func.sum(Sales.sales).desc()) \
        .limit(limit) \
        .all()

        results = []
        for customer_row in top_customers: # Renombrado para claridad
            results.append({
                "customer_id": customer_row.customer_id,
                "customer_name": customer_row.customer_name, # Incluido
                "total_spent": float(customer_row.total_spent) if customer_row.total_spent is not None else 0.0,
                "total_orders": int(customer_row.total_orders) if customer_row.total_orders is not None else 0
            })

        return jsonify({
            "status": "success",
            "customers": results
        }), 200

    except Exception as e:
        print(f"Error al obtener top clientes: {e}")
        return jsonify({
            "status": "error",
            "message": "Error interno del servidor al obtener top clientes."
        }), 500

@sales_bp.route('/api/analytics/products', methods=['GET'])
def get_top_products():
    """
    Endpoint para obtener los principales productos por ventas, con un límite opcional.
    """
    try:
        limit = request.args.get('limit', 10, type=int)

        # Usando 'Sales.product_id' y 'Sales.product_name' de tu modelo Sales
        top_products = db.session.query(
            Sales.product_id,
            Sales.product_name, # Incluido según tu modelo
            func.sum(Sales.sales).label('total_sales'),
            func.sum(Sales.quantity).label('total_quantity_sold')
        ).group_by(Sales.product_id, Sales.product_name) \
        .order_by(func.sum(Sales.sales).desc()) \
        .limit(limit) \
        .all()

        results = []
        for product_row in top_products: # Renombrado para claridad
            results.append({
                "product_id": product_row.product_id,
                "product_name": product_row.product_name, # Incluido
                "total_sales": float(product_row.total_sales) if product_row.total_sales is not None else 0.0,
                "total_quantity_sold": int(product_row.total_quantity_sold) if product_row.total_quantity_sold is not None else 0
            })

        return jsonify({
            "status": "success",
            "products": results
        }), 200

    except Exception as e:
        print(f"Error al obtener top productos: {e}")
        return jsonify({
            "status": "error",
            "message": "Error interno del servidor al obtener top productos."
        }), 500

@sales_bp.route('/api/database/info', methods=['GET'])
def get_database_info():
    """
    Endpoint para obtener información de la base de datos PostgreSQL.
    Muestra la versión de PostgreSQL, el conteo de registros y el tamaño de la tabla.
    """
    try:
        record_count = Sales.query.count()
        db_version = db.session.execute(text("SELECT version()")).scalar()
        table_size = db.session.execute(text(
            "SELECT pg_size_pretty(pg_total_relation_size('sales'))"
        )).scalar()

        # Usando 'created_at' y 'updated_at' de tu modelo Sales
        # Asegúrate de que tu tabla 'sales' tenga estas columnas o ajústalo.
        recent_activity_count = db.session.execute(text(
            "SELECT COUNT(*) FROM sales WHERE created_at >= NOW() - INTERVAL '1 hour' OR updated_at >= NOW() - INTERVAL '1 hour'"
        )).scalar()
        if recent_activity_count is None: # Manejar caso donde el conteo es None
            recent_activity_count = 0

        return jsonify({
            'status': 'success',
            'database_type': 'PostgreSQL',
            'version': db_version,
            'total_records_in_sales_table': record_count,
            'sales_table_size': table_size,
            'recent_activity_last_hour': recent_activity_count,
            'connection_status': 'active'
        }), 200
    except Exception as e:
        print(f"Error al obtener información de la base de datos: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error al obtener información de la base de datos: {str(e)}. Verifica la conexión a PostgreSQL.',
            'connection_status': 'failed'
        }), 500