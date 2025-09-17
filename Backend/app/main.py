# Backend/app/main.py
from fastapi import FastAPI
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Empresa Amiga API")

# импорт роутеров по твоим именам файлов
from app.routes.client_routes import router as client_router
from app.routes.product_routes import router as product_router
from app.routes.venta_routes   import router as venta_router

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/db-ping")
def db_ping():
    conn = None
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME", "postgres"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "")
        )
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            cur.fetchone()
        return {"db": "ok"}
    except Exception as e:
        return {"db": "error", "detail": str(e)}
    finally:
        if conn:
            conn.close()

# подключение роутеров
app.include_router(client_router,  prefix="/api", tags=["Clientes"])
app.include_router(product_router, prefix="/api", tags=["Productos"])
app.include_router(venta_router,   prefix="/api", tags=["Ventas"])
