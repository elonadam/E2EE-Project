from db_manager import DatabaseManager
from Rulon_GUI import StartWindow

db = DatabaseManager()
db.create_tables()
if __name__ == "__main__":
    start = StartWindow()
    start.mainloop()

 