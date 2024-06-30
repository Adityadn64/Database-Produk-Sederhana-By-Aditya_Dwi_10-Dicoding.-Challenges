import streamlit as st
import json
import time
import pandas as pd
import numpy as np
import cv2
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from PIL import Image
from streamlit_cookies_controller import CookieController

# Set page configuration
st.set_page_config(page_title="Database Produk Sederhana", layout="wide", page_icon="logo.png")

# Header HTML
st.markdown("""
<head>
    <meta name="dicoding:email" content="adityadwinugraha.2021@gmail.com">
</head>
""", unsafe_allow_html=True)

# Function to load data from JSON
def load_database():
    with open('data.json', 'r') as f:
        data = json.load(f)
    return data

# Function to save data to JSON
def save_database(data):
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)

# Load the product data
data = load_database()

def ceda():
    global data
    updated_data = {}
    for tuple_product in data.items():
        product_name = tuple_product[0]
        product_info = tuple_product[1]

        # Check if product name is a tuple
        if isinstance(product_name, tuple):
            product_name = product_name[0]  # Access the actual product name
        
        # Capitalize the product name (if needed)
        product_name = ' '.join(word.capitalize() for word in product_name.split())
        
        # Remove leading and trailing whitespaces
        product_name = product_name.strip()

        # Check if info is empty, fill with default values if True
        if not product_info or not isinstance(product_info.get("quantity"), (int, float)):
            product_info["quantity"] = 0

        if not isinstance(product_info.get("price"), (int, float)):
            product_info["price"] = 0

        updated_data[product_name] = product_info
    
    # Sort data by product name
    sorted_data = dict(sorted(updated_data.items(), key=lambda x: x[0]))

    return sorted_data

data = ceda()

# Save the updated data back to the file
save_database(data)

# Sort the product data by product name
data = dict(sorted(data.items()))

# Title of the page
st.title("Database Produk Sederhana")

with open('Auth/config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
)

# Create instance of CookieController
controller = CookieController()

# Function to authenticate user
def authenticate(username, password):
    if username in config['credentials']['usernames']:
        if config['credentials']['usernames'][username]['password'] == password:
            return True
    return False

# Login form
if not st.session_state["authentication_status"]:
    tab1, tab2 = st.tabs(["Username/Password", "Verification Face"])

    with tab1: authenticator.login()
    with tab2:
        img_file_buffer = st.camera_input(label="Camera")

        from Auth.weight import *
        
        # Muat deskripsi wajah yang dikenal
        known_face_descriptor = np.load(my_face)

        # Fungsi untuk mendeteksi dan memverifikasi wajah
        def verify_face(image, known_face_descriptor):
            # Konversi gambar ke grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = detector(gray)

            for face in faces:
                # Prediksi landmark wajah
                shape = predictor(gray, face)
                # Dapatkan deskripsi wajah
                face_descriptor = face_rec.compute_face_descriptor(image, shape)
                face_descriptor = np.array(face_descriptor)

                # Hitung jarak antara wajah yang dikenali dengan wajah saat ini
                distance = np.linalg.norm(known_face_descriptor - face_descriptor)

                if distance < 0.5:  # Threshold untuk verifikasi wajah
                    return "Wajah dikenali, akses diberikan!", True
                else:
                    return "Wajah tidak dikenali, akses ditolak.", False

            return "Tidak ada wajah terdeteksi.", None
        
        if img_file_buffer is not None:
            # Baca gambar yang diunggah
            img = Image.open(img_file_buffer)
            img_array = np.array(img)

            # Proses gambar untuk verifikasi wajah
            result, conditions = verify_face(img_array, known_face_descriptor)
            
            if conditions:
                st.success(result)
                st.session_state["authentication_status"] = True
                st.session_state["username"] = "sitisaudah"
                st.session_state["name"] = config['credentials']['usernames']['sitisaudah']["name"]
                
                # Set cookie upon successful login
                controller.set("authentication_status", True)
                controller.set("username", "sitisaudah")
                controller.set("name", st.session_state["name"])

                st.rerun()
                
            else:
                st.error(result)

    if st.session_state["authentication_status"] is False:
        st.error('Username/password is incorrect')

    elif st.session_state["authentication_status"] is None:
        st.warning('Please enter your username and password')

