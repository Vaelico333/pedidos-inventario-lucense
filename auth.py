import bcrypt
import streamlit as st

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

def login_user():
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Contraseña", type="password", key="login_pass")
    db = st.session_state.db
    if st.button("Entrar"):
        doc = db.collection("users").document(email).get().to_dict()
        if doc.exists and check_password(password, doc["password_hash"]):
            st.session_state.user = {
                "email": email,
                "name": doc["name"],
                "role": doc.get("role", "user")
            }
            st.rerun()
        else:
            st.error("Credenciales inválidas")

def register_user():
    st.subheader("Crear cuenta")
    name = st.text_input("Nombre", key="reg_name")
    email = st.text_input("Email", key="reg_email")
    password = st.text_input("Contraseña", type="password", key="reg_pass")
    confirm = st.text_input("Confirmar contraseña", type="password", key="reg_confirm")
    db = st.session_state.db

    if st.button("Registrarse"):
        if password != confirm:
            st.error("Las contraseñas no coinciden")
        elif not name or not email or not password:
            st.error("Completa todos los campos")
        elif db.collection("users").document(email).get().exists:
            st.error("Ese email ya está registrado")
        else:
            db.collection("users").document(email).set({
                "name": name,
                "password_hash": hash_password(password),
                "role": "user"
            })
            st.success("Cuenta creada. Inicia sesión.")
