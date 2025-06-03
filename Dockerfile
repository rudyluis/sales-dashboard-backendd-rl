# sales-dashboard-backendd/Dockerfile
# Usa una imagen base de Python. Elegimos la 3.9 slim-buster por ser ligera.
FROM python:3.9-slim-buster

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo requirements.txt al directorio de trabajo del contenedor
COPY requirements.txt .

# Instala las dependencias de Python listadas en requirements.txt
# --no-cache-dir: no guarda caché de pip para reducir el tamaño de la imagen
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el resto del código del directorio actual (el backend) al contenedor
COPY . .

# Expone el puerto 5000, que es donde Flask escuchará.
# Render.com inyectará su propia variable $PORT, pero esta es una buena práctica.
EXPOSE 5000

# Comando para iniciar la aplicación Flask usando Gunicorn (un servidor WSGI).
# Gunicorn ejecutará la aplicación 'app' dentro del módulo 'app'.
# -w 4: 4 workers (procesos)
# -b 0.0.0.0:5000: escucha en todas las interfaces en el puerto 5000
# En Render, usarás "gunicorn -w 4 -b 0.0.0.0:$PORT app:app" como Start Command directamente,
# pero mantenerlo aquí es útil para pruebas locales con Docker.
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
