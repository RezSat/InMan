import customtkinter as ctk
import tkinter.messagebox as messagebox
from config import COLORS

class ViewEmployeeRecords:
    def __init__(self, main_frame, return_to_manager):
        self.main_frame = main_frame
        self.return_to_manager = return_to_manager
        
        # Placeholder for employee data - you'll replace this with actual database query
        self.employees = [
            {
                "emp_id": "EMP001", 
                "name": "John Doe", 
                "division": "IT",
                "items": [
                    {"item_id": "ITM001", "name": "Dell XPS Laptop"},
                    {"item_id": "ITM002", "name": "HP Monitor"}
                ]
            },
            {
                "emp_id": "EMP002", 
                "name": "Jane Smith", 
                "division": "HR",
                "items": [
                    {"item_id": "ITM003", "name": "Logitech Mouse"},
                    {"item_id": "ITM004", "name": "HP Printer"}
                ]
            },
            {
                "emp_id": "EMP003", 
                "name": "Bob Johnson", 
                "division": "IT",
                "items": [
                    {"item_id": "ITM005", "name": "Dell Keyboard"},
                    {"item_id": "ITM006", "name": "HP Scanner"}
                ]
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
            text="Employee Records",
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
        # Main Container
        self.container = ctk.CTkFrame(
            self.main_frame,
            fg_color=COLORS["secondary_bg"],
            corner_radius=15,
            border_width=2,
            border_color=COLORS["white"]
        )
        self.container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Split into two main sections
        self.employees_list_frame = ctk.CTkFrame(
            self.container, 
            fg_color="transparent", 
            corner_radius=10
        )
        self.employees_list_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        self.items_details_frame = ctk.CTkFrame(
            self.container, 
            fg_color=COLORS["black"], 
            corner_radius=10
        )
        self.items_details_frame.pack(side ="right", fill="both", expand=True, padx=10, pady=10)

        # Employees List
        employees_title = ctk.CTkLabel(
            self.employees_list_frame, 
            text="Employees",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        employees_title.pack(pady=(0,10))

        # Scrollable Employees List
        self.employees_scroll = ctk.CTkScrollableFrame(
            self.employees_list_frame,
            fg_color="transparent",
            scrollbar_button_color=COLORS["pink"],
            scrollbar_button_hover_color=COLORS["darker_pink"]
        )
        self.employees_scroll.pack(fill="both", expand=True)

        # Populate Employees
        for employee in self.filtered_employees:
            self.create_employee_row(employee)

        # Items Details Section
        items_title = ctk.CTkLabel(
            self.items_details_frame, 
            text="Employee Items",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["white"]
        )
        items_title.pack(pady=(0,10))

        # Scrollable Items List
        self.items_scroll = ctk.CTkScrollableFrame(
            self.items_details_frame,
            fg_color="transparent",
            scrollbar_button_color=COLORS["pink"],
            scrollbar_button_hover_color=COLORS["darker_pink"]
        )
        self.items_scroll.pack(fill="both", expand=True)

    def create_employee_row(self, employee):
        employee_frame = ctk.CTkFrame(
            self.employees_scroll, 
            fg_color=COLORS["black"],
            corner_radius=10
        )
        employee_frame.pack(fill="x", pady=5)

        # Employee Info
        info_frame = ctk.CTkFrame(employee_frame, fg_color="transparent")
        info_frame.pack(padx=10, pady=10, fill="x")

        ctk.CTkLabel(
            info_frame, 
            text=f"{employee['emp_id']} - {employee['name']}",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left")

        ctk.CTkLabel(
            info_frame, 
            text=employee['division'],
            font=ctk.CTkFont(size=12)
        ).pack(side="right")

        # Bind click event to show employee items
        employee_frame.bind("<Button-1>", lambda e, emp=employee: self.show_employee_items(emp))
        employee_frame.bind("<Enter>", lambda e: employee_frame.configure(fg_color=COLORS["pink"]))
        employee_frame.bind("<Leave>", lambda e: employee_frame.configure(fg_color=COLORS["black"]))

    def show_employee_items(self, employee):
        # Clear previous items
        for widget in self.items_scroll.winfo_children():
            widget.destroy()

        # Title with employee name
        ctk.CTkLabel(
            self.items_scroll, 
            text=f"Items for {employee['name']} ({employee['emp_id']})",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["white"]
        ).pack(pady=(0,10))

        # Show items
        for item in employee.get('items', []):
            self.create_item_row(item)

    def create_item_row(self, item):
        item_frame = ctk.CTkFrame(
            self.items_scroll, 
            fg_color=COLORS["secondary_bg"],
            corner_radius=10
        )
        item_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(
            item_frame, 
            text=f"{item['item_id']} - {item['name']}",
            font=ctk.CTkFont(size=14)
        ).pack(padx=10, pady=10)

        # View More Details Button
        view_button = ctk.CTkButton(
            item_frame,
            text="View More Details",
            command=lambda i=item: self.show_item_details(i),
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=120
        )
        view_button.pack(side="right", padx=10)

    def show_item_details(self, item):
        # Create a popup window for item details
        details_window = ctk.CTkToplevel(self.main_frame)
        details_window.title(f"Item Details: {item['item_id']}")
        details_window.geometry("400x300")
        details_window.configure(fg_color=COLORS["secondary_bg"])

        # Title
        ctk.CTkLabel(
            details_window,
            text=item['name'],
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["white"]
        ).pack(pady=(10, 10))

        # Item ID
        ctk.CTkLabel(
            details_window,
            text=f"Item ID: {item['item_id']}",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["white"]
        ).pack(pady=(5, 5))

        # Status
        ctk.CTkLabel(
            details_window,
            text=f"Status: {'Active' if item.get('is_common', False) else 'Individual'}",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["white"]
        ).pack(pady=(5, 5))

        # Close Button
        close_button = ctk.CTkButton(
            details_window,
            text="Close",
            command=details_window.destroy,
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=100
        )
        close_button.pack(pady=(20, 10))

    def perform_search(self):
        search_term = self.search_entry.get().lower()
        self.filtered_employees = [
            emp for emp in self.employees 
            if (search_term in emp["emp_id"].lower() or 
                search_term in emp["name"].lower() or 
                search_term in emp["division"].lower())
        ]
        
        # Refresh the employee view
        self.clear_main_frame()
        self.create_header()
        self.create_employees_view()

    def display(self):
        self.clear_main_frame()
        self.create_header()
        self.create_employees_view()

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()