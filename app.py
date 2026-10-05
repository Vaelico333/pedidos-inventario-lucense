import streamlit as st
from firestore_client import get_db
from auth import login_user, register_user, hash_password
from pedidos import PaginaPedidos as pp
import json

def main():
    st.set_page_config(page_title="Pedidos e Inventario Lucense", 
                    layout="wide",
                    page_icon="./LOGO-LUCENSE_COMPLETO.webp")

    if "db" not in st.session_state:
        st.session_state.db = get_db()
    db = st.session_state.db
    db.collection("users").document("darzorgal@gmail.com").update({
    "role": "admin"})
    if 'pedido' not in st.session_state:
        st.session_state.pedido = {}

    col_titulo, col_user = st.columns([4,1])
    with col_titulo:
        st.title("Aplicación de inventario del bar Lucense")

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
                users = list(db.collection("users").stream())
                if not users:
                    st.info("No hay usuarios")
                for u in users:
                    data = u.to_dict()
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
                new_name = c1.text_input("Nombre")
                new_email = c2.text_input("Email")
                new_role = c3.selectbox("Rol", ["user", "admin"])
                new_pass = st.text_input("Contraseña", type="password")

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
                role_email = st.text_input("Email del usuario")
                new_role = st.selectbox("Nuevo rol", ["user", "admin"])
                if st.button("Actualizar rol"):
                    ref = db.collection("users").document(role_email)
                    if ref.get().exists:
                        ref.update({"role": new_role})
                        st.success(f"Rol de {role_email} → {new_role}")
                    else:
                        st.error("Usuario no encontrado")

                st.divider()
    st.divider()
    if "user" in st.session_state:
        boton_pedidos = st.menu_button("📝 Menú", 
                                    ["Escribir un pedido", 
                                        "Acceder al inventario", 
                                        "Ver estadísticas"],
                                        key="boton_menu", 
                                        width="content")
        
        with open("./proveedores.json", encoding="utf-8") as f:
            proveedores = json.load(f)

        if boton_pedidos == "Escribir un pedido":
            st.title("🛒 Hacer pedido")
            pp.render_resumen_pedido()

            for prov in proveedores.keys():
                with st.expander(prov, key=f'expander_{prov}'):
                    pp.render_bloque_proveedor(prov, proveedores[prov])

        elif boton_pedidos == "Acceder al inventario":
            st.title("⚠️ En construcción 📦")

        elif boton_pedidos == "Ver estadísticas":
            st.title("⚠️ En construcción 📊")

if __name__ == '__main__':
    main()