#Realizamos las importaciones necesarias
from fastapi import FastAPI, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from typing import Optional,Literal
from pydantic import BaseModel,Field,EmailStr

#Instancia del servidor
app= FastAPI(
    title= "Mi API de biblioteca",
    description= "Ali Daniel Flores García",
    version="1.0"
)

#TB ficticia
# BD ficticia de libros
libros = [
    {"id": 1, "nombre": "El Quijote", "estado": "disponible", "anio": 1605, "paginas": 1056},
    {"id": 2, "nombre": "Cien años de soledad", "estado": "prestado", "anio": 1967, "paginas": 417},
    {"id": 3, "nombre": "1984", "estado": "disponible", "anio": 1949, "paginas": 328},
    {"id": 4, "nombre": "Un mundo feliz", "estado": "prestado", "anio": 1932, "paginas": 288},
    {"id": 5, "nombre": "Fahrenheit 451", "estado": "disponible", "anio": 1953, "paginas": 256},
    {"id": 6, "nombre": "El Señor de los Anillos", "estado": "prestado", "anio": 1954, "paginas": 1178},
    {"id": 7, "nombre": "Orgullo y prejuicio", "estado": "disponible", "anio": 1813, "paginas": 432},
    {"id": 8, "nombre": "Harry Potter y la piedra filosofal", "estado": "prestado", "anio": 1997, "paginas": 254},
    {"id": 9, "nombre": "La sombra del viento", "estado": "disponible", "anio": 2001, "paginas": 575},
    {"id": 10, "nombre": "El principito", "estado": "prestado", "anio": 1943, "paginas": 96}
]

usuario=[
    {"id":1,"nombre":"Fany","correo":"fany@example.com"},
    {"id":2,"nombre":"Ali","correo":"ali@example.com"},
    {"id":3,"nombre":"Dulce","correo":"dulce@example.com"},
    {"id":4,"nombre":"Carlos","correo":"carlos@example.com"}
]

prestamos = [
    {"id_prestamo": 1, "id_libro": 2, "id_usuario": 1},
    {"id_prestamo": 2, "id_libro": 4, "id_usuario": 2}
]

#Validamos con ayuda de literal para los estados del libro
estadoLibro=Literal["disponible","prestado"]


#Zona de validaciones
class Usuario(BaseModel):
    id: int = Field(..., gt=0, description="Identificador de usuario")
    nombre: str = Field(..., min_length=3, max_length=50, examples=["Alí"])
    correo: EmailStr = Field(..., description="Correo electrónico válido")

class Libro(BaseModel):
    id: int = Field(..., gt=0, description="Identificador de libro")
    estado: estadoLibro = Field(..., description="Estado del libro, puede ser 'disponible' o 'prestado'")
    nombre: str = Field(..., min_length=2, max_length=100, examples=["El Quijote"])
    anio: int = Field(..., gt=1450, le=2026, description="Mayor a 1450 y menor o igual al año actual.")
    paginas: int = Field(..., gt=1, description="Número de páginas del libro, debe ser mayor a 1")

class NuevoPrestamo(BaseModel):
    idLibro: int = Field(..., gt=0)
    idUsuario: int = Field(..., gt=0, description="Identificador de usuario válido")

#ENDPOINTS DE LIBROS
# Listar libros
@app.get("/v1/libros/", tags=['HTTP CRUD LIBROS'])
async def VerLibros():
    return {"total": len(libros), "libros": libros, "status": "200"}

#Listar libros disponibles
@app.get("/v1/libros/disponibles", tags=['HTTP CRUD LIBROS'])
async def VerLibrosDisponibles():
    librosDisponibles = [lb for lb in libros if lb["estado"] == "disponible"]
    return {"total": len(librosDisponibles), "libros": librosDisponibles, "status": "200"}

#Buscar libro por nombre
@app.get("/v1/libros/buscar", tags=['HTTP CRUD LIBROS'])
async def BuscarLibro(nombre: str):
    if not nombre or len(nombre.strip()) < 2:
        raise HTTPException(status_code=400, detail="El nombre del libro no es válido")  
    librosEncontrados = [lb for lb in libros if nombre.lower() in lb["nombre"].lower()]
    if not librosEncontrados:
        raise HTTPException(status_code=404, detail="No se encontraron libros con ese nombre")
        
    return {"libros": librosEncontrados, "status": "200"}

