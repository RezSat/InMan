import customtkinter as ctk
from config import COLORS
from gui.manager import ManagerTools

class LoginPage:
    def __init__(self, main_frame, app):
        self.main_frame = main_frame
        self.app = app
        self.entries = {}
        
    def display(self):
        self.clear_main_frame()
        
        # Create a container frame for centering the login form
        container = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Logo and Welcome text
        logo_frame = ctk.CTkFrame(container, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=20, pady=(20, 30))
        
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
        
        welcome_label = ctk.CTkLabel(
            container,
            text="Login! to be the Inventory Manager",
            font=ctk.CTkFont(size=20, weight="bold", family="Verdana")
        )
        welcome_label.grid(row=1, column=0, pady=(0, 20))
        
        # Login form frame
        form_frame = ctk.CTkFrame(
            container,
            fg_color=COLORS.get("secondary_bg", "transparent"),
            corner_radius=15,
            border_width=2,
            border_color=COLORS["pink"]
        )
        form_frame.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")
        
        # Username field
        username_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        username_frame.grid(row=0, column=0, padx=30, pady=(30, 15), sticky="ew")
        
        username_label = ctk.CTkLabel(
            username_frame,
            text="Username",
            font=ctk.CTkFont(size=14, family="Verdana")
        )
        username_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.entries["username"] = ctk.CTkEntry(
            username_frame,
            width=300,
            height=40,
            placeholder_text="Enter your username",
            border_color=COLORS["pink"],
            corner_radius=8
        )
        self.entries["username"].grid(row=1, column=0)
        
        # Password field
        password_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        password_frame.grid(row=1, column=0, padx=30, pady=15, sticky="ew")
        
        password_label = ctk.CTkLabel(
            password_frame,
            text="Password",
            font=ctk.CTkFont(size=14, family="Verdana")
        )
        password_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.entries["password"] = ctk.CTkEntry(
            password_frame,
            width=300,
            height=40,
            placeholder_text="Enter your password",
            show="•",
            border_color=COLORS["pink"],
            corner_radius=8
        )
        self.entries["password"].grid(row=1, column=0)
        
        
        # Login button
        login_button = ctk.CTkButton(
            form_frame,
            text="Login",
            command=self.handle_login,
            width=300,
            height=40,
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            text_color=COLORS["white"],
            font=ctk.CTkFont(size=15, weight="bold"),
            corner_radius=8
        )
        login_button.grid(row=3, column=0, padx=30, pady=(15, 30))
        

    def handle_login(self):
        username = self.entries["username"].get()
        password = self.entries["password"].get()
        # Add your login logic here
        self.main_frame.master.winfo_children()[0].winfo_children()[2].configure(text="Manger Tools")
        self.main_frame.master.winfo_children()[0].winfo_children()[2].configure(command=self.show_manager_tools)
        self.clear_main_frame()
        self.show_manager_tools()

        print(self.app)
        print(f"Login attempt with username: {username}")

    def show_manager_tools(self):
        self.clear_main_frame()
        ManagerTools(self.main_frame, self.app).display()
              
    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()