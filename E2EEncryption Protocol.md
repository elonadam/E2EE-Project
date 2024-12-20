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

The server uses an **SQLite database** to securely store and manage client data, including public keys, user credentials, messages, and acknowledgment flags. SQLite is a lightweight, file-based database ideal for applications with low to moderate concurrent usage, such as a messaging server.

- **Lightweight**: SQLite requires no separate server process, making it easy to integrate into a small-scale messaging application.  
- **File-Based**: All data is stored in a single `data.db` file, simplifying deployment and management.  
- **Reliability**: Despite its simplicity, SQLite provides ACID compliance, ensuring data integrity. 
- **Security**: To prevent SQL injection, placeholders (e.g., '?') are used in place of variable names.

---

### **SQLite Schema and Data Storage**

The database includes the following tables:

#### **1. Users Table**  
**Purpose**: Stores client public keys, hashed passwords, and phone numbers for authentication and secure RSA key exchange.

**Schema**:
```sql
CREATE TABLE users (
    user_phone INTEGER PRIMARY KEY,
    public_key TEXT,
    user_pw VARCHAR(100)
);
```

- **Columns**:
  - `user_phone`: A unique identifier for each client (e.g., their phone number). This is the primary key.
  - `public_key`: The client’s RSA public key, used for encrypting the AES session key.
  - `user_pw`: The client’s hashed password for authentication.

- **Storage Operations**:
  - **Adding a User**: The `add_user` function inserts a new user into the table.
    ```python
    self.c.execute("INSERT INTO users VALUES (?, ?, ?)", (user_phone, public_key, user_pw))
    ```
  - **Fetching User Information**: Queries such as `get_user` and `get_user_public_key` retrieve user details or the public key based on the phone number.

2. **Messages Table**  
**Purpose**: Temporarily stores encrypted messages for offline delivery, along with metadata like sender/recipient, timestamps, and acknowledgment flags. 

**Schema**:
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

- **Columns**:
  - `message_index`: Unique identifier for each message. Auto-incremented.
  - `sender_phone`: Phone number of the sender.
  - `recipient_phone`: Phone number of the recipient.
  - `encrypted_aes_key`: RSA-encrypted AES session key.
  - `ciphertext`: The AES-encrypted message content.
  - `iv`: Initialization Vector used for AES encryption.
  - `date`: Timestamp of when the message was added (e.g., `10:37:46 07-12-2024`).
  - `blue_v`: Boolean flag indicating whether the message was acknowledged (true if acknowledged).

- **Storage Operations**:
  - **Adding a Message**: The `add_message` function inserts a new message, including a timestamp and an unacknowledged flag (`blue_v = False`).
    ```python
    self.c.execute("""
    INSERT INTO messages (sender_phone, recipient_phone, encrypted_aes_key, ciphertext, iv, date, blue_v)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (sender_num, recipient_num, encrypted_aes_key, ciphertext, iv, curr_timestamp, False))
    ```
  - **Fetching Messages**: The `fetch_messages_for_user` function retrieves all messages for a given recipient and updates their acknowledgment status (`blue_v = True`).
    ```python
    self.c.execute("UPDATE messages SET blue_v = ? WHERE recipient_phone = ? AND blue_v = ?", (True, user_phone, 0))
    self.c.execute("SELECT sender_phone, recipient_phone, encrypted_aes_key, iv, ciphertext, date, blue_v FROM messages WHERE recipient_phone=?", (user_phone,))
    ```
  - **Acknowledging Messages**: The `acknowledge_message` function updates the `blue_v` flag for a specific message index.
    ```python
    self.c.execute("UPDATE messages SET blue_v = ? WHERE message_index = ?", (True, message_index))
    ```

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
   - The public key is sent to the server and stored in the `users` table.

       - The server acts as a trusted directory for public keys, ensuring that the sender can request the recipient's public key when needed.
       - Storing only public keys on the server minimizes the risk of sensitive data leaks if the server is compromised.

  - **Client RSA Private Key**:
   - The private key is encrypted with AES-256 using a user-derived password and stored locally on the client.

#### **Message Exchange Phase**

##### **Sending a Message (Sender)**

1. **Encrypt the Message**:

- Before encrypting the message, the sender generates:
  1. A **random AES key** (256 bits).
  2. A **random Initialization Vector (IV)** (128 bits) for use with AES in GCM mode.
     
     - The sender encrypts the actual message using AES and the IV.

