# Frontend/app.py
import datetime as dt
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
import streamlit as st

# ----------------------- CONFIG -----------------------
DEFAULT_BACKEND = "http://fastapi_service_v0:8000"   # твой FastAPI, порт 2347 -> 8000
DEFAULT_USER    = "admin"                   # см. Backend/.env
DEFAULT_PASS    = "admin123"

st.set_page_config(page_title="Empresa Amiga — Admin", layout="wide")
st.title("Empresa Amiga — Admin (Streamlit)")

# ----------------------- SIDEBAR -----------------------
with st.sidebar:
    st.header("Settings")

    backend = st.text_input(
        "Backend URL",
        value=st.session_state.get("backend", DEFAULT_BACKEND),
        help="Base URL of your FastAPI",
    )
    st.session_state["backend"] = backend

    api_user = st.text_input(
        "API user",
        value=st.session_state.get("api_user", DEFAULT_USER),
        help="HTTP Basic username",
    )
    st.session_state["api_user"] = api_user

    api_pass = st.text_input(
        "API password",
        value=st.session_state.get("api_pass", DEFAULT_PASS),
        type="password",
        help="HTTP Basic password",
    )
    st.session_state["api_pass"] = api_pass

    col_h1, col_h2 = st.columns(2)
    with col_h1:
        if st.button("Check /health"):
            try:
                r = requests.get(f"{backend}/health", timeout=5)
                st.success(f"/health → {r.status_code} {r.json()}")
            except Exception as e:
                st.error(f"Backend not reachable: {e}")
    with col_h2:
        if st.button("Check /db-ping"):
            try:
                r = requests.get(f"{backend}/db-ping", timeout=5)
                st.info(f"/db-ping → {r.status_code} {r.json()}")
            except Exception as e:
                st.error(f"DB ping failed: {e}")

    st.divider()
    page = st.radio(
        "Pages",
        ["Dashboard", "Add Client", "Add Product", "New Sale"],
        index=["Dashboard", "Add Client", "Add Product", "New Sale"].index(
            st.session_state.get("current_page", "Dashboard")
        ),
    )
    st.session_state["current_page"] = page


# ----------------------- API HELPERS -----------------------
def _auth() -> HTTPBasicAuth:
    return HTTPBasicAuth(st.session_state["api_user"], st.session_state["api_pass"])

def api_get(path: str):
    """GET with BasicAuth; raises with readable message on error."""
    url = f"{st.session_state['backend']}{path}"
    try:
        r = requests.get(url, auth=_auth(), timeout=30)
    except Exception as e:
        raise RuntimeError(f"GET {path} network error: {e}")
    if not r.ok:
        # try to surface FastAPI JSON error
        try:
            detail = r.json()
        except Exception:
            detail = r.text
        raise RuntimeError(f"GET {path} failed: {r.status_code} {detail}")
    return r.json()

def api_post(path: str, payload: dict):
    """POST with BasicAuth; raises with readable message on error."""
    url = f"{st.session_state['backend']}{path}"
    try:
        r = requests.post(url, json=payload, auth=_auth(), timeout=30)
    except Exception as e:
        raise RuntimeError(f"POST {path} network error: {e}")
    if not r.ok:
        try:
            detail = r.json()
        except Exception:
            detail = r.text
        raise RuntimeError(f"POST {path} failed: {r.status_code} {detail}")
    return r.json()

