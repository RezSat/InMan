#gui/ui.py
import customtkinter as ctk
from .sidebar import create_sidebar
from .inventory import InventoryDisplay
from .dashboard import Dashboard
from .login import LoginPage
from .utils import load_inventory, save_inventory
from config import  COLORS

class InventoryApp():
    def __init__(self):
        # Initialize window
        self.window = ctk.CTk()
        self.window.title("InMan")
        self.window.geometry("1200x700")
        
        # Set appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Configure grid layout
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        
        # Initialize data
        self.inventory = load_inventory()
        
        # Initialize sidebar and main content area
        create_sidebar(self.window, self)
        self.create_main_frame()
        
    def create_main_frame(self):
        self.main_frame = ctk.CTkFrame(self.window)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        # Initially show dashboard
        self.show_dashboard()
    
    def show_dashboard(self):
        self.clear_main_frame()
        Dashboard(self.main_frame, self.inventory).display()

    def show_login(self):
        self.clear_main_frame()
        LoginPage(self.main_frame, self.inventory).display()

    def show_inventory(self):
        self.clear_main_frame()
        InventoryDisplay(self.main_frame, self.inventory).display()

    def run(self):
        self.window.mainloop()

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

