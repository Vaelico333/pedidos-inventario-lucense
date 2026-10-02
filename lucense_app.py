import streamlit as st
from firestore_client import get_db
import hashlib

st.set_page_config(page_title="Inventario", layout="wide")
db = get_db()

# --- Autenticación simple ---
if "user" not in st.session_state:
    st.subheader("Iniciar sesión")
    email = st.text_input("Email")
    password = st.text_input("Contraseña", type="password")
    
    if st.button("Entrar"):
        # Verificar en Firestore (colección "users")
        doc = db.collection("users").document(email).get()
        if doc.exists and doc["password_hash"] == hashlib.sha256(password.encode()).hexdigest():
            st.session_state.user = doc["name"]
            st.success(f"Bienvenido, {doc['name']}")
        else:
            st.error("Credenciales inválidas")
else:
    st.subheader(f"📦 Inventario — {st.session_state.user}")
    
    # CRUD de productos
    nombre = st.text_input("Nombre producto")
    cantidad = st.number_input("Cantidad", min_value=0)
    
    if st.button("Agregar"):
        doc_ref = db.collection("productos").document()
        doc_ref.set({"nombre": nombre, "cantidad": cantidad, "usuario": st.session_state.user})
        st.success("Producto agregado")
    
    # Listar
    st.write("### Productos")
    for doc in db.collection("productos").stream():
        st.write(f"- {doc['nombre']}: {doc['cantidad']} unidades")
    
    if st.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()   