from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductResponse
from app.services.product_service import get_productos,get_producto,create_producto,update_producto,delete_producto

import os

router = APIRouter()
security = HTTPBasic()

def verify_credentials(credentials: HTTPBasicCredentials):
    if credentials.username != os.getenv("API_USER") or credentials.password != os.getenv("API_PASSWORD"):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    return credentials.username

@router.get("/productos", response_model = list[ProductResponse])
def listar_productos(credentials: HTTPBasicCredentials = Depends(security)):
    verify_credentials(credentials)
    return get_productos()

@router.get("/productos/{producto_id}", response_model = ProductResponse)
def obtener_producto(producto_id: int, credentials: HTTPBasicCredentials = Depends(security)):
    verify_credentials(credentials)
    producto = get_producto(producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="producto no encontrado")
    return producto

@router.post("/productos", response_model=ProductResponse)
def crear_producto(producto:ProductCreate, credentials: HTTPBasicCredentials = Depends(security)):
    verify_credentials(credentials)
    return create_producto(producto)

@router.put("/productos/{producto_id}", response_model=ProductResponse)
def actualizar_producto(producto_id: int, producto:ProductUpdate, credentials: HTTPBasicCredentials = Depends(security)):
    verify_credentials(credentials)
    return update_producto(producto_id, producto)

@router.delete("/productos/{producto_id}")
def eliminar_producto(producto_id: int, credentials: HTTPBasicCredentials = Depends(security)):
    verify_credentials(credentials)
    return delete_producto(producto_id)
