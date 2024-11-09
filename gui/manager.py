import customtkinter as ctk

class ManagerTools():
    def __init__(self, main_frame, inventory):
        self.main_frame = main_frame
        self.inventory = inventory

    def display(self):
        self.clear_main_frame()
        title = ctk.CTkLabel(self.main_frame, text="Manager Tools", font=ctk.CTkFont(size=24, weight="bold"))
        title.grid(row=0, column=0, padx=20, pady=20, columnspan=2)

        button_card_style = {
            
        }

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()