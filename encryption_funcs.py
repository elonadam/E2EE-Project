# import hashlib
# import secrets
import os
import bcrypt
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.serialization import BestAvailableEncryption, NoEncryption
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

"""
bcrypt.hashpw() takes a byte-string password and a salt (generated by bcrypt.gensalt())
 and returns a hashed password.
 
bcrypt.checkpw() verifies a plain-text password against a stored hash.

don't need to store the salt separately with bcrypt; it is embedded in the hash itself.

"""


def hash_password_bcrypt(password):
    """
    Hashes a password using bcrypt.

    Args:
        password (str): The plain-text password to hash.

    Returns:
        bytes: The bcrypt hash of the password.
    """
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    print(f"inside hash_pw func, salt is {salt}, hashed is {hashed}\n")
    return hashed


def verify_password_bcrypt(password, hashed):
    """
    Verifies a password against a given bcrypt hash.

    Args:
        password (str): The plain-text password to verify.
        hashed (bytes): The bcrypt hash to verify against.

    Returns:
        bool: True if the password matches the hash, False otherwise.
    """
    print(
        f"inside verify func, password is {password} hashed as param is {hashed} \n bcrypt computed: {bcrypt.checkpw(password.encode(), hashed)}")
    return bcrypt.checkpw(password.encode(), hashed)


def generate_rsa_key_pair(passphrase: bytes = None):  # we can delete param i think
    """
    Generate an RSA private/public key pair.

    :return: (private_key_pem, public_key_pem)
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    # Serialize private key TODO 3 if not using passprase delete this
    if passphrase:
        encryption_algo = BestAvailableEncryption(passphrase)
    else:
        encryption_algo = NoEncryption()

    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption_algo
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
        raise ValueError(f"Error loading public key: {e}")


def load_private_key(user_phone: int):
    filename = f"private_keys/{user_phone}_private_key.pem.enc"
    with open(filename, "rb") as f:
        encrypted_private_key = f.read()
        print(f"inside load prive key: loaded {encrypted_private_key} and this type is {type(encrypted_private_key)}")
    return encrypted_private_key


def save_private_key(encrypted_private_key: bytes, user_phone: int):
    """
    This method saves the private key to safe file.
    """
    # Define the directory path
    directory = "private_keys"

    # Create the directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)

    filename = f"private_keys/{user_phone}_private_key.pem.enc"
    with open(filename, "wb") as f:
        f.write(encrypted_private_key)


def rsa_encrypt_aes_key(aes_key: bytes, recipient_public_key_pem: bytes) -> bytes:
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


# def rsa_decrypt_aes_key(enc_aes_key: bytes, recipient_private_key_pem: bytes, passphrase: bytes = None) -> bytes:
def rsa_decrypt_aes_key(enc_aes_key: bytes, recipient_phone):
    # recipient_private_key = load_private_key(recipient_private_key_pem, passphrase)
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
    """
    Encrypt plaintext using AES-GCM.
    :return: (nonce, ciphertext)
    """
    if isinstance(plaintext, str):  # Convert string to bytes if necessary
        plaintext = plaintext.encode('utf-8')

    aesgcm = AESGCM(aes_key)
    nonce = os.urandom(12)  # 96-bit nonce
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    # AESGCM combines tag into the ciphertext internally, but you can separate if needed.
    # In AESGCM from cryptography, the tag is appended to the ciphertext automatically.
    return nonce, ciphertext


def decrypt_message_with_aes(aes_key: bytes, nonce: bytes, ciphertext: bytes) -> bytes:
    aesgcm = AESGCM(aes_key)
    try:
        return aesgcm.decrypt(nonce, ciphertext, None)
    except Exception as e:
        raise ValueError(f"Decryption failed: {e}")
