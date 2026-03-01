# Realizamos las importaciones necesarias
from fastapi import FastAPI, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from typing import Optional, Literal
from pydantic import BaseModel, Field, EmailStr

# Instancia del servidor
app = FastAPI(
    title="Mi API de biblioteca",
    description="Ali Daniel Flores García",
    version="1.0"
)

# BD ficticia de libros
libros = [
    {"id": 1, "nombre": "El Quijote", "estado": "prestado", "anio": 1605, "paginas": 1056},
    {"id": 2, "nombre": "Cien años de soledad", "estado": "prestado", "anio": 1967, "paginas": 417},
    {"id": 3, "nombre": "1984", "estado": "prestado", "anio": 1949, "paginas": 328},
    {"id": 4, "nombre": "Un mundo feliz", "estado": "prestado", "anio": 1932, "paginas": 288},
    {"id": 5, "nombre": "Fahrenheit 451", "estado": "prestado", "anio": 1953, "paginas": 256},
    {"id": 6, "nombre": "El Señor de los Anillos", "estado": "disponible", "anio": 1954, "paginas": 1178},
    {"id": 7, "nombre": "Orgullo y prejuicio", "estado": "disponible", "anio": 1813, "paginas": 432},
    {"id": 8, "nombre": "Harry Potter y la piedra filosofal", "estado": "disponible", "anio": 1997, "paginas": 254},
    {"id": 9, "nombre": "La sombra del viento", "estado": "disponible", "anio": 2001, "paginas": 575},
    {"id": 10, "nombre": "El principito", "estado": "disponible", "anio": 1943, "paginas": 96}
]

# BD ficticia de usuarios
usuario = [
    {"id": 1, "nombre": "Fany", "correo": "fany@example.com"},
    {"id": 2, "nombre": "Ali", "correo": "ali@example.com"},
    {"id": 3, "nombre": "Dulce", "correo": "dulce@example.com"},
    {"id": 4, "nombre": "Carlos", "correo": "carlos@example.com"}
]

# BD ficticia de préstamos
prestamos = [
    {"idPrestamo": 1, "idLibro": 1, "idUsuario": 1},
    {"idPrestamo": 2, "idLibro": 2, "idUsuario": 2},
    {"idPrestamo": 3, "idLibro": 3, "idUsuario": 2},
    {"idPrestamo": 4, "idLibro": 4, "idUsuario": 3},
    {"idPrestamo": 5, "idLibro": 5, "idUsuario": 4}
]

# Limitamos las opciones de estado para que no escriban otra cosa
estadoLibro = Literal["disponible", "prestado"]


# Zona de modelos (Plantillas para recibir datos)
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

class LibroUpdate(BaseModel):
    estado: Optional[estadoLibro] = Field(None, description="Estado del libro")
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    anio: Optional[int] = Field(None, gt=1450, le=2026)
    paginas: Optional[int] = Field(None, gt=1)

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=3, max_length=50)
    correo: Optional[EmailStr] = None

class PrestamoUpdate(BaseModel):
    idLibro: Optional[int] = Field(None, gt=0)
    idUsuario: Optional[int] = Field(None, gt=0)


# ------------------- ENDPOINTS DE LIBROS ------------------------

# Mostrar todos los libros
@app.get("/v1/libros/", tags=['HTTP CRUD LIBROS'])
async def VerLibros():
    return {"total": len(libros), "libros": libros, "status": "200"}

# Mostrar únicamente los libros que se pueden pedir prestados
@app.get("/v1/libros/disponibles", tags=['HTTP CRUD LIBROS'])
async def VerLibrosDisponibles():
    librosDisponibles = [lb for lb in libros if lb["estado"] == "disponible"]
    return {"total": len(librosDisponibles), "libros": librosDisponibles, "status": "200"}

# Buscar un libro escribiendo una parte de su nombre
@app.get("/v1/libros/buscar", tags=['HTTP CRUD LIBROS'])
async def BuscarLibro(nombre: str):
    if not nombre or len(nombre.strip()) < 2:
        raise HTTPException(status_code=400, detail="El nombre del libro no es válido")  
    
    librosEncontrados = [lb for lb in libros if nombre.lower() in lb["nombre"].lower()]
    if not librosEncontrados:
        raise HTTPException(status_code=404, detail="No se encontraron libros con ese nombre")
        
    return {"libros": librosEncontrados, "status": "200"}

