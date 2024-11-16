# gui/tools/update_employee_details.py

import customtkinter as ctk
import tkinter.messagebox as messagebox
from config import COLORS

class UpdateEmployeeDetail:
    def __init__(self, main_frame, return_to_manager):
        self.main_frame = main_frame
        self.return_to_manager = return_to_manager
        
        # Sample Employee Data
        self.employees = [
            {
                "emp_id": "EMP001", 
                "name": "John Doe", 
                "division": "IT",
                "date_joined": "2022-01-15",
                "item_count": 5
            },
            {
                "emp_id": "EMP002", 
                "name": "Jane Smith", 
                "division": "HR",
                "date_joined": "2021-11-20",
                "item_count": 3
            },
            {
                "emp_id": "EMP003", 
                "name": "Mike Johnson", 
                "division": "Finance",
                "date_joined": "2023-03-10",
                "item_count": 2
            },
            {
                "emp_id": "EMP004", 
                "name": "Sarah Williams", 
                "division": "Marketing",
                "date_joined": "2022-07-05",
                "item_count": 4
            },
            {
                "emp_id": "EMP005", 
                "name": "David Brown", 
                "division": "Sales",
                "date_joined": "2021-05-12",
                "item_count": 6
            }
        ]
        self.filtered_employees = self.employees.copy()

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
            text="Update Employee Details",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["white"]
        )
        title.pack(side="left", padx=20)

        # Search and Filter Section
        search_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        search_frame.pack(side="right")
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search employees...",
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

    def create_employees_view(self):
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
        self.employees_scroll = ctk.CTkScrollableFrame(
            self.container,
            fg_color="transparent",
            scrollbar_button_color=COLORS["pink"],
            scrollbar_button_hover_color=COLORS["darker_pink"]
        )
        self.employees_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # Configure grid columns
        for i in range(6):  # 6 columns
            self.employees_scroll.grid_columnconfigure(i, weight=1)

        # Create Headers
        headers = ["Emp ID", "Name", "Division", "Date Joined", "Item Count", "Action"]
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
        for idx, employee in enumerate(self.filtered_employees, 1):
            self.create_employee_row(idx, employee)

    def create_employee_row(self, row_idx, employee):
        # Employee Details Cells
        details = [
            ("emp_id", 100),
            ("name", 200),
            ("division", 150),
            ("date_joined", 150),
            ("item_count", 100)
        ]

        for col, (key, width) in enumerate(details):
            cell_frame = ctk.CTkFrame(self.employees_scroll, fg_color=COLORS["black"])
            cell_frame.grid(row=row_idx, column=col, padx=2, pady=2, sticky="nsew")
            
            ctk.CTkLabel(
                cell_frame,
                text=str(employee.get(key, "N/A")),
                font=ctk.CTkFont(size=13),
                wraplength=width-20
            ).pack(padx=10, pady=8)
        
        # Action Cell
        action_frame = ctk.CTkFrame(self.employees_scroll, fg_color=COLORS["black"])
        action_frame.grid(row=row_idx, column=5, padx=2, pady=2, sticky="nsew")
        
        update_button = ctk.CTkButton(
            action_frame,
            text="Update",
            command=lambda e=employee: self.open_update_dialog(e),
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=100
        )
        update_button.pack(padx=10, pady=8)

    def open_update_dialog(self, employee):
        # Create a top-level window for updating employee details
        self.update_window = ctk.CTkToplevel(self.main_frame)
        self.update_window.title(f"Update Employee: {employee['emp_id']}")
        self.update_window.geometry("500x400")
        self.update_window.configure(fg_color=COLORS["secondary_bg"])
        # Make the popup modal and prevent interaction with the main window
        self.update_window.grab_set()

        # Ensure the popup is on top of other windows
        self.update_window.lift()
        self.update_window.focus_force()

        # Prevent the popup from being closed by the window manager's close button
        self.update_window.protocol("WM_DELETE_WINDOW", self.update_window.destroy)

        # Name Entry
        name_label = ctk.CTkLabel(self.update_window, text="Name:", font=ctk.CTkFont(size=14))
        name_label.pack(pady=(20, 5))
        name_entry = ctk.CTkEntry(
            self.update_window, 
            width=300, 
            height=40, 
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["black"],
            border_color=COLORS["ash"],
            placeholder_text=employee['name']
        )
        name_entry.pack(pady=5)

        # Division Dropdown
        division_label = ctk.CTkLabel(self.update_window, text="Division:", font=ctk.CTkFont(size=14))
        division_label.pack(pady=(10, 5))
        division_dropdown = ctk.CTkComboBox(
            self.update_window,
            width=300,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["black"],
            border_color=COLORS["ash"],
            button_color=COLORS["pink"],
            button_hover_color=COLORS["darker_pink"],
            dropdown_fg_color=COLORS["black"],
            values=["IT", "HR", "Finance", "Operations", "Marketing", "Sales"],
            state="readonly"
        )
        division_dropdown.pack(pady=5)

        # Set the current value of the dropdown
        division_dropdown.set(employee['division'])

        # Update Button
        update_btn = ctk.CTkButton(
            self.update_window,
            text="Update",
            command=lambda: self.update_employee(employee['emp_id'], name_entry.get(), division_dropdown.get(), self.update_window),
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=120,
            height=35,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        update_btn.pack(pady=(20, 10))

    def update_employee(self, emp_id, name, division, window):
        # Simulate updating employee details
        messagebox.showinfo("Success", f"Employee {emp_id} updated successfully.")
        window.destroy()
        self.create_employees_view()  # Refresh the employee view

    def perform_search(self):
        search_term = self.search_entry.get().lower()
        self.filtered_employees = [
            emp for emp in self.employees 
            if (search_term in emp["emp_id"].lower() or 
                search_term in emp["name"].lower() or 
                search_term in emp["division"].lower())
        ]
        
        # Refresh the employee view
        self.create_employees_view()

    def display(self):
        self.clear_main_frame()
        self.create_header()
        self.create_employees_view()

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()