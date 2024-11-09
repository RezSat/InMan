import customtkinter as ctk

class Dashboard:
    def __init__(self, main_frame, inventory):
        self.main_frame = main_frame
        self.inventory = inventory
    
    def display(self):
        # Clear the main frame and display dashboard stats
        self.clear_main_frame()
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


    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
