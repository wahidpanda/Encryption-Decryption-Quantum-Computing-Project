import streamlit as st
from PIL import Image
import numpy as np
import cv2
import csv
import os  
import qrcode
import io

# Function to create a CSV file to store user credentials
def create_credentials_file():
    with open("user_credentials.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["username", "password"])

# Function to register a new user
def register_user(username, password):
    with open("user_credentials.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([username, password])
    st.success("Registration successful. Please log in.")

# Function to check if a user exists in the CSV file and if the password matches
def login_user(username, password):
    with open("user_credentials.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["username"] == username and row["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome, {username}! You are now logged in.")
                return True
    st.error("Invalid username or password. Please try again.")
    return False
# Function to perform BB84 key exchange
def bb84_key_exchange(length):
    alice_bits = np.random.randint(2, size=length)
    alice_bases = np.random.randint(2, size=length)
    bob_bases = np.random.randint(2, size=length)
    bob_results = [alice_bits[i] if alice_bases[i] == bob_bases[i] else np.random.randint(2) for i in range(length)]
    return alice_bits, alice_bases, bob_bases, bob_results

# Function to encrypt a message using the generated key
def encrypt_message(message, key):
    encrypted_message = ''.join(chr(ord(message[i]) ^ key[i % len(key)]) for i in range(len(message)))
    return encrypted_message

# Function to decrypt an encrypted message using the same key
def decrypt_message(encrypted_message, key):
    decrypted_message = ''.join(chr(ord(encrypted_message[i]) ^ key[i % len(key)]) for i in range(len(encrypted_message)))
    return decrypted_message

# Function to encrypt an image using the provided key
def encrypt_image(image, key):
    _, buffer = cv2.imencode('.png', image)
    image_data = buffer.tobytes()
    encrypted_image_data = bytearray()
    for i in range(len(image_data)):
        encrypted_byte = image_data[i] ^ key[i % len(key)]  # XOR operation with the key
        encrypted_image_data.append(encrypted_byte)
    return bytes(encrypted_image_data)

# Function to decrypt an encrypted image using the provided key
def decrypt_image(encrypted_image_data, key):
    decrypted_image_data = bytearray()
    for i in range(len(encrypted_image_data)):
        decrypted_byte = encrypted_image_data[i] ^ key[i % len(key)]  # XOR operation with the key
        decrypted_image_data.append(decrypted_byte)
    decrypted_image = cv2.imdecode(np.frombuffer(bytes(decrypted_image_data), np.uint8), 1)
    return decrypted_image

# Function to perform Quantum Key Distribution (QKD) and generate a key pair
def generate_qkd_key_pair(image_shape):
    key_length = image_shape[0] * image_shape[1] * 3  # Assuming RGB images
    sender_key = np.random.randint(256, size=key_length, dtype=np.uint8)
    receiver_key = np.random.randint(256, size=key_length, dtype=np.uint8)
    return sender_key, receiver_key

# Function to encrypt an image using QKD
def encrypt_image_qkd(image_data, qkd_key):
    encrypted_image_data = bytearray()
    for i in range(len(image_data)):
        encrypted_byte = image_data[i] ^ qkd_key[i % len(qkd_key)]  # XOR operation with QKD key
        encrypted_image_data.append(encrypted_byte)
    return bytes(encrypted_image_data)

# Function to decrypt an image using QKD
def decrypt_image_qkd(encrypted_image_data, qkd_key, image_shape):
    decrypted_image_data = bytearray()
    for i in range(len(encrypted_image_data)):
        decrypted_byte = encrypted_image_data[i] ^ qkd_key[i % len(qkd_key)]  # XOR operation with QKD key
        decrypted_image_data.append(decrypted_byte)
    return np.array(decrypted_image_data).reshape(image_shape)

# Function to generate a QR code for the shared key
def generate_qr_code(shared_key):
    qr = qrcode.QRCode(
        version=3,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=5,  # Adjust box size to make QR code smaller
        border=2,
    )
    qr.add_data(shared_key)
    qr.make(fit=True)
    img = qr.make_image(fill_color="green", back_color="white")
    return img

# Main function to run the application
def main():
   
    


    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.title("🔒 Lock Chat")
        st.subheader("A platform that encrypts your messages with Quantum Key Distribution (QKD) and decrypts them securely.")
        st.image("https://image.binance.vision/editor-uploads/bd1d649021654f8f9a9059e02a7c1278.gif", use_column_width=False, width=700)
        st.sidebar.title("Authentication")

        option = st.sidebar.radio("Choose an option", ("Login", "Register"))
        if option == "Register":
            new_username = st.sidebar.text_input("Username")
            new_password = st.sidebar.text_input("Password", type="password")
            if st.sidebar.button("Register"):
                # Implement registration logic
                register_user(new_username, new_password)
        elif option == "Login":
            username = st.sidebar.text_input("Username")
            password = st.sidebar.text_input("Password", type="password")
            if st.sidebar.button("Login"):
                # Implement login logic
                login_user(username, password)
                st.session_state.logged_in = True

    elif st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        

    if st.session_state.logged_in:
        st.sidebar.title("Navigation")
        navigation_option = st.sidebar.radio("Go to:", ("Secure Chat Interface", "Image Encryption and Decryption"))

        if navigation_option == "Secure Chat Interface":
            st.subheader("Secure Chat Interface")
            st.write(f"Welcome to the Secure Chat Interface, {st.session_state.username}!")

            message_to_send = st.text_area("Type your message here to send:")
            if st.button("Send Message"):
                st.success("Message sent successfully!")
                shared_key = bb84_key_exchange(len(message_to_send))[0]
                encrypted_message = encrypt_message(message_to_send, shared_key)

                # Generate QR code for the shared key
                qr_code_img = generate_qr_code(''.join(map(str, shared_key)))
                img_byte_arr = io.BytesIO()
                qr_code_img.save(img_byte_arr, format='PNG')
                st.image(img_byte_arr, caption="QR Code for Shared Key", use_column_width=True)

                st.session_state.message_sent = message_to_send
                st.session_state.shared_key = shared_key
                st.session_state.encrypted_message = encrypted_message
                st.session_state.encrypted_message_sent = True
            

            if "encrypted_message_sent" in st.session_state and st.session_state.encrypted_message_sent:
                st.write("Encrypted Message:", st.session_state.encrypted_message)
                st.write("Shared Key:", ''.join(map(str, st.session_state.shared_key)))

            # Decryption section
            encrypted_message_received = st.text_input("Enter the encrypted message received:")
            shared_key_received = st.text_input("Enter the shared key received:")
            if st.button("Decrypt Message"):
                encrypted_message_received = encrypted_message_received.strip()
                if encrypted_message_received:
                    decrypted_message = decrypt_message(encrypted_message_received, list(map(int, shared_key_received)))
                    st.write("Decrypted message:", decrypted_message)
                    st.success("Message decrypted successfully!")
                else:
                    st.error("Please enter a valid encrypted message.")

        elif navigation_option == "Image Encryption and Decryption":
            st.subheader("Image Encryption and Decryption")

            # Image encryption
            st.title("Secure Image Transfer ")

            uploaded_file = st.file_uploader("Upload an image to send", type=["jpg", "png", "jpeg"])
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                st.image(image, caption="Original Image", use_column_width=True)

                image_data = np.array(image)

                if st.button("Send Image"):
                    try:
                        sender_key, receiver_key = generate_qkd_key_pair(image_data.shape)
                        encrypted_image_data = encrypt_image_qkd(image_data.flatten(), sender_key)
                        st.success("Image uploaded and encrypted successfully!")
                        st.success("Encryption Key:")
                        st.text_area("Copy and Paste the Encryption Key", " ".join(map(str, sender_key)), height=100)
                    except Exception as e:
                        st.error(f"Encryption error: {str(e)}")

            decryption_key = st.text_input("Enter decryption key:")
            if st.button("Receive Image"):
                try:
                    image = Image.open(uploaded_file)
                    image_data = np.array(image)
                    if decryption_key:
                        decrypted_image_data = decrypt_image_qkd(image_data.flatten(), list(map(int, decryption_key.split())), image_data.shape)
                        decrypted_image = Image.fromarray(decrypted_image_data.astype(np.uint8))
                        st.image(decrypted_image, caption="Decrypted Image", use_column_width=True)
                        st.success("Image decrypted successfully!")
                    else:
                        st.error("Please enter a decryption key!")
                except Exception as e:
                    st.error(f"Decryption error: {str(e)}")

            

if __name__ == "__main__":
    main()