# ----------------------- PAGES -----------------------
if page == "Add Client":
    st.subheader("Create new client")
    with st.form("client_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre   = st.text_input("First name*", max_chars=100)
            email    = st.text_input("Email", max_chars=150)
            telefono = st.text_input("Phone", max_chars=50)
        with col2:
            apellido       = st.text_input("Last name*", max_chars=100)
            direccion      = st.text_input("Address", max_chars=200)
            fecha_registro = st.date_input("Registration date", value=dt.date.today())

        submitted = st.form_submit_button("Add client")
        if submitted:
            if not nombre.strip() or not apellido.strip():
                st.warning("First name and last name are required.")
            else:
                payload = {
                    "nombre": nombre.strip(),
                    "apellido": apellido.strip(),
                    "email": email.strip() or None,
                    "telefono": telefono.strip() or None,
                    "direccion": direccion.strip() or None,
                    "fecha_registro": str(fecha_registro),
                }
                try:
                    res = api_post("/api/clientes", payload)
                    st.success(f"Client created: id={res.get('id', 'unknown')}")
                except Exception as e:
                    st.error(str(e))

elif page == "Add Product":
    st.subheader("Create new product")
    with st.form("product_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Name*", max_chars=120)
            precio = st.number_input("Price*", min_value=0.0, step=0.01, value=0.0)
            stock  = st.number_input("Stock*", min_value=0, step=1, value=0)
        with col2:
            descripcion   = st.text_area("Description", height=120)
            fecha_creacion = st.date_input("Created at", value=dt.date.today())

        submitted = st.form_submit_button("Add product")
        if submitted:
            if not nombre.strip() or precio <= 0:
                st.warning("Name and positive price are required.")
            else:
                payload = {
                    "nombre": nombre.strip(),
                    "descripcion": descripcion.strip() or None,
                    "precio": float(precio),
                    "stock": int(stock),
                    "fecha_creacion": str(fecha_creacion),
                }
                try:
                    res = api_post("/api/productos", payload)
                    st.success(f"Product created: id={res.get('id', 'unknown')}")
                except Exception as e:
                    st.error(str(e))

elif page == "New Sale":
    st.subheader("Register a new sale")

    # load clients/products
    try:
        clients   = api_get("/api/clientes")
        products  = api_get("/api/productos")
    except Exception as e:
        st.error(str(e))
        st.stop()

    clients_df  = pd.DataFrame(clients)  if clients  else pd.DataFrame(columns=["id","nombre","apellido"])
    products_df = pd.DataFrame(products) if products else pd.DataFrame(columns=["id","nombre","precio","stock"])

    if clients_df.empty or products_df.empty:
        st.info("Need clients and products to create a sale.")
        st.stop()

    client_map  = {f"{row['id']} — {row['nombre']} {row.get('apellido','')}": row["id"] for _, row in clients_df.iterrows()}
    client_label = st.selectbox("Client", list(client_map.keys()))
    cliente_id   = client_map[client_label]
    fecha_venta  = st.date_input("Sale date", value=dt.date.today())

    st.markdown("#### Items")
    max_lines = 5
    line_items = []
    for i in range(max_lines):
        with st.expander(f"Item #{i+1}", expanded=(i == 0)):
            prod_label = st.selectbox(
                "Product",
                [f"{r['id']} — {r['nombre']} (stock {r.get('stock','?')})" for _, r in products_df.iterrows()],
                key=f"prod_{i}"
            )
            prod_id   = int(prod_label.split(" — ")[0])
            prod_row  = products_df[products_df["id"] == prod_id].iloc[0]
            def_price = float(prod_row.get("precio", 0.0))
            cantidad  = st.number_input("Quantity",   min_value=0,   step=1,   value=0,         key=f"qty_{i}")
            unit_price= st.number_input("Unit price", min_value=0.0, step=0.01, value=def_price, key=f"price_{i}")

            if cantidad > 0:
                subtotal = float(cantidad) * float(unit_price)
                line_items.append({
                    "producto_id":   prod_id,
                    "cantidad":      int(cantidad),
                    "precio_unitario": float(unit_price),
                    "subtotal":      round(subtotal, 2),
                })
                st.caption(f"Subtotal: {subtotal:.2f}")

    total = round(sum(li["subtotal"] for li in line_items), 2)
    st.markdown(f"### Total: **{total:.2f}**")

    if st.button("Create sale"):
        if not line_items:
            st.warning("Please add at least one item.")
        else:
            try:
                # 1) create venta
                venta_payload = {
                    "cliente_id": int(cliente_id),
                    "fecha_venta": str(fecha_venta),
                    "total": total,
                }
                venta_res = api_post("/api/ventas", venta_payload)
                venta_id  = venta_res.get("id")
                if not venta_id:
                    raise RuntimeError(f"Cannot get venta id from response: {venta_res}")

                # 2) add detalle_ventas
                created = 0
                for li in line_items:
                    det_payload = {"venta_id": venta_id, **li}
                    _ = api_post("/api/detalle_ventas", det_payload)
                    created += 1

                st.success(f"Sale created (id={venta_id}) with {created} item(s).")
            except Exception as e:
                st.error(str(e))

elif page == "Dashboard":
    st.subheader("Sales dashboard")

    # ventas → time series
    try:
        ventas = api_get("/api/ventas")
    except Exception as e:
        st.error(str(e))
        ventas = []

    # detalle + productos → top products
    try:
        detalle = api_get("/api/detalle_ventas")
    except Exception as e:
        st.error(str(e))
        detalle = []

    try:
        productos = api_get("/api/productos")
    except Exception as e:
        st.error(str(e))
        productos = []

    col_a, col_b = st.columns(2, gap="large")

    # Chart 1: sales by date
    with col_a:
        st.markdown("#### Sales over time")
        if ventas:
            vdf = pd.DataFrame(ventas)
            if {"fecha_venta", "total"}.issubset(vdf.columns):
                vdf["fecha_venta"] = pd.to_datetime(vdf["fecha_venta"]).dt.date
                series = vdf.groupby("fecha_venta")["total"].sum().reset_index()
                series = series.sort_values("fecha_venta")
                st.line_chart(
                    series.rename(columns={"fecha_venta": "date", "total": "sales"}),
                    x="date", y="sales", height=280
                )
            else:
                st.info("ventas data does not contain fecha_venta/total.")
        else:
            st.info("No ventas yet.")

    # Chart 2: top products by quantity
    with col_b:
        st.markdown("#### Top products (by quantity)")
        if detalle and productos:
            ddf = pd.DataFrame(detalle)
            pdf = pd.DataFrame(productos)
            if not ddf.empty and {"producto_id", "cantidad"}.issubset(ddf.columns):
                qty = ddf.groupby("producto_id")["cantidad"].sum().reset_index()
                name_map = {row["id"]: row["nombre"] for _, row in pdf.iterrows()} if not pdf.empty else {}
                qty["producto"] = qty["producto_id"].map(name_map).fillna(qty["producto_id"])
                qty = qty.sort_values("cantidad", ascending=False).head(10)
                st.bar_chart(
                    qty.rename(columns={"producto": "Product", "cantidad": "Qty"}),
                    x="Product", y="Qty", height=280
                )
            else:
                st.info("detalle_ventas data does not contain producto_id/cantidad.")
        else:
            st.info("No detalle_ventas or productos yet.")
