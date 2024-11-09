import customtkinter as ctk

def create_sidebar(window, app):
    sidebar = ctk.CTkFrame(window, width=200, corner_radius=0)
    sidebar.grid(row=0, column=0, rowspan=4, sticky="nsew")
    sidebar.grid_propagate(False)

    # Logo label
    logo_label = ctk.CTkLabel(sidebar, text="InMan", font=ctk.CTkFont(size=20, weight="bold"))
    logo_label.grid(row=0, column=0, padx=20, pady=20)

    # Sidebar buttons
    btn_dashboard = ctk.CTkButton(sidebar, text="Dashboard", command=app.show_dashboard)
    btn_dashboard.grid(row=1, column=0, padx=20, pady=10)

    btn_add = ctk.CTkButton(sidebar, text="Add Item", command=app.show_add_item)
    btn_add.grid(row=2, column=0, padx=20, pady=10)

    btn_view = ctk.CTkButton(sidebar, text="View Inventory", command=app.show_inventory)
    btn_view.grid(row=3, column=0, padx=20, pady=10)

    # Version label at bottom
    version_label = ctk.CTkLabel(sidebar, text="v1.0")
    version_label.grid(row=4, column=0, padx=20, pady=20, sticky="s")

    btn_update = ctk.CTkButton(sidebar, text="Check for Updates", command=print('checking for updates'))
    btn_update.grid(row=5, column=0, padx=20, pady=10)
