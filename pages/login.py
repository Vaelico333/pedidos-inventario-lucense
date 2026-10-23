from google.cloud.firestore_v1.document import DocumentReference
from google.cloud.firestore_v1.base_document import DocumentSnapshot
import streamlit as st
from servicios.auth import login_user, hash_password
import json

def main():

    from pages.pedidos import pagina_pedidos
    st.set_page_config(page_title="Iniciar sesión - Inventario Lucense",
    page_icon="img/LOGO-LUCENSE_COMPLETO.webp",
    layout="wide",
    menu_items={'Get Help':'darzorgal@gmail.com'})
    
    st.set_page_config(page_title="Pedidos e Inventario Lucense", 
                    layout="wide",
                    page_icon="./img/LOGO-LUCENSE_COMPLETO.webp")

    # Creación en código de usuario admin: Imprescindible en primera compilación para que puedan crearse luego más usuarios.
    # db.collection("users").document("darzorgal@gmail.com").update({"role": "admin"}) -> creación manual de admin, descomentar si se necesita


    col_img, col_titulo, col_user = st.columns([1,3,1])
    with col_img:
        st.image("./img/LOGO-LUCENSE_COMPLETO.webp")
    with col_titulo:
        st.title("Aplicación de inventario del bar Lucense")

    # Usuario no autenticado
    if "user" not in st.session_state:
        with col_user:
            with st.expander("Acceder", key="btn-login"):
                login_user()
            # with st.expander("Registrarse", key="btn-reg"):
                # register_user()
            # Prefiero registrar mediante admin, para mejorar la seguridad
    # ──────────────────────────────────────────────
    #  APP PRINCIPAL (usuario autenticado)
    # ──────────────────────────────────────────────
    else:
        st.switch_page("pages/landing.py")

if __name__ == '__main__':
    main()
