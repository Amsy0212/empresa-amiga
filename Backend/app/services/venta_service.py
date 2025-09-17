from fastapi import HTTPException
from app.models.database import get_db_connection
from app.schemas.venta_schema import VentaCreate, VentaResponse
from app.services.product_service import get_producto
from app.services.client_service import get_cliente

def get_ventas():
    """
    Obtiene todos las ventas
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id,cliente_id, fecha_venta,total FROM ventas;")
    ventas = cursor.fetchall()
    cursor.close()
    conn.close()
    return [{"id":c[0],"cliente_id":c[1], "fecha_venta":c[2],
             "total":c[3]} for c in ventas]

def get_venta(venta_id: int):
    """
    Obtiene una venta por su ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id,cliente_id, fecha_venta,total "
                   "FROM ventas WHERE id =%s;",(venta_id,))
    venta = cursor.fetchone()
    cursor.close()
    conn.close()
    if venta:
        return {"id": venta[0], "cliente_id": venta[1], "fecha_venta": venta[2],
                "total": venta[3]}
    return None

def get_venta_cliente(user_id: int):
    """
    Obtiene venta por el ID CLIENTE.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id,cliente_id, fecha_venta,total "
                   "FROM ventas WHERE cliente_id =%s;", (user_id,))
    ventas = cursor.fetchall()
    cursor.close()
    conn.close()
    if ventas:
        return [{"id": c[0], "cliente_id": c[1], "fecha_venta": c[2],
                 "total": c[3]} for c in ventas]
    return None

def create_venta(venta: VentaCreate):
    """
    Crear una venta en base de datos
    """

    # Validacion de producto y cliente que existan
    producto = get_producto(venta.producto_id)
    cliente = get_cliente(venta.cliente_id)

    if not producto:
        raise HTTPException(status_code=404, detail="Producto inexistente")
    elif not cliente:
        raise HTTPException(status_code=404, detail="Cliente inexistente")

    # Conexión a la base de datos
    conn = get_db_connection()
    cursor = conn.cursor()

    # Validacion del stock disponible del producto
    cursor.execute("SELECT stock, precio FROM productos WHERE id = %s;", (venta.producto_id,))
    producto_data = cursor.fetchone()

    if not producto_data:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    stock_disponible, precio_unitario = producto_data

    if venta.cantidad > stock_disponible:
        raise HTTPException(
            status_code=400,
            detail=f"Stock insuficiente. Disponible: {stock_disponible}, Solicitado: {venta.cantidad}"
        )

    # Insertar la venta
    cursor.execute(
        "INSERT INTO ventas(cliente_id,total) "
        "VALUES(%s,%s) RETURNING id;",
        (venta.cliente_id, venta.total)
    )

    venta_id = cursor.fetchone()[0]

    # Insertar el detalle de la venta
    cursor.execute(
        "INSERT INTO detalle_ventas(venta_id, producto_id, cantidad, precio_unitario) "
        "VALUES(%s, %s, %s, %s) RETURNING id;",
        (venta_id, venta.producto_id, venta.cantidad, precio_unitario)
    )

    # Actualizar el stock del producto
    nuevo_stock = stock_disponible - venta.cantidad
    cursor.execute(
        "UPDATE productos SET stock = %s WHERE id = %s;",
        (nuevo_stock, venta.producto_id)
    )
    print(
        f"Inserción en detalle_ventas: venta_id={venta_id}, "
        f"producto_id={venta.producto_id}, cantidad={venta.cantidad}, "
        f"precio_unitario={precio_unitario}"
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"cliente_id":venta.cliente_id,"total":venta.total, "producto_id":venta.producto_id,"cantidad":venta.cantidad}

def get_detalle_ventas():
    """
    Obtiene los detalles de todas las ventas
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id,venta_id, producto_id,cantidad,precio_unitario,subtotal"
                   " FROM detalle_ventas;")
    detalle_ventas = cursor.fetchall()
    cursor.close()
    conn.close()
    return [{"id":c[0],"venta_id":c[1], "producto_id":c[2],"cantidad":c[3],
             "precio_unitario":c[4],"subtotal":c[5]} for c in detalle_ventas]

def get_detalle_venta(venta_id: int):
    """
    Obtiene el detalles de una venta
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id,venta_id, producto_id,cantidad,precio_unitario,subtotal"
                   " FROM detalle_ventas WHERE id =%s;",(venta_id,))
    detalleventa = cursor.fetchone()
    cursor.close()
    conn.close()
    if detalleventa:
        return {"id":detalleventa[0], "venta_id":detalleventa[1], "producto_id":detalleventa[2],
                 "cantidad":detalleventa[3], "precio_unitario":detalleventa[4], "subtotal":detalleventa[5] }
    return None

def update_venta(venta_id: int, venta:VentaCreate):
    """
    Actualiza una venta en la base de datos
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE ventas SET cliente_id = %s, total =%s WHERE id = %s RETURNING id;",
        (venta.cliente_id, venta.total, venta_id)
    )
    update_ventas_id = cursor.fetchone()[0]
    cursor.execute(
        "UPDATE detalle_ventas SET producto_id = %s, cantidad =%s WHERE venta_id = %s RETURNING id;",
        (venta.producto_id, venta.cantidad, update_ventas_id)
    )
    update_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return {"id": venta_id,**venta.dict()} if update_ventas_id else None


def delete_venta(venta_id:int):
    """
    Elimina una venta por su ID y por cascada tambien elimina su detalle de venta
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM detalle_ventas WHERE venta_id = %s RETURNING id;",(venta_id,))
    cursor.execute("DELETE FROM ventas WHERE id = %s RETURNING id;", (venta_id,))
    deleted_id = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()

    return deleted_id is not None
