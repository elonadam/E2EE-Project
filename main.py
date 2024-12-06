import sqlite3

# Connect to the database
conn = sqlite3.connect("messages.sqlite")
cursor = conn.cursor()

try:
    # Create `users` table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER
        user_num INTEGER PRIMARY KEY
    );
    """)
except sqlite3.Error as e:
    print("Error creating `users` table:", e)

try:
    # Create `messages` table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        sender_id INTEGER,
        recipient_id INTEGER,
        subject TEXT,
        content TEXT,
        date TEXT,
        blue_v BOOLEAN,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    );
    """)
except sqlite3.Error as e:
    print("Error creating `messages` table:", e)

# Commit changes and close connection
conn.commit()
conn.close()


conn = sqlite3.connect("messages.sqlite")
cursor = conn.cursor()

# Fetch table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in database:", tables)

conn.close()

"""
all above is creation and check tables in memory
"""

from funcs import *

# Example: Add a user
add_user(1, "John Doe", "john@example.com")

# Example: Add a message
add_message(1, 1, 2, "Hello", "This is a test message.", False)

# Example: Fetch and print all users
users = get_users()
for user in users:
    print(user)

# Example: Fetch and print messages for a user
messages = get_messages_for_user(1)
for message in messages:
    print(message)