from tkinter import messagebox
import customtkinter as ctk
from config import COLORS
from controllers import get_all_items_with_no_attrs, get_all_employees, assign_item_to_employee, get_all_items_names_dict

class AssignItemsToEmployees:
    def __init__(self, main_frame, return_to_manager):
        self.main_frame = main_frame
        self.return_to_manager = return_to_manager
        self.available_items = get_all_items_with_no_attrs()
        self.employees_data = get_all_employees()
        self.items_names_dict = get_all_items_names_dict()
        self.filtered_employees = self.employees_data.copy()

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
            text="Assign Items to Employees",
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
        
        # Create Headers
        headers = ["Employee ID", "Name", "Action"]
        for col, header in enumerate(headers):
            header_frame = ctk.CTkFrame(self.employees_scroll, fg_color=COLORS["black"])
            header_frame.grid(row=0, column=col, padx=2, pady=2, sticky="nsew")
            
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
        # Employee Details Cells
        for col, (key, width) in enumerate([
            ("emp_id", 100), 
            ("name", 200)
        ]):
            cell_frame = ctk.CTkFrame(self.employees_scroll, fg_color=COLORS["black"])
            cell_frame.grid(row=row_idx, column=col, padx=2, pady=2, sticky="nsew")
            
            ctk.CTkLabel(
                cell_frame,
                text=str(employee[key]),
                font=ctk.CTkFont(size=13),
                wraplength=width-20
            ).pack(padx=10, pady=8)
        
        # Action Cell
        action_frame = ctk.CTkFrame(self.employees_scroll, fg_color=COLORS["black"])
        action_frame.grid(row=row_idx, column=2, padx=2, pady=2, sticky="nsew")
        
        assign_button = ctk.CTkButton(
            action_frame,
            text="Assign Items",
            command=lambda: self.open_assign_items_window(employee),
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=100
        )
        assign_button.pack(padx=10, pady=8)

    def open_assign_items_window(self, employee):
        assign_window = ctk.CTkToplevel(self.main_frame)
        assign_window.title(f"Assign Items to {employee['name']}")
        assign_window.geometry("400x500")
        assign_window.configure(fg_color=COLORS["secondary_bg"])

        # Make the popup modal
        assign_window.grab_set()
        assign_window.lift()
        assign_window.focus_force()

        # Title
        title = ctk.CTkLabel(
            assign_window,
            text=f"Assign Items to {employee['name']}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["white"]
        )
        title.pack(pady=20)

        # Scrollable frame for items
        items_frame = ctk.CTkScrollableFrame(
            assign_window,
            fg_color="transparent",
            scrollbar_button_color=COLORS["pink"],
            scrollbar_button_hover_color=COLORS["darker_pink"]
        )
        items_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.item_rows = []
        self.add_item_row(items_frame)

        # Add more items button
        add_button = ctk.CTkButton(
            assign_window,
            text="+ Add Another Item",
            command=lambda: self.add_item_row(items_frame),
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=150,
            height=35,
            font=ctk.CTkFont(size=14)
        )
        add_button.pack(pady=10)

        # Buttons frame
        buttons_frame = ctk.CTkFrame(assign_window, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=10)

        # Save button
        save_button = ctk.CTkButton(
            buttons_frame,
            text="Save",
            command=lambda: self.save_assigned_items(employee, assign_window),
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=100,
            height=35,
            font=ctk.CTkFont(size=14)
        )
        save_button.pack(side="left", padx=10)

        # Cancel button
        cancel_button = ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            command=assign_window.destroy,
            fg_color=COLORS["darker_pink"],
            hover_color=COLORS["pink"],
            width=100,
            height=35,
            font=ctk.CTkFont(size=14)
        )
        cancel_button.pack(side="right", padx=10)

    def add_item_row(self, parent):
        item_frame = ctk.CTkFrame(parent, fg_color=COLORS["black"])
        item_frame.pack(fill="x", padx=5, pady=5)

        # Item Dropdown
        item_dropdown = ctk.CTkComboBox(
            item_frame,
            values=self.available_items,
            height=35,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["black"],
            border_color=COLORS["ash"],
            button_color=COLORS["pink"],
            button_hover_color=COLORS["darker_pink"],
            dropdown_fg_color=COLORS["black"],
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

        self.item_rows.append((item_dropdown, serial_entry))

    def save_assigned_items(self, employee, window):
        for item_dropdown, serial_entry in self.item_rows:
            if item_dropdown.get() and serial_entry.get():
                a = assign_item_to_employee(employee["emp_id"], self.items_names_dict[item_dropdown.get()], serial_entry.get())
                if a:
                    messagebox.showinfo("Success", f"Item: {item_dropdown.get()} assigned to {employee['name']} successfully.")
                else:
                    messagebox.showerror("Error", f"Failed to assign item: {item_dropdown.get()} to {employee['name']}.")
        window.destroy()

    def perform_search(self):
        search_term = self.search_entry.get().lower()
        self.filtered_employees = [
            emp for emp in self.employees_data 
            if (search_term in emp["emp_id"].lower() or 
                search_term in emp["name"].lower() or 
                search_term in emp["division"].lower())
        ]
        self.display()

    def display(self):
        self.clear_main_frame()
        self.create_header()
        self.create_employees_view()

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
