import sqlite3
from datetime import datetime

""" funcs here are:
create tables - as it sounds, void
add_user - adding one user, input (user_phone INTEGER,user_name STRING)
check_user_exists
close - close connection to db
verify_user_credentials
fetch_messages_for_user
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
                user_name TEXT,
                user_pw TEXT
            );
            """)
            self.c.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                message_index INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_num INTEGER,
                recipient_num INTEGER,
                subject TEXT,
                content TEXT,
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

    def add_user(self, user_phone, user_name, user_pw):

        # to call here to hash func on user_pw

        try:
            self.c.execute("INSERT INTO users VALUES (?, ?, ?)", (user_phone, user_name, user_pw))
            print(f"User {user_name} added successfully!")
        except sqlite3.Error as e:
            print(f"Error adding user {user_name}: {e}")

        self.conn.commit()

    def check_user_exists(self, user_phone):
        self.c.execute("SELECT user_phone FROM users WHERE user_phone=?", (user_phone,))
        return self.c.fetchone() is not None

    def add_message(self, sender_num, recipient_num, subject, content):
        """
        add message to DB, auto increment primary key message_index
        has auto timestamp
        :param sender_num:
        :param recipient_num:
        :param subject:
        :param content:
        :return:
        """
        curr_timestamp = datetime.now().strftime(" %H:%M:%S %d-%m-%Y")  # str type,output = 10:37:46 07-12-2024
        try:
            # Insert a single message
            self.c.execute("""
            INSERT INTO messages (sender_id, recipient_id, subject, content, date, blue_v)
            VALUES (?, ?, ?, ?, ?, ?)""",
                           (sender_num, recipient_num, subject, content, curr_timestamp, False))
            # blue_v will be checked later, date is not provide but assigned here

            print(f"message from {sender_num} to {recipient_num} added successfully!")
        except sqlite3.Error as e:
            print(f"Error adding message from {sender_num}: {e}")

        # Commit changes and close the connection
        self.conn.commit()

    def close(self):
        self.conn.close()

    def verify_user_credentials(self, user_phone, password):
        self.c.execute("SELECT user_pw FROM users WHERE user_phone=?", (user_phone,))
        row = self.c.fetchone()
        return row is not None and row[0] == password

    def fetch_messages_for_user(self, user_phone):
        self.c.execute("SELECT sender_num, subject, content, date FROM messages WHERE recipient_num=?", (user_phone,))
        return self.c.fetchall()
