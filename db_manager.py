import sqlite3
from datetime import datetime


class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect("data.db")  # connect to the database
        self.c = self.conn.cursor()

    def create_tables(self):  # create tables in DB
        """
        Creates the users and messages tables in the SQLite database if not exist
        """

        try:
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
                blue_v BOOLEAN DEFAULT 0,
                seen_notification BOOLEAN DEFAULT 0
            );
            """)
            self.conn.commit()  # commit changes and close the connection
            print("Tables created successfully.")
        except sqlite3.Error as e:
            print("Error creating tables:", e)
        finally:
            self.conn.close()

    def add_user(self, user_phone, public_key, user_pw): # adding user to the DB from the GUI
        try:
            self.c.execute("INSERT INTO users VALUES (?, ?, ?)", (user_phone, public_key, user_pw))
            print(f"User {user_phone} added successfully!")
        except sqlite3.Error as e:
            print(f"Error adding user {user_phone}: {e}")

        self.conn.commit()

    def check_user_exists(self, user_phone): # check if user exist to recive the messages
        self.c.execute("SELECT user_phone FROM users WHERE user_phone=?", (user_phone,))
        return self.c.fetchone() is not None

    def add_message(self, sender_num, recipient_num, encrypted_aes_key, ciphertext, iv): # add message to DB
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

        # commit changes and close the connection
        self.conn.commit()

    def fetch_messages_for_user(self, user_phone): # extract messages that were sent to the user from DB

        self.c.execute("UPDATE messages SET blue_v = ? WHERE recipient_phone = ? AND blue_v = ?", (True, user_phone, 0))
        self.conn.commit()
        self.c.execute(
            "SELECT sender_phone, recipient_phone, encrypted_aes_key, iv, ciphertext, date, blue_v FROM messages WHERE recipient_phone=?",
            (user_phone,))
        return self.c.fetchall()

    def get_user(self, phone): # fetch user number to check if exist
        try:
            query = "SELECT * FROM users WHERE user_phone = ?"
            self.c.execute(query, (phone,))
            return self.c.fetchone()
        except sqlite3.Error as e:
            print(f"Error while checking user existence: {e}")
            return False

    def get_user_public_key(self, phone): # get the public key of the user to encrypt later
        try:
            query = "SELECT public_key FROM users WHERE user_phone = ?"
            self.c.execute(query, (phone,))
            return self.c.fetchone()
        except sqlite3.Error as e:
            print(f"Error fetching public key for user {phone}: {e}")
            return False

    def seen_notification_sender(self, sender_p): # iterate through the messages to check if the user read the message to notify the sender
        # The query chose only messages that delivered to recipient and sender didn't got notification yet
        query = """ 
            SELECT message_index FROM messages WHERE
             sender_phone = ? 
             AND blue_v = 1 
             AND (seen_notification != 1 OR seen_notification IS NULL)"""
        self.c.execute(query, (sender_p,))
        results = self.c.fetchall()
        message_indexes = [row[0] for row in results]

        if message_indexes: # true if at least one message
            placeholders = ",".join("?" * len(message_indexes)) # creates a sequence of '?' in the length of
            # message_indexes
            update_query = f"UPDATE messages SET seen_notification = 1 WHERE message_index IN ({placeholders})"
            self.c.execute(update_query, message_indexes)
            self.conn.commit()
        return message_indexes
