from typing import Any
import streamlit as st
from servicios.creador_pdf import generar_pdf_pedido
from datetime import datetime



def llamada_agregar_producto(prov: str, producto: str, presentacion: str):

    cant_prod: float = st.session_state.get(f"cantidad_{prov}_{producto}", 0)
    id_item = f'{prov} - {presentacion} - {producto}'

    cantidad_final = st.session_state.pedido.get(id_item, 0) + cant_prod
    if cantidad_final > 0:
        st.session_state.pedido[id_item] = st.session_state.pedido.get(id_item, 0) + cant_prod
        st.toast(f'{prov}: {cant_prod} x {producto} añadido al pedido', icon="➕")
    elif cantidad_final == 0:
        if id_item in st.session_state.pedido:
            st.session_state.pedido.pop(id_item)
            st.toast(f'{producto} de {prov} retirado de la lista por tener 0 unidades', icon="🗑️")
    else:
        st.warning("No se puede pedir menos de 0 productos")
    st.rerun(scope="render_resumen_pedido")


@st.fragment(key="pedidos")
def pagina_pedidos(datos: dict[str, dict[str, dict[str, str] | str] | list[str] | str]):

    from servicios.mods import render_bloque_proveedor, busqueda
    from servicios.sidebar import barra_pedidos

    st.set_page_config(page_title="Pedidos - Inventario Lucense",
    page_icon="img/LOGO-LUCENSE_COMPLETO.webp",
    layout="wide",
    menu_items={'Get Help':'darzorgal@gmail.com'})
    prov = list(datos.keys())
    barra_pedidos(prov)
    col_titulo, col_buscar = st.columns(2)
    with col_titulo:
        st.title("🛒 Hacer pedido")
    with col_buscar:
        col_input, col_btn = st.columns(2, vertical_alignment="center")
        with col_input:
            buscar = st.text_input(label="", placeholder="Introduce un producto", key="texto-buscar")
        with col_btn:
            btn_buscar = st.button("🔎 Buscar", key="btn-buscar")
    if btn_buscar:
        encontrado = 0
        for prov, cats in datos.items():
            for cat, info in cats.items():
                if isinstance(info, dict):
                    for prod, pres in info.items():
                        if buscar.lower() in prod.lower():
                            encontrado += 1
                            busqueda(prov, prod, pres)
        if not encontrado:
            st.warning('Producto no encontrado')
        else:
            st.warning(f'Encontrados {encontrado} productos.')
    for prov in datos.keys():
        with st.expander(prov, key=f'expander_{prov}'):
            render_bloque_proveedor(prov, datos[prov])