2. **Encrypt the AES Key**:

   - The AES session key is encrypted with the recipient’s public RSA key.
        - RSA encryption ensures that only the recipient (who has the corresponding private key) can decrypt the AES key.
        - Encrypting the AES key allows both the sender and the recipient to securely use a symmetric encryption algorithm (AES) for the actual message, combining the efficiency of AES with the security of RSA.

3. **Package the Encrypted Message**:
  - The sender creates a message package containing:
    - The **sender's public key** (for recipient verification).
    - The **recipient's public key** (recipient's public key).
    - The **encrypted AES key** (RSA-encrypted with the recipient's public key).
    - The **ciphertext** (the AES-encrypted message - includes the subject and content).
    - The **IV** (used for AES encryption of the message).
    - The **delivery confirmation** (message received flag).

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
   - If the recipient is online, the server relays it securely to them.
   - If the recipient is offline, the server stores the message in their inbox for later delivery.

5. **Store the Message on the Server**:
   - The encrypted message, AES key, IV, and metadata are sent to the server and stored in the `messages` table.

##### **Receiving a Message (Recipient)**

1. **Fetch Stored Messages**:
   - When the recipient connects, the server retrieves all stored messages from the `messages` table using the `fetch_messages_for_user` function.

2. **Decrypt the AES Key**:

    - The recipient receives the package and extracts the encrypted AES key.
    - Then they decrypt the AES key using their private RSA key:
         - Only the recipient has access to their RSA private key, ensuring that only they can decrypt the AES key and, consequently, the message.

3. **Decrypt the Message**:

   - The recipient decrypts the message using the AES key and IV.
      - Decrypting the message with AES is efficient and ensures that the original plaintext message is retrieved securely.

4. **Send Acknowledgment**:
   - The recipient sends an acknowledgment, which updates the `blue_v` flag in the `messages` table via the `acknowledge_message` function.
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
---

### **Offline Delivery**

1. **Storing Offline Messages**:
   - If the recipient is offline, the server stores the message in the `messages` table with `blue_v = False`.

2. **Delivery Upon Reconnection**:
   - The server delivers all stored messages to the recipient when they reconnect.

3. **Cleanup**:
   - Once the recipient acknowledges a message, it is flagged as acknowledged (`blue_v = True`), ensuring reliable delivery tracking.


### **Ensuring Completeness of Messages (Source and Content)**

#### **Achieving Completeness**

Completeness of a message guarantees that it reaches the intended recipient fully intact and can be decrypted and acknowledged. This is achieved through a combination of verification mechanisms, secure storage, and encryption methods.

#### **Implementation Details**
1. **Source Verification**
   - Each user registers with an RSA public key stored in the database.
   - When sending a message, the recipient’s public key is verified in the database.
   - The key is used to encrypt the AES session key, ensuring that only the intended recipient can decrypt it.

2. **Message and Metadata Storage**
   - Messages are stored in the `messages` table along with the following metadata:
     - Sender and recipient phone numbers.
     - Encrypted AES key.
     - Initialization Vector (IV).
     - Encrypted message content (`ciphertext`).
     - Timestamp (`date`).
     - Acknowledgment flag (`blue_v`).

3. **Acknowledgment Tracking**
   - Each message is marked as unacknowledged (`blue_v = False`) upon insertion into the database.
   - When the recipient opens a message, the acknowledgment flag is updated to `blue_v = True`.

4. **Handling Offline Recipients**
   - Messages for offline recipients are stored in the `messages` table.
   - These messages are automatically delivered when the recipient reconnects.

5. **Integrity Verification**
   - AES encryption ensures that tampered ciphertext cannot be decrypted successfully.
   - The acknowledgment mechanism tracks whether messages have been fully received and read.

---

### **Security Features and Guarantees**

| **Requirement**         | **Implementation with RSA**                                                      |
|--------------------------|-----------------------------------------------------------------------------------|
| **Confidentiality**      | Messages are encrypted using AES-256; AES keys are RSA-2048 encrypted.                |
| **Authentication**       | RSA ensures that only the recipient can decrypt the AES key, confirming the recipient’s identity. |
| **Integrity**            | AES encryption ensures that tampered ciphertext cannot be successfully decrypted. |
| **Acknowledgment**       | Mandatory acknowledgment ensures message delivery and decryption confirmation.    |
| **Resistance to MITM**   | RSA encryption prevents unauthorized decryption without the private key. |
| **Offline Delivery**     | Server securely stores encrypted messages for offline recipients.          |