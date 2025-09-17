from app.models.database import get_db_connection
from app.schemas.client_schema import ClienteCreate,ClienteUpdate

def get_clientes():
    """
    Obtiene todos los clientes
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre,apellido, email, telefono, direccion FROM clientes;")
    clientes = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        {"id": c[0], "nombre":c[1], "apellido":c[2], "email":c[3], "telefono":c[4],
         "direccion":c[5]} for c in clientes
    ]

def get_cliente(client_id: int):
    """
    Obtiene un cliente por su ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, apellido, email, telefono, "
                   "direccion FROM clientes WHERE id = %s;", (client_id,))
    cliente = cursor.fetchone()
    cursor.close()
    conn.close()
    if cliente:
        return {"id": cliente[0], "nombre": cliente[1], "apellido": cliente[2],
                "email": cliente[3], "telefono": cliente[4], "direccion": cliente[5]}
    return None

def create_cliente(cliente: ClienteCreate):
    """
    Crea un cliente en la base de datos
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO clientes (nombre, apellido, email, telefono, direccion) VALUES (%s,%s,%s,%s,%s) RETURNING id;",
        (cliente.nombre, cliente.apellido,cliente.email,cliente.telefono,cliente.direccion)
                   )
    cliente_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return {"id":cliente_id, **cliente.dict()}

def update_cliente(cliente_id: int, cliente: ClienteUpdate):
    """
    Actualiza un cliente en la base de datos
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE clientes SET nombre = %s, apellido = %s, email = %s, telefono = %s, direccion =%s WHERE id = %s RETURNING id;",
        (cliente.nombre, cliente.apellido, cliente.email, cliente.telefono, cliente.direccion, cliente_id)
    )
    updated_id = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return {"id": cliente_id, **cliente.dict()} if updated_id else None


def delete_cliente(cliente_id: int):
    """
    Elimina un cliente por su ID
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clientes WHERE id = %s RETURNING id;", (cliente_id,))
    deleted_id = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return deleted_id is not None