# Dar de alta un libro nuevo en el catálogo
@app.post("/v1/libros/", tags=['HTTP CRUD LIBROS'], status_code=201)
async def AgregarLibro(nuevoLibro: Libro):
    if not nuevoLibro.nombre or len(nuevoLibro.nombre.strip()) < 2:
        raise HTTPException(status_code=400, detail="El nombre del libro no es válido o faltan datos")

    # Evitamos que se registren dos libros con el mismo ID
    for lb in libros:
        if lb["id"] == nuevoLibro.id:
            raise HTTPException(status_code=400, detail="El libro con este ID ya existe")
            
    libros.append(nuevoLibro.model_dump())
    return {
        "mensaje": "Libro registrado exitosamente",
        "libro": nuevoLibro,
        "status": "201"
    }

# Reemplazar toda la información de un libro
@app.put("/v1/libros/{id}", tags=['HTTP CRUD LIBROS'])
async def ActualizarLibro(id: int, libroActualizado: Libro):
    libroIdx = next((index for (index, lb) in enumerate(libros) if lb["id"] == id), None)
    
    if libroIdx is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    
    if libroActualizado.id != id:
        raise HTTPException(status_code=400, detail="El ID del cuerpo debe coincidir con el de la ruta")
    
    # Validamos que no se pueda reemplazar la información si el libro está prestado en este momento
    if libros[libroIdx]["estado"] == "prestado":
        raise HTTPException(status_code=400, detail="No puedes modificar un libro mientras esté prestado a un usuario")
        
    libros[libroIdx] = libroActualizado.model_dump()
    return {"mensaje": "Libro actualizado completamente", "libro": libros[libroIdx]}

# Modificar solo algunos datos de un libro (ej. cambiar solo las páginas)
@app.patch("/v1/libros/{id}", tags=['HTTP CRUD LIBROS'])
async def ModificarLibro(id: int, libroModificado: LibroUpdate):
    libroEncontrado = next((lb for lb in libros if lb["id"] == id), None)
    
    if not libroEncontrado:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    
    # Validamos que el libro esté en la biblioteca antes de dejar editar sus datos
    if libroEncontrado["estado"] == "prestado":
        raise HTTPException(status_code=400, detail="No puedes modificar un libro mientras esté prestado a un usuario")
        
    datosActualizar = libroModificado.model_dump(exclude_unset=True)
    libroEncontrado.update(datosActualizar)
    return {"mensaje": "Libro modificado exitosamente", "libro": libroEncontrado}

# Borrar un libro del sistema
@app.delete("/v1/libros/{id}", tags=['HTTP CRUD LIBROS'])
async def EliminarLibro(id: int):
    libroEncontrado = next((lb for lb in libros if lb["id"] == id), None)
    
    if not libroEncontrado:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    
    # Comprobamos que el libro esté devuelto antes de borrarlo definitivamente
    if libroEncontrado["estado"] == "prestado":
        raise HTTPException(status_code=400, detail="No se puede eliminar un libro que está actualmente prestado")
        
    libros.remove(libroEncontrado)
    return {"mensaje": "Libro eliminado del catálogo"}

# ------------------------- ENDPOINTS DE USUARIOS --------------------------

# Mostrar a todos los usuarios
@app.get("/v1/usuarios/", tags=['HTTP CRUD USUARIOS'])
async def VerUsuarios():
    return {
        "total": len(usuario),
        "usuarios": usuario,
        "status": "200"
    }

# Registrar un nuevo usuario
@app.post("/v1/usuarios/", tags=['HTTP CRUD USUARIOS'])
async def AgregarUsuario(nuevoUsuario: Usuario):
    for usr in usuario:
        # Validamos que el ID no esté repetido
        if usr["id"] == nuevoUsuario.id:
            raise HTTPException(status_code=400, detail="El usuario con este ID ya existe")
        # Validamos que el correo no esté ocupado por alguien más
        if usr["correo"] == nuevoUsuario.correo:
            raise HTTPException(status_code=400, detail="Este correo ya está registrado")
            
    usuario.append(nuevoUsuario.model_dump())
    return {
        "mensaje": "Usuario agregado exitosamente",
        "usuario": nuevoUsuario,
        "status": "201"
    }

