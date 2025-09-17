# Dockerfile para el servicio de Faker Populator
FROM python:3.9-slim

#Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# copiar el archivo de requerimiento e instalar las dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copiar el resto del codigo fuente al contenedor
COPY . .

# El comando por defect ejecute el script
CMD ["python","main.py"]