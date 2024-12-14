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
---

### **Protocol Workflow**

#### **Registration Phase**

1. **Key Pair Generation (Client)**:
   - Each client generates an **RSA key pair**:
     - **Public Key**: Used to encrypt the AES key.
     - **Private Key**: Used to decrypt the AES key.
   - RSA keys are asymmetric, meaning the public key is shared with others while the private key remains secret.

       - Asymmetric encryption allows for secure communication without needing a pre-shared secret. 
       - RSA keys are well-suited for encrypting small pieces of data (like an AES key).

   **Client RSA Public Key**:
   - During registration, each client sends their public key to the server over a secure channel.
   - The server securely stores each client’s public key, indexed by their unique identifier.

       - The server acts as a trusted directory for public keys, ensuring that the sender can request the recipient's public key when she needs to send a message.
       - Storing only public keys on the server minimizes the risk of sensitive data leaks if the server is compromised.

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
  - **Client RSA Private Key**:
    - It is encrypted with AES-256 using a strong user-derived password.

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

#### **Message Exchange Phase**

##### **Sending a Message (Sender)**

1. **Encrypt the Message**:

- Before encrypting the message, the sender generates:
  1. A **random AES key** (256 bits).
  2. A **random Initialization Vector (IV)** (128 bits) for use with AES in CBC mode.
     
     ```python
     from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
     from cryptography.hazmat.primitives import padding
     import os

     def generate_aes_key():
         return os.urandom(32)  # 256-bit key
     aes_key = generate_aes_key()
    
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
    ```

     - The sender encrypts the actual message using AES and the random AES key:
    ```plaintext
    ciphertext = AES_Encrypt(message, AES_key, IV)
    ```

2. **Encrypt the AES Key**:

   - The AES session key is encrypted with the the recipient’s public RSA key.
     
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
     
        - RSA encryption ensures that only the the recipient (who has the corresponding private key) can decrypt the AES key.
        - Encrypting the AES key allows both the sender and the recipient to securely use a symmetric encryption algorithm (AES) for the actual message, combining the efficiency of AES with the security of RSA.

3. **Package the Encrypted Message**:
  - The sender creates a message package containing:
    - The **sender's public key** (for recipient verification).
    - The **recipient's public key** (recipient's public key).
    - The **encrypted AES key** (RSA-encrypted with the recipient's public key).
    - The **IV** (used for AES encryption of the message).
    - The **ciphertext** (the AES-encrypted message - includes the subject and content).

    ```json
    {
        "sender_public_key": "<the sender's public key>",
        "recipient_public_key": "<recipient's public key>",
        "encrypted_aes_key": "<RSA-encrypted AES key>",
        "iv": "<Initialization Vector>",
        "ciphertext": "<AES-encrypted message>"
    }
    ```
    
4. **Send the Message**:
   - Transmit the message package to the server.
   - The server relays it securely to the recipient.


##### **Receiving a Message (Recipient)**

1. **Decrypt the AES Key**:

   - The the recipient uses its private RSA key to decrypt the AES session key.
     
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

   - Use the decrypted AES key and IV to decrypt the ciphertext:
     
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
   - After successfully decrypting the message, the recipient must send an acknowledgment message to the sender via the server.
   - The acknowledgment contains:
     - **Recipient's identifier**.
     - **Message ID** (the time that the message was sent).
     - **Acknowledgment status** (e.g., "received").
       
     ```json
     {
         "recipient_id": "<recipient's unique identifier>",
         "message_id": "<unique message ID>",
         "status": "received"
     }
     ```

4. **Verify Acknowledgment** (Sender):
   - Upon receiving the acknowledgment, the sender verifies that the acknowledgment corresponds to the message sent (by matching the `message_id`).
   - The acknowledgment ensures that the message was successfully delivered and decrypted.

---

### **Offline Delivery**

1. If the recipient is offline:
   - The server temporarily stores the encrypted message.
   - Upon the recipient’s reconnection, the server delivers the message.
       - This ensures that messages are not lost if the recipient is unavailable when the sender transmits them.

2. After successful delivery:
   - The server waits for the recipient's acknowledgment and confirms its receipt to the sender.

3. The message and acknowledgment are deleted from the server after delivery and confirmation.
       - This minimizes the server's storage requirements and reduces the risk of exposing sensitive information if the server is compromised.

### **Security Features and Guarantees**

| **Requirement**         | **Implementation with RSA**                                                      |
|--------------------------|-----------------------------------------------------------------------------------|
| **Confidentiality**      | Messages are encrypted using AES-256; AES keys are RSA-2048 encrypted.                |
| **Authentication**       | RSA ensures that only the the recipient can decrypt the AES key. |
| **Integrity**            | AES encryption ensures that tampered ciphertext cannot be successfully decrypted. |
| **Acknowledgment**       | Mandatory acknowledgment ensures message delivery and decryption confirmation.    |
| **Resistance to MITM**   | RSA encryption prevents unauthorized decryption without the private key. |
| **Offline Delivery**     | Server securely stores encrypted messages for offline recipients.          |
