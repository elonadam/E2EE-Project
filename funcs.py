import sqlite3
from datetime import datetime

"""
create tables - as it sounds, void
add_user - adding one user, input (user_phone INTEGER,user_name STRING)


"""


# saving the actual creation for later, if will need later
def create_tables():
    """
    Creates the `users` and `messages` tables in the SQLite database
    if they do not already exist.
    """
    # Connect to the database
    conn = sqlite3.connect("data.db")
    c = conn.cursor()

    try:
        # Create `users` table
        c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_phone INTEGER PRIMARY KEY,
            user_name TEXT
        );
        """)
        print("Table `users` created successfully.")
    except sqlite3.Error as e:
        print("Error creating `users` table:", e)

    try:
        # Create `messages` table
        c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            message_index INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER,
            recipient_id INTEGER,
            subject TEXT,
            content TEXT,
            date TEXT,
            blue_v BOOLEAN
        );
        """)
        print("Table `messages` created successfully.")
    except sqlite3.Error as e:
        print("Error creating `messages` table:", e)

    # commit changes and close the connection
    conn.commit()
    conn.close()


def add_user(user_phone, user_name):
    # connect to the database
    conn = sqlite3.connect("data.db")
    c = conn.cursor()

    try:
        # Insert a single user
        c.execute("INSERT INTO users VALUES (?, ?)", (user_phone, user_name))
        print(f"User {user_name} added successfully!")
    except sqlite3.Error as e:
        print(f"Error adding user {user_name}: {e}")

    # Commit changes and close the connection
    conn.commit()
    conn.close()


add_user(300, 'lucy')
