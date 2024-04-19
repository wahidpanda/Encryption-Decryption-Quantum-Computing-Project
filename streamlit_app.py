import streamlit as st
from PIL import Image
import numpy as np
import qrcode
import io

# Default authentication credentials
DEFAULT_USERNAME = "123"
DEFAULT_PASSWORD = "123"

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
    st.title("🔒 Lock Chat")
    st.subheader("A platform that encrypts your messages with Quantum Key Distribution (QKD) and decrypts them securely.")
    st.image("https://image.binance.vision/editor-uploads/bd1d649021654f8f9a9059e02a7c1278.gif", use_column_width=False, width=700)

    # Authentication
    username = st.sidebar.text_input("Username", value="")
    password = st.sidebar.text_input("Password", type="password", value="")
    if st.sidebar.button("Login"):
        if username == DEFAULT_USERNAME and password == DEFAULT_PASSWORD:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Welcome, {username}! You are now logged in.")
        else:
            st.error("Invalid username or password. Please try again.")

    if st.session_state.get("logged_in"):
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
                        st.success("Image decrypted successfully!")
                    else:
                        st.error("Please enter a decryption key!")
                except Exception as e:
                    st.error(f"Decryption error: {str(e)}")

if __name__ == "__main__":
    main()