# Only show app content if logged in
if st.session_state["authentication_status"]:
    st.write(f'Welcome *{st.session_state["name"]}*')
    
    # Add item function
    def add_item():
        new_name = st.text_input("Nama Produk", key="new_name")
        new_quantity = st.number_input("Quantity", min_value=0, key="new_quantity")
        new_harga = st.number_input("Price", min_value=0, key="new_harga")
        if st.button("Tambah Produk"):
            if new_name:
                data[new_name] = {"quantity": new_quantity, "price": new_harga}
                save_database(data)
                st.success(f"{new_name} berhasil ditambahkan!")
            else:
                st.error("Nama produk tidak boleh kosong.")

    # Convert data to DataFrame
    def load_df():
        data = ceda()
        df = pd.DataFrame.from_dict(data, orient='index')
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'Produk', 'quantity': 'Quantity', 'price': 'Price'}, inplace=True)
        df['Total Price'] = df['Quantity'] * df['Price']
        return df

    df = load_df()
                    
    # Edit mode logic
    tab1, tab2, tab3 = st.tabs(["Preview", "Edit", "Advanced"])

    with tab1:
        # Display the DataFrame as a table
        df = load_df()
        total_keseluruhan_barang = df["Quantity"].sum()
        total_keseluruhan_harga = f"Rp {df['Total Price'].sum():,.0f}"
        
        df['Price'] = df['Price'].apply(lambda x: f"Rp {x:,}")
        df['Total Price'] = df['Total Price'].apply(lambda x: f"Rp {x:,}")
        
        st.dataframe(data=df, use_container_width=True)
        st.dataframe(data=pd.DataFrame({"Total Keseluruhan Barang": [total_keseluruhan_barang], "Total Keseluruhan Harga": [total_keseluruhan_harga]}), use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("Edit Produk")
        # Create edited dataframe without 'Total Price'
        edited_df = load_df()[['Produk', 'Quantity', 'Price']]

        # produk_search = st.selectbox("Pilih produk untuk dihapus", df['Produk'].tolist())
        # if produk_search in data:
        edited_df = st.data_editor(edited_df, num_rows="dynamic", use_container_width=True)

        if st.button("Update Semua"):
            updated_data = {}
            for index, row in edited_df.iterrows():
                updated_data[row['Produk']] = {"quantity": row['Quantity'], "price": row['Price']}
            save_database(updated_data)
            st.success("Semua data berhasil diperbarui!")
            data = load_database()
            df = load_df()
            
        st.dataframe(data=pd.DataFrame({"Total Keseluruhan Barang": [total_keseluruhan_barang], "Total Keseluruhan Harga": [total_keseluruhan_harga]}), use_container_width=True)
        # else:
        #     st.error("Produk tidak ditemukan.")

        # produk_search = st.selectbox("Pilih produk untuk dihapus", df['Produk'].tolist())
        # if produk_search in data:
        #     del data[produk_search]
        #     save_data(data)
        #     st.success(f"{produk_search} berhasil dihapus!")
        #     data = load_database()
        #     df = load_df()
        # else:
        #     st.error("Produk tidak ditemukan.")

    # Sticky CSS for buttons

    with tab3:
        file_path = 'data.json'

        # Download button
        if st.button("Backup Database"):
            file_name=f"Database_{time.strftime('%Y-%m-%d_%H-%M-%S')}.json"
            st.download_button(label="Download Database", data=open(file_path, 'rb').read(), file_name=file_name)
            st.info(f"File name: {file_name}")

        # Function to check if JSON structure matches expected structure
        def check_json_structure(data):
            for key, value in data.items():
                if not isinstance(value, dict):
                    st.error(f"Expected dictionary for key '{key}', got '{type(value).__name__}'")
                    return False
                
                if 'quantity' not in value or 'price' not in value:
                    st.error(f"Missing 'quantity' or 'price' in '{key}'")
                    return False
                
                if not isinstance(value['quantity'], (int, float)):
                    st.error(f"Expected 'quantity' to be integer or float in '{key}'")
                    return False
                
                if not isinstance(value['price'], (int, float)):
                    st.error(f"Expected 'price' to be integer or float in '{key}'")
                    return False
                
            return True

        # Function to restore database from uploaded file
        def restore_database(uploaded_file):
            content = uploaded_file.getvalue()
            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                st.error("File yang diunggah bukan berkas JSON yang valid.")
                return None
            
            if not check_json_structure(data):
                st.error("Struktur JSON tidak sesuai dengan yang diharapkan.")
                return None
            
            return data

        # Function to save data to JSON file
        def save_data(data, file_path):
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
                
        # File upload for restoring database
        uploaded_file = st.file_uploader("Upload JSON file to restore database", type=["json"])

        if uploaded_file is not None:
            if st.button("Restore Database"):
                restored_data = restore_database(uploaded_file)
                if restored_data:
                    st.success("Database berhasil dipulihkan dari file yang diunggah.")
                    save_data(restored_data, 'data.json')
                else:
                    st.error("Gagal memulihkan database.")
                    
        authenticator.logout()

    st.markdown("""
    <style>
    #save_btn, #edit_btn {
        position: -webkit-sticky;
        position: sticky;
        top: 0;
        z-index: 1;
    }
    </style>
    """, unsafe_allow_html=True)
