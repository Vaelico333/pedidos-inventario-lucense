import json
from datetime import datetime
from pathlib import Path

import streamlit as st

from servicios.creador_pdf import generar_pdf_pedido


RUTA_DATOS = Path(__file__).parent / "datos" / "datos_proveedores.json"


def cargar_proveedores() -> dict:
    with RUTA_DATOS.open(encoding="utf-8") as archivo:
        return json.load(archivo)


def clave_pedido(proveedor: str, presentacion: str, producto: str) -> str:
    return f"{proveedor} - {presentacion} - {producto}"


def agregar_al_pedido(proveedor: str, producto: str, presentacion: str, clave_cantidad: str) -> None:
    cantidad = float(st.session_state.get(clave_cantidad, 0))
    if cantidad <= 0:
        st.session_state.mensaje_local = "Introduce una cantidad mayor que cero."
        return

    clave = clave_pedido(proveedor, presentacion, producto)
    st.session_state.pedido[clave] = st.session_state.pedido.get(clave, 0) + cantidad
    st.session_state.mensaje_local = f"Añadido: {cantidad:g} x {producto} ({proveedor})."


def render_producto(proveedor: str, producto: str, presentacion: str, prefijo: str) -> None:
    col_nombre, col_cantidad, col_accion = st.columns([2, 1, 1], vertical_alignment="center")
    clave_cantidad = f"cantidad_{prefijo}_{proveedor}_{producto}"
    clave_widget = f"{prefijo}_{proveedor}_{producto}"

    with col_nombre:
        st.markdown(f"**{producto}**")
        st.caption(presentacion)
    with col_cantidad:
        st.number_input(
            "Cantidad",
            min_value=0.0,
            step=0.01,
            key=clave_cantidad,
            label_visibility="collapsed",
        )
    with col_accion:
        if st.button("Añadir", key=f"anadir_{clave_widget}"):
            agregar_al_pedido(proveedor, producto, presentacion, clave_cantidad)
            st.rerun()


@st.fragment(key="busqueda_local")
def render_busqueda(datos: dict) -> None:
    col_entrada, col_boton = st.columns([4, 1], vertical_alignment="bottom")
    with col_entrada:
        consulta = st.text_input(
            "Buscar producto",
            placeholder="Introduce un producto",
            key="consulta_busqueda_local",
        )
    with col_boton:
        buscar = st.button("🔎 Buscar", key="boton_busqueda_local", use_container_width=True)

    if buscar:
        st.session_state.resultado_busqueda_local = consulta.strip()

    consulta_activa = st.session_state.get("resultado_busqueda_local", "")
    if not consulta_activa:
        return

    coincidencias = []
    for proveedor, datos_proveedor in datos.items():
        productos = datos_proveedor.get("Productos", {})
        if isinstance(productos, dict):
            coincidencias.extend(
                (proveedor, producto, presentacion)
                for producto, presentacion in productos.items()
                if consulta_activa.casefold() in producto.casefold()
            )

    st.caption(f"{len(coincidencias)} resultado(s) para «{consulta_activa}»")
    if not coincidencias:
        st.info("No se encontraron productos con ese nombre.")
        return

    for proveedor, producto, presentacion in coincidencias:
        render_producto(proveedor, producto, presentacion, "busqueda")
        st.divider()

def render_pedido(datos: dict) -> None:
    st.sidebar.header("📋 Pedido actual")
    pedido = st.session_state.pedido

    if not pedido:
        st.sidebar.info("El pedido está vacío.")
        return

    proveedores = {}
    for prov in datos.keys():
        proveedores[prov] = []
    for indice, (clave, cantidad) in enumerate(list(pedido.items())):
        partes = clave.split(" - ", 2)
        if len(partes) != 3:
            continue
        proveedor, presentacion, producto = partes
        proveedores[proveedor].append(f"{cantidad:g} x {producto} · {presentacion}")
    for proveedor, productos in proveedores.items():
        if productos:
            st.sidebar.markdown(f"**{proveedor}**")
        for producto in productos:
            st.sidebar.caption(producto)
            if st.sidebar.button("Quitar", key=f"quitar_pedido_{producto}"):
                pedido.pop(clave, None)
                st.rerun()
        if productos:
            st.sidebar.divider()

    if st.sidebar.button("🗑️ Vaciar pedido", key="vaciar_pedido_local"):
        pedido.clear()
        st.rerun()

    fecha = datetime.now().strftime("%d/%m/%Y")
    pdf = generar_pdf_pedido(pedido)
    st.sidebar.download_button(
        "Descargar PDF",
        data=pdf,
        file_name=f"pedido_lucense_{fecha}.pdf",
        mime="application/pdf",
        type="primary",
        key="descargar_pdf_local",
    )


def main() -> None:
    st.set_page_config(
        page_title="Pedidos Lucense · Pruebas locales",
        page_icon="🛒",
        layout="wide",
    )

    if "pedido" not in st.session_state:
        st.session_state.pedido = {}

    datos = cargar_proveedores()
    st.markdown("""
    <style>
        [class*="st-key-btn_menu"] button {
            min-height: 120px;
            font-size: 1.4rem;
            color: #000;
            border-radius: 12px;
        }
    </style>""", 
    unsafe_allow_html=True)
    col_ped, col_inv, col_dash = st.columns(3)
    with col_ped:
        btn_pedido = st.button("Hacer pedido", width="stretch", key="btn_menu_pedido", type="primary")
    with col_inv:
        btn_inventario = st.button("Gestionar inventario", width="stretch", key="btn_menu_inventario", type="primary")
    with col_dash:
        btn_dashboard = st.button("Ver estadísticas", width="stretch", key="btn_menu_dashboard", type="primary")
    

    if btn_pedido:
        render_pedido(datos)
        st.title("🛒 Hacer pedido")
        st.subheader("Buscar en el catálogo")
        render_busqueda(datos)

        st.divider()
        st.subheader("Catálogo por proveedor")
        for proveedor, datos_proveedor in datos.items():
            with st.expander(proveedor):
                telefonos = datos_proveedor.get("Teléfono", [])
                if isinstance(telefonos, list):
                    telefono = " · ".join(telefonos)
                else:
                    telefono = str(telefonos)
                st.caption(f"Teléfono: {telefono}")

                productos = datos_proveedor.get("Productos", {})
                if isinstance(productos, dict):
                    for producto, presentacion in productos.items():
                        render_producto(proveedor, producto, presentacion, "catalogo")
                        st.divider()

    elif btn_inventario:
        st.title("📦 Inventario")
        st.info("Esta sección todavía está en construcción en la aplicación desplegada.")

    elif btn_dashboard:
        st.title("📊 Estadísticas")
        st.info("Esta sección todavía está en construcción en la aplicación desplegada.")

    if mensaje := st.session_state.pop("mensaje_local", None):
        st.toast(mensaje)


if __name__ == "__main__":
    main()
