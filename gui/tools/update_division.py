# gui/tools/update_division.py

import customtkinter as ctk
import tkinter.messagebox as messagebox
from config import COLORS
#from controllers.crud import update_division  

class UpdateDivision:
    def __init__(self, main_frame, return_to_manager):
        self.main_frame = main_frame
        self.return_to_manager = return_to_manager
        
        # Sample Division Data (replace with actual data source)
        self.divisions = [
            {"division_id": "DIV001", "name": "IT Department"},
            {"division_id": "DIV002", "name": "HR Department"},
            {"division_id": "DIV003", "name": "Finance Department"},
            {"division_id": "DIV004", "name": "Marketing Department"},
            {"division_id": "DIV005", "name": "Sales Department"}
        ]
        self.filtered_divisions = self.divisions.copy()

    def create_header(self):
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # Back Button
        back_button = ctk.CTkButton(
            header_frame,
            text="<- Back to Manager Tools",
            command=self.return_to_manager,
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        back_button.pack(side="left")
        
        # Title
        title = ctk.CTkLabel(
            header_frame,
            text="Update Divisions",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["white"]
        )
        title.pack(side="left", padx=20)

        # Search and Filter Section
        search_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        search_frame.pack(side="right")
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search divisions...",
            width=200,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["black"],
            border_color=COLORS["ash"]
        )
        self.search_entry.pack(side="left", padx=5)
        
        search_button = ctk.CTkButton(
            search_frame,
            text="Search",
            command=self.perform_search,
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=100,
            height=40
        )
        search_button.pack(side="left", padx=5)

    def create_divisions_view(self):
        # Destroy existing container if it exists
        if hasattr(self, 'container'):
            self.container.destroy()

        # Main Container
        self.container = ctk.CTkFrame(
            self.main_frame,
            fg_color=COLORS["secondary_bg"],
            corner_radius=15,
            border_width=2,
            border_color=COLORS["white"]
        )
        self.container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Scrollable Frame
        self.divisions_scroll = ctk.CTkScrollableFrame(
            self.container,
            fg_color="transparent",
            scrollbar_button_color=COLORS["pink"],
            scrollbar_button_hover_color=COLORS["darker_pink"]
        )
        self.divisions_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # Configure grid columns
        for i in range(4):  # 4 columns
            self.divisions_scroll.grid_columnconfigure(i, weight=1)

        # Create Headers
        headers = ["Division ID", "Name", "Employee Count", "Action"]
        for col, header in enumerate(headers):
            header_frame = ctk.CTkFrame(self.divisions_scroll, fg_color=COLORS["black"])
            header_frame.grid(row=0, column=col, padx=2, pady=2, sticky="nsew")
            
            ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=COLORS["white"]
            ).pack(padx=10, pady=8)
        
        # Add Divisions
        for idx, division in enumerate(self.filtered_divisions, 1):
            self.create_division_row(idx, division)

    def create_division_row(self, row_idx, division):
        # Division Details Cells
        details = [
            ("division_id", 150),
            ("name", 250),
        ]

        for col, (key, width) in enumerate(details):
            cell_frame = ctk.CTkFrame(self.divisions_scroll, fg_color=COLORS["black"])
            cell_frame.grid(row=row_idx, column=col, padx=2, pady=2, sticky="nsew")
            
            ctk.CTkLabel(
                cell_frame,
                text=str(division.get(key, "N/A")),
                font=ctk.CTkFont(size=13),
                wraplength=width-20
            ).pack(padx=10, pady=8)
        
        # Employee Count Cell (placeholder)
        emp_count_frame = ctk.CTkFrame(self.divisions_scroll, fg_color=COLORS["black"])
        emp_count_frame.grid(row=row_idx, column=2, padx=2, pady=2, sticky="nsew")
        
        ctk.CTkLabel(
            emp_count_frame,
            text="5",  # Placeholder - replace with actual employee count
            font=ctk.CTkFont(size=13)
        ).pack(padx=10, pady=8)
        
        # Action Cell
        action_frame = ctk.CTkFrame(self.divisions_scroll, fg_color=COLORS["black"])
        action_frame.grid(row=row_idx, column=3, padx=2, pady=2, sticky="nsew")
        
        update_button = ctk.CTkButton(
            action_frame,
            text="Update",
            command=lambda d=division: self.open_update_dialog(d),
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=100
        )
        update_button.pack(padx=10, pady=8)

    def open_update_dialog(self, division):
        # Create a top-level window for updating division details
        self.update_window = ctk.CTkToplevel(self.main_frame)
        self.update_window.title(f"Update Division: {division['division_id']}")
        self.update_window.geometry("500x300")
        self.update_window.configure(fg_color=COLORS["secondary_bg"])
        self.update_window.grab_set()
        self.update_window.lift()
        self.update_window.focus_force()
        self.update_window.protocol("WM_DELETE_WINDOW", self.update_window.destroy)

        # Division Name Entry
        name_label = ctk.CTkLabel(self.update_window, text="Division Name:", font=ctk.CTkFont(size=14))
        name_label.pack(pady=(20, 5))
        name_entry = ctk.CTkEntry(
            self.update_window, 
            width=300, 
            height=40, 
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["black"],
            border_color=COLORS["ash"],
            placeholder_text=division['name']
        )
        name_entry.pack(pady=5)

        # Update Button
        update_btn = ctk.CTkButton(
            self.update_window,
            text="Update",
            command=lambda: self.update_division(division['division_id'], name_entry.get(), self.update_window),
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=120,
            height=35,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        update_btn.pack(pady=(20, 10))

    def update_division(self, division_id, new_name, window):
        # Simulate updating division details
        messagebox.showinfo("Success", f"Division {division_id} updated to '{new_name}' successfully.")
        window.destroy()
        self.create_divisions_view()  # Refresh the division view

    def perform_search(self):
        search_term = self.search_entry.get().lower()
        self.filtered_divisions = [
            div for div in self.divisions 
            if (search_term in div["division_id"].lower() or 
                search_term in div["name"].lower())
        ]
        
        # Refresh the division view
        self.create_divisions_view()

    def display(self):
        self.clear_main_frame()
        self.create_header()
        self.create_divisions_view()

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()