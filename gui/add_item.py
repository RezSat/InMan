import customtkinter as ctk

class AddItemForm:
    def __init__(self, main_frame, inventory):
        self.main_frame = main_frame
        self.inventory = inventory
        self.entries = {}

    def display(self):
        self.clear_main_frame()
        
        # Form fields and submit button
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
    
    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
