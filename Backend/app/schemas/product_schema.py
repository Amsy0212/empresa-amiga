from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime

class ProductBase(BaseModel):
    nombre: str
    descripcion: str
    precio: Decimal
    stock: int
    fecha_creacion: Optional[datetime]

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int

