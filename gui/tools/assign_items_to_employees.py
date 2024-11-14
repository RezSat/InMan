# gui/tools/assign_items_to_employees.py

import customtkinter as ctk
from config import COLORS

class AssignItemsToEmployees:
    def __init__(self, main_frame, return_to_manager):
        self.main_frame = main_frame
        self.return_to_manager = return_to_manager
        self.row_frames = []
        self.current_rows = 0
        self.min_rows = 5  # Minimum number of rows to show
        self.available_items = ["Item A", "Item B", "Item C", "Item D", "Item E"]  # Example items

    def create_header(self):
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        # Back button
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

        # Title label
        title = ctk.CTkLabel(
            header_frame,
            text="Assign Items to Employees",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["white"]
        )
        title.pack(side="left", padx=20)

        # Save button
        save_button = ctk.CTkButton(
            header_frame,
            text="Save Changes",
            command=self.save_changes,
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        save_button.pack(side="right", padx=20)

    def create_spreadsheet(self):
        # Main container frame
        outer_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=COLORS["secondary_bg"],
            corner_radius=15,
            border_width=2,
            border_color=COLORS["white"]
        )
        outer_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Create headers container
        headers_frame = ctk.CTkFrame(outer_frame, fg_color=COLORS["black"], height=50)
        headers_frame.pack(fill="x", padx=5, pady=5)

        # Create column headers
        headers = ["EMP ID", "NAME", "ITEM", "SERIAL NUMBER"]
        for i, header in enumerate(headers):
            header_label = ctk.CTkLabel(
                headers_frame,
                text=header,
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=COLORS["white"]
            )
            header_label.grid(row=0, column=i, padx=10, pady=10, sticky="ew")

        # Configure the grid columns for the headers
        headers_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Create scrollable frame for rows
        self.scrollable_frame = ctk.CTkScrollableFrame(
            outer_frame,
            fg_color="transparent",
            scrollbar_button_color=COLORS["pink"],
            scrollbar_button_hover_color=COLORS["darker_pink"]
        )
        self.scrollable_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Configure grid columns for the scrollable frame
        self.scrollable_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Add initial rows
        for _ in range(self.min_rows):
            self.add_row()

    def add_row(self):
        self.current_rows += 1
        row_number = self.current_rows

        # Employee ID (non-editable)
        emp_id = ctk.CTkLabel(
            self.scrollable_frame,
            text=f"EMP{row_number:03d}",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["white"]
        )
        emp_id.grid(row=row_number - 1, column=0, padx=5, pady=5, sticky="ew")

        # Name (non-editable)
        name = ctk. CTkLabel(
            self.scrollable_frame,
            text=f"Employee {row_number}",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["white"]
        )
        name.grid(row=row_number - 1, column=1, padx=5, pady=5, sticky="ew")

        # Item Dropdown
        item_dropdown = ctk.CTkComboBox(
            self.scrollable_frame,
            height=35,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["black"],
            border_color=COLORS["ash"],
            button_color=COLORS["pink"],
            button_hover_color=COLORS["darker_pink"],
            dropdown_fg_color=COLORS["black"],
            values=self.available_items,
            state="readonly"
        )
        item_dropdown.grid(row=row_number - 1, column=2, padx=5, pady=5, sticky="ew")

        # Serial Number Entry
        serial_entry = ctk.CTkEntry(
            self.scrollable_frame,
            height=35,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["black"],
            border_color=COLORS["ash"],
            border_width=2,
            placeholder_text="Enter Serial Number"
        )
        serial_entry.grid(row=row_number - 1, column=3, padx=5, pady=5, sticky="ew")

        # Store the row's widgets for later access
        self.row_frames.append((emp_id, name, item_dropdown, serial_entry))

    def save_changes(self):
        assigned_items_data = []
        for emp_id, name, item_dropdown, serial_entry in self.row_frames:
            assigned_items_data.append({
                "emp_id": emp_id.cget("text"),
                "name": name.cget("text"),
                "item": item_dropdown.get(),
                "serial_number": serial_entry.get()
            })
        
        print("Assigned Items Data:", assigned_items_data)
        # Here you would typically save this data to your database

    def display(self):
        self.clear_main_frame()
        self.create_header()
        self.create_spreadsheet()

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()