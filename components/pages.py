import streamlit as st
import sqlite3
import pandas as pd
import components.crypto as crypto
from components.database import get_encrypted_text

def render_dashboard():
    st.subheader("Dashboard Aplikasi")
    conn = sqlite3.connect("database/database.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM questions")
    total_soal = cursor.fetchone()[0]
    
    col1, col2 = st.columns(2)
    col1.metric("Total Soal", total_soal)
    col2.metric("Soal Terakhir Diinput", "Lihat di menu Lihat Soal")
    
    st.info("Gunakan menu Input Soal untuk menambahkan soal baru dan menu Lihat Soal untuk melihat soal yang sudah ada.")

def render_input_page():
    if not st.session_state.get("logged_in", False):
        st.warning("Anda harus login untuk mengakses fitur ini.")
        return
    
    st.subheader("Input Soal Ujian")

    tabs = st.tabs(["Input Teks", "Input Gambar", "Input File"])

    with tabs[0]:
        st.header("Input Soal Teks")
        st.subheader("Enkripsi Soal")
        crypto.render_text_encryption()
        st.subheader("Dekripsi Soal")
        crypto.render_text_decryption()
    
    with tabs[1]:
        st.header("Input Soal Gambar")
        st.subheader("Enkripsi Gambar")
        crypto.render_image_encryption()
        st.subheader("Dekripsi Gambar")
        crypto.render_image_decryption()
    
    with tabs[2]:
        st.header("Input Soal File")
        st.subheader("Enkripsi File")
        crypto.render_file_encryption()
        st.subheader("Dekripsi File")
        crypto.render_file_decryption()

def render_view_page():
    if not st.session_state.get("logged_in", False):
        st.warning("Anda harus login untuk mengakses fitur ini.")
        return
    
    st.subheader("Lihat Soal Ujian")
    questions = get_encrypted_text()
    if questions:
        df = pd.DataFrame(questions)
        st.dataframe(df)
    else:
        st.warning("Tidak ada soal yang tersedia.")