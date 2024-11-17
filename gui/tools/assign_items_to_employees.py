import customtkinter as ctk
from config import COLORS
from controllers import get_all_items_with_no_attrs

class AssignItemsToEmployees:
    def __init__(self, main_frame, return_to_manager):
        self.main_frame = main_frame
        self.return_to_manager = return_to_manager
        self.available_items = get_all_items_with_no_attrs()
        self.employee_data = [
            {"emp_id": "EMP001", "name": "John Doe"},
            {"emp_id": "EMP002", "name": "Jane Smith"},
            {"emp_id": "EMP003", "name": "Emily Johnson"},
            {"emp_id": "EMP004", "name": "Michael Brown"},
        ]
        self.create_ui()

    def create_ui(self):
        self.clear_main_frame()
        self.create_header()
        self.create_employee_grid()

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

        # Search box
        self.search_entry = ctk.CTkEntry(
            header_frame,
            placeholder_text="Search Employees...",
            width=200,
            font=ctk.CTkFont(size=14)
        )
        self.search_entry.pack(side="right", padx=20)

    def create_employee_grid(self):
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
        headers_frame = ctk.CTkFrame(outer_frame, fg_color=COLORS["black"])
        headers_frame.grid(row=0, column=0, sticky="nsew")

        # Create column headers
        headers = ["EMP ID", "NAME", "ASSIGN ITEMS"]
        for col, header in enumerate(headers):
            header_label = ctk.CTkLabel(
                headers_frame,
                text=header,
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=COLORS["white"]
            )
            header_label.grid(row=0, column=col, padx=5, pady=5, sticky="nsew")  # Adjusted padding

        # Configure grid weights for responsiveness
        for i in range(len(headers)):
            headers_frame.grid_columnconfigure(i, weight=1)

        # Employee rows
        for idx, emp in enumerate(self.employee_data, 1):
            self.add_employee_row(outer_frame, emp, idx)

    def add_employee_row(self, outer_frame, emp, row_idx):
        row_frame = ctk.CTkFrame(outer_frame, fg_color=COLORS["black"])
        row_frame.grid(row=row_idx, column=0, sticky="nsew", padx=5, pady=5)

        # Configure grid weights for the row
        row_frame.grid_columnconfigure(0, weight=1)
        row_frame.grid_columnconfigure(1, weight=1)
        row_frame.grid_columnconfigure(2, weight=1)

        # Employee ID Cell
        emp_id_label = ctk.CTkLabel(
            row_frame,
            text=emp['emp_id'],
            font=ctk.CTkFont(size=14),
            text_color=COLORS["white"]
        )
        emp_id_label.grid(row=0, column=0, padx=5, pady=5, sticky="ew")  # Adjusted padding

        # Name Cell
        name_label = ctk.CTkLabel(
            row_frame,
            text=emp['name'],
            font=ctk.CTkFont(size=14),
            text_color=COLORS["white"]
        )
        name_label.grid(row=0, column=1, padx=5, pady=5, sticky="ew")  # Adjusted padding

        # Assign Items Button
        assign_button = ctk.CTkButton(
            row_frame,
            text="Assign Items",
            command=lambda: self.open_assign_items_window(emp),
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        assign_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")  # Adjusted padding

    def open_assign_items_window(self, emp):
        assign_window = ctk.CTkToplevel(self.main_frame)
        assign_window.title(f"Assign Items to {emp['name']}")
        assign_window.geometry("400x400")

        # Create dropdowns and entry fields for item assignment
        self.item_rows = []
        self.add_item_row(assign_window)

        # Add button to create more item rows
        add_button = ctk.CTkButton(
            assign_window,
            text="+ Add Item",
            command=lambda: self.add_item_row(assign_window),
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        add_button.pack(pady=10)

        # Save and Cancel buttons
        save_button = ctk.CTkButton(
            assign_window,
            text="Save",
            command=lambda: self.save_assigned_items(emp),
            fg_color=COLORS["green"],
            hover_color=COLORS["darker_green"],
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        save_button.pack(side="left", padx=20, pady=10)

        cancel_button = ctk.CTkButton(
            assign_window,
            text="Cancel",
            command=assign_window.destroy,
            fg_color=COLORS["red"],
            hover_color=COLORS["darker_red"],
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        cancel_button.pack(side="right", padx=20, pady=10)

    def add_item_row(self, parent):
        item_frame = ctk.CTkFrame(parent)
        item_frame.pack(fill="x", padx=5, pady=5)

        # Item Dropdown
        item_dropdown = ctk.CTkComboBox(
            item_frame,
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
        item_dropdown.grid(row=0, column=0, padx=5, pady=5)

        # Serial Number Entry
        serial_entry = ctk.CTkEntry(
            item_frame,
            height=35,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["black"],
            border_color=COLORS["ash"],
            border_width=2,
            placeholder_text="Enter Serial Number"
        )
        serial_entry.grid(row=0, column=1, padx=5, pady=5)

        # Store the row's widgets for later access
        self.item_rows.append((item_dropdown, serial_entry))

    def save_assigned_items(self, emp):
        assigned_items_data = []
        for item_dropdown, serial_entry in self.item_rows:
            assigned_items_data.append({
                "emp_id": emp['emp_id'],
                "name": emp['name'],
                "item": item_dropdown.get(),
                "serial_number": serial_entry.get()
            })
        
        print("Assigned Items Data:", assigned_items_data)
        # Here you would typically save this data to your database

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()