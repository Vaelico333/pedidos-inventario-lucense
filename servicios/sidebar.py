import streamlit as st

def usuario_barra_lateral():
    "Crea el encabezamiento de la barra lateral adecuado para el usuario actual."
    from servicios.auth import hash_password
    user = st.session_state.user
    st.sidebar.header(f"Estás conectado como **{user['name']}**")
    st.sidebar.caption(f"Rol: {user['role']}")
    if st.sidebar.button("Cerrar sesión"):
        del st.session_state.user
        st.session_state.logged_in = False
        st.rerun()

    if user["role"] == "admin":
        admin_barra_lateral(user)

def admin_barra_lateral(user):
    "Crea el menú de gestión de usuarios de la barra lateral."
    db = st.session_state.db
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
            ref = db.collection("users").document(role_email)
            if ref.get().exists:
                ref.update({"role": new_role})
                st.success(f"Rol de {role_email} → {new_role}")
            else:
                st.error("Usuario no encontrado")

def barra_pedidos(proveedores: list):
    """
    Crea el encabezamiento apropiado para el usuario, y debajo despliega la lista
    de productos a incluir en el pedido y el botón para generar un PDF, 
    o un aviso de que la lista está vacía.
    """
    from servicios.creador_pdf import generar_pdf_pedido
    from datetime import datetime

    def llamada_borrar_producto(prov: str, producto: str) -> None:
        "Borra un producto de la lista de la barra lateral."
        id_item = f'{prov} - {producto}'
        if id_item in st.session_state.pedido:
            st.session_state.pedido.pop(id_item)
            st.toast(f'{producto} de {prov} retirado de la lista con éxito', icon="🗑️")
        st.rerun(scope="render_resumen_pedido")
    
    usuario_barra_lateral()

    st.sidebar.header("📋 Pedido Actual")
    if st.session_state.pedido:
        if st.sidebar.button("🗑️ Borrar lista"):
            st.session_state.pedido.clear()
        col_txt, col_borrar = st.columns([1,1])
        prov_dict: dict[str, list[str]] = dict.fromkeys(proveedores,[])
        for item, cantidad in list(st.session_state.pedido.items()):
            prov, pres, prod = item.split('-', 2)
            if prov in prov_dict.keys():
                prov_dict[prov].append(f"✅ **{cantidad}x** {pres} de {prod}")
                with col_txt:
                    for p in prov_dict.keys():
                        if prov_dict[p]:
                            st.title(p) 
                            [st.markdown(i) for i in prov_dict[p]]
                with col_borrar:
                    st.sidebar.button("Borrar", key=f'btn_borrar_{prod}',on_click=llamada_borrar_producto, args=(prov, prod))
        st.sidebar.divider()
        datos_pdf = generar_pdf_pedido(st.session_state.pedido)
        fecha = datetime.now().strftime('%d/%m/%Y')
        st.sidebar.download_button("Generar PDF", data=datos_pdf, file_name=f"pedido_lucense_{fecha}.pdf", type="primary", key="btn_pdf", icon="📝")

    else:
        st.sidebar.info('Pedido vacío')    

def barra_inventario(db=None):
    """
    usuario_barra_lateral + 
    tabla con snapshot -> estado actual de inventario
    """
    usuario_barra_lateral()
    if db:
        # CRUD: extraer "saldo" de última snapshot, incluir fecha
        st.sidebar.header("📋 Inventario a fecha ")
    else:
        st.sidebar.header("No hay inventario")
    pass

def barra_dashboard():
    pass