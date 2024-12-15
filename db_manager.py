import sqlite3
from datetime import datetime

""" funcs here are:
create tables - as it sounds, void
add_user - adding one user, input (user_phone INTEGER,user_name STRING)
add_message
check_user_exists
close - close connection to db
verify_user_credentials
fetch_messages_for_user
get_user_public_key(user_phone)
acknowledge_message
"""
class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect("data.db")  # Connect to the database
        self.c = self.conn.cursor()

    def create_tables(self):  # saving the actual creation for later, if will need later
        """
        Creates the `users` and `messages` tables in the SQLite database
        if they do not already exist.
        """

        try:  # Create tables
            self.c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_phone INTEGER PRIMARY KEY,
                public_key TEXT,
                user_pw VARCHAR(100)
            );
            """)
            self.c.execute("""
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
            """)
            self.conn.commit()  # commit changes and close the connection
            print("Tables created successfully.")
        except sqlite3.Error as e:
            print("Error creating tables:", e)
        finally:
            self.conn.close()

    def add_user(self, user_phone, public_key, user_pw):
        try:
            self.c.execute("INSERT INTO users VALUES (?, ?, ?)", (user_phone, public_key, user_pw))
            print(f"User {user_phone} added successfully!")
        except sqlite3.Error as e:
            print(f"Error adding user {user_phone}: {e}")

        self.conn.commit()

    def check_user_exists(self, user_phone):
        self.c.execute("SELECT user_phone FROM users WHERE user_phone=?", (user_phone,))
        return self.c.fetchone() is not None

    def add_message(self, sender_num, recipient_num, encrypted_aes_key, ciphertext, iv):
        """
        add message to DB, auto increment primary key message_index
        has auto timestamp
        :param sender_num:
        :param recipient_num:
        :param encrypted_aes_key:
        :param ciphertext:
        :param iv:
        :return:
        """
        curr_timestamp = datetime.now().strftime(" %H:%M:%S %d-%m-%Y")  # str type,output = 10:37:46 07-12-2024
        try:
            # Insert a single message
            self.c.execute("""
                INSERT INTO messages (sender_phone, recipient_phone, encrypted_aes_key, ciphertext, iv, date, blue_v)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (sender_num, recipient_num, encrypted_aes_key, ciphertext, iv, curr_timestamp, False))
            # blue_v will be checked later, date is not provide but assigned here

            print(f"message from {sender_num} to {recipient_num} added successfully!")
        except sqlite3.Error as e:
            print(f"Error adding message from {sender_num}: {e}")

        # Commit changes and close the connection
        self.conn.commit()
        
    def close(self):
        self.conn.close()

    def verify_user_credentials(self, user_phone, password): #QQ how does this work?
        self.c.execute("SELECT user_pw FROM users WHERE user_phone=?", (user_phone,))
        row = self.c.fetchone()
        return row is not None and row[0] == password

    def fetch_messages_for_user(self, user_phone):
        self.c.execute("SELECT sender_phone, encrypted_aes_key, ciphertext, iv, date FROM messages WHERE recipient_phone=?", 
                        (user_phone,))
        return self.c.fetchall()

    def get_user(self, phone):
        try:
            query = "SELECT * FROM users WHERE user_phone = ?"
            self.c.execute(query, (phone,))
            return self.c.fetchone()
        except sqlite3.Error as e:
            print(f"Error while checking user existence: {e}")
            return False
                
    def get_user_public_key(self, phone):
        try:
            query = "SELECT public_key FROM users WHERE user_phone = ?"
            self.c.execute(query, (phone,))
            return self.c.fetchone()
        except sqlite3.Error as e:
            print(f"Error fetching public key for user {phone}: {e}")
            return False
        
    def acknowledge_message(self, message_index):
        try:
            self.c.execute("UPDATE messages SET blue_v = ? WHERE message_index = ?", (True, message_index))
            self.conn.commit()
            print(f"Message {message_index} acknowledged successfully!")
        except sqlite3.Error as e:
            print(f"Error acknowledging message {message_index}: {e}")
