# Importar imagen base de python
FROM python:3.12-slim

# Crear en el contenedor la carpeta de trabajo
WORKDIR /app

# Copiar los requerimientos al contenedor
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el codigo del servidor
COPY . .

# Exponer el puerto de trabajo
EXPOSE 5000

# Comando a ejecutar para levantar el servidor (NOTA EL CAMBIO A API.API:app)
CMD ["uvicorn", "API.API:app", "--host", "0.0.0.0", "--port", "5000"]