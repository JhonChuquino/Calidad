# Imagen base ligera con Python 3.11
FROM python:3.11-slim

# Carpeta de trabajo dentro del contenedor
WORKDIR /app

# Copiar el código
COPY app.py .

# Instalar dependencias necesarias
RUN pip install --no-cache-dir flask pymongo

# Variables de entorno por defecto (pueden ser sobrescritas por docker-compose)
ENV MONGO_URL=mongodb://mongo:27017/pharma_store_db
ENV API_KEY=nube

# Comando de inicio
CMD ["python", "app.py"]
