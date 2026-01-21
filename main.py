import customtkinter as ctk
from gui.ui import InventoryApp
from models import initialize_database
import hashlib
import winreg
import webbrowser

COLORS = {
    'black': '#2c363f',
    'pink': '#e75a7c',
    'darker_pink': '#8F344A',
    'white': '#f2f5ea',
    'ash': '#d6dbd2',
    'green': '#4CAF50',
    "secondary_bg": "#1A1A1A",
}

class ProductKeyPrompt:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Enter the Product Key to Unlock InMan")
        self.root.geometry("550x600")
        self.root.configure(fg_color=COLORS['secondary_bg'])
        self.hashkey = "c052eb83528666dfb18df5d39cf6ab1c3058bb7b5720135a1012b5a3ba093042"
        self.show_key = False
        
        # Center the window on screen
        self.center_window()
        
        # Create main container for centering
        container = ctk.CTkFrame(
            self.root,
            fg_color="transparent"
        )
        container.place(relx=0.5, rely=0.5, anchor="center")

        # Logo Frame
        logo_frame = ctk.CTkFrame(container, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=20, pady=(20, 10))  # Reduced bottom padding
        
        # InMan logo with split colors
        in_label = ctk.CTkLabel(
            logo_frame,
            text="In",
            font=ctk.CTkFont(size=48, weight="bold", family="Verdana"),
            text_color=COLORS["pink"]
        )
        in_label.grid(row=0, column=0)
        
        man_label = ctk.CTkLabel(
            logo_frame,
            text="Man",
            font=ctk.CTkFont(size=48, weight="bold", family="Verdana"),
            text_color=COLORS["white"]
        )
        man_label.grid(row=0, column=1)

        # Software credit with clickable link
        credit_frame = ctk.CTkFrame(container, fg_color="transparent")
        credit_frame.grid(row=1, column=0, pady=(0, 20))
        
        credit_label = ctk.CTkLabel(
            credit_frame,
            text="Software by RezSat: ",
            font=ctk.CTkFont(size=14, family="Verdana"),
            text_color=COLORS["white"]
        )
        credit_label.grid(row=0, column=0)
        
        link_label = ctk.CTkLabel(
            credit_frame,
            text="http://rezsat.vercel.app",
            font=ctk.CTkFont(size=14, family="Verdana", underline=True),
            text_color=COLORS["pink"],
            cursor="hand2"
        )
        link_label.grid(row=0, column=1)
        link_label.bind("<Button-1>", lambda e: webbrowser.open("http://rezsat.vercel.app"))

        # Welcome text
        welcome_label = ctk.CTkLabel(
            container,
            text="Enter Product Key to Unlock",
            font=ctk.CTkFont(size=20, weight="bold", family="Verdana")
        )
        welcome_label.grid(row=2, column=0, pady=(0, 20))

        # Main form frame
        self.form_frame = ctk.CTkFrame(
            container,
            fg_color=COLORS.get("secondary_bg", "transparent"),
            corner_radius=15,
            border_width=2,
            border_color=COLORS["pink"]
        )
        self.form_frame.grid(row=3, column=0, padx=20, pady=20, sticky="nsew")

        # Product key entry frame
        key_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        key_frame.grid(row=0, column=0, padx=30, pady=(30, 15), sticky="ew")

        # Product key label
        key_label = ctk.CTkLabel(
            key_frame,
            text="Product Key",
            font=ctk.CTkFont(size=14, family="Verdana")
        )
        key_label.grid(row=0, column=0, sticky="w", pady=(0, 5))

        # Entry frame to contain both entry and toggle button
        entry_container = ctk.CTkFrame(key_frame, fg_color="transparent")
        entry_container.grid(row=1, column=0, sticky="ew")

        # Product key entry
        self.key_entry = ctk.CTkEntry(
            entry_container,
            width=350,
            height=45,
            placeholder_text="Enter your product key",
            border_color=COLORS["pink"],
            corner_radius=8,
            show="•"
        )
        self.key_entry.grid(row=0, column=0, padx=(0, 10))

        # Toggle visibility button
        self.toggle_button = ctk.CTkButton(
            entry_container,
            text="👁",
            width=45,
            height=45,
            command=self.toggle_key_visibility,
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            corner_radius=8
        )
        self.toggle_button.grid(row=0, column=1)

        # Unlock button
        self.unlock_button = ctk.CTkButton(
            self.form_frame,
            text="Unlock InMan",
            command=self.check_product_key,
            width=350,
            height=45,
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            text_color=COLORS["white"],
            font=ctk.CTkFont(size=15, weight="bold"),
            corner_radius=8
        )
        self.unlock_button.grid(row=2, column=0, padx=30, pady=(15, 30))

        # Error message label (hidden by default)
        self.error_label = ctk.CTkLabel(
            self.form_frame,
            text="",
            text_color=COLORS["pink"],
            font=ctk.CTkFont(size=14, family="Verdana")
        )
        self.error_label.grid(row=3, column=0, pady=(0, 15))

    def center_window(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 550
        window_height = 600
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def toggle_key_visibility(self):
        self.show_key = not self.show_key
        if self.show_key:
            self.key_entry.configure(show="")
            self.toggle_button.configure(text="🔒")
        else:
            self.key_entry.configure(show="•")
            self.toggle_button.configure(text="👁")

    def check_product_key(self):
        product_key = self.key_entry.get()
        hashed_product_key = hashlib.sha256(product_key.upper().encode()).hexdigest()
        
        if hashed_product_key == self.hashkey:
            try:
                reg_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, "Software\\InMan")
                winreg.SetValueEx(reg_key, "ProductKey", 0, winreg.REG_SZ, hashed_product_key)
                winreg.CloseKey(reg_key)
                self.root.destroy()
                initialize_database()
                app = InventoryApp()
                app.run()
            except Exception as e:
                self.error_label.configure(text=f"Error: {str(e)}")
        else:
            self.error_label.configure(text="Invalid Product Key")
            self.key_entry.configure(border_color="red")
            self.root.after(2000, lambda: self.key_entry.configure(border_color=COLORS["pink"]))

    def run(self):
        try:
            reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\InMan")
            product_key = winreg.QueryValueEx(reg_key, "ProductKey")[0]
            winreg.CloseKey(reg_key)
            if product_key == self.hashkey:
                self.root.destroy()
                initialize_database()
                app = InventoryApp()
                app.run()
            else:
                self.root.mainloop()
        except Exception:
            self.root.mainloop()

if __name__ == "__main__":
    product_key_prompt = ProductKeyPrompt()
    product_key_prompt.run()