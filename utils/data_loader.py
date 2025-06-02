# utils/data_loader.py
import requests
import pandas as pd
import io
from datetime import datetime
from models.sales import Sales # Importa el modelo Sales que acabas de crear
from models import db # Importa la instancia de SQLAlchemy desde models/__init__.py
from decimal import Decimal # Para manejar números con precisión decimal
from sqlalchemy import text # Para ejecutar comandos SQL planos

class DataLoader:
    def __init__(self, csv_url):
        self.csv_url = csv_url

    def load_csv_to_database(self):
        """
        Descarga un archivo CSV desde una URL y carga sus datos en la tabla 'sales'
        de PostgreSQL. Limpia la tabla antes de cargar nuevos datos y los inserta en lotes.
        """
        try:
            print("🔄 Descargando datos del CSV...")
            # Realiza una solicitud HTTP para obtener el contenido del CSV
            response = requests.get(self.csv_url)
            response.raise_for_status() # Lanza un error si la solicitud no fue exitosa

            # Lee el CSV directamente desde el contenido de la respuesta usando pandas
            csv_data = io.StringIO(response.text)
            df = pd.read_csv(csv_data)

            print(f"📊 CSV cargado en memoria con {len(df)} registros")

            # Limpiar datos existentes en la tabla 'sales'
            # Usamos TRUNCATE para PostgreSQL, que es más eficiente que DELETE ALL y reinicia los IDs.
            try:
                # 'CASCADE' es importante si hay otras tablas que dependen de 'sales'
                db.session.execute(text('TRUNCATE TABLE sales RESTART IDENTITY CASCADE'))
                db.session.commit()
                print("🗑️ Datos existentes eliminados de la tabla 'sales'")
            except Exception as e:
                # Este error puede ocurrir la primera vez si la tabla está vacía o no existe aún
                print(f"⚠️ Error limpiando tabla (puede ser normal si la tabla está vacía): {e}")
                db.session.rollback() # Deshace cualquier cambio si hubo un error

            # Insertar nuevos datos en lotes para mejorar el rendimiento
            records_inserted = 0
            batch_size = 500  # Número de registros a insertar en cada lote
            batch_records = []

            print("📦 Preparando datos para la inserción...")
            for index, row in df.iterrows():
                try:
                    # Convertir fechas de string a objetos date de Python
                    order_date = None
                    ship_date = None

                    if pd.notna(row['OrderDate']):
                        order_date = datetime.strptime(str(row['OrderDate']), '%m/%d/%Y').date()

                    if pd.notna(row['ShipDate']):
                        ship_date = datetime.strptime(str(row['ShipDate']), '%m/%d/%Y').date()

                    # Crear una instancia del modelo Sales con los datos de la fila actual
                    sales_record = Sales(
                        no=int(row['No']) if pd.notna(row['No']) else None,
                        row_id=int(row['RowID']) if pd.notna(row['RowID']) else None,
                        order_id=str(row['OrderID']) if pd.notna(row['OrderID']) else '',
                        order_date=order_date,
                        ship_date=ship_date,
                        ship_mode=str(row['ShipMode']) if pd.notna(row['ShipMode']) else '',
                        customer_id=str(row['CustomerID']) if pd.notna(row['CustomerID']) else '',
                        customer_name=str(row['CustomerName']) if pd.notna(row['CustomerName']) else '',
                        segment=str(row['Segment']) if pd.notna(row['Segment']) else '',
                        country=str(row['Country']) if pd.notna(row['Country']) else '',
                        city=str(row['City']) if pd.notna(row['City']) else '',
                        state=str(row['State']) if pd.notna(row['State']) else '',
                        postal_code=str(row['Postal Code']) if pd.notna(row['Postal Code']) else '', # ¡Cuidado con el espacio en "Postal Code"!
                        region=str(row['Region']) if pd.notna(row['Region']) else '',
                        product_id=str(row['ProductID']) if pd.notna(row['ProductID']) else '',
                        category=str(row['Category']) if pd.notna(row['Category']) else '',
                        sub_category=str(row['Sub-Category']) if pd.notna(row['Sub-Category']) else '', # ¡Cuidado con el guion en "Sub-Category"!
                        product_name=str(row['ProductName']) if pd.notna(row['ProductName']) else '',
                        # Convertir a Decimal para los tipos Numeric de la DB
                        sales=Decimal(str(row['Sales'])) if pd.notna(row['Sales']) else Decimal('0'),
                        quantity=int(row['Quantity']) if pd.notna(row['Quantity']) else 0,
                        discount=Decimal(str(row['Discount'])) if pd.notna(row['Discount']) else Decimal('0'),
                        profit=Decimal(str(row['Profit'])) if pd.notna(row['Profit']) else Decimal('0')
                    )

                    batch_records.append(sales_record)
                    records_inserted += 1

                    # Si el lote alcanza el tamaño definido, inserta los registros y reinicia el lote
                    if len(batch_records) >= batch_size:
                        db.session.bulk_save_objects(batch_records) # Inserción masiva
                        db.session.commit() # Confirma la transacción
                        print(f"💾 Insertados {records_inserted} registros...")
                        batch_records = [] # Limpia el lote

                except Exception as e:
                    # Si hay un error en un registro, lo salta e imprime un mensaje
                    print(f"❌ Error procesando registro en la fila {index}: {e}. Saltando registro.")
                    continue # Continúa con el siguiente registro

            # Inserta cualquier registro restante en el último lote
            if batch_records:
                db.session.bulk_save_objects(batch_records)
                db.session.commit()
                print(f"💾 Insertados los últimos {len(batch_records)} registros.")

            print(f"✅ Carga completada: {records_inserted} registros insertados en PostgreSQL")

            # Actualiza las estadísticas de la tabla en PostgreSQL (importante para el optimizador de consultas)
            db.session.execute(text('ANALYZE sales'))
            db.session.commit()
            print("✨ Estadísticas de la tabla 'sales' actualizadas.")

            return True, records_inserted # Retorna éxito y el número de registros

        except requests.exceptions.RequestException as e:
            db.session.rollback() # Deshace cualquier cambio si hubo un error de red
            print(f"❌ Error al descargar el CSV: {e}. Verifica la URL y tu conexión a internet.")
            return False, 0
        except pd.errors.EmptyDataError:
            db.session.rollback()
            print("❌ Error: El archivo CSV está vacío o no tiene el formato esperado.")
            return False, 0
        except Exception as e:
            db.session.rollback() # Deshace cualquier cambio si hubo un error general
            print(f"❌ Error inesperado durante la carga de datos: {e}")
            return False, 0