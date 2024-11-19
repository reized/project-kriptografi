import streamlit as st
from streamlit_option_menu import option_menu
from components import auth, pages
from components.database import init_db

init_db()

st.title("Aplikasi Keamanan Soal")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if st.session_state["logged_in"]:
    st.sidebar.header(f"Selamat datang, {st.session_state['username']}!")

    with st.sidebar:
        menu = option_menu(
            menu_title="Menu",
            options=["Dashboard", "Input Soal", "Lihat Soal"],
            default_index=0,
        )

    if st.sidebar.button("Logout"):
        st.session_state["logged_in"] = False
        del st.session_state["username"]
        st.rerun()

    if menu == "Dashboard":
        pages.render_dashboard()
    elif menu == "Input Soal":
        pages.render_input_page()
    elif menu == "Lihat Soal":
        pages.render_view_page()
else:
    st.sidebar.info("Silakan login untuk mengakses fitur.")
    auth.render_auth_page()