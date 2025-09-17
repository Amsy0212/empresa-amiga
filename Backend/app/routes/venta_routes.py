from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.schemas.venta_schema import VentaCreate,VentaResponse
from app.schemas.venta_detail_schema import DetalleVentaCreate,DetalleVentaResponse
from app.services.venta_service import *

import os

router = APIRouter()
security = HTTPBasic()

def verify_credentials(credentials: HTTPBasicCredentials):
    if credentials.username != os.getenv("API_USER") or credentials.password != os.getenv("API_PASSWORD"):
        raise HTTPException(status_code=401, detail="Acceso no autorizado")
    return credentials.username

@router.get("/ventas", response_model = list[VentaResponse])
def listar_ventas(credentials: HTTPBasicCredentials = Depends(security)):
    verify_credentials(credentials)
    return get_ventas()

@router.get("/ventas/{venta_id}", response_model = VentaResponse)
def obtener_venta(venta_id: int, credentials: HTTPBasicCredentials = Depends(security)):
    verify_credentials(credentials)
    venta = get_venta(venta_id)
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return venta

@router.get("/ventas/{cliente_id}", response_model = VentaResponse)
def obtener_venta_cliente(cliente_id: int, credentials: HTTPBasicCredentials = Depends(security)):
    verify_credentials(credentials)
    venta = get_venta_cliente(cliente_id)
    if not venta:
        raise HTTPException(status_code=404, detail="El cliente no tiene venta realizada")
    return venta

@router.get("/detalle_ventas", response_model = list[DetalleVentaResponse])
def listar_detalle_ventas(credentials: HTTPBasicCredentials = Depends(security)):
    verify_credentials(credentials)
    return get_detalle_ventas()

@router.get("/detalle_ventas/{detalle_venta_id}", response_model = DetalleVentaResponse)
def obtener_detalle_ventas(detalle_venta_id: int, credentials: HTTPBasicCredentials = Depends(security)):
    verify_credentials(credentials)
    venta = get_detalle_venta(detalle_venta_id)
    if not venta:
        raise HTTPException(status_code=404, detail="Detalle de venta no encontrado")
    return venta

@router.post("/ventas", response_model=VentaCreate)
def crear_venta(venta:VentaCreate, credentials: HTTPBasicCredentials = Depends(security)):
    verify_credentials(credentials)
    return create_venta(venta)

@router.put("/ventas/{venta_id}", response_model=VentaCreate)
def actualizar_venta(venta_id: int, venta:VentaCreate, credentials: HTTPBasicCredentials = Depends(security)):
    verify_credentials(credentials)
    return update_venta(venta_id, venta)

@router.delete("/ventas/{venta_id}")
def eliminar_venta(venta_id: int, credentials: HTTPBasicCredentials = Depends(security)):
    verify_credentials(credentials)
    return delete_venta(venta_id)
