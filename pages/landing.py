import streamlit as st

st.set_page_config(page_title="Inicio - Inventario Lucense",
page_icon="img/LOGO-LUCENSE_COMPLETO.webp",
layout="wide",
menu_items={'Get Help':'darzorgal@gmail.com'})

st.markdown("""
    <style>
        class*="st-key-botones_menu" {
            min-height: 80px;
            font-size: 1.4rem;
            border-radius: 12px;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Bienvenido a la app de gestión de inventario de Lucense")
with st.container(key="botones_menu", horizontal=True):
    col_ped, col_inv, col_dash = st.columns(3)
    with col_ped:
        btn_pedido = st.button("Hacer pedido", width="stretch", key="btn_menu_pedido", type="primary")
    with col_inv:
        btn_inventario = st.button("Gestionar inventario", width="stretch", key="btn_menu_inventario", type="primary")
    with col_dash:
        btn_dashboard = st.button("Ver estadísticas", width="stretch", key="btn_menu_dashboard", type="primary")

if btn_pedido:
    st.switch_page("pages/pedidos.py")
elif btn_inventario:
    st.switch_page("pages/inventario.py")
elif btn_dashboard:
    st.switch_page("pages/inventario")