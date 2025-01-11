from tkinter import messagebox
import customtkinter as ctk
from config import COLORS
from controllers import (
    get_all_items_with_no_attrs, 
    get_all_employees, 
    assign_item_to_employee, 
    get_all_items_names_dict,
    get_employee_details_with_items
)
from controllers.crud import get_employee_details_with_items_one

class AssignItemsToEmployees:
    def __init__(self, main_frame, return_to_manager):
        self.main_frame = main_frame
        self.return_to_manager = return_to_manager
        self.available_items = get_all_items_with_no_attrs()
        self.employees_data = get_all_employees()
        self.items_names_dict = get_all_items_names_dict()
        self.filtered_employees = self.employees_data.copy()
        self.max_items_per_assignment = 10  # Limit to prevent excessive assignments

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
        # Clear existing widgets if any
        if hasattr(self, 'container'):
            self.container.destroy()

        # Create main container
        self.container = ctk.CTkFrame(
            self.main_frame,
            fg_color=COLORS["secondary_bg"],
            corner_radius=15,
            border_width=2,
            border_color=COLORS["white"]
        )
        self.container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Scrollable frame for employees
        self.employees_scroll = ctk.CTkScrollableFrame(
            self.container,
            fg_color="transparent",
            scrollbar_button_color=COLORS["pink"],
            scrollbar_button_hover_color=COLORS["darker_pink"]
        )
        self.employees_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # Configure grid columns
        for i in range(4):  # 4 columns
            self.employees_scroll.grid_columnconfigure(i, weight=1)

        # Headers
        headers = ["Employee ID", "Name", "Division", "Action"]
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
            ("emp_id", 150),
            ("name", 250),
            ("division", 150)
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
        action_frame.grid(row=row_idx, column=3, padx=2, pady=2, sticky="nsew")
        
        assign_button = ctk.CTkButton(
            action_frame,
            text="Assign Items",
            command=lambda e=employee: self.open_assign_items_window(e),
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=100
        )
        assign_button.pack(padx=10, pady=8)

    def open_assign_items_window(self, employee):
        # Create a larger, more comprehensive assign window
        assign_window = ctk.CTkToplevel(self.main_frame)
        assign_window.title(f"Assign Items to {employee['name']}")
        assign_window.geometry(f"1200x700")
        assign_window.configure(fg_color=COLORS["secondary_bg"])

        # Make the popup modal
        assign_window.grab_set()
        assign_window.lift()
        assign_window.focus_force()

        # Main container with scrollbar
        main_container = ctk.CTkScrollableFrame(
            assign_window,
            fg_color="transparent",
            scrollbar_button_color=COLORS["pink"],
            scrollbar_button_hover_color=COLORS["darker_pink"]
        )
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Title with employee name
        title_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 20))

        title = ctk.CTkLabel(
            title_frame,
            text=f"Assign Items to {employee['name']}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["white"]
        )
        title.pack(side="left")

        # Employee ID display
        emp_id_label = ctk.CTkLabel(
            title_frame,
            text=f"Employee ID: {employee['emp_id']}",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["ash"]  # Using ash for subdued text
        )
        emp_id_label.pack(side="right")

        # Current Items Display
        current_items_frame = ctk.CTkFrame(main_container, fg_color=COLORS["black"])
        current_items_frame.pack(fill="x", pady=10)
        
        current_items_title = ctk.CTkLabel(
            current_items_frame, 
            text="Current Assigned Items:", 
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["white"]
        )
        current_items_title.pack(pady=(10, 5))

        # Fetch and display current items
        try:
            current_employee_details = get_employee_details_with_items_one(employee['emp_id'])
            
            if current_employee_details and current_employee_details['items']:
                # Create a scrollable frame for current items if many
                current_items_scroll = ctk.CTkScrollableFrame(
                    current_items_frame, 
                    height=150,  # Fixed height with scroll
                    fg_color="transparent",
                    scrollbar_button_color=COLORS["pink"],
                    scrollbar_button_hover_color=COLORS["darker_pink"]
                )
                current_items_scroll.pack(fill="x", padx=10, pady=5)

                for item in current_employee_details['items']:
                    item_frame = ctk.CTkFrame(current_items_scroll, fg_color="transparent")
                    item_frame.pack(fill="x", pady=3)

                    item_label = ctk.CTkLabel(
                        item_frame, 
                        text=f"{item['name']}",
                        font=ctk.CTkFont(size=14),
                        text_color=COLORS["white"],
                        width=200,
                        anchor="w"
                    )
                    item_label.pack(side="left", padx=(0, 10))

                    serial_label = ctk.CTkLabel(
                        item_frame, 
                        text=f"Serial: {item.get('unique_key', 'N/A')}",
                        font=ctk.CTkFont(size=12),
                        text_color=COLORS["ash"]
                    )
                    serial_label.pack(side="left")
            else:
                ctk.CTkLabel(
                    current_items_frame, 
                    text="No items currently assigned",
                    font=ctk.CTkFont(size=14, slant="italic"),
                    text_color=COLORS["ash"]
                ).pack(pady=5)
        except Exception as e:
            ctk.CTkLabel(
                current_items_frame, 
                text=f"Error fetching current items: {str(e)}",
                text_color=COLORS["pink"]
            ).pack(pady=5)

        # Items Assignment Section
        items_assignment_frame = ctk.CTkFrame(main_container, fg_color=COLORS["black"])
        items_assignment_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            items_assignment_frame, 
            text="Assign New Items:", 
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["white"]
        ).pack(pady=10)

        # Dynamic item rows
        self.item_rows = []
        self.add_item_row(items_assignment_frame)

        # Add more items button
        add_button = ctk.CTkButton(
            main_container,
            text="+ Add Another Item",
            command=lambda: self.add_item_row(items_assignment_frame),
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=250,  # Wider button
            height=40,
            font=ctk.CTkFont(size=14)
        )
        add_button.pack(pady=10)

        # Buttons frame
        buttons_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=10)

        # Cancel button
        cancel_button = ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            command=assign_window.destroy,
            fg_color=COLORS["black"],
            hover_color=COLORS["black"],
            border_color=COLORS["pink"],
            border_width=1,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14),
            text_color=COLORS["white"]
        )
        cancel_button.pack(side="left", padx=10)

        # Save button
        save_button = ctk.CTkButton(
            buttons_frame,
            text="Save Assignments",
            command=lambda: self.save_assigned_items(employee, assign_window),
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        save_button.pack(side="right", padx=10)

    def add_item_row(self, parent):
        if len(self.item_rows) >= self.max_items_per_assignment:
            messagebox.showwarning("Limit Reached", f"Maximum {self.max_items_per_assignment} items can be assigned at once.")
            return

        # Create a frame with consistent background and spacing
        item_frame = ctk.CTkFrame(parent, fg_color=COLORS["black"])
        item_frame.pack(fill="x", pady=5)

        # Dropdown for item selection
        item_dropdown = ctk.CTkOptionMenu(
            item_frame,
            width=250,  # Increased width
            height=40,
            fg_color=COLORS["pink"],
            button_color=COLORS["darker_pink"],
            dropdown_fg_color=COLORS["secondary_bg"],
            dropdown_hover_color=COLORS["darker_pink"],
            text_color=COLORS["white"],
            dropdown_text_color=COLORS["white"],
            values=list(self.items_names_dict.keys()),
            variable=ctk.StringVar(value="Select Item"),
            font=ctk.CTkFont(size=14)
        )
        item_dropdown.pack(side="left", padx=(0, 10))

        # Entry for serial key
        serial_entry = ctk.CTkEntry(
            item_frame,
            width=300,  # Increased width
            height=40,
            fg_color=COLORS["secondary_bg"],
            border_color=COLORS["pink"],
            border_width=1,
            text_color=COLORS["white"],
            placeholder_text="Enter Serial Key",
            placeholder_text_color=COLORS["ash"],
            font=ctk.CTkFont(size=14)
        )
        serial_entry.pack(side="left", padx=(0, 10))
        

        # Remove item button with a more minimalist design
        remove_button = ctk.CTkButton(
            item_frame,
            text="✖",  # Using a clear remove symbol
            width=40,
            height=40,
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            command=lambda frame=item_frame: self.remove_item_row(frame)
        )
        remove_button.pack(side="left", padx=(0, 20))

        # Attributes Section
        attributes_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        attributes_frame.pack(fill="x", pady=10)

        # Add Attribute Button
        add_attribute_button = ctk.CTkButton(
            attributes_frame,
            text="+ Add Attribute",
            command=lambda: self.add_attribute_row(attributes_frame),
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=150,
            height=30,
            font=ctk.CTkFont(size=12)
        )
        add_attribute_button.pack(side="left", padx=(0, 10))

        # Store references for later use
        self.item_rows.append({
            'frame': item_frame,
            'dropdown': item_dropdown,
            'serial_entry': serial_entry,
            'attributes_frame': attributes_frame,
            'attributes': []  # List to store attribute rows
        })

    def add_attribute_row(self, parent):
        # Create a frame for the attribute row
        row_frame = ctk.CTkFrame(parent, fg_color=COLORS["black"])
        row_frame.pack(fill="x", pady=5)

        # Entry for attribute key
        key_entry = ctk.CTkEntry(
            row_frame,
            width=150,
            height=30,
            fg_color=COLORS["secondary_bg"],
            border_color=COLORS["pink"],
            border_width=1,
            text_color=COLORS["white"],
            placeholder_text="Attribute Key",
            placeholder_text_color=COLORS["ash"],
            font=ctk.CTkFont(size=12)
        )
        key_entry.pack(side="left", padx=(0, 10))

        # Entry for attribute value
        value_entry = ctk.CTkEntry(
            row_frame,
            width=150,
            height=30,
            fg_color=COLORS["secondary_bg"],
            border_color=COLORS["pink"],
            border_width=1,
            text_color=COLORS["white"],
            placeholder_text="Attribute Value",
            placeholder_text_color=COLORS["ash"],
            font=ctk.CTkFont(size=12)
        )
        value_entry.pack(side="left", padx=(0, 10))

        # Remove attribute button
        remove_attribute_button = ctk.CTkButton(
            row_frame,
            text="✖",
            width=30,
            height=30,
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            command=row_frame.destroy
        )
        remove_attribute_button.pack(side="left")

        # Store the attribute row
        for item_row in self.item_rows:
            if item_row['frame'] == parent.master:
                item_row['attributes'].append({
                    'key_entry': key_entry,
                    'value_entry': value_entry
                })
                break

    def remove_item_row(self, frame):
        # Ensure at least one row remains
        if len(self.item_rows) > 1:
            # Remove from UI
            frame.destroy()
            
            # Remove from tracking list
            self.item_rows = [row for row in self.item_rows if row['frame'] != frame]

    def save_assigned_items(self, employee, assign_window):
        for row in self.item_rows:
            item_dropdown = row['dropdown']
            serial_entry = row['serial_entry']
            
            item_name = item_dropdown.get()
            serial_key = serial_entry.get()

            if item_name == "Select Item" or not serial_key:
                continue  # Skip if no valid item or serial key

            item_id = self.items_names_dict[item_name]
            try:
                attribute_details = {}
                for attribute in row['attributes']:
                    key = attribute['key_entry'].get()
                    value = attribute['value_entry'].get()
                    if key and value:
                        attribute_details[key] = value
                assign_item_to_employee(employee["emp_id"], item_id, serial_key, attribute_details)
            except Exception as e:
                print(e)
                messagebox.showerror("Error", f"Failed to assign {item_name}: {str(e)}")
                return

        messagebox.showinfo("Success", "Items assigned successfully!")
        assign_window.destroy()

    def perform_search(self):
        search_term = self.search_entry.get().lower()
        self.filtered_employees = [
            emp for emp in self.employees_data if search_term in emp['name'].lower()
        ]
        self.update_employee_list()

    def update_employee_list(self):
        # Check if the container exists, if not create it
        if not hasattr(self, 'container'):
            self.create_employees_view()
        else:
            # Clear existing rows, keeping headers
            for widget in self.employees_scroll.winfo_children()[4:]:
                widget.destroy()
            
            # Repopulate with filtered employees
            for idx, employee in enumerate(self.filtered_employees, 1):
                self.create_employee_row(idx, employee)

    def display(self):
        self.clear_main_frame()
        self.create_header()
        self.create_employees_view()

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
