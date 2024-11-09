import customtkinter as ctk

class InventoryDisplay:
    def __init__(self, main_frame, inventory):
        self.main_frame = main_frame
        self.inventory = inventory

    def display(self):
        # Clear the main frame and add inventory display logic here
        self.clear_main_frame()
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
    
    
    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
