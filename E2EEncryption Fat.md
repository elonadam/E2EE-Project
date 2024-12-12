### **End-to-End Encrypted Messaging Protocol Using RSA and AES**

### **Components and Key Choices**

#### **1. Encryption Algorithms**

- **RSA-2048**:

  - **Purpose**: Used for secure key exchange.
  - **Why RSA-2048?**: Provides strong security against modern computational capabilities while balancing performance.
  - **Usage**: Encrypts AES session keys.

- **AES-256**:

  - **Purpose**: Used for encrypting message payloads.
  - **Why AES-256?**: Faster than RSA for large data encryption and provides strong security against brute-force attacks.
  - **Usage**: Encrypts the actual message content using a session key.

#### **3. Sockets and Data Transmission**

- **Purpose**: Sockets are used for real-time communication between the client and the server.
- **Implementation**:
  - Use **secure sockets (TLS)** to establish a secure channel for data transmission.
  - Ensure mutual authentication with certificates.

**Example of Socket Initialization:**
```python
import socket
import ssl

# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Wrap the socket with SSL/TLS
context = ssl.create_default_context()
wrapped_socket = context.wrap_socket(client_socket, server_hostname="example.com")

# Connect to the server
wrapped_socket.connect(("example.com", 443))

# Send data (e.g., the public key or encrypted message)
wrapped_socket.sendall(b"Hello, Secure Server!")

# Close the connection
wrapped_socket.close()
```

- **Temporary Data in RAM**: Any sensitive data, such session keys or decrypted messages, resides only in RAM during processing and is securely erased afterward.

---

### **Protocol Workflow**

#### **1. Registration Phase**

1. **Key Pair Generation (Client)**:

   - The client generates an RSA key pair.
   - Example Code:
     ```python
     from cryptography.hazmat.primitives.asymmetric import rsa
     from cryptography.hazmat.primitives import serialization

     def generate_rsa_keypair():
         private_key = rsa.generate_private_key(
             public_exponent=65537,
             key_size=2048
         )
         public_key = private_key.public_key()

         return {
             "private_key": private_key,
             "public_key": public_key
         }
     client_keys = generate_rsa_keypair()
     ```

2. **Public Key Transmission**:

   - The client sends its public key to the server over a **secure channel** (e.g., HTTPS).
   - The server stores the public key securely.


3. **Key Storage**:

- **Client-Side**:

  - **Client RSA Private Key**:
    - Stored in a **secure enclave or keychain** (e.g., Android Keystore, iOS Keychain).
    - If hardware-backed storage isn’t available, it is encrypted with AES-256 using a strong user-derived password.
    - **Code Example for Secure Storage**:
      ```python
      from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
      from cryptography.hazmat.primitives import hashes
      from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
      import os

      def encrypt_private_key(private_key_pem, password):
          salt = os.urandom(16)
          kdf = PBKDF2HMAC(
              algorithm=hashes.SHA256(),
              length=32,
              salt=salt,
              iterations=100000
          )
          encryption_key = kdf.derive(password.encode())
          cipher = Cipher(algorithms.AES(encryption_key), modes.CFB(os.urandom(16)))
          encryptor = cipher.encryptor()
          encrypted_private_key = encryptor.update(private_key_pem) + encryptor.finalize()
          return salt, encrypted_private_key
      ```

      - **Secure Enclave/Keychain**: Directly generate and store keys using platform APIs, ensuring the private key is non-exportable (e.g., Android Keystore).

  - **Server RSA Public Key**:
    - Embedded in the client application during deployment.
    - Validated using signatures or fingerprints to prevent tampering.
    - Stored in a read-only section of the application’s configuration or hardcoded within the app binary.

