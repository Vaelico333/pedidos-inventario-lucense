from google.cloud.firestore_v1.document import DocumentReference
from google.cloud.firestore_v1.base_document import DocumentSnapshot
import streamlit as st
from servicios.firestore_client import get_db
from servicios.auth import login_user, register_user, hash_password
import json
from google.cloud.firestore import Client

def main():

    from paginas.pedidos import PaginaPedidos as pp
    st.set_page_config(page_title="Pedidos e Inventario Lucense", 
                    layout="wide",
                    page_icon="./img/LOGO-LUCENSE_COMPLETO.webp")

    # Carga de la base de datos
    if "db" not in st.session_state:
        st.session_state.db = get_db()
    db: Client = st.session_state.db
    # db.collection("users").document("darzorgal@gmail.com").update({"role": "admin"}) -> creación manual de admin, descomentar si se necesita

    # Creación de objeto "pedido" en memoria
    if 'pedido' not in st.session_state:
        st.session_state.pedido = {}

    col_titulo, col_user = st.columns([3,1])
    with col_titulo:
        st.title("Aplicación de inventario del bar Lucense")

    # Usuario no autenticado
    if "user" not in st.session_state:
        with col_user:
            with st.expander("Acceder", key="btn-login"):
                login_user()
            with st.expander("Registrarse", key="btn-reg"):
                register_user()
    # ──────────────────────────────────────────────
    #  APP PRINCIPAL (usuario autenticado)
    # ──────────────────────────────────────────────
    else:
        user = st.session_state.user
        st.sidebar.header(f"👤 {user['name']}")
        st.sidebar.caption(f"Rol: {user['role']}")
        if st.sidebar.button("Cerrar sesión"):
            del st.session_state.user
            st.rerun()

        # ── PANEL ADMIN ──────────────────────────
        if user["role"] == "admin":
            st.sidebar.subheader("Admin")
            if st.sidebar.button("Gestionar usuarios"):
                st.session_state.show_admin = True
            else:
                st.session_state.show_admin = False

            if st.session_state.get("show_admin"):
                st.title("⚙️ Gestión de usuarios")

                # Listar usuarios
                st.subheader("Usuarios registrados")
                users: list[DocumentSnapshot] = list(db.collection("users").stream())
                if not users:
                    st.info("No hay usuarios")
                for u in users:
                    data: dict[str, str] = u.to_dict()
                    col1, col2, col3 = st.columns([3, 1, 1])
                    col1.write(f"**{data['name']}** — `{u.id}`")
                    col2.write(f"Rol: `{data.get('role', 'user')}`")
                    if u.id != user["email"]:  # no eliminarse a sí mismo
                        if col3.button("Eliminar", key=f"del_{u.id}"):
                            db.collection("users").document(u.id).delete()
                            st.success(f"Usuario {u.id} eliminado")
                            st.rerun()

                # Crear usuario manualmente
                st.divider()
                st.subheader("Crear usuario")
                c1, c2, c3 = st.columns(3)
                new_name: str = c1.text_input("Nombre")
                new_email: str = c2.text_input("Email")
                new_role = c3.selectbox("Rol", ["user", "admin"])
                new_pass: str = st.text_input("Contraseña", type="password")

                if st.button("Crear usuario"):
                    if not new_name or not new_email or not new_pass:
                        st.error("Completa todos los campos")
                    elif db.collection("users").document(new_email).get().exists:
                        st.error("Ese email ya existe")
                    else:
                        db.collection("users").document(new_email).set({
                            "name": new_name,
                            "password_hash": hash_password(new_pass),
                            "role": new_role
                        })
                        st.success("Usuario creado")

                # Cambiar rol
                st.divider()
                st.subheader("Cambiar rol")
                role_email: str = st.text_input("Email del usuario")
                new_role: str = st.selectbox("Nuevo rol", ["user", "admin"])
                if st.button("Actualizar rol"):
                    ref: DocumentReference = db.collection("users").document(role_email)
                    if ref.get().exists:
                        ref.update({"role": new_role})
                        st.success(f"Rol de {role_email} → {new_role}")
                    else:
                        st.error("Usuario no encontrado")

                st.divider()
    st.divider()
    if "user" in st.session_state:
        boton_menu: str | None = st.menu_button("📝 Menú", 
                                    ["Escribir un pedido", 
                                        "Acceder al inventario", 
                                        "Ver estadísticas"],
                                        key="boton_menu", 
                                        width="content")
        
        with open("./datos/datos_proveedores.json", encoding="utf-8") as f:
            proveedores: dict[str, dict[str, dict[str, str] | str] | list[str] | str] = json.load(f)

        if boton_menu == "Escribir un pedido":
            pp.pagina_pedidos(proveedores)

        elif boton_menu == "Acceder al inventario":
            st.title("⚠️ En construcción 📦")

        elif boton_menu == "Ver estadísticas":
            st.title("⚠️ En construcción 📊")

if __name__ == '__main__':
    main()
else:
    pass
