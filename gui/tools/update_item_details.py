# gui/tools/update_item_details.py

from tkinter import messagebox
import customtkinter as ctk
from config import COLORS
from collections import defaultdict
from controllers.crud import get_all_items, update_item_details

class UpdateItemDetails:
    def __init__(self, main_frame, return_to_manager):

        self.main_frame = main_frame
        self.attribute_rows = []
        self.return_to_manager = return_to_manager
        
        # Fetch real items from the database
        raw_items = get_all_items()
        self.items_data = self.convert_items_to_dicts(raw_items)
        self.filtered_items = self.items_data.copy()
        self.collect_attributes = defaultdict()
        
    def convert_items_to_dicts(self, items):
            """
            Convert SQLAlchemy Item objects to dictionaries with detailed attributes
            """
            items_data = []
            for item in items:
                item_dict = {
                    "item_id": item.item_id,
                    "name": item.name,
                    "status": item.status,
                    "is_common": item.is_common,
                    "attributes": []
                }
                
                # Add attributes
                for attr in item.attributes:
                    item_dict["attributes"].append({
                        "name": attr.name,
                        "value": attr.value
                    })
                
                items_data.append(item_dict)
            
            return items_data

    def create_header(self):
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
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
        
        title = ctk.CTkLabel(
            header_frame,
            text="Select Item to Update",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["white"]
        )
        title.pack(side="left", padx=20)

        # Search and filter section
        search_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        search_frame.pack(side="right")
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search items...",
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

    def create_items_view(self):
        # Main container
        container = ctk.CTkFrame(
            self.main_frame,
            fg_color=COLORS["secondary_bg"],
            corner_radius=15,
            border_width=2,
            border_color=COLORS["white"]
        )
        container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create scrollable frame
        self.items_scroll = ctk.CTkScrollableFrame(
            container,
            fg_color="transparent",
            scrollbar_button_color=COLORS["pink"],
            scrollbar_button_hover_color=COLORS["darker_pink"]
        )
        self.items_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        for i in range(3):
            self.items_scroll.grid_columnconfigure(i, weight=1)
        # Create headers
        headers = ["Item ID", "Item Name", "Action"]
        for col, header in enumerate(headers):
            header_frame = ctk.CTkFrame(self.items_scroll, fg_color=COLORS["black"])
            header_frame.grid(row=0, column=col, padx=2, pady=2, sticky="nsew")
            
            ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=COLORS["white"]
            ).pack(padx=10, pady=8)
        
        # Add items
        for idx, item in enumerate(self.filtered_items, 1):
            self.create_item_row(idx, item)

    def create_item_row(self, row_idx, item):
        # Item ID Cell
        id_frame = ctk.CTkFrame(self.items_scroll, fg_color=COLORS["black"])
        id_frame.grid(row=row_idx, column=0, padx=2, pady=2, sticky="nsew")
        ctk.CTkLabel(
            id_frame,
            text=item["item_id"],
            font=ctk.CTkFont(size=13),
        ).pack(padx=10, pady=8)
        
        # Name Cell
        name_frame = ctk.CTkFrame(self.items_scroll, fg_color=COLORS["black"])
        name_frame.grid(row=row_idx, column=1, padx=2, pady=2, sticky="nsew")
        ctk.CTkLabel(
            name_frame,
            text=item["name"],
            font=ctk.CTkFont(size=13),
            wraplength=300
        ).pack(padx=10, pady=8, fill="x")
        
        # Action Cell
        action_frame = ctk.CTkFrame(self.items_scroll, fg_color=COLORS["black"])
        action_frame.grid(row=row_idx, column=2, padx=2, pady=2, sticky="nsew")
        
        select_button = ctk.CTkButton(
            action_frame,
            text="Select",
            command=lambda i=item: self.open_update_popup(i),
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=100
        )
        select_button.pack(padx=10, pady=8)

    def perform_search(self):
        search_term = self.search_entry.get().lower()
        self.filtered_items = [
            item for item in self.items_data 
            if search_term in item["name"].lower()
        ]
        
        # Clear previous items
        for widget in self.items_scroll.winfo_children():
            widget.destroy()
        
        # Recreate headers
        headers = ["Item ID", "Item Name", "Action"]
        for col, header in enumerate(headers):
            header_frame = ctk.CTkFrame(self.items_scroll, fg_color=COLORS["black"])
            header_frame.grid(row=0, column=col, padx=2, pady=2, sticky="nsew")
            
            ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=COLORS["white"]
            ).pack(padx=10, pady=8)
        
        # Add filtered items
        for idx, item in enumerate(self.filtered_items, 1):
            self.create_item_row(idx, item)

    def open_update_popup(self, item):
        # Create popup window
        self.popup = ctk.CTkToplevel(self.main_frame)
        self.popup.title("Update Item")
        self.popup.geometry("600x700")
        self.popup.configure(fg_color=COLORS["secondary_bg"])
        
        # Reset the attributes collection
        self.collect_attributes = {}
        self.attribute_rows = []

        # Make the popup modal
        self.popup.grab_set()
        self.popup.lift()
        self.popup.focus_force()
        self.popup.protocol("WM_DELETE_WINDOW", self.popup.destroy)
        self.center_popup()
        
        # Create scrollable frame for content
        content_frame = ctk.CTkScrollableFrame(
            self.popup,
            fg_color="transparent",
            scrollbar_button_color=COLORS["pink"],
            scrollbar_button_hover_color=COLORS["darker_pink"]
        )
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = ctk.CTkLabel(
            content_frame,
            text=f"Update Item: {item['item_id']}",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=(0, 20))
        
        # Item Name
        name_label = ctk.CTkLabel(
            content_frame,
            text="Item Name:",
            font=ctk.CTkFont(size=16)
        )
        name_label.pack(anchor="w", pady=(10, 5))
        
        self.item_name_entry = ctk.CTkEntry(
            content_frame,
            font=ctk.CTkFont(size=16),
            fg_color=COLORS["black"],
            border_color=COLORS["ash"],
            border_width=2
        )
        self.item_name_entry.insert(0, item["name"])
        self.item_name_entry.pack(fill="x", pady=(0, 10))

        # Status Dropdown
        status_label = ctk.CTkLabel(
            content_frame,
            text="Status:",
            font=ctk.CTkFont(size=16)
        )
        #status_label.pack(anchor="w", pady=(10, 5))
        
        self.status_dropdown = ctk.CTkComboBox(
            content_frame,
            values=["active", "retired", "lost"],
            font=ctk.CTkFont(size=16),
            fg_color=COLORS["black"],
            border_color=COLORS["ash"],
            button_color=COLORS["pink"],
            button_hover_color=COLORS["darker_pink"],
            dropdown_fg_color=COLORS["black"]
        )
        self.status_dropdown.set(item.get("status", "active"))
        #self.status_dropdown.pack(fill="x", pady=(0, 10))

        # Common Item Checkbox
        self.common_checkbox = ctk.CTkCheckBox(
            content_frame,
            text="Is Common Item",
            font=ctk.CTkFont(size=16),
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"]
        )
        if item.get("is_common", False):
            self.common_checkbox.select()
        self.common_checkbox.pack(anchor="w", pady=(10, 20))

        # Attributes Section
        attributes_section = ctk.CTkFrame(content_frame, fg_color="transparent")
        attributes_section.pack(fill="x", pady=20)
        
        attributes_title = ctk.CTkLabel(
            attributes_section,
            text="Item Attributes",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        attributes_title.pack(anchor="w", pady=(0, 10))
        
        self.attributes_container = ctk.CTkFrame(attributes_section, fg_color="transparent")
        self.attributes_container.pack(fill="x")
        
        # Populate existing attributes
        if item.get("attributes") and isinstance(item["attributes"], list):
            for attr in item["attributes"]:
                if isinstance(attr, dict) and "name" in attr and "value" in attr:
                    self.add_attribute_row(attr['name'], attr['value'])
        
        # Add attribute button
        add_btn_frame = ctk.CTkFrame(attributes_section, fg_color="transparent")
        add_btn_frame.pack(fill="x", pady=20)
        
        add_attribute_btn = ctk.CTkButton(
            add_btn_frame,
            text="+ Add New Attribute",
            command=lambda: self.add_attribute_row(),
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            height=40,
            font=ctk.CTkFont(size=14)
        )
        add_attribute_btn.pack(side="left")

        # Save and Cancel buttons
        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))

        save_button = ctk.CTkButton(
            button_frame,
            text="Save",
            command=lambda: self.save_item(item),
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=100
        )
        save_button.pack(side="left", padx=(0, 10))

        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.popup.destroy,
            fg_color=COLORS["darker_pink"],
            hover_color=COLORS["pink"],
            width=100
        )
        cancel_button.pack(side="left")

    def center_popup(self):
        """
        Center the popup window on the screen
        """
        self.popup.update_idletasks()
        
        # Get screen width and height
        screen_width = self.popup.winfo_screenwidth()
        screen_height = self.popup.winfo_screenheight()
        
        # Calculate window width and height
        window_width = 600
        window_height = 700
        
        # Calculate position x and y coordinates
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.popup.geometry(f'{window_width}x{window_height}+{x}+{y}')
        
    def add_attribute_row(self, name='', value=''):
        """
        Create a new attribute row in the popup.
        Args:
            name (str): Pre-filled attribute name if editing existing
            value (str): Pre-filled value if editing existing
        """
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
        return row_frame
    
    def remove_attribute_row(self, row_frame):
        """Remove an attribute row and clean up the collect_attributes dictionary"""
        # Find and remove the entries from collect_attributes
        entries_to_remove = []
        for key, value in self.collect_attributes.items():
            if key.master == row_frame or value.master == row_frame:
                entries_to_remove.append(key)
        
        for key in entries_to_remove:
            del self.collect_attributes[key]
        
        # Remove the row from attribute_rows list
        if row_frame in self.attribute_rows:
            self.attribute_rows.remove(row_frame)
        
        # Destroy the row widget
        row_frame.destroy()
        
    def save_item(self, item):
        updated_item = {
            "item_id": item["item_id"],
            "name": self.item_name_entry.get(),
            "status": self.status_dropdown.get(),
            "is_common": self.common_checkbox.get(),
            "attributes": []
        }

        attrs = {}
        for attribute, value_entry in self.collect_attributes.items():
            # Determine if the attribute is created new or selected
            if attribute.winfo_manager():  # Check if the name_entry is visible
                attribute_name = attribute.get()  # This is the name_entry
                attrs[attribute_name] = value_entry.get()
            else:
                attribute_name = attribute.get()  # This is the attribute_combo
                attrs[attribute_name] = value_entry.get()
                # UI is messed up, its the other way around so that need to fixed.

        updated_item["attributes"] = attrs

        print("Updated Item Data:", updated_item)
        update_item_details(updated_item)
        # Here you would typically call a function to update the item in the database
        messagebox.showinfo('Succes', f"Item {updated_item['item_id']} updated sucessfully.")
        self.popup.destroy()
        self.display()

    def display(self):
        self.clear_main_frame()
        self.create_header()
        self.create_items_view()

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()