import customtkinter as ctk
from config import COLORS
import os
import zipfile
import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime

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
        text="Package to Share",
        command=self_package_application,
        **button_style
    )
    btn_update.grid(row=5, column=0, padx=20, pady=10)

    return sidebar

def self_package_application():
    """
    Self-package the application into a zip file
    """
    try:
        # Get the current directory
        current_dir = os.getcwd()
        
        # Prompt user to choose save location for the zip file
        save_path = filedialog.asksaveasfilename(
            defaultextension=".zip",
            filetypes=[("Zip files", "*.zip")],
            title="Save Packaged Application"
        )
        
        # Check if user cancelled
        if not save_path:
            return
        
        # List of required files and folders
        required_items = [
            '.db',  # Database file
            '.exe',  # Executable
            '_internal'  # Internal folder created by PyInstaller
        ]
        
        # Create a zip file
        with zipfile.ZipFile(save_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Walk through the current directory
            for root, dirs, files in os.walk(current_dir):
                for file in files:
                    # Check if file matches required extensions
                    if any(item in file for item in required_items):
                        file_path = os.path.join(root, file)
                        # Add file to zip, preserving directory structure
                        arcname = os.path.relpath(file_path, current_dir)
                        zipf.write(file_path, arcname)
                
                # Add _internal folder if it exists
                for dir in dirs:
                    if dir == '_internal':
                        dir_path = os.path.join(root, dir)
                        for subroot, subdirs, subfiles in os.walk(dir_path):
                            for subfile in subfiles:
                                file_path = os.path.join(subroot, subfile)
                                arcname = os.path.relpath(file_path, current_dir)
                                zipf.write(file_path, arcname)
        
        # Get file size of the created zip
        zip_size = os.path.getsize(save_path)
        
        # Show success message
        messagebox.showinfo(
            "Packaging Successful",
            f"Application packaged successfully!\n"
            f"Save Location: {save_path}\n"
            f"File Size: {zip_size / (1024 * 1024):.2f} MB"
        )
    
    except Exception as e:
        # Show error message if something goes wrong
        messagebox.showerror(
            "Packaging Error", 
            f"Failed to package application:\n{str(e)}"
        )

# Optional: Add a method to create a timestamped backup
def create_timestamped_backup():
    """
    Create a timestamped backup of the application
    """
    try:
        # Get the current directory
        current_dir = os.getcwd()
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create backup filename
        backup_filename = f"InMan_Backup_{timestamp}.zip"
        
        # Create a zip file
        with zipfile.ZipFile(backup_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Walk through the current directory
            for root, dirs, files in os.walk(current_dir):
                for file in files:
                    # Exclude certain files/folders if needed
                    if not any(exclude in file for exclude in ['.log', '.tmp']):
                        file_path = os.path.join(root, file)
                        # Add file to zip, preserving directory structure
                        arcname = os.path.relpath(file_path, current_dir)
                        zipf.write(file_path, arcname)
        
        # Get file size of the backup
        backup_size = os.path.getsize(backup_filename)
        
        # Show success message
        messagebox.showinfo(
            "Backup Successful",
            f"Backup created successfully!\n"
            f"Backup Location: {backup_filename}\n"
            f"File Size: {backup_size / (1024 * 1024):.2f} MB"
        )
    
    except Exception as e:
        # Show error message if something goes wrong
        messagebox.showerror(
            "Backup Error", 
            f"Failed to create backup:\n{str(e)}"
        )

# Optional: Add to your menu or toolbar
def setup_packaging_menu(self):
    """
    Add packaging options to a menu
    """
    packaging_menu = tk.Menu(self.menubar, tearoff=0)
    packaging_menu.add_command(
        label="Package Application", 
        command=self_package_application
    )
    packaging_menu.add_command(
        label="Create Backup", 
        command=create_timestamped_backup
    )
    self.menubar.add_cascade(label="Packaging", menu=packaging_menu)