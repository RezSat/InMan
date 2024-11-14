import customtkinter as ctk
import tkinter.messagebox as messagebox
from config import COLORS
from controllers.crud import get_all_employees, update_employee

class UpdateEmployeeDetail:
    def __init__(self, main_frame, return_to_manager):
        self.main_frame = main_frame
        self.return_to_manager = return_to_manager
        
        # Fetch existing employees
        self.employees = self.fetch_employees()
        self.filtered_employees = self.employees.copy()

    def fetch_employees(self):
        # Use the get_all_employees function from your CRUD controller
        try:
            employees = get_all_employees()
            return [
                {
                    "emp_id": emp.emp_id,
                    "name": emp.name,
                    "division": emp.division.name,  # Assuming division is related
                    "date_joined": emp.date_joined.strftime("%Y-%m-%d"),
                    "item_count": emp.item_count
                } for emp in employees
            ]
        except Exception as e:
            messagebox.showerror("Error", f"Could not fetch employees: {str(e)}")
            return []

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
            fg_color=COLORS["darker_pink"],
            hover_color=COLORS["pink"],
            width=100
        )
        update_button.pack(padx=10, pady=8)

    def open_update_dialog(self, employee):
        # Create a top-level window for updating employee details
        update_window = ctk.CTkToplevel(self.main_frame)
        update_window.title(f"Update Employee: {employee['emp_id']}")
        update_window.geometry("500x400")
        update_window.configure(fg_color=COLORS["secondary_bg"])

        # Name Entry
        name_label = ctk.CTkLabel(update_window, text="Name:", font=ctk.CTkFont(size=14))
        name_label.pack(pady=(20, 5))
        name_entry = ctk.CTkEntry(
            update_window, 
            width=300, 
            height=40, 
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["black"],
            border_color=COLORS["ash"],
            default_value=employee['name']
        )
        name_entry.pack(pady=5)

        # Division Dropdown
        division_label = ctk.CTkLabel(update_window, text="Division:", font=ctk.CTkFont(size=14))
        division_label.pack(pady=(10, 5))
        division_dropdown = ctk.CTkComboBox(
            update_window,
            width=300,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["black"],
            border_color=COLORS["ash"],
            button_color=COLORS["pink"],
            button_hover_color=COLORS ["darker_pink"],
            dropdown_fg_color=COLORS["black"],
            values=["IT", "HR", "Finance", "Operations", "Marketing", "Sales"],
            state="readonly",
            default_value=employee['division']
        )
        division_dropdown.pack(pady=5)

        # Update Button
        update_btn = ctk.CTkButton(
            update_window,
            text="Update",
            command=lambda: self.update_employee(employee['emp_id'], name_entry.get(), division_dropdown.get(), update_window),
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=120,
            height=35,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        update_btn.pack(pady=(20, 10))

    def update_employee(self, emp_id, name, division, window):
        # Call the update_employee function from your CRUD controller
        try:
            update_employee(emp_id, name, division)
            messagebox.showinfo("Success", "Employee details updated successfully.")
            window.destroy()
            self.create_employees_view()  # Refresh the employee view
        except Exception as e:
            messagebox.showerror("Error", f"Could not update employee: {str(e)}")

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