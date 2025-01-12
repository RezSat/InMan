from controllers.crud import assign_item_to_employee, get_all_employees, get_all_employees_ids, get_employee, get_item
from models.models import Employee, EmployeeItem, Item
from utils.search import search_items
from models.database import SessionLocal, session_scope


"""
list_employees = get_all_employees_ids()
for employee in list_employees:
    x = assign_item_to_employee(employee, 2, unique_key="-")"""

"""results = search_items("")
for idx, item in enumerate(results, 1):
    print(idx, item)
    if item['attributes']:
        for i, attr in enumerate(item['attributes']):
            print(attr)

"""
"""
    def add_attribute_row(self, name='', value=''):

        row_frame = ctk.CTkFrame(self.attributes_container, fg_color="transparent")
        row_frame.pack(fill="x", pady=5)
        
        # Existing attributes dropdown
        attribute_combo = ctk.CTkComboBox(
            row_frame,
            values=["Brand", "Model", "Serial Number", "Create New"],
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["black"],
            border_color=COLORS["ash"],
            button_color=COLORS["pink"],
            button_hover_color=COLORS["darker_pink"],
            dropdown_fg_color=COLORS["black"],
            width=200
        )
        
        # Attribute name entry (hidden initially)
        name_entry = ctk.CTkEntry(
            row_frame,
            placeholder_text="Attribute Name",
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["black"],
            border_color=COLORS["ash"],
            width=200
        )
        
        # Value entry
        value_entry = ctk.CTkEntry(
            row_frame,
            placeholder_text="Value",
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["black"],
            border_color=COLORS["ash"],
            width=200
        )
        
        # Remove button
        remove_btn = ctk.CTkButton(
            row_frame,
            text="×",
            width=40,
            height=40,
            font=ctk.CTkFont(size=16),
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            command=lambda: self.remove_attribute_row(row_frame)
        )
        
        def on_attribute_select(choice):
            if choice == "Create New":
                attribute_combo.pack_forget()
                value_entry.pack_forget()
                name_entry.pack(side="left", padx=(0, 10))
                value_entry.pack(side="left", padx=(0, 10))
                remove_btn.pack_forget()
                remove_btn.pack(side="left")
                
                # Update collect_attributes
                if attribute_combo in self.collect_attributes:
                    del self.collect_attributes[attribute_combo]
                self.collect_attributes[name_entry] = value_entry
            else:
                if name_entry.winfo_manager():  # If name_entry is visible
                    name_entry.pack_forget()
                    attribute_combo.pack(side="left", padx=(0, 10))
                value_entry.pack(side="left", padx=(0, 10))
                remove_btn.pack(side="left")
                
                # Update collect_attributes
                if name_entry in self.collect_attributes:
                    del self.collect_attributes[name_entry]
                self.collect_attributes[attribute_combo] = value_entry
        
        attribute_combo.configure(command=on_attribute_select)
        
        # If we have existing values, set them up
        if name and name in ["Brand", "Model", "Serial Number"]:
            attribute_combo.set(name)
            attribute_combo.pack(side="left", padx=(0, 10))
            value_entry.insert(0, value)
            value_entry.pack(side="left", padx=(0, 10))
            remove_btn.pack(side="left")
            self.collect_attributes[attribute_combo] = value_entry
        elif name:  # Custom attribute
            attribute_combo.set("Create New")
            on_attribute_select("Create New")
            name_entry.insert(0, name)
            value_entry.insert(0, value)
        else:  # New empty row
            attribute_combo.pack(side="left", padx=(0, 10))
            value_entry.pack(side="left", padx=(0, 10))
            remove_btn.pack(side="left")
            self.collect_attributes[attribute_combo] = value_entry
        
        self.attribute_rows.append(row_frame)
        """