# Reemplazar los datos completos de un usuario
@app.put("/v1/usuarios/{id}", tags=['HTTP CRUD USUARIOS'])
async def ActualizarUsuario(id: int, usuarioActualizado: Usuario):
    usrIdx = next((index for (index, usr) in enumerate(usuario) if usr["id"] == id), None)
    
    if usrIdx is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    if usuarioActualizado.id != id:
        raise HTTPException(status_code=400, detail="El ID del cuerpo debe coincidir con la ruta")
        
    usuario[usrIdx] = usuarioActualizado.model_dump()
    return {"mensaje": "Usuario actualizado completamente", "usuario": usuario[usrIdx]}

# Cambiar solo un dato del usuario (ej. solo el correo)
@app.patch("/v1/usuarios/{id}", tags=['HTTP CRUD USUARIOS'])
async def ModificarUsuario(id: int, usrModificado: UsuarioUpdate):
    usrEncontrado = next((usr for usr in usuario if usr["id"] == id), None)
    
    if not usrEncontrado:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    datosActualizar = usrModificado.model_dump(exclude_unset=True)
    usrEncontrado.update(datosActualizar)
    return {"mensaje": "Usuario modificado exitosamente", "usuario": usrEncontrado}

# Borrar un usuario del sistema
@app.delete("/v1/usuarios/{id}", tags=['HTTP CRUD USUARIOS'])
async def EliminarUsuario(id: int):
    usrEncontrado = next((usr for usr in usuario if usr["id"] == id), None)
    
    if not usrEncontrado:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    # Buscamos en el historial si este usuario tiene algún libro que no haya devuelto
    librosSinDevolver = 0
    for p in prestamos:
        if p["idUsuario"] == id:
            libroDelPrestamo = next((lb for lb in libros if lb["id"] == p["idLibro"]), None)
            if libroDelPrestamo and libroDelPrestamo["estado"] == "prestado":
                librosSinDevolver += 1
                
    # Si detectamos libros en su poder, impedimos borrar al usuario
    if librosSinDevolver > 0:
        raise HTTPException(status_code=400, detail="No puedes eliminar a un usuario que aún tiene libros sin devolver")
        
    usuario.remove(usrEncontrado)
    return {"mensaje": "Usuario eliminado del sistema"}

# ------------------------- ENDPOINTS DE PRÉSTAMOS --------------------------

# Ver la lista de quién tiene cada libro
@app.get("/v1/prestamos/", tags=['HTTP CRUD PRÉSTAMOS'])
async def VerPrestamos():
    listaPrestamos = []
    
    for p in prestamos:
        # Emparejamos los datos para mostrar nombres en lugar de puros números
        libroEncontrado = next((lb for lb in libros if lb["id"] == p["idLibro"]), None)
        usuarioEncontrado = next((usr for usr in usuario if usr["id"] == p["idUsuario"]), None)
        
        listaPrestamos.append({
            "idPrestamo": p["idPrestamo"],
            "idLibro": p["idLibro"],
            "nombreLibro": libroEncontrado["nombre"] if libroEncontrado else "Libro no encontrado",
            "idUsuario": p["idUsuario"],
            "nombreUsuario": usuarioEncontrado["nombre"] if usuarioEncontrado else "Usuario no encontrado",
            "estadoActual": libroEncontrado["estado"] if libroEncontrado else "Desconocido"
        })
        
    return {
        "total": len(listaPrestamos), 
        "prestamos": listaPrestamos, 
        "status": "200"
    }

# Entregar un libro a un usuario
@app.post("/v1/prestamos/", tags=['HTTP CRUD PRÉSTAMOS'], status_code=201)
async def RegistrarPrestamo(datosPrestamo: NuevoPrestamo):
    libroEncontrado = next((lb for lb in libros if lb["id"] == datosPrestamo.idLibro), None)
    if not libroEncontrado:
        raise HTTPException(status_code=400, detail="El libro solicitado no existe")
    
    usuarioEncontrado = next((usr for usr in usuario if usr["id"] == datosPrestamo.idUsuario), None)
    if not usuarioEncontrado:
        raise HTTPException(status_code=400, detail="El usuario no existe")

    # Comprobamos que el libro no esté en manos de alguien más
    if libroEncontrado["estado"] == "prestado":
        raise HTTPException(status_code=409, detail="El libro ya se encuentra prestado a otra persona")

    # Evitamos que un solo usuario acapare los libros (Límite de 3 préstamos activos)
    librosEnPoder = 0
    for p in prestamos:
        if p["idUsuario"] == datosPrestamo.idUsuario:
            lb = next((l for l in libros if l["id"] == p["idLibro"]), None)
            if lb and lb["estado"] == "prestado":
                librosEnPoder += 1
                
    if librosEnPoder >= 3:
         raise HTTPException(status_code=400, detail="El usuario ha alcanzado el límite de 3 libros sin devolver")

    # Asignamos el número de préstamo que sigue
    nuevoIdPrestamo = max([p["idPrestamo"] for p in prestamos], default=0) + 1
    prestamos.append({
        "idPrestamo": nuevoIdPrestamo,
        "idLibro": datosPrestamo.idLibro,
        "idUsuario": datosPrestamo.idUsuario
    })
    
    # Actualizamos el estado para que nadie más lo pueda pedir
    libroEncontrado["estado"] = "prestado"
    
    return {"mensaje": "Préstamo registrado exitosamente", "idPrestamo": nuevoIdPrestamo, "status": "201"}

