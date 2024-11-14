import customtkinter as ctk
import tkinter.messagebox as messagebox
from config import COLORS

class ViewEmployeeRecords:
    def __init__(self, main_frame, return_to_manager):
        self.main_frame = main_frame
        self.return_to_manager = return_to_manager
        
        # Sample Employee Data with Items
        self.employees = [
            {
                "emp_id": "EMP001",
                "name": "John Doe",
                "division": "IT",
                "date_joined": "2022-01-15",
                "item_count": 2,
                "items": [
                    {"item_id": 1, "name": "Laptop", "unique_key": "LAP123"},
                    {"item_id": 2, "name": "Mouse", "unique_key": "MOU456"}
                ]
            },
            {
                "emp_id": "EMP002",
                "name": "Jane Smith",
                "division": "HR",
                "date_joined": "2021-11-20",
                "item_count": 1,
                "items": [
                    {"item_id": 3, "name": "Office Chair", "unique_key": "CHA789"}
                ]
            }
        ]

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
            text="View Employee Records",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["white"]
        )
        title.pack(side="left", padx=20)

    def create_employee_view(self):
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
        self.employees_scroll = ctk.CTkScrollableFrame(
            container,
            fg_color="transparent",
            scrollbar_button_color=COLORS["pink"],
            scrollbar_button_hover_color=COLORS["darker_pink"]
        )
        self.employees_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # Configure grid columns
        for i in range(5):  # 5 columns
            self.employees_scroll.grid_columnconfigure(i, weight=1)

        # Create Headers
        headers = ["Emp ID", "Name", "Division", "Date Joined", "Items"]
        for col, header in enumerate(headers):
            header_frame = ctk.CTkFrame(self.employees_scroll, fg_color=COLORS["black"])
            header_frame.grid(row=0, column=col, padx=2, pady=2, sticky="nsew")
            
            ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=COLORS["white"]
            ).pack(padx=10, pady=8)
        
        # Add Employees
        for idx, employee in enumerate(self.employees, 1):
            self.create_employee_row(idx, employee)

    def create_employee_row(self, row_idx, employee):
        # Employee Details Cells
        details = [
            ("emp_id", 100),
            ("name", 200),
            ("division", 150),
            ("date_joined", 150)
        ]

        for col, (key, width) in enumerate(details):
            cell_frame = ctk.CTkFrame(self.employees_scroll, fg_color=COLORS["black"])
            cell_frame.grid(row=row_idx, column=col, padx=2, pady=2, sticky="nsew")
            
            ctk.CTkLabel(
                cell_frame,
                text=str(employee.get(key, "N/A")),
                font =ctk.CTkFont(size=12),
                text_color=COLORS["white"]
            ).pack(padx=10, pady=8)

        # Items Cell
        items_frame = ctk.CTkFrame(self.employees_scroll, fg_color=COLORS["black"])
        items_frame.grid(row=row_idx, column=4, padx=2, pady=2, sticky="nsew")

        items_list = ctk.CTkScrollableFrame(items_frame, fg_color="transparent")
        items_list.pack(fill="both", expand=True)

        for item in employee['items']:
            item_button = ctk.CTkButton(
                items_list,
                text=f"{item['name']} ({item['unique_key']})",
                command=lambda item=item: self.show_item_details(item),
                fg_color=COLORS["pink"],
                hover_color=COLORS["darker_pink"],
                width=150,
                height=30,
                font=ctk.CTkFont(size=12)
            )
            item_button.pack(pady=5)

    def show_item_details(self, item):
        details_window = ctk.CTkToplevel(self.main_frame)
        details_window.title(f"Item Details: {item['name']}")
        details_window.geometry("400x300")
        details_window.configure(fg_color=COLORS["secondary_bg"])

        # Item Name
        name_label = ctk.CTkLabel(details_window, text="Item Name:", font=ctk.CTkFont(size=14))
        name_label.pack(pady=(20, 5))
        name_value = ctk.CTkLabel(details_window, text=item['name'], font=ctk.CTkFont(size=14, weight="bold"))
        name_value.pack(pady=5)

        # Unique Key
        unique_key_label = ctk.CTkLabel(details_window, text="Unique Key:", font=ctk.CTkFont(size=14))
        unique_key_label.pack(pady=(10, 5))
        unique_key_value = ctk.CTkLabel(details_window, text=item['unique_key'], font=ctk.CTkFont(size=14, weight="bold"))
        unique_key_value.pack(pady=5)

        # Additional Item Details (if any)
        # You can add more details here based on your requirements

        # Close Button
        close_button = ctk.CTkButton(
            details_window,
            text="Close",
            command=details_window.destroy,
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=100,
            height=30,
            font=ctk.CTkFont(size=12)
        )
        close_button.pack(pady=(20, 10))

    def display(self):
        self.create_header()
        self.create_employee_view()