#Registrar un libro
@app.post("/v1/libros/", tags=['HTTP CRUD LIBROS'], status_code=201)
async def AgregarLibro(nuevoLibro: Libro):
    if not nuevoLibro.nombre or len(nuevoLibro.nombre.strip()) < 2:
        raise HTTPException(status_code=400, detail="El nombre del libro no es válido o faltan datos")

    for lb in libros:
        if lb["id"] == nuevoLibro.id:
            raise HTTPException(status_code=400, detail="El libro con este ID ya existe")
            
    libros.append(nuevoLibro.model_dump()) # Usamos model_dump() en Pydantic v2
    return {
        "mensaje": "Libro registrado exitosamente",
        "libro": nuevoLibro,
        "status": "201"
    }

#ENDOPOINTS DE USUARIOS
@app.get("/v1/usuarios/",tags=['HTTP CRUD USUARIOS'])
async def VerUsuarios():
    return {
        "total":len(usuario),
        "usuarios":usuario,
        "status":"200"
    }

@app.post("/v1/usuarios/",tags=['HTTP CRUD USUARIOS'])
async def AgregarUsuario(nuevoUsuario:Usuario):
    for usr in usuario:
        if usr["id"] == nuevoUsuario.id:
            raise HTTPException(
                status_code=400,
                detail="El usuario con este ID ya existe"
            )
    usuario.append(nuevoUsuario.model_dump())
    return {
        "mensaje":"Usuario agregado exitosamente",
        "usuario":nuevoUsuario,
        "status":"201"
    }

#ENDPOINTS DE PRÉSTAMOS
#Registrar el préstamo de un libro a un usuario
@app.post("/v1/prestamos/", tags=['HTTP CRUD PRÉSTAMOS'], status_code=201)
async def RegistrarPrestamo(datosPrestamo: NuevoPrestamo):
    #Verificamos si el libro existe
    libroEncontrado = next((lb for lb in libros if lb["id"] == datosPrestamo.idLibro), None)
    if not libroEncontrado:
        raise HTTPException(status_code=400, detail="El libro no existe")
    
    #Verificamos si el usuario existe
    usuarioEncontrado = next((usr for usr in usuario if usr["id"] == datosPrestamo.idUsuario), None)
    if not usuarioEncontrado:
        raise HTTPException(status_code=400, detail="El usuario no existe")

    #409 Conflict si el libro ya está prestado
    if libroEncontrado["estado"] == "prestado":
        raise HTTPException(status_code=409, detail="El libro ya se encuentra prestado")

    #Realizamos el préstamo
    nuevoIdPrestamo = max([p["idPrestamo"] for p in prestamos], default=0) + 1
    prestamos.append({
        "idPrestamo": nuevoIdPrestamo,
        "idLibro": datosPrestamo.idLibro,
        "idUsuario": datosPrestamo.idUsuario
    })
    
    #Actualizamos el estado del libro
    libroEncontrado["estado"] = "prestado"
    
    return {"mensaje": "Préstamo registrado exitosamente", "idPrestamo": nuevoIdPrestamo, "status": "201"}

#Marcamos un libro como devuelto
@app.put("/v1/prestamos/devolver/{id_prestamo}", tags=['HTTP CRUD PRÉSTAMOS'], status_code=200)
async def DevolverLibro(idPrestamo: int):
    prestamoEncontrado = next((p for p in prestamos if p["idPrestamo"] == idPrestamo), None)
    
    #conflict 409 si el registro de préstamo ya no existe
    if not prestamoEncontrado:
        raise HTTPException(status_code=409, detail="El registro de préstamo ya no existe")
        
    #Actualizamos el estado del libro a disponible
    for lb in libros:
        if lb["id"] == prestamoEncontrado["idLibro"]:
            lb["estado"] = "disponible"
            break

    return {"mensaje": "El libro ha sido devuelto satisfactoriamente", "status": "200"}

#Eliminar el registro de un préstamo
@app.delete("/v1/prestamos/{id_prestamo}", tags=['HTTP CRUD PRÉSTAMOS'])
async def EliminarRegistroPrestamo(idPrestamo: int):
    prestamoEncontrado = next((p for p in prestamos if p["idPrestamo"] == idPrestamo), None)
    
    #409 Conflict si el registro de préstamo ya no existe
    if not prestamoEncontrado:
        raise HTTPException(status_code=409, detail="El registro de préstamo ya no existe")
        
    prestamos.remove(prestamoEncontrado)
    
    return {"mensaje": "Registro de préstamo eliminado", "status": "200"}