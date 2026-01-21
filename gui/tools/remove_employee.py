import customtkinter as ctk
from config import COLORS
import tkinter.messagebox as messagebox
from controllers.crud import get_all_employees, delete_employee

class RemoveEmployee:
    def __init__(self, main_frame, return_to_manager):
        self.main_frame = main_frame
        self.return_to_manager = return_to_manager

        self.employees_data = get_all_employees()
        self.filtered_employees = self.employees_data.copy()
        self.selected_employees = set()

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
            text="Remove Employees",
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

        bulk_remove_button = ctk.CTkButton(
            search_frame,
            text="Remove Selected",
            command=self.confirm_bulk_remove,
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=150,
            height=40,
            state="disabled"  # Initially disabled
        )
        bulk_remove_button.pack(side="left", padx=5)
        self.bulk_remove_button = bulk_remove_button

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
        
        # Create Headers
        headers = ["Select", "Employee ID", "Employee Name", "Division", "Action"]
        for col, header in enumerate(headers):
            header_frame = ctk.CTkFrame(self.employees_scroll, fg_color=COLORS["black"])
            header_frame.grid(row=0, column=col, padx=2, pady=2, sticky="nsew")

            if header == "Select":
                # Select All Checkbox
                self.select_all_checkbox = ctk.CTkCheckBox(
                    header_frame,
                    text="",
                    command=self.toggle_select_all,
                    fg_color=COLORS["pink"],
                    hover_color=COLORS["darker_pink"],
                    checkmark_color=COLORS["white"]
                )
                self.select_all_checkbox.pack(padx=10, pady=8)
            else:
                ctk.CTkLabel(
                    header_frame,
                    text=header,
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=COLORS["white"]
                ).pack(padx=10, pady=8)
        
        # Configure grid weights for responsiveness
        for i in range(len(headers)):
            self.employees_scroll.grid_columnconfigure(i, weight=1)

        # Add Employees
        for idx, employee in enumerate(self.filtered_employees, 1):
            self.create_employee_row(idx, employee)

    def create_employee_row(self, row_idx, employee):
        # Select Checkbox Cell
        select_frame = ctk.CTkFrame(self.employees_scroll, fg_color=COLORS["black"])
        select_frame.grid(row=row_idx, column=0, padx=2, pady=2, sticky="nsew")

        checkbox = ctk.CTkCheckBox(
            select_frame,
            text="",
            command=lambda emp=employee: self.toggle_employee_selection(emp),
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            checkmark_color=COLORS["white"]
        )
        if employee["emp_id"] in self.selected_employees:
            checkbox.select()
        checkbox.pack(padx=10, pady=8)

        # Employee ID Cell
        for col, (key, width) in enumerate([
            ("emp_id", 100),
            ("name", 200),
            ("division", 150)
        ], 1):  # Start from column 1
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
        action_frame.grid(row=row_idx, column=4, padx=2, pady=2, sticky="nsew")  # Changed to column 4

        remove_button = ctk.CTkButton(
            action_frame,
            text="Remove",
            command=lambda emp=employee: self.confirm_remove_employee(emp),
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=100
        )
        remove_button.pack(padx=10, pady=8)

    def perform_search(self):
        search_term = self.search_entry.get().lower()
        self.filtered_employees = [
            emp for emp in self.employees_data
            if (search_term in emp["emp_id"].lower() or
                search_term in emp["name"].lower() or
                search_term in emp["division"].lower())
        ]

        # Clear previous employees
        for widget in self.employees_scroll.winfo_children():
            widget.destroy()

        # Recreate headers and employees
        self.create_employees_view()

        # Update UI state after recreating the view
        self.update_select_all_checkbox()
        self.update_bulk_remove_button()

    def confirm_remove_employee(self, employee):
        # Create confirmation popup
        confirm = messagebox.askyesno(
            "Confirm Removal", 
            f"Are you sure you want to remove the employee:\n{employee['emp_id']} - {employee['name']}?"
        )
        
        if confirm:
            self.remove_employee(employee)

    def remove_employee(self, employee):
        # Remove employee from data source
        d = delete_employee(employee["emp_id"])
        self.employees_data = get_all_employees()
        self.filtered_employees = self.employees_data.copy()
        
        # Refresh the employee view
        self.display()

    def display(self):
        self.clear_main_frame()
        self.create_header()
        self.create_employees_view()
        self.update_select_all_checkbox()
        self.update_bulk_remove_button()

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def toggle_select_all(self):
        if self.select_all_checkbox.get():
            # Select all filtered employees
            self.selected_employees = {emp["emp_id"] for emp in self.filtered_employees}
        else:
            # Deselect all
            self.selected_employees.clear()

        self.display()  # Refresh the view to show checkbox states
        self.update_select_all_checkbox()
        self.update_bulk_remove_button()

    def toggle_employee_selection(self, employee):
        emp_id = employee["emp_id"]
        if emp_id in self.selected_employees:
            self.selected_employees.remove(emp_id)
        else:
            self.selected_employees.add(emp_id)

        self.update_bulk_remove_button()
        self.update_select_all_checkbox()

    def update_bulk_remove_button(self):
        if self.selected_employees:
            self.bulk_remove_button.configure(state="normal")
        else:
            self.bulk_remove_button.configure(state="disabled")

    def update_select_all_checkbox(self):
        filtered_emp_ids = {emp["emp_id"] for emp in self.filtered_employees}
        selected_filtered = self.selected_employees.intersection(filtered_emp_ids)

        if not filtered_emp_ids:
            self.select_all_checkbox.deselect()
        elif selected_filtered == filtered_emp_ids:
            self.select_all_checkbox.select()
        else:
            self.select_all_checkbox.deselect()

    def confirm_bulk_remove(self):
        if not self.selected_employees:
            return

        selected_count = len(self.selected_employees)
        confirm = messagebox.askyesno(
            "Confirm Bulk Removal",
            f"Are you sure you want to remove {selected_count} selected employee(s)?\n\nThis action cannot be undone."
        )

        if confirm:
            self.bulk_remove_employees()

    def bulk_remove_employees(self):
        removed_count = 0
        for emp_id in list(self.selected_employees):
            try:
                delete_employee(emp_id)
                removed_count += 1
            except Exception as e:
                messagebox.showerror("Error", f"Failed to remove employee {emp_id}: {str(e)}")

        # Clear selections
        self.selected_employees.clear()

        # Refresh data and display
        self.employees_data = get_all_employees()
        self.filtered_employees = self.employees_data.copy()
        self.update_bulk_remove_button()
        self.display()

        # Show success message
        if removed_count > 0:
            messagebox.showinfo("Success", f"Successfully removed {removed_count} employee(s).")