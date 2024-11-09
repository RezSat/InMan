import customtkinter as ctk
import json
from datetime import datetime

class InventoryApp:
    def __init__(self):
        # Initialize window
        self.window = ctk.CTk()
        self.window.title("Inventory Management System")
        self.window.geometry("1200x700")
        
        # Set appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Configure grid layout
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)
        
        # Initialize data
        self.inventory = []
        self.load_inventory()
        
        self.create_sidebar()
        self.create_main_frame()
        
    def create_sidebar(self):
        # Sidebar frame
        sidebar = ctk.CTkFrame(self.window, width=200, corner_radius=0)
        sidebar.grid(row=0, column=0, rowspan=4, sticky="nsew")
        sidebar.grid_propagate(False)
        
        # Logo label
        logo_label = ctk.CTkLabel(sidebar, text="Inventory\nManager", font=ctk.CTkFont(size=20, weight="bold"))
        logo_label.grid(row=0, column=0, padx=20, pady=20)
        
        # Sidebar buttons
        btn_dashboard = ctk.CTkButton(sidebar, text="Dashboard", command=self.show_dashboard)
        btn_dashboard.grid(row=1, column=0, padx=20, pady=10)
        
        btn_add = ctk.CTkButton(sidebar, text="Add Item", command=self.show_add_item)
        btn_add.grid(row=2, column=0, padx=20, pady=10)
        
        btn_view = ctk.CTkButton(sidebar, text="View Inventory", command=self.show_inventory)
        btn_view.grid(row=3, column=0, padx=20, pady=10)
        
        # Version label at bottom
        version_label = ctk.CTkLabel(sidebar, text="v1.0")
        version_label.grid(row=4, column=0, padx=20, pady=20, sticky="s")
        
    def create_main_frame(self):
        # Main content frame
        self.main_frame = ctk.CTkFrame(self.window)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        # Initially show dashboard
        self.show_dashboard()
        
    def show_dashboard(self):
        self.clear_main_frame()
        
        # Dashboard title
        title = ctk.CTkLabel(self.main_frame, text="Dashboard", font=ctk.CTkFont(size=24, weight="bold"))
        title.grid(row=0, column=0, padx=20, pady=20, columnspan=2)
        
        # Stats frames
        stats_frame1 = ctk.CTkFrame(self.main_frame)
        stats_frame1.grid(row=1, column=0, padx=10, pady=10)
        
        total_items = len(self.inventory)
        total_value = sum(float(item['price']) * float(item['quantity']) for item in self.inventory)
        
        # Stats labels
        ctk.CTkLabel(stats_frame1, text=f"Total Items: {total_items}", font=ctk.CTkFont(size=16)).pack(padx=20, pady=10)
        ctk.CTkLabel(stats_frame1, text=f"Total Value: ${total_value:.2f}", font=ctk.CTkFont(size=16)).pack(padx=20, pady=10)
        
    def show_add_item(self):
        self.clear_main_frame()
        
        # Add item form
        title = ctk.CTkLabel(self.main_frame, text="Add New Item", font=ctk.CTkFont(size=24, weight="bold"))
        title.grid(row=0, column=0, padx=20, pady=20, columnspan=2)
        
        # Form fields
        labels = ['Item Name:', 'Category:', 'Quantity:', 'Price:', 'Description:']
        self.entries = {}
        
        for i, label in enumerate(labels):
            ctk.CTkLabel(self.main_frame, text=label).grid(row=i+1, column=0, padx=20, pady=10)
            if label == 'Description:':
                self.entries[label] = ctk.CTkTextbox(self.main_frame, height=100)
            else:
                self.entries[label] = ctk.CTkEntry(self.main_frame)
            self.entries[label].grid(row=i+1, column=1, padx=20, pady=10, sticky="ew")
        
        # Submit button
        submit_btn = ctk.CTkButton(self.main_frame, text="Add Item", command=self.add_item)
        submit_btn.grid(row=len(labels)+1, column=0, columnspan=2, pady=20)
        
    def show_inventory(self):
        self.clear_main_frame()
        
        # Inventory title
        title = ctk.CTkLabel(self.main_frame, text="Current Inventory", font=ctk.CTkFont(size=24, weight="bold"))
        title.grid(row=0, column=0, padx=20, pady=20, columnspan=4)
        
        # Headers
        headers = ['Item Name', 'Category', 'Quantity', 'Price', 'Actions']
        for i, header in enumerate(headers):
            ctk.CTkLabel(self.main_frame, text=header, font=ctk.CTkFont(weight="bold")).grid(row=1, column=i, padx=10, pady=10)
        
        # Inventory items
        for i, item in enumerate(self.inventory):
            ctk.CTkLabel(self.main_frame, text=item['name']).grid(row=i+2, column=0, padx=10, pady=5)
            ctk.CTkLabel(self.main_frame, text=item['category']).grid(row=i+2, column=1, padx=10, pady=5)
            ctk.CTkLabel(self.main_frame, text=item['quantity']).grid(row=i+2, column=2, padx=10, pady=5)
            ctk.CTkLabel(self.main_frame, text=f"${item['price']}").grid(row=i+2, column=3, padx=10, pady=5)
            
            # Action buttons
            actions_frame = ctk.CTkFrame(self.main_frame)
            actions_frame.grid(row=i+2, column=4, padx=10, pady=5)
            
            edit_btn = ctk.CTkButton(actions_frame, text="Edit", width=60, command=lambda x=item: self.edit_item(x))
            edit_btn.pack(side="left", padx=5)
            
            delete_btn = ctk.CTkButton(actions_frame, text="Delete", width=60, fg_color="red", command=lambda x=item: self.delete_item(x))
            delete_btn.pack(side="left", padx=5)
    
    def add_item(self):
        # Get values from entries
        new_item = {
            'name': self.entries['Item Name:'].get(),
            'category': self.entries['Category:'].get(),
            'quantity': self.entries['Quantity:'].get(),
            'price': self.entries['Price:'].get(),
            'description': self.entries['Description:'].get("1.0", "end-1c"),
            'date_added': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.inventory.append(new_item)
        self.save_inventory()
        self.show_inventory()
    
    def edit_item(self, item):
        # Implement edit functionality
        pass
    
    def delete_item(self, item):
        self.inventory.remove(item)
        self.save_inventory()
        self.show_inventory()
    
    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def load_inventory(self):
        try:
            with open('inventory.json', 'r') as file:
                self.inventory = json.load(file)
        except FileNotFoundError:
            self.inventory = []
    
    def save_inventory(self):
        with open('inventory.json', 'w') as file:
            json.dump(self.inventory, file, indent=4)
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = InventoryApp()
    app.run()