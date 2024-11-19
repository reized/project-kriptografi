import streamlit as st
import base64
import io
import zipfile
from hashlib import sha256
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.fernet import Fernet
from stegano import lsb
from PIL import Image
from components.database import save_encrypted_text

def caesar_encrypt(text, shift):
    encrypted = ''.join(
        chr((ord(char) - 32 + shift) % 95 + 32) if 32 <= ord(char) <= 126 else char
        for char in text
    )
    return encrypted

def caesar_decrypt(text, shift):
    decrypted = ''.join(
        chr((ord(char) - 32 - shift) % 95 + 32) if 32 <= ord(char) <= 126 else char
        for char in text
    )
    return decrypted

def generate_rsa_keys():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_key, public_key, private_pem, public_pem

def rsa_encrypt(public_key, data):
    return public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def rsa_decrypt(private_key, encrypted_data):
    return private_key.decrypt(
        encrypted_data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def render_text_encryption():
    text = st.text_area("Masukkan teks:")
    shift = st.number_input("Shift (Caesar Cipher):", min_value=0, max_value=25, value=3, key="caesar_enc")
    aes_key = st.text_input("Masukkan kunci AES (16/24/32 karakter):", type="password", key="aes_enc")
    
    if st.button("Enkripsi Teks"):
        if text:
            if aes_key and len(aes_key) in (16, 24, 32):
                cipher = Fernet(base64.urlsafe_b64encode(sha256(aes_key.encode()).digest()))
                encrypted1 = caesar_encrypt(text, shift)
                encrypted2 = cipher.encrypt(encrypted1.encode())
                save_encrypted_text(encrypted2)
                st.success(f"Teks dengan Super Enkripsi Caesar Cipher dan AES: {encrypted2.decode()}")
            else:
                st.error("Masukkan kunci AES yang valid!")
        else:
            st.error("Masukkan teks terlebih dahulu!")

def render_text_decryption():
    encrypted_text = st.text_area("Masukkan teks terenkripsi:")
    shift = st.number_input("Geser (Caesar Cipher):", min_value=0, max_value=25, value=3, key="caesar_dec")
    aes_key = st.text_input("Masukkan kunci AES (16/24/32 karakter):", type="password", key="aes_dec")

    if st.button("Dekripsi Teks"):
        if encrypted_text:
            if aes_key and len(aes_key) in (16, 24, 32):
                try:
                    cipher = Fernet(base64.urlsafe_b64encode(sha256(aes_key.encode()).digest()))
                    decrypted1 = cipher.decrypt(encrypted_text.encode()).decode()
                    decrypted2 = caesar_decrypt(decrypted1, shift)
                    st.success(f"Teks setelah dekripsi Enkripsi Caesar Cipher dan AES: {decrypted2}")
                except Exception as e:
                    st.error(f"Kesalahan: {str(e)}")
            else:
                st.error("Masukkan kunci AES yang valid!")
        else:
            st.error("Masukkan teks terenkripsi terlebih dahulu!")

def render_image_encryption():
    uploaded_image = st.file_uploader("Unggah Gambar", type=["png"], key="img_enc")
    text = st.text_area("Masukkan teks yang ingin disembunyikan:")
    encryption_key = st.text_input("Masukkan kunci enkripsi untuk teks:", type="password", key="key_enc")

    if st.button("Enkripsi Gambar"):
        if uploaded_image and text and encryption_key:
            try:
                cipher = Fernet(base64.urlsafe_b64encode(sha256(encryption_key.encode()).digest()))
                encrypted_text = cipher.encrypt(text.encode()).decode()

                image = Image.open(uploaded_image)
                encrypted_image = lsb.hide(image, encrypted_text)
                file_name=f"encrypted_{uploaded_image.name}"

                st.success(f"Gambar berhasil dienkripsi sebagai {file_name}!")

                buffer = io.BytesIO()
                encrypted_image.save(buffer, format="PNG")
                buffer.seek(0)

                st.download_button(
                    label="Unduh Gambar Terenkripsi",
                    data=buffer,
                    file_name=file_name,
                    mime="image/png"
                )
            except Exception as e:
                st.error(f"Kesalahan saat mengenkripsi gambar: {str(e)}")
        else:
            st.error("Pastikan semua input diisi dengan benar!")

def render_image_decryption():
    uploaded_image = st.file_uploader("Unggah Gambar Terenkripsi", type=["png"], key="img_dec")
    decryption_key = st.text_input("Masukkan kunci untuk mendekripsi teks:", type="password", key="key_dec")

    if st.button("Dekripsi Gambar"):
        if uploaded_image and decryption_key:
            try:
                image = Image.open(uploaded_image)
                encrypted_text = lsb.reveal(image)

                if encrypted_text:
                    cipher = Fernet(base64.urlsafe_b64encode(sha256(decryption_key.encode()).digest()))
                    decrypted_text = cipher.decrypt(encrypted_text.encode()).decode()
                    st.success(f"Teks Tersembunyi: {decrypted_text}")
                else:
                    st.warning("Gambar tidak memiliki teks tersembunyi.")
            except Exception as e:
                st.error(f"Terjadi kesalahan saat mendekripsi gambar: {str(e)}")
        else:
            st.error("Unggah gambar terenkripsi dan masukkan kunci terlebih dahulu!")

def render_file_encryption():
    uploaded_file = st.file_uploader("Unggah File", type=["pdf", "docx", "txt"], key="file_enc")
    if st.button("Enkripsi File"):
        if uploaded_file:
            private_key, public_key, private_pem, public_pem = generate_rsa_keys()

            file_data = uploaded_file.read()
            encrypted_file = rsa_encrypt(public_key, file_data)
            file_name = f"encrypted_{uploaded_file.name}.enc"

            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.writestr(file_name, encrypted_file)
                zip_file.writestr("private_key.pem", private_pem)

            zip_buffer.seek(0)

            st.success(f"File berhasil dienkripsi sebagai {file_name}!")

            st.download_button(
                label="Unduh File Terenkripsi dan Kunci Privat",
                data=zip_buffer,
                file_name="encrypted_files.zip",
                mime="application/zip"
            )

def render_file_decryption():
    uploaded_file = st.file_uploader("Unggah File Terenkripsi", type=["enc"], key="file_dec")
    private_key_file = st.file_uploader("Unggah Kunci Privat RSA (format .pem)", type=["pem"], key="private_key_file")

    if st.button("Dekripsi File"):
        if uploaded_file and private_key_file:
            try:
                private_key_pem = private_key_file.read()
                private_key = serialization.load_pem_private_key(
                    private_key_pem,
                    password=None
                )
                encrypted_data = uploaded_file.read()
                
                decrypted_file = rsa_decrypt(private_key, encrypted_data)
                original_name = uploaded_file.name.replace(".enc", "")

                st.success(f"File berhasil didekripsi sebagai {original_name}!")

                st.download_button(
                    label="Unduh File Didekripsi",
                    data=decrypted_file,
                    file_name=original_name,
                    mime="application/octet-stream"
                )
            except Exception as e:
                st.error(f"Kesalahan: {str(e)}")
        else:
            st.error("Unggah file terenkripsi dan file kunci privat RSA!")