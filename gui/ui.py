#gui/ui.py
import customtkinter as ctk
from .sidebar import create_sidebar
from .inventory import InventoryDisplay
from .dashboard import Dashboard
from .login import LoginPage
from .utils import load_inventory, save_inventory, clear_children
from config import  COLORS

class InventoryApp():
    def __init__(self):
        # Initialize window
        self.window = ctk.CTk()
        self.window.title("InMan")
        self.window.geometry("1200x700")

        # centering the window
        self.window.update_idletasks()
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        window_width = 1200
        window_height = 700

        # calculate position x and y coordinates
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.window.geometry(f'{window_width}x{window_height}+{x}+{y-20}')

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
    
    def _show_screen(self, screen):
        self.clear_main_frame()
        screen(self.main_frame, self.inventory).display()

    def show_dashboard(self):
        self._show_screen(Dashboard)

    def show_login(self):
        self._show_screen(LoginPage)

    def show_inventory(self):
        self._show_screen(InventoryDisplay)

    def run(self):
        self.window.mainloop()

    def clear_main_frame(self):
        clear_children(self.main_frame)

