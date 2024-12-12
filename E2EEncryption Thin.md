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

#### **2. Key Storage**

- **Client-Side**:

  - **Client RSA Private Key**:
    - Stored in a **secure enclave or keychain**.
    - If hardware-backed storage isn’t available, it is encrypted with AES-256 using a strong user-derived password.

      - **Secure Enclave/Keychain**: Directly generate and store keys using platform APIs, ensuring the private key is non-exportable.

  - **Server RSA Public Key**:
    - Embedded in the client application during deployment.
    - Validated using signatures or fingerprints to prevent tampering.
    - Stored in a read-only section of the application’s configuration or hardcoded within the app binary.

- **Server-Side**:

  - **Server RSA Private Key**:
    - Stored in a **Hardware Security Module (HSM)** or a **Key Management System (KMS)**.

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

### **1. Key Setup**

#### **Client-Side (Alice and Bob):**
1. **Key Pair Generation**:
   - Each client generates an **RSA key pair**:
     - **Public Key**: Used to encrypt data (or the AES key in this case).
     - **Private Key**: Used to decrypt data (or the AES key).
   - RSA keys are asymmetric, meaning the public key is shared with others while the private key remains secret.

   **Why?**
   - Asymmetric encryption allows for secure communication without needing a pre-shared secret. This is ideal for systems where the sender (Alice) and recipient (Bob) may not have direct contact to exchange a symmetric key securely.
   - RSA keys are well-suited for encrypting small pieces of data (like an AES key).

2. **Public Key Registration**:
   - During registration, each client sends their **public key** to the server over a secure channel (e.g., HTTPS).
   - The server securely stores each client’s public key, indexed by their unique identifier.

   **Why?**
   - The server acts as a trusted directory for public keys, ensuring that Alice can request Bob's public key when she needs to send a message.
   - Storing only public keys on the server minimizes the risk of sensitive data leaks if the server is compromised.

---

### **2. Initial Registration**

1. **Client Key Pair Generation**:
   - Each client generates their RSA key pair.    
   - The private key is stored securely on the client.

   **Why?**
   - The RSA private key is kept secret on the client’s device, ensuring that only the client can decrypt messages sent to them. The public key is shared for encryption.

2. **Public Key Upload**:
   - The public key is uploaded to the server during registration.

   **Why?**
   - This ensures that other clients can retrieve the recipient's public key when they want to send a message.

3. **Server Storage**:
   - The server stores the public key associated with the client's unique identifier (e.g., user ID or phone number).

   **Why?**
   - Storing public keys allows the server to act as a "key distribution center," ensuring clients can securely retrieve public keys without direct communication between them.

---

### **3. Message Encryption**

#### **Step 1: Generate AES Key**
- Before encrypting the message, the sender (Alice) generates:
  1. A **random AES key** (256 bits).
  2. A **random Initialization Vector (IV)** (128 bits) for use with AES in CBC mode.

   **Why?**
   - AES is much faster and more efficient for encrypting large data (like messages) compared to RSA.
   - Using an IV ensures that encrypting the same plaintext multiple times produces different ciphertexts, enhancing security.

---

#### **Step 2: Encrypt the AES Key with RSA**
- Alice encrypts the AES key using Bob’s public RSA key:
  ```plaintext
  encrypted_aes_key = RSA_Encrypt(AES_key, Bob_Public_Key)
  ```

   **Why?**
   - RSA encryption ensures that only Bob (who has the corresponding private key) can decrypt the AES key.
   - Encrypting the AES key allows Alice and Bob to securely use a symmetric encryption algorithm (AES) for the actual message, combining the efficiency of AES with the security of RSA.

---

#### **Step 3: Encrypt the Message with AES**
- Alice encrypts the actual message using AES and the random AES key:
  ```plaintext
  ciphertext = AES_Encrypt(message, AES_key, IV)
  ```

   **Why?**
   - AES is significantly faster and more efficient than RSA for encrypting large messages. Encrypting the message with AES ensures both security and performance.

---

#### **Step 4: Package the Data**
- Alice creates a message package containing:
  - The **encrypted AES key** (RSA-encrypted).
  - The **IV** (used for AES encryption).
  - The **ciphertext** (AES-encrypted message).
  - Optionally, Alice’s **public key** (if needed for sender verification).

- Example of the message structure:
  ```json
  {
      "sender_public_key": "<Alice's public key>",
      "encrypted_aes_key": "<RSA-encrypted AES key>",
      "iv": "<Initialization Vector>",
      "ciphertext": "<AES-encrypted message>"
  }
  ```

   **Why?**
   - This package contains all the necessary information for Bob to decrypt the message.
   - Including Alice’s public key (optional) allows Bob to verify the sender’s identity if needed.

---

#### **Step 5: Send the Message**
- Alice sends the package to the server, which relays it to Bob.

   **Why?**
   - The server acts as an intermediary, ensuring the message reaches Bob even if he is offline.

---

### **4. Message Decryption**

#### **Step 1: Retrieve and Decrypt AES Key**
- Bob receives the package and extracts the encrypted AES key.
- Bob decrypts the AES key using his private RSA key:
  ```plaintext
  AES_key = RSA_Decrypt(encrypted_aes_key, Bob_Private_Key)
  ```

   **Why?**
   - Only Bob has access to his RSA private key, ensuring that only he can decrypt the AES key and, consequently, the message.

---

#### **Step 2: Decrypt the Message**
- Bob uses the decrypted AES key and IV to decrypt the ciphertext:
  ```plaintext
  message = AES_Decrypt(ciphertext, AES_key, IV)
  ```

   **Why?**
   - Decrypting the message with AES is efficient and ensures that the original plaintext message is retrieved securely.

---

### **5. Offline Delivery**

1. If Bob is offline:
   - The server stores the encrypted message temporarily.
   - When Bob reconnects, the server delivers the message to him.

   **Why?**
   - This ensures that messages are not lost if the recipient is unavailable when the sender transmits them.

2. The message is deleted from the server after successful delivery.

   **Why?**
   - This minimizes the server's storage requirements and reduces the risk of exposing sensitive information if the server is compromised.

---

### **6. Security Features and Guarantees**

| **Requirement**         | **Implementation with RSA**                                                      |
|--------------------------|-----------------------------------------------------------------------------------|
| **Confidentiality**      | Messages are encrypted using AES-256; AES keys are RSA-encrypted.                |
| **Authentication**       | RSA ensures that only Bob can decrypt the AES key, confirming the recipient’s identity. |
| **Integrity**            | Optional HMAC or MAC can be added to verify the message's authenticity and prevent tampering. |
| **Resistance to MITM**   | RSA ensures that only the recipient with the private key can decrypt the AES key. |
| **Offline Delivery**     | The server can store encrypted messages securely for offline recipients.          |

