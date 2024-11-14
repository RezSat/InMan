# gui/tools/view_division_structure.py

import customtkinter as ctk
import tkinter.messagebox as messagebox
from config import COLORS

class ViewDivisionStructure:
    def __init__(self, main_frame, return_to_manager):
        self.main_frame = main_frame
        self.return_to_manager = return_to_manager
        
        # Sample Division Data matching the model structure
        self.divisions = [
            {
                "division_id": 1, 
                "name": "IT Department", 
                "employee_count": 15,
                "items": [
                    {"name": "Laptop", "count": 20},
                    {"name": "Desktop", "count": 10},
                    {"name": "Monitor", "count": 15}
                ]
            },
            {
                "division_id": 2, 
                "name": "HR Department", 
                "employee_count": 10,
                "items": [
                    {"name": "Printer", "count": 5},
                    {"name": "Scanner", "count": 3},
                    {"name": "Conference Phone", "count": 2}
                ]
            }
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
            text="Division Structure",
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
        for i in range(5):  # 5 columns
            self.divisions_scroll.grid_columnconfigure(i, weight=1)

        # Create Headers
        headers = ["Division ID", "Name", "Employees", "Total Items", "Action"]
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
            ("division_id", 100),
            ("name", 200),
            ("employee_count", 100)
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
        
        # Total Items Cell
        total_items = sum(item['count'] for item in division.get('items', []))
        total_items_frame = ctk.CTkFrame(self.divisions_scroll, fg_color=COLORS["black"])
        total_items_frame.grid(row=row_idx, column=3, padx=2, pady=2, sticky="nsew")
        
        ctk.CTkLabel(
            total_items_frame,
            text=str(total_items),
            font=ctk.CTkFont(size=13)
        ).pack(padx=10, pady=8)
        
        # Action Cell
        action_frame = ctk.CTkFrame(self.divisions_scroll, fg_color=COLORS["black"])
        action_frame.grid(row=row_idx, column=4, padx=2, pady=2, sticky="nsew")
        
        view_button = ctk.CTkButton(
            action_frame,
            text="View Items",
            command=lambda d=division: self.show_division_items(d),
            fg_color=COLORS["darker_pink"],
            hover_color=COLORS["pink"],
            width=100
        )
        view_button.pack(padx=10, pady=8)

    def show_division_items(self, division):
        # Create a top-level window to show division items
        self.items_window = ctk.CTkToplevel(self.main_frame)
        self.items_window.title(f"Items in {division['name']}")
        self.items_window.geometry("500x400")
        self.items_window.configure(fg_color=COLORS["secondary_bg"])
        
        # Make the popup modal
        self.items_window.grab_set()
        self.items_window.lift()
        self.items_window.focus_force()
        self.items_window.protocol("WM_DELETE_WINDOW", self.items_window.destroy)

        # Title
        title = ctk.CTkLabel(
            self.items_window, 
            text=f"Items in {division['name']}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color= COLORS["white"]
        )
        title.pack(pady=10)

        # Create a frame for the items
        items_frame = ctk.CTkFrame(self.items_window, fg_color=COLORS["secondary_bg"])
        items_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Create headers for items
        items_headers = ["Item Name", "Count"]
        for col, header in enumerate(items_headers):
            header_label = ctk.CTkLabel(
                items_frame,
                text=header,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=COLORS["white"]
            )
            header_label.grid(row=0, column=col, padx=10, pady=5)

        # Populate items
        for idx, item in enumerate(division['items'], 1):
            item_name_label = ctk.CTkLabel(
                items_frame,
                text=item['name'],
                font=ctk.CTkFont(size=12),
                text_color=COLORS["white"]
            )
            item_name_label.grid(row=idx, column=0, padx=10, pady=5)

            item_count_label = ctk.CTkLabel(
                items_frame,
                text=str(item['count']),
                font=ctk.CTkFont(size=12),
                text_color=COLORS["white"]
            )
            item_count_label.grid(row=idx, column=1, padx=10, pady=5)

        # Close button
        close_button = ctk.CTkButton(
            self.items_window,
            text="Close",
            command=self.items_window.destroy,
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"]
        )
        close_button.pack(pady=10)

        # Initialize the UI components
        self.create_header()
        self.create_divisions_view() 