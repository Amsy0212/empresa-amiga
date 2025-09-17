FROM python:3.9

#Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copiar el resto del codigo fuente al contenedor
COPY . .

# El comando por defect ejecute el script
WORKDIR /app
# ...
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

