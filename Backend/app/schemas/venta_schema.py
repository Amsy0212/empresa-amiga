from datetime import datetime
from pydantic import BaseModel

class VentaBase(BaseModel):
    cliente_id: int
    total: float

class VentaCreate(VentaBase):
    producto_id: int
    cantidad: int

class VentaResponse(VentaBase):
    id: int
    fecha_venta: datetime