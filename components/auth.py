import streamlit as st
import hashlib
from components.database import get_user, create_user

def hash_text(text):
    return hashlib.sha256(text.encode()).hexdigest()

def render_auth_page():
    tabs = st.tabs(["Login", "Register"])

    with tabs[0]:
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            hashed_password = hash_text(password)
            user = get_user(username)
            if user and user["password"] == hashed_password:
                st.success("Login berhasil!")
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["current_menu"] = "Akun Saya"
                st.rerun()
            else:
                st.error("Username atau password salah.")

    with tabs[1]:
        st.subheader("Register Akun Baru")
        new_user = st.text_input("Buat Username Baru")
        new_pass = st.text_input("Buat Password Baru", type="password")
        confirm_pass = st.text_input("Konfirmasi Password Baru", type="password")

        if st.button("Daftar"):
            if new_pass != confirm_pass:
                st.error("Password tidak cocok.")
            else:
                try:
                    create_user(new_user, hash_text(new_pass))
                    st.success("Akun berhasil dibuat! Silakan login.")
                except Exception as e:
                    st.error(f"Error: {e}")
