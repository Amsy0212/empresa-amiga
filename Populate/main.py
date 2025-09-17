import os
import time
import random
from dotenv import load_dotenv
from db import get_connection, insert_cliente, insert_venta, insert_detalle_venta, update_venta_total,insert_producto

# cargar variables entorno
load_dotenv()
INSERT_INTERVAL = int(os.getenv("INSERT_INTERVAL", "10"))
NUM_RECORDS = int(os.getenv("NUM_RECORDS", "5"))


def populate_data():
    """
    Funcion que conecta a la bd y cada ciclo inserta datos falsos en :
    - inserta un cliente
    - crea una venta para ese cliente
    - inserta uno o dos productos y sus respectivas en la venta
    - adctualiza el total de la venta en funcion de los getalles ingresados
    """
    try:
        conn = get_connection()
        for _ in range(NUM_RECORDS):
            # insertar un cliente
            cliente_id = insert_cliente(conn)
            print(f"Cliente insertado con id: {cliente_id}")

            # crear una venta para el cliente
            venta_id = insert_venta(conn, cliente_id)

            # para la venta se insertaran entre 1 y 2 productos
            for _ in range(random.randint(1, 20)):
                producto_id = insert_producto(conn)
                cantidad = random.randint(1, 500)
                # Se simula el precio unitario; en un caso real podria recuperarse del producto insertado
                precio_unitario = round(random.randint(10, 5000), 2)
                insert_detalle_venta(conn, venta_id, producto_id, cantidad, precio_unitario)
                print(f"Detalle insertado para venta: {venta_id}, producto {producto_id}")

            # Actualizar el total de la venta
            update_venta_total(conn, venta_id)
            print(f"Venta{venta_id} actualizado con el total correspondiente: \n")

        conn.close()
    except Exception as e:
        print("Error al poblar datos:", e)


if __name__ == "__main__":
    while True:
        print("Insertando datos falsos en la base de datos")
        populate_data()
        print(f"Esperando {INSERT_INTERVAL} segundos para la siguiente insercion..\n")
        time.sleep(INSERT_INTERVAL)