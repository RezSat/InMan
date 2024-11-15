# main.py
from gui.ui import *
from models import initialize_database

if __name__ == "__main__":
    initialize_database()
    app = InventoryApp()
    app.run()
