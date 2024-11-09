import customtkinter as ctk
import tkinter as tk
from tkinter import font

def show_available_fonts(window):
    # Get all available system fonts
    available_fonts = sorted(font.families())
    
    # Create a frame to display font examples
    font_frame = ctk.CTkScrollableFrame(window, width=600, height=400)
    font_frame.grid(row=0, column=0, padx=20, pady=20)
    
    # Display some sample fonts
    sample_text = "InMan"
    
    # Modern and professional fonts that are commonly available
    showcase_fonts = [
        ("Helvetica", "Modern and Clean"),
        ("Arial Black", "Bold and Professional"),
        ("Verdana", "Clear and Modern"),
        ("Tahoma", "Professional"),
        ("Georgia", "Elegant"),
        ("Segoe UI", "Modern UI"),
        ("Trebuchet MS", "Dynamic"),
        ("Calibri", "Contemporary"),
        ("Futura", "Minimalist"),
        ("Century Gothic", "Modern Geometric")
    ]
    
    for i, (font_name, description) in enumerate(showcase_fonts):
        try:
            # Create a frame for each font example
            example_frame = ctk.CTkFrame(font_frame)
            example_frame.grid(row=i, column=0, padx=10, pady=5, sticky="ew")
            
            # Split "InMan" into two colors with the selected font
            in_label = ctk.CTkLabel(
                example_frame,
                text="In",
                font=ctk.CTkFont(family=font_name, size=40, weight="bold"),
                text_color="#FF69B4"  # Pink
            )
            in_label.grid(row=0, column=0, padx=(10, 0))
            
            man_label = ctk.CTkLabel(
                example_frame,
                text="Man",
                font=ctk.CTkFont(family=font_name, size=40, weight="bold"),
                text_color="white"
            )
            man_label.grid(row=0, column=1, padx=(0, 10))
            
            # Add font description
            desc_label = ctk.CTkLabel(
                example_frame,
                text=f"{font_name} - {description}",
                font=ctk.CTkFont(size=12),
                text_color="gray"
            )
            desc_label.grid(row=1, column=0, columnspan=2, pady=(0, 5))
            
        except Exception as e:
            continue

# Example usage
if __name__ == "__main__":
    app = ctk.CTk()
    app.title("Font Showcase")
    show_available_fonts(app)
    app.mainloop()

# Modified sidebar code with a more modern font
def create_sidebar(window, app):
    sidebar = ctk.CTkFrame(window, width=200, corner_radius=0)
    sidebar.grid(row=0, column=0, rowspan=4, sticky="nsew")
    sidebar.grid_propagate(False)

    # Logo container frame
    logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
    logo_frame.grid(row=0, column=0, padx=20, pady=20)

    # Modern font choice - you can replace "Helvetica" with any font from the showcase
    in_label = ctk.CTkLabel(
        logo_frame, 
        text="In",
        font=ctk.CTkFont(family="Helvetica", size=60, weight="bold"),
        text_color=COLORS["pink"]
    )
    in_label.grid(row=0, column=0)

    man_label = ctk.CTkLabel(
        logo_frame,
        text="Man",
        font=ctk.CTkFont(family="Helvetica", size=60, weight="bold"),
        text_color="white"
    )
    man_label.grid(row=0, column=1)
    
    # Rest of the sidebar code...
    # (Previous button and label implementations remain the same)