- **Server-Side**:

  - **Server RSA Private Key**:
    - Stored in a **Hardware Security Module (HSM)** or a **Key Management System (KMS)**.
    - Example Code for Storage in an Encrypted File:
      ```python
      def store_private_key_securely(private_key_pem, file_path, password):
          salt, encrypted_key = encrypt_private_key(private_key_pem, password)
          with open(file_path, "wb") as key_file:
              key_file.write(salt + encrypted_key)
      ```
      - HSMs ensure tamper-proof hardware storage and provide cryptographic operations without exporting private keys.
      - If HSMs are unavailable, the private key is stored in an encrypted file (e.g., using AES-256) with strict file system permissions limiting access to authorized processes.
      - The private key is regularly rotated and backed up in a secure, offline location.

  - **Client RSA Public Keys**:
    - Stored in the server database with proper access controls.
    - Example Storage:
      - Each client’s public key is stored in a table indexed by a unique client ID.
      - The database is encrypted at rest using a server-managed encryption key.

  - **AES Session Keys**:
    - Ephemeral session keys are generated for each message or session.
    - Stored only in memory (RAM) during the session’s lifetime and securely erased after use.
    - Code to Securely Erase:
      ```python
      import ctypes
      import os

      def secure_erase(key):
          length = len(key)
          offset = ctypes.addressof(ctypes.create_string_buffer(key))
          ctypes.memset(offset, 0, length)
      ```

#### **2. Message Exchange Phase**

##### **Sending a Message (Client)**

1. **Generate AES-256 Session Key**:

   - A random AES key is generated for encrypting the message.
   - Example Code:
     ```python
     import os
     def generate_aes_key():
         return os.urandom(32)  # 256-bit key
     aes_key = generate_aes_key()
     ```

2. **Encrypt the Message**:

   - The message is encrypted using AES-256 in CBC mode with a random IV.
   - Example Code:
     ```python
     from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
     from cryptography.hazmat.primitives import padding

     def aes_encrypt(message, aes_key):
         iv = os.urandom(16)
         cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
         encryptor = cipher.encryptor()

         padder = padding.PKCS7(128).padder()
         padded_message = padder.update(message) + padder.finalize()
         ciphertext = encryptor.update(padded_message) + encryptor.finalize()

         return {
             "ciphertext": ciphertext,
             "iv": iv
         }
     encrypted_message = aes_encrypt(b"Hello, this is a test!", aes_key)
     ```

3. **Encrypt the AES Key**:

   - The AES session key is encrypted with the **server’s public RSA key**.
   - Example Code:
     ```python
     from cryptography.hazmat.primitives.asymmetric import padding
     from cryptography.hazmat.primitives import hashes

     def rsa_encrypt_with_public_key(public_key, data):
         encrypted = public_key.encrypt(
             data,
             padding.OAEP(
                 mgf=padding.MGF1(algorithm=hashes.SHA256()),
                 algorithm=hashes.SHA256(),
                 label=None
             )
         )
         return encrypted
     encrypted_aes_key = rsa_encrypt_with_public_key(server_public_key, aes_key)
     ```

4. **Send the Message**:

   - The payload is sent to the server:
     ```json
     {
         "encrypted_message": "<base64_encoded_ciphertext>",
         "encrypted_aes_key": "<base64_encoded_rsa_ciphertext>",
         "iv": "<base64_encoded_iv>",
         "mac": "<base64_encoded_mac>"
     }
     ```

##### **Receiving a Message (Server)**

1. **Decrypt the AES Key**:

   - The server uses its private RSA key to decrypt the AES session key.
   - Example Code:
     ```python
     def rsa_decrypt_with_private_key(private_key, encrypted_data):
         decrypted = private_key.decrypt(
             encrypted_data,
             padding.OAEP(
                 mgf=padding.MGF1(algorithm=hashes.SHA256()),
                 algorithm=hashes.SHA256(),
                 label=None
             )
         )
         return decrypted
     aes_key = rsa_decrypt_with_private_key(server_private_key, encrypted_aes_key)
     ```

2. **Decrypt the Message**:

   - The server decrypts the message using the AES key and IV.
   - Example Code:
     ```python
     def aes_decrypt(encrypted_message, aes_key, iv):
         cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
         decryptor = cipher.decryptor()

         unpadder = padding.PKCS7(128).unpadder()
         padded_message = decryptor.update(encrypted_message) + decryptor.finalize()
         message = unpadder.update(padded_message) + unpadder.finalize()
         return message
     message = aes_decrypt(encrypted_message["ciphertext"], aes_key, encrypted_message["iv"])
     ```

3. **Send Acknowledgment**:

   - The server sends a confirmation response to the client, ensuring delivery.
   - 
---

### **User Flow**

1. **Registration**:
   - User installs the application, generates RSA keys, and registers with the server.
2. **Messaging**:
   - User composes a message, which is encrypted and sent securely.
3. **Receiving Messages**:
   - The recipient decrypts the message and views it in plaintext.
