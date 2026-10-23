import streamlit as st
from servicios.firestore_client import get_db

def main():

    # Carga de la base de datos
    if "db" not in st.session_state:
        st.session_state.db = get_db()
    db = st.session_state.db
    # Creación de item "logged_in" para comprobar fácilmente si el usuario está en sesión
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    # Creación de objeto "pedido" en memoria
    if 'pedido' not in st.session_state:
        st.session_state.pedido = {}

    login = st.Page("pages/login.py", title="Iniciar sesión - Lucense", url_path="login", default=True)
    inicio = st.Page("pages/landing.py", title="Inicio", url_path="", default=True)
    pedidos = st.Page("pages/pedidos.py", title="Pedidos - Lucense", url_path="pedidos")
    inventario = st.Page("pages/inventario.py", title="Inventario - Lucense", url_path="inventario")
    dashboard = st.Page("pages/dashboard.py", title="Estadísticas - Lucense", url_path="dashboard")

    if st.session_state.logged_in == False:
        pg = st.navigation([login])
    else:
        pg = st.navigation([
            inicio,
            pedidos,
            inventario,
            dashboard
        ])
    pg.run()

if __name__ == '__main__':
    main()
