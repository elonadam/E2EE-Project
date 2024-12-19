### **End-to-End Encrypted Messaging Protocol Using RSA and AES**

### **Components and Key Choices**

#### **1. Encryption Algorithms**

- **RSA-2048**:
  - **Purpose**: Used for secure key exchange.
  - **Why RSA-2048?**: RSA-1024 is too weak, while RSA-3072 is quite slow and often overkill for most applications, making RSA-2048 the preferred choice for balancing security and performance in this case.
  - **Usage**: Encrypts AES session keys.

- **AES-256**:
  - **Purpose**: Used for encrypting message payloads.
  - **Why AES-256?**: Faster than RSA for large data encryption and provides strong security against brute-force attacks.
  - **Usage**: Encrypts the actual message content using a session key.
---

### **Database Integration: SQLite**

#### **Purpose of the Database**

The server uses an **SQLite database** to securely store and manage client data, including public keys, messages, and acknowledgment flags. SQLite is a lightweight, file-based database ideal for applications with low to moderate concurrent usage, such as a messaging server.

- **Lightweight**: SQLite requires no separate server process, making it easy to integrate into a small-scale messaging application.  
- **File-Based**: All data is stored in a single `.db` file, simplifying deployment and management.  
- **Reliability**: Despite its simplicity, SQLite provides ACID compliance, ensuring data integrity.  

---

### **SQLite Schema**

The database includes the following tables:

1. **Users Table**  
   - **Purpose**: Stores client public keys for secure RSA key exchange.  

   ```sql
   CREATE TABLE users (
        user_phone INTEGER PRIMARY KEY,
        public_key TEXT,
        user_pw VARCHAR(100)
   );
   ```
   - `user_phone`: A unique identifier for each client (in our case, their phone number).  
   - `public_key`: The client’s RSA public key.
   - `user_pw`: The client’s hashed password.

2. **Messages Table**  
   - **Purpose**: Temporarily stores encrypted messages for offline delivery.  

   ```sql
    CREATE TABLE IF NOT EXISTS messages (
        message_index INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_phone INTEGER,
        recipient_phone INTEGER,
        encrypted_aes_key TEXT,
        ciphertext TEXT,
        iv TEXT,
        date TEXT,
        blue_v BOOLEAN
    );
   ```
   - `message_index`: Unique identifier for each row in the table.  
   - `sender_phone`: Unique identifier of the message sender.  
   - `recipient_phone`: Unique identifier of the message recipient.  
   - `encrypted_aes_key`: RSA-encrypted AES session key.  
   - `ciphertext`: The AES-encrypted message content.  
   - `iv`: Initialization Vector used for AES encryption.  
   - `date`: Automatically logs when the message was stored.
   - `blue_v`: The delivery confirmation.

### **Protocol Workflow**

#### **Registration Phase**

1. **Key Pair Generation (Client)**:
   - Each client generates an **RSA key pair**:
     - **Public Key**: Used to encrypt the AES key.
     - **Private Key**: Used to decrypt the AES key.
   - RSA keys are asymmetric, meaning the public key is shared with others while the private key remains secret.

    - Asymmetric encryption allows for secure communication without needing a pre-shared secret. This is ideal for systems where the sender and recipient may not have direct contact to exchange a symmetric key securely.
    - RSA keys are well-suited for encrypting small pieces of data (like an AES key).

   **Client RSA Public Key**:
   - During registration, each client sends their public key to the server over a secure channel.
   - The server securely stores each client’s public key, indexed by their unique identifier. QQrefernce where in table

       - The server acts as a trusted directory for public keys, ensuring that the sender can request the recipient's public key when she needs to send a message.
       - Storing only public keys on the server minimizes the risk of sensitive data leaks if the server is compromised.

  - **Client RSA Private Key**:
    - It is encrypted with AES-256 using a strong user-derived password and stored locally.

#### **Message Exchange Phase**

##### **Sending a Message (Sender)**

1. **Encrypt the Message**:

- Before encrypting the message, the sender generates:
  1. A **random AES key** (256 bits).
  2. A **random Initialization Vector (IV)** (128 bits) for use with AES in GCM mode.
     
     - The sender encrypts the actual message using AES and the IV.

2. **Encrypt the AES Key**:

   - The AES session key is encrypted with the the recipient’s public RSA key.
        - RSA encryption ensures that only the the recipient (who has the corresponding private key) can decrypt the AES key.
        - Encrypting the AES key allows both the sender and the recipient to securely use a symmetric encryption algorithm (AES) for the actual message, combining the efficiency of AES with the security of RSA.

3. **Package the Encrypted Message**:
  - The sender creates a message package containing:
    - The **sender's public key** (for recipient verification).
    - The **recipient's public key** (recipient's public key).
    - The **encrypted AES key** (RSA-encrypted with the recipient's public key).
    - The **ciphertext** (the AES-encrypted message - includes the subject and content).
    - The **IV** (used for AES encryption of the message).
    - The **delivery confirmation** (message received flag)

    ```json
    {
        "sender_public_key": "<Sender's public key>",
        "recipient_public_key": "<Recipient's public key>",
        "encrypted_aes_key": "<RSA-encrypted AES key>",
        "ciphertext": "<AES-encrypted message>",
        "iv": "<Initialization Vector>",
        "blue_v": "<Message received flag>"
    }
    ```
    
4. **Send the Message**:
   - Transmit the message package to the server.
   - The server relays it securely to the recipient.


##### **Receiving a Message (Recipient)**

1. **Decrypt the AES Key**:

    -  The recipient receives the package and extracts the encrypted AES key.
    - Then he decrypts the AES key using his private RSA key:
    - Only the recipient has access to his RSA private key, ensuring that only he can decrypt the AES key and, consequently, the message.

2. **Decrypt the Message**:

   - The server decrypts the message using the AES key and IV.
      - Decrypting the message with AES is efficient and ensures that the original plaintext message is retrieved securely.

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

### **Offline Delivery** QQnot relevent?

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
| **Authentication**       | RRSA ensures that only the the recipient can decrypt the AES key, confirming the recipient’s identity. |
| **Integrity**            | AES encryption ensures that tampered ciphertext cannot be successfully decrypted. |
| **Acknowledgment**       | Mandatory acknowledgment ensures message delivery and decryption confirmation.    |
| **Resistance to MITM**   | RSA encryption prevents unauthorized decryption without the private key. |
| **Offline Delivery**     | Server securely stores encrypted messages for offline recipients.          |


הנחות:
מספר טלפון חייב להתחיל ב5.

[05:50, 18/12/2024] Elon Adam: אפשר לציין בפרוטוקול שאנחנו מבצעים עוד שלב הגנה מפני התקפות על ידי שימוש ב placeholder של סימן שאלה בתוך השאילתות sql במקום לבצע השמה ישירה, זאת כדי למנוע sql injection
[05:51, 18/12/2024] Elon Adam: זה למשל קוד לא מוגן

# Dangerous and prone to SQL injection
user_input = "example_user"
cursor.execute("SELECT * FROM users WHERE username = '" + user_input + "'")