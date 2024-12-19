# gui/tools/update_division.py

import customtkinter as ctk
import tkinter.messagebox as messagebox
from config import COLORS
from controllers.crud import (
    get_all_divisions_with_counts, 
    update_dvision,  # Note: There's a typo in the original function name, should be update_division
    create_division
)

class UpdateDivision:
    def __init__(self, main_frame, return_to_manager):
        self.main_frame = main_frame
        self.return_to_manager = return_to_manager
        self.load_divisions()

    def load_divisions(self):
        """
        Load divisions from the database with their counts
        """
        try:
            self.divisions = get_all_divisions_with_counts()
            self.filtered_divisions = self.divisions.copy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load divisions: {str(e)}")
            self.divisions = []
            self.filtered_divisions = []

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

        # Search and Add Section
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

        # Add Division Button
        add_button = ctk.CTkButton(
            search_frame,
            text="+ Add Division",
            command=self.open_add_division_dialog,
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=100,
            height=40
        )
        add_button.pack(side="left", padx=5)

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
        
        # Employee Count Cell
        emp_count_frame = ctk.CTkFrame(self.divisions_scroll, fg_color=COLORS["black"])
        emp_count_frame.grid(row=row_idx, column=2, padx=2, pady=2, sticky="nsew")
        
        ctk.CTkLabel(
            emp_count_frame,
            text=str(division.get('employee_count', 0)),
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
        name_label = ctk.CTkLabel(self.update_window, text="Division Name:")
        name_label.pack(pady=(20, 5))

        self.name_entry = ctk.CTkEntry(self.update_window, width=300)
        self.name_entry.insert(0, division['name'])
        self.name_entry.pack(pady=(0, 20))

        # Update Button
        update_button = ctk.CTkButton(
            self.update_window,
            text="Update Division",
            command=lambda: self.update_division(division['division_id']),
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"]
        )
        update_button.pack(pady=10)

    def update_division(self, division_id):
        new_name = self.name_entry.get()
        try:
            update_dvision(division_id, new_name)  # Call the actual update function
            messagebox.showinfo("Success", "Division updated successfully!")
            self.update_window.destroy()
            self.load_divisions()  # Reload divisions to reflect changes
            self.create_divisions_view()  # Refresh the view
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update division: {str(e)}")

    def perform_search(self):
        search_term = self.search_entry.get().lower()
        self.filtered_divisions = [
            div for div in self.divisions if search_term in div['name'].lower()
        ]
        self.create_divisions_view()  # Refresh the view with filtered results

    def open_add_division_dialog(self):
        # Create a top-level window for adding a new division
        self.add_window = ctk.CTkToplevel(self.main_frame)
        self.add_window.title("Add New Division")
        self.add_window.geometry("500x200")
        self.add_window.configure(fg_color=COLORS["secondary_bg"])
        self.add_window.grab_set()
        self.add_window.lift()
        self.add_window.focus_force()
        self.add_window.protocol("WM_DELETE_WINDOW", self.add_window.destroy)

        # Division Name Entry
        name_label = ctk.CTkLabel(self.add_window, text="New Division Name:")
        name_label.pack(pady=(20, 5))

        self.new_name_entry = ctk.CTkEntry(self.add_window, width=300)
        self.new_name_entry.pack(pady=(0, 20))

        # Add Button
        add_button = ctk.CTkButton(
            self.add_window,
            text="Add Division",
            command=self.add_division,
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"]
        )
        add_button.pack(pady=10)

    def add_division(self):
        new_name = self.new_name_entry.get()
        try:
            create_division(new_name)  # Call the actual create function
            messagebox.showinfo("Success", "Division added successfully!")
            self.add_window.destroy()
            self.load_divisions()  # Reload divisions to reflect changes
            self.create_divisions_view()  # Refresh the view
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add division: {str(e)}")

    def display(self):
        self.clear_main_frame()
        self.create_header()
        self.create_divisions_view()

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()