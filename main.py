import sqlite3

from funcs import *


# test zone #####################################################

# Add a user
#add_user(1, "John Doe")

# Add a message
add_message(5000, 1, 'dope', "auto increment work.")


# end of test zone #############################################
d = datetime.now().strftime(" %H:%M:%S %d-%m-%Y")
print(d)
print(type(d))

# # Example: Fetch and print all users
# users = get_users()
# for user in users:
#     print(user)
#
# # Example: Fetch and print messages for a user
# messages = get_messages_for_user(1)
# for message in messages:
#     print(message)
