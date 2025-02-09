import os
from tkinter import messagebox

import bcrypt
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.serialization import NoEncryption
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Global variable to store logs
log_str = ""


def hash_password_bcrypt(password):
    # Hashes a password using bcrypt, returns bcrypt hash
    salt = bcrypt.gensalt()  # Generate a salt to make more unique
    hashed = bcrypt.hashpw(password.encode(), salt)  # result of hash
    return hashed


def verify_password_bcrypt(password, hashed):
    # Verifies a password against a given bcrypt hash, gets password as str from GUI and hashed from DB to compare, return bool
    return bcrypt.checkpw(password.encode(), hashed)


def generate_rsa_key_pair():
    # generate public and private RSA keys
    private_key = rsa.generate_private_key(
        public_exponent=65537,  # standard prime integer for rsa
        key_size=2048,
        backend=default_backend()
    )

    # Serialize private key
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption()  # not using passphrase
    )

    # Serialize public key
    public_key = private_key.public_key()
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_key_pem, public_key_pem


def load_public_key(public_key_pem: bytes):
    if isinstance(public_key_pem, tuple):  # Ensure it's not a tuple
        public_key_pem = public_key_pem[0]
    if isinstance(public_key_pem, str):  # Convert string to bytes
        public_key_pem = public_key_pem.encode('utf-8')
    try:
        return serialization.load_pem_public_key(public_key_pem, backend=default_backend())
    except Exception as e:
        # Display the message box instead of raising an error
        messagebox.showerror(
            title="Error",
            message="Cannot send message to unregistered phone number."
        )
        return None


def load_private_key(user_phone: int):  # load private key from local storge
    global log_str
    filename = f"private_keys/{user_phone}_private_key.pem.enc"
    with open(filename, "rb") as f:
        encrypted_private_key = f.read()
        str = f"\033[1mLoaded private key:\033[0m\n{encrypted_private_key} and this type is {type(encrypted_private_key)}.\n"
        print(str)
        log_str += str + "\n"
    return encrypted_private_key


def save_private_key(encrypted_private_key, user_phone):
    # This method saves the private key to safe file.

    directory = "private_keys"  # define the directory path

    # Create the directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)

    filename = f"private_keys/{user_phone}_private_key.pem.enc"
    with open(filename, "wb") as f:
        f.write(encrypted_private_key)


def rsa_encrypt_aes_key(aes_key, recipient_public_key_pem):  # encrypting the aes with rsa
    try:
        recipient_public_key = load_public_key(recipient_public_key_pem)
        enc_aes_key = recipient_public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return enc_aes_key
    except Exception as e:
        return None


def rsa_decrypt_aes_key(enc_aes_key: bytes, recipient_phone):
    # load enc private key from file
    recipient_private_key = load_private_key(recipient_phone)
    try:
        # load the private key
        private_key = serialization.load_pem_private_key(
            recipient_private_key,
            password=None,
            backend=default_backend()
        )

        #  decrypt the aes key using private key
        aes_key = private_key.decrypt(
            enc_aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return aes_key

    except Exception as e:
        raise ValueError(f"Error decrypting AES key: {e}")


def encrypt_message_with_aes(aes_key, plaintext):
    # gets aes key and plaintext to encrypt and store later
    if isinstance(plaintext, str):  # Convert string to bytes if necessary
        plaintext = plaintext.encode('utf-8')

    aesgcm = AESGCM(aes_key)
    nonce = os.urandom(12)  # 96 bit nonce
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    # AESGCM is appended tag to into ciphertext automatically
    return nonce, ciphertext


def decrypt_message_with_aes(aes_key, nonce, ciphertext):  # as it sounds
    aesgcm = AESGCM(aes_key)
    try:
        return aesgcm.decrypt(nonce, ciphertext, None)
    except Exception as e:
        raise ValueError(f"Decryption failed: {e}")
