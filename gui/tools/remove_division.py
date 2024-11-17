# gui/tools/remove_division.py

import customtkinter as ctk
import tkinter.messagebox as messagebox
from config import COLORS
from controllers.crud import delete_division, get_all_divisions

class RemoveDivision:
    def __init__(self, main_frame, return_to_manager):
        self.main_frame = main_frame
        self.return_to_manager = return_to_manager
        
        self.divisions = get_all_divisions()
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
            text="Remove Divisions",
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
        # Main Container
        container = ctk.CTkFrame(
            self.main_frame,
            fg_color=COLORS["secondary_bg"],
            corner_radius=15,
            border_width=2,
            border_color=COLORS["white"]
        )
        container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Scrollable Frame
        self.divisions_scroll = ctk.CTkScrollableFrame(
            container,
            fg_color="transparent",
            scrollbar_button_color=COLORS["pink"],
            scrollbar_button_hover_color=COLORS["darker_pink"]
        )
        self.divisions_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # Create Headers
        headers = ["Division ID", "Name", "Action"]
        for col, header in enumerate(headers):
            header_frame = ctk.CTkFrame(self.divisions_scroll, fg_color=COLORS["black"])
            header_frame.grid(row=0, column=col, padx=2, pady=2, sticky="nsew")
            
            ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=COLORS["white"]
            ).pack(padx=10, pady=8)

        for i in range(len(headers)):
            self.divisions_scroll.grid_columnconfigure(i, weight=1)
        
        # Add Divisions
        for idx, division in enumerate(self.filtered_divisions, 1):
            self.create_division_row(idx, division)

    def create_division_row(self, row_idx, division):
        # Division ID Cell
        for col, (key, width) in enumerate([
            ("division_id", 100), 
            ("name", 200)
        ]):
            cell_frame = ctk.CTkFrame(self.divisions_scroll, fg_color=COLORS["black"])
            cell_frame.grid(row=row_idx, column=col, padx=2, pady=2, sticky="nsew")
            
            ctk.CTkLabel(
                cell_frame,
                text=division[key],
                font=ctk.CTkFont(size=12),
                text_color=COLORS["white"]
            ).pack(padx=10, pady=5)

        # Action Button
        action_frame = ctk.CTkFrame(self.divisions_scroll, fg_color=COLORS["black"])
        action_frame.grid(row=row_idx, column=2, padx=2, pady=2, sticky="nsew")
        
        remove_button = ctk.CTkButton(
            action_frame,
            text="Remove",
            command=lambda div=division: self.confirm_remove_division(division),
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"]
        )
        remove_button.pack(padx=10, pady=5)

    def perform_search(self):
        search_term = self.search_entry.get().lower()
        self.filtered_divisions = [div for div in self.divisions if search_term in div["name"].lower()]
        self.display()

    def confirm_remove_division(self, division):
        confirm = messagebox.askyesno(
            "Confirm Removal", 
            f"Are you sure you want to remove the Division:\n{division['division_id']} - {division['name']}?"
        )

        if confirm:
            self.remove_division(division)

    def remove_division(self, division):
        # Call the delete function from the controller
        action = delete_division(division['division_id'])
        self.divisions = get_all_divisions()
        self.filtered_divisions = self.divisions.copy()
        self.display()

    def display(self):
        self.clear_main_frame()
        self.create_header()
        self.create_divisions_view()

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()