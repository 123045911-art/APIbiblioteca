#imoprtar imagen base de python
FROM python:3.12-slim

#Crear en el contenedor la capreta de trabajo
WORKDIR /api

#Copiar los requerimientos al contenedor
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

#Instalamos las dependencias de FASTAPI
RUN pip install --no-cache-dir -r requirements.txt

#Copia el codigo del servidor 
COPY ./API .

#Exponer el puerto de trabajo
EXPOSE 5000

#Comndo a ejecutar levantar  servidor
CMD ["uvicorn", "API.main:app", "--host", "0.0.0.0", "--port", "5000","--reload"]