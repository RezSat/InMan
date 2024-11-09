import customtkinter as ctk
from config import COLORS

def create_sidebar(window, app):
    sidebar = ctk.CTkFrame(window, width=200, corner_radius=6)
    sidebar.grid(row=0, column=0, rowspan=4, padx=20, pady=20, sticky="nsew")
    sidebar.grid_propagate(False)

    # Logo container frame to ensure proper alignment
    logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
    logo_frame.grid(row=0, column=0, padx=20, pady=20)

    # Split logo into two labels with different colors
    in_label = ctk.CTkLabel(
        logo_frame, 
        text="In",
        font=ctk.CTkFont(size=40, weight="bold", family="Verdana"),
        text_color=COLORS["pink"]
    )
    in_label.grid(row=0, column=0)

    man_label = ctk.CTkLabel(
        logo_frame,
        text="Man",
        font=ctk.CTkFont(size=40, weight="bold", family="Verdana"),
        text_color=COLORS['white']
    )
    man_label.grid(row=0, column=1)
    
    # Common button style configuration
    button_style = {
        "height": 40,
        "width": 140,
        "fg_color": COLORS["pink"],      # Background pink when not hovering
        "hover_color": COLORS["white"],   # Background white when hovering
        "text_color": COLORS["black"],    # Text color
        "font": ctk.CTkFont(size=16, weight="bold", family="futura"),
        "corner_radius": 8,
        "border_width": 1,               # Add border for better hover effect
        "border_color": COLORS["ash"]   # White border
    }
    
    # Sidebar buttons with consistent styling
    btn_dashboard = ctk.CTkButton(
        sidebar,
        text="Dashboard",
        command=app.show_dashboard,
        **button_style
    )
    btn_dashboard.grid(row=1, column=0, padx=20, pady=10)

    btn_add = ctk.CTkButton(
        sidebar,
        text="Login",
        command=app.show_login,
        **button_style
    )
    btn_add.grid(row=2, column=0, padx=20, pady=10)

    btn_view = ctk.CTkButton(
        sidebar,
        text="View Inventory",
        command=app.show_inventory,
        **button_style
    )
    btn_view.grid(row=3, column=0, padx=20, pady=10)

    # Version label at bottom
    version_label = ctk.CTkLabel(
        sidebar,
        text="v1.0",
        font=ctk.CTkFont(size=16, family="Verdana")
    )
    version_label.grid(row=4, column=0, padx=20, pady=20, sticky="s")

    btn_update = ctk.CTkButton(
        sidebar,
        text="Check for Updates",
        command=lambda: print('checking for updates'),
        **button_style
    )
    btn_update.grid(row=5, column=0, padx=20, pady=10)

    return sidebar