# Marcar que el usuario regresó el libro a la biblioteca
@app.put("/v1/prestamos/devolver/{idPrestamo}", tags=['HTTP CRUD PRÉSTAMOS'], status_code=200)
async def DevolverLibro(idPrestamo: int):
    prestamoEncontrado = next((p for p in prestamos if p["idPrestamo"] == idPrestamo), None)
    
    if not prestamoEncontrado:
        raise HTTPException(status_code=409, detail="El registro de préstamo ya no existe")
        
    libroAsociado = next((lb for lb in libros if lb["id"] == prestamoEncontrado["idLibro"]), None)
    
    # Verificamos si alguien intenta devolver un libro que ya había sido devuelto
    if libroAsociado and libroAsociado["estado"] == "disponible":
         raise HTTPException(status_code=400, detail="Este libro ya fue devuelto anteriormente")

    # Liberamos el libro para que alguien más lo pueda pedir
    if libroAsociado:
        libroAsociado["estado"] = "disponible"

    return {"mensaje": "El libro ha sido devuelto satisfactoriamente", "status": "200"}

# Borrar un registro de préstamo del historial
@app.delete("/v1/prestamos/{idPrestamo}", tags=['HTTP CRUD PRÉSTAMOS'])
async def EliminarRegistroPrestamo(idPrestamo: int):
    prestamoEncontrado = next((p for p in prestamos if p["idPrestamo"] == idPrestamo), None)
    
    if not prestamoEncontrado:
        raise HTTPException(status_code=409, detail="El registro de préstamo ya no existe")
        
    libroEncontrado = next((lb for lb in libros if lb["id"] == prestamoEncontrado["idLibro"]), None)
    
    # Impedimos borrar la evidencia de un préstamo si el libro no ha regresado a la biblioteca
    if libroEncontrado and libroEncontrado["estado"] == "prestado":
        raise HTTPException(
            status_code=400, 
            detail="No puedes borrar este registro porque el libro aún está en préstamo"
        )
        
    prestamos.remove(prestamoEncontrado)
    
    return {"mensaje": "Registro de préstamo eliminado", "status": "200"}

# Corregir un error de captura en un préstamo (ej. pusiste mal al usuario o al libro)
@app.patch("/v1/prestamos/{idPrestamo}", tags=['HTTP CRUD PRÉSTAMOS'])
async def ModificarPrestamo(idPrestamo: int, prestamoModificado: PrestamoUpdate):
    prestamoEncontrado = next((p for p in prestamos if p["idPrestamo"] == idPrestamo), None)
    
    if not prestamoEncontrado:
        raise HTTPException(status_code=404, detail="Registro de préstamo no encontrado")
        
    libroAsociado = next((lb for lb in libros if lb["id"] == prestamoEncontrado["idLibro"]), None)
    
    # Para no arruinar el inventario, no permitimos editar un registro activo, primero se debe devolver el libro
    if libroAsociado and libroAsociado["estado"] == "prestado":
        raise HTTPException(status_code=400, detail="Para modificar este registro, primero el usuario debe devolver el libro")
        
    datosActualizar = prestamoModificado.model_dump(exclude_unset=True)
    
    if "idLibro" in datosActualizar:
        if not any(lb["id"] == datosActualizar["idLibro"] for lb in libros):
            raise HTTPException(status_code=400, detail="El nuevo ID de libro no existe")
            
    if "idUsuario" in datosActualizar:
        if not any(usr["id"] == datosActualizar["idUsuario"] for usr in usuario):
            raise HTTPException(status_code=400, detail="El nuevo ID de usuario no existe")
            
    prestamoEncontrado.update(datosActualizar)
    return {"mensaje": "Registro de préstamo modificado", "prestamo": prestamoEncontrado}