# gui/tools/update_employee_details.py

import customtkinter as ctk
import tkinter.messagebox as messagebox
from config import COLORS
from controllers.crud import get_all_division_names, get_all_divisions, get_division_id_from_name, get_employee_details_with_items, remove_item_attribute, remove_item_from_employee, save_item_attribute, update_employee, update_employee_id

class UpdateEmployeeDetail:
    def __init__(self, main_frame, return_to_manager):
        self.main_frame = main_frame
        self.return_to_manager = return_to_manager
        self.employees = []
        self.filtered_employees = []
        self.divisions = get_all_division_names()
        self.load_employees()

    def load_employees(self):
        # Load actual employee data from database
        employee_details = get_employee_details_with_items()
        self.employees = [{
            "emp_id": emp["emp_id"],
            "name": emp["name"],
            "division": emp["division"],
            "items": emp["items"]
        } for emp in employee_details]
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

        # Search Frame
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
        if hasattr(self, 'container'):
            self.container.destroy()

        self.container = ctk.CTkFrame(
            self.main_frame,
            fg_color=COLORS["secondary_bg"],
            corner_radius=15,
            border_width=2,
            border_color=COLORS["white"]
        )
        self.container.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.employees_scroll = ctk.CTkScrollableFrame(
            self.container,
            fg_color="transparent",
            scrollbar_button_color=COLORS["pink"],
            scrollbar_button_hover_color=COLORS["darker_pink"]
        )
        self.employees_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        for i in range(5):  # 5 columns
            self.employees_scroll.grid_columnconfigure(i, weight=1)

        # Headers
        headers = ["Emp ID", "Name", "Division", "Items Count", "Action"]
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
        details = [
            ("emp_id", 100),
            ("name", 200),
            ("division", 150),
            ("items", 100, lambda e: str(len(e.get("items", []))))
        ]

        for col, (key, width, *transform) in enumerate(details):
            cell_frame = ctk.CTkFrame(self.employees_scroll, fg_color=COLORS["black"])
            cell_frame.grid(row=row_idx, column=col, padx=2, pady=2, sticky="nsew")
            
            value = employee.get(key, "N/A")
            if transform:
                value = transform[0](employee)
                
            ctk.CTkLabel(
                cell_frame,
                text=str(value),
                font=ctk.CTkFont(size=13),
                wraplength=width-20
            ).pack(padx=10, pady=8)
        
        # Action Cell
        action_frame = ctk.CTkFrame(self.employees_scroll, fg_color=COLORS["black"])
        action_frame.grid(row=row_idx, column=4, padx=2, pady=2, sticky="nsew")
        
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
        self.update_window = ctk.CTkToplevel(self.main_frame)
        self.update_window.title(f"Update Employee: {employee['emp_id']}")
        self.update_window.geometry("700x650")
        self.update_window.configure(fg_color=COLORS["secondary_bg"])
        self.update_window.grab_set()
        self.update_window.lift()
        self.update_window.focus_force()

        # Create main container with scrollbar
        main_container = ctk.CTkScrollableFrame(
            self.update_window,
            fg_color="transparent",
            scrollbar_button_color=COLORS["pink"],
            scrollbar_button_hover_color=COLORS["darker_pink"]
        )
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Employee ID Section
        emp_id_frame = ctk.CTkFrame(main_container, fg_color=COLORS["black"])
        emp_id_frame.pack(fill="x", pady=10)
        
        emp_id_label = ctk.CTkLabel(
            emp_id_frame,
            text=f"Employee ID: {employee['emp_id']}",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        emp_id_label.pack(side="left", padx=20, pady=10)
        
        change_id_button = ctk.CTkButton(
            emp_id_frame,
            text="Change ID",
            command=lambda: self.open_id_change_dialog(employee),
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=100
        )
        change_id_button.pack(side="right", padx=20, pady=10)

        # Name Entry
        name_label = ctk.CTkLabel(main_container, text="Name:", font=ctk.CTkFont(size=14))
        name_label.pack(pady=(20, 5))
        name_entry = ctk.CTkEntry(
            main_container,
            width=300,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["black"],
            border_color=COLORS["ash"]
        )
        name_entry.insert(0, employee['name'])
        name_entry.pack(pady=5)

        # Division Dropdown
        division_label = ctk.CTkLabel(main_container, text="Division:", font=ctk.CTkFont(size=14))
        division_label.pack(pady=(10, 5))
        division_dropdown = ctk.CTkComboBox(
            main_container,
            width=300,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["black"],
            border_color=COLORS["ash"],
            button_color=COLORS["pink"],
            button_hover_color=COLORS["darker_pink"],
            dropdown_fg_color=COLORS["black"],
            values=self.divisions,
            state="readonly"
        )
        division_dropdown.set(employee['division'])
        division_dropdown.pack(pady=5)

        # Items Section
        items_label = ctk.CTkLabel(
            main_container,
            text="Assigned Items:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        items_label.pack(pady=(20, 10))

        # Create items container
        items_container = ctk.CTkFrame(main_container, fg_color=COLORS["black"])
        items_container.pack(fill="x", padx=20, pady=10)

        # Add items
        for item in employee.get('items', []):
            item_frame = ctk.CTkFrame(items_container, fg_color=COLORS["secondary_bg"])
            item_frame.pack(fill="x", padx=5, pady=2)
            
            ctk.CTkLabel(
                item_frame,
                text=f"{item['name']} (ID: {item['item_id']})",
                font=ctk.CTkFont(size=13)
            ).pack(side="left", padx=10, pady=5)
            
            remove_btn = ctk.CTkButton(
                item_frame,
                text="Remove",
                command=lambda e_id=employee['emp_id'], i_id=item['item_id'], frame=item_frame: 
                    self.remove_item(e_id, i_id, frame),
                fg_color=COLORS["pink"],
                hover_color=COLORS["darker_pink"],
                width=80,
                height=25
            )
            remove_btn.pack(side="right", padx=10, pady=5)

            # Attributes Section
        attributes_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        attributes_frame.pack(fill="x", pady=5)

        # Display existing attributes for the item
        for attribute in item.get('attributes', []):
            attr_frame = ctk.CTkFrame(attributes_frame, fg_color=COLORS["black"])
            attr_frame.pack(fill="x", pady=2)

            ctk.CTkLabel(
                attr_frame,
                text=f"{attribute['name']}: {attribute['value']}",
                font=ctk.CTkFont(size=12),
                text_color=COLORS["white"]
            ).pack(side="left", padx=10, pady=5)

            # Button to remove attribute
            remove_attr_btn = ctk.CTkButton(
                attr_frame,
                text="Remove",
                command=lambda a=attribute, item_id=item['item_id']: self.remove_attribute(employee['emp_id'], item_id, a['name']),
                fg_color=COLORS["pink"],
                hover_color=COLORS["darker_pink"],
                width=70,
                height=25
            )
            remove_attr_btn.pack(side="right", padx=10, pady=5)

        # Button to add new attribute
        add_attr_btn = ctk.CTkButton(
            item_frame,
            text="+ Add Attribute",
            command=lambda item_id=item['item_id']: self.add_attribute(employee['emp_id'],item_id),
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=120,
            height=25
        )
        add_attr_btn.pack(side="right", padx=10, pady=5)

        # Button Frame for Update and Cancel
        button_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        button_frame.pack(pady=20)

        # Cancel Button
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.update_window.destroy,
            fg_color=COLORS["black"],
            hover_color=COLORS["pink"],
            width=150,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        cancel_btn.pack(side="left", padx=10)

        # Update Button
        update_btn = ctk.CTkButton(
            button_frame,
            text="Update Employee Details",
            command=lambda: self.update_employee_details(
                employee['emp_id'],
                name_entry.get(),
                division_dropdown.get()
            ),
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        update_btn.pack(side="left", padx=10)

    def add_attribute(self, emp_id, item_id):
        # Open a dialog to add a new attribute
        attr_window = ctk.CTkToplevel(self.update_window)
        attr_window.title("Add Attribute")
        attr_window.geometry("400x300")
        attr_window.configure(fg_color=COLORS["secondary_bg"])
        attr_window.grab_set()

        key_label = ctk.CTkLabel(attr_window, text="Attribute name:", font=ctk.CTkFont(size=14))
        key_label.pack(pady=(20, 5))
        key_entry = ctk.CTkEntry(attr_window, width=200, height=40, font=ctk.CTkFont(size=14))
        key_entry.pack(pady=5)

        value_label = ctk.CTkLabel(attr_window, text="Attribute Value:", font=ctk.CTkFont(size=14))
        value_label.pack(pady=(10, 5))
        value_entry = ctk.CTkEntry(attr_window, width=200, height=40, font=ctk.CTkFont(size=14))
        value_entry.pack(pady=5)

        add_btn = ctk.CTkButton(
            attr_window,
            text="Add",
            command=lambda: self.save_attribute(emp_id, item_id, key_entry.get(), value_entry.get(), attr_window),
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"]
        )
        add_btn.pack(pady=20)

    def save_attribute(self, emp_id, item_id, name, value, window):
        if not name or not value:
            messagebox.showerror("Error", "Both key and value must be provided.")
            return

        result = save_item_attribute(item_id, name, value)
        if result:
            window.destroy()
            self.load_employees()  # Refresh the employee data
            self.update_window.destroy()
            employee = next((emp for emp in self.employees if emp['emp_id'] == emp_id), None)
            if employee:
                self.open_update_dialog(employee)
            self.create_employees_view()
            messagebox.showinfo("Success", f"Attribute '{name}: {value}' added successfully.")

        else:
            messagebox.showerror("Error", "Failed to save attribute.")
            
    def remove_attribute(self, emp_id, item_id, name):
        result = remove_item_attribute(item_id, name)
        if result:
            self.update_window.destroy()
            self.load_employees()  # Refresh the employee data
            employee = next((emp for emp in self.employees if emp['emp_id'] == emp_id), None)
            if employee:
                self.open_update_dialog(employee)
            self.create_employees_view()
            messagebox.showinfo(
                "Attribute Removed", 
                f"Attribute '{name}' removed successfully from item {item_id}"
            )   
        else:
            messagebox.showerror("Error", "Failed to remove attribute.") 
    
    def open_id_change_dialog(self, employee):
        confirm_window = ctk.CTkToplevel(self.update_window)
        confirm_window.title("Change Employee ID")
        confirm_window.geometry("400x250")
        confirm_window.configure(fg_color=COLORS["secondary_bg"])
        confirm_window.grab_set()
        
        warning_label = ctk.CTkLabel(
            confirm_window,
            text="Warning: Changing Employee ID is a critical operation.\nPlease confirm you want to proceed.",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["pink"]
        )
        warning_label.pack(pady=20)
        
        new_id_entry = ctk.CTkEntry(
            confirm_window,
            placeholder_text="New Employee ID",
            width=200,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["black"],
            border_color=COLORS["ash"]
        )
        new_id_entry.pack(pady=20)
        
        confirm_btn = ctk.CTkButton(
            confirm_window,
            text="Confirm Change",
            command=lambda: self.update_employee_id(
                employee['emp_id'],
                new_id_entry.get(),
                confirm_window
            ),
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=150,
            height=35
        )
        confirm_btn.pack(pady=10)
        
        cancel_btn = ctk.CTkButton(
            confirm_window,
            text="Cancel",
            command=confirm_window.destroy,
            fg_color=COLORS["black"],
            hover_color=COLORS["ash"],
            width=150,
            height=35
        )
        cancel_btn.pack(pady=10)

    def update_employee_id(self, old_id, new_id, window):
            if not new_id:
                messagebox.showerror("Error", "New ID cannot be empty!")
                return
                
            # Here you would add validation for the new ID format
            try:
                # Update employee ID in database
                # This would need to be implemented in your crud.py
                update_employee_id(old_id, new_id)
                
                messagebox.showinfo("Succe+++ss", f"Employee ID updated from {old_id} to {new_id}")
                window.destroy()
                self.update_window.destroy()
                self.load_employees()
                self.create_employees_view()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update employee ID: {str(e)}")

    def update_employee_details(self, emp_id, name, division):
        try:
            # Update employee details in database
            update_employee(emp_id, new_name=name, new_division_id=get_division_id_from_name(division))
            
            messagebox.showinfo("Success", f"Employee {emp_id} details updated successfully")
            self.update_window.destroy()
            self.load_employees()
            self.create_employees_view()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update employee details: {str(e)}")

    def remove_item(self, emp_id, item_id, item_frame):
        try:
            # Remove item from employee in database
            result = remove_item_from_employee(emp_id, item_id)
            
            if result:
                # Remove the item frame from the GUI
                self.load_employees()
                item_frame.destroy()
                
                # Fully refresh the update dialog
                self.update_window.destroy()  # Close current update window
                
                # Find the specific employee again
                employee = next((emp for emp in self.employees if emp['emp_id'] == emp_id), None)
                
                if employee:
                    # Reopen the update dialog with refreshed data
                    self.open_update_dialog(employee)
                
                # Optionally refresh the main employees view
                
                self.create_employees_view()
                
                # Show success message
                messagebox.showinfo(
                    "Item Removed", 
                    f"Item {item_id} has been removed from employee {emp_id}"
                )
            else:
                messagebox.showerror(
                    "Error", 
                    f"Failed to remove item {item_id} from employee {emp_id}"
                )
        
        except Exception as e:
            messagebox.showerror(
                "Error", 
                f"An error occurred while removing the item: {str(e)}"
            )

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