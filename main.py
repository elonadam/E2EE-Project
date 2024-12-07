import sqlite3

from db_manager import DatabaseManager
from Rulon_GUI import StartWindow

db = DatabaseManager()

if __name__ == "__main__":
    start = StartWindow()
    start.mainloop()








# test zone #####################################################

# Add a user
#add_user(1, "John Doe")

# Add a message
# add_message(5000, 1, 'dope', "auto increment work.")

#db.create_tables()


# end of test zone #############################################
