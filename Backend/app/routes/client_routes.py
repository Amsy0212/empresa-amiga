from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.services.client_service import get_clientes,create_cliente,delete_cliente, get_cliente,update_cliente
from app.schemas.client_schema import ClienteCreate, ClienteUpdate, ClienteResponse

import os

router = APIRouter()
security = HTTPBasic()

def verify_credentials(credentials: HTTPBasicCredentials):
    if credentials.username != os.getenv("API_USER") or credentials.password != os.getenv("API_PASSWORD"):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    return credentials.username

@router.get("/clientes", response_model = list[ClienteResponse])
def listar_clientes(credentials: HTTPBasicCredentials = Depends(security)):
    verify_credentials(credentials)
    return get_clientes()

@router.get("/clientes/{client_id}", response_model = ClienteResponse)
def obtener_cliente(client_id:int, credentials: HTTPBasicCredentials = Depends(security)):
    verify_credentials(credentials)
    cliente = get_cliente(client_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente

@router.post("/clientes", response_model = ClienteResponse)
def crear_cliente(cliente:ClienteCreate, credentials: HTTPBasicCredentials = Depends(security)):
    verify_credentials(credentials)
    return create_cliente(cliente)

@router.put("/clientes/{client_id}", response_model = ClienteResponse)
def actualizar_clientes(client_id:int, cliente: ClienteUpdate, credentials: HTTPBasicCredentials = Depends(security)):
    verify_credentials(credentials)
    return update_cliente(client_id,cliente)

@router.delete("/clientes/{client_id}")
def eliminar_clientes(client_id:int, credentials: HTTPBasicCredentials = Depends(security)):
    verify_credentials(credentials)
    return delete_cliente(client_id)