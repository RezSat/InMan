import customtkinter as ctk
from collections import defaultdict

from controllers.crud import create_item
from config import COLORS

class AddItems:
    def __init__(self, main_frame, return_to_manager):
        self.main_frame = main_frame
        self.return_to_manager = return_to_manager
        self.attribute_rows = []
        self.collect_attributes = defaultdict()
        
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
            text="Add New Items",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["white"]
        )
        title.pack(side="left", padx=20)

    def create_scrollable_form(self):
        # Main container frame to hold everything
        outer_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=COLORS["secondary_bg"],
            corner_radius=15,
            border_width=2,
            border_color=COLORS["white"]
        )
        outer_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create a canvas
        canvas = ctk.CTkCanvas(
            outer_frame,
            bg=COLORS["secondary_bg"],
            highlightthickness=0,
            borderwidth=0
        )
        
        # Create scrollbar
        scrollbar = ctk.CTkScrollbar(
            outer_frame,
            orientation="vertical",
            command=canvas.yview
        )
        
        # Create the inner frame that will hold the content
        self.scrollable_frame = ctk.CTkFrame(
            canvas,
            fg_color=COLORS["secondary_bg"]
        )
        
        # Configure the canvas
        def configure_canvas(event):
            # Set the scroll region to the entire inner frame
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Set the canvas width to match the outer frame
            canvas_width = outer_frame.winfo_width() - scrollbar.winfo_width() - 10
            canvas.itemconfig(frame_id, width=canvas_width)
            
        # Bind the configure event
        self.scrollable_frame.bind("<Configure>", configure_canvas)
        
        # Create window in canvas
        frame_id = canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw"
        )
        
        # Pack the scrollbar and canvas
        scrollbar.pack(side="right", fill="y", padx=(0, 5))
        canvas.pack(side="left", fill="both", expand=True)
        
        # Configure canvas y-scrolling
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Create the form content
        self.create_form_content(self.scrollable_frame)

    def create_form_content(self, parent):
        # Main container with good padding
        form_container = ctk.CTkFrame(parent, fg_color="transparent")
        form_container.pack(fill="both", expand=True, padx=40, pady=30)
        
        # Item Information Section
        info_section = ctk.CTkFrame(form_container, fg_color="transparent")
        info_section.pack(fill="x", pady=(0, 30))
        
        section_title = ctk.CTkLabel(
            info_section,
            text="Enter item details to create:",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        section_title.pack(anchor="w", pady=(0, 20))
        
        # Basic Info Grid
        info_grid = ctk.CTkFrame(info_section, fg_color="transparent")
        info_grid.pack(fill="x")
        info_grid.grid_columnconfigure(1, weight=1)
        
        # Create input fields
        self.item_name = self.create_input_field(info_grid, "Item Name:", 0)
        
        # Common Item Row
        common_frame = ctk.CTkFrame(info_section, fg_color="transparent")
        common_frame.pack(fill="x", pady=20)
        
        # Common item checkbox
        self.common_checkbox = ctk.CTkCheckBox(
            common_frame,
            text="Is Common Item",
            font=ctk.CTkFont(size=16),
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"]
        )
        self.common_checkbox.pack(side="left", padx=(0, 40))
        

        # Attributes Section
        attributes_section = ctk.CTkFrame(form_container, fg_color="transparent")
        attributes_section.pack(fill="x", pady=20)
        
        attributes_title = ctk.CTkLabel(
            attributes_section,
            text="Item Attributes",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        attributes_title.pack(anchor="w", pady=(0, 20))
        
        # Container for attribute rows
        self.attributes_container = ctk.CTkFrame(attributes_section, fg_color="transparent")
        self.attributes_container.pack(fill="x")
        
        # Add initial attribute row
        self.add_attribute_row()
        
        # Add attribute button
        add_btn_frame = ctk.CTkFrame(attributes_section, fg_color="transparent")
        add_btn_frame.pack(fill="x", pady=20)
        
        add_attribute_btn = ctk.CTkButton(
            add_btn_frame,
            text="+ Add Another Attribute",
            command=self.add_attribute_row,
            fg_color=COLORS["pink"],
            hover_color=COLORS["ash"],
            height=40,
            font=ctk.CTkFont(size=14)
        )
        add_attribute_btn.pack(side="left")
        
        # Submit Button
        submit_button = ctk.CTkButton(
            form_container,
            text="Add Item",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            height=50,
            command=self.add_item
        )
        submit_button.pack(fill="x", pady=(30, 0))

    def create_input_field(self, parent, label_text, row):
        label = ctk.CTkLabel(
            parent,
            text=label_text,
            font=ctk.CTkFont(size=16)
        )
        label.grid(row=row, column=0, sticky="w", pady=(20, 5))
        
        entry = ctk.CTkEntry(
            parent,
            height=40,
            font=ctk.CTkFont(size=16),
            fg_color=COLORS["black"],
            border_color=COLORS["ash"],
            border_width=2
        )
        entry.grid(row=row, column=1, sticky="ew", padx=(20, 0))
        return entry

    def add_attribute_row(self):
        row_frame = ctk.CTkFrame(self.attributes_container, fg_color="transparent")
        row_frame.pack(fill="x", pady=5)
        
        # Existing attributes dropdown
        attribute_combo = ctk.CTkComboBox(
            row_frame,
            values=["Select Existing", "Create New", "Brand", "Model", "Serial Number"],
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["black"],
            border_color=COLORS["ash"],
            button_color=COLORS["pink"],
            button_hover_color=COLORS["darker_pink"],
            dropdown_fg_color=COLORS["black"],
            width=200
        )
        attribute_combo.pack(side="left", padx=(0, 10))
        
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
        value_entry.pack(side="left", padx=10)
        
        # Remove button
        remove_btn = ctk.CTkButton(
            row_frame,
            text="×",
            width=40,
            height=40,
            font=ctk.CTkFont(size=16),
            fg_color=COLORS["darker_pink"],
            hover_color=COLORS["pink"],
            command=lambda: row_frame.destroy()
        )
        remove_btn.pack(side="left")
        
        def on_attribute_select(choice):
            if choice == "Create New":
                attribute_combo.pack_forget()
                name_entry.pack(side="left", padx=(0, 10))
                value_entry.pack(side="left", padx=(0, 10))
            else:
                if name_entry.winfo_manager():  # If name_entry is visible
                    name_entry.pack_forget()
                    attribute_combo.pack(side="left", padx=(0, 10))
                value_entry.pack(side="left", padx=(0, 10))
            
            # update the collect_attributes dictionary
            if choice == "Create New":
                self.collect_attributes[name_entry] = value_entry
            else:
                self.collect_attributes[attribute_combo] = value_entry
            
        attribute_combo.configure(command=on_attribute_select)
        self.attribute_rows.append(row_frame)

    def display(self):
        self.clear_main_frame()
        self.create_header()
        self.create_scrollable_form()

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def add_item(self):
        print("Attributes:")
        for attribute, value_entry in self.collect_attributes.items():
            # Determine if the attribute is created new or selected
            if attribute.winfo_manager():  # Check if the name_entry is visible
                attribute_name = attribute.get()  # This is the name_entry
            else:
                attribute_name = attribute.get()  # This is the attribute_combo

            print(f"Name: {attribute_name}, Value: {value_entry.get()}")

        print("Common Item:", self.common_checkbox.get())
        print("Item Name:", self.item_name.get())