import customtkinter as ctk
from gui.ui import *
from models import initialize_database
import os
import hashlib
import base64

class ProductKeyPrompt:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Product Key Prompt")
        self.product_key_label = ctk.CTkLabel(self.root, text="Enter Product Key:")
        self.product_key_label.pack()
        self.product_key_entry = ctk.CTkEntry(self.root, show="*")
        self.product_key_entry.pack()
        self.submit_button = ctk.CTkButton(self.root, text="Submit", command=self.check_product_key)
        self.submit_button.pack()

    def check_product_key(self):
        product_key = self.product_key_entry.get()
        hashed_product_key = hashlib.sha256(product_key.encode()).hexdigest()
        if hashed_product_key == "YOUR_HASHED_PRODUCT_KEY_HERE":
            with open("product_key.txt", "w") as f:
                f.write(base64.b64encode(product_key.encode()).decode())
            self.root.destroy()
            initialize_database()
            app = InventoryApp()
            app.run()
        else:
            ctk.CTkLabel(self.root, text="Invalid Product Key", text_color="red").pack()

    def run(self):
        if os.path.exists("product_key.txt"):
            with open("product_key.txt", "r") as f:
                product_key = base64.b64decode(f.read().encode()).decode()
            hashed_product_key = hashlib.sha256(product_key.encode()).hexdigest()
            if hashed_product_key == "YOUR_HASHED_PRODUCT_KEY_HERE":
                self.root.destroy()
                initialize_database()
                app = InventoryApp()
                app.run()
            else:
                ctk.CTkLabel(self.root, text="Invalid Product Key", text_color="red").pack()
        else:
            self.root.mainloop()

if __name__ == "__main__":
    product_key_prompt = ProductKeyPrompt()
    product_key_prompt.run()