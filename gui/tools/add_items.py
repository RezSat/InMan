import customtkinter as ctk
from config import COLORS

class AddItems:
    def __init__(self, main_frame, return_to_manager):
        self.main_frame = main_frame
        self.return_to_manager = return_to_manager
        self.attribute_rows = []
        
    def create_header(self):
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        back_button = ctk.CTkButton(
            header_frame,
            text="← Back to Manager Tools",
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
        # Create a container frame
        container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create canvas and scrollbar
        canvas = ctk.CTkCanvas(
            container,
            bg=COLORS['black'],
            highlightthickness=0
        )
        scrollbar = ctk.CTkScrollbar(
            container,
            orientation="vertical",
            command=canvas.yview
        )
        
        # Create the scrollable frame
        scrollable_frame = ctk.CTkFrame(canvas, fg_color=COLORS["secondary_bg"])
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Configure canvas
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=canvas.winfo_reqwidth())
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack the scrollbar and canvas
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Bind mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Create the form inside scrollable frame
        self.create_form_content(scrollable_frame)

    def create_form_content(self, parent):
        # Main form container with padding
        padding_frame = ctk.CTkFrame(parent, fg_color="transparent")
        padding_frame.pack(fill="both", expand=True, padx=30, pady=30)

        # Basic item information
        basic_info = ctk.CTkFrame(padding_frame, fg_color="transparent")
        basic_info.pack(fill="x", pady=(0, 20))
        
        # Item name and unique key
        self.create_input_field(basic_info, "Item Name:", 0)
        self.create_input_field(basic_info, "Unique Key:", 1)
        
        # Common item checkbox
        common_frame = ctk.CTkFrame(basic_info, fg_color="transparent")
        common_frame.grid(row=2, column=0, columnspan=2, sticky="w", pady=20)
        
        common_checkbox = ctk.CTkCheckBox(
            common_frame,
            text="Is Common Item",
            font=ctk.CTkFont(size=16),
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"]
        )
        common_checkbox.pack(side="left")

        # Status selection
        status_frame = ctk.CTkFrame(basic_info, fg_color="transparent")
        status_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        
        status_label = ctk.CTkLabel(
            status_frame,
            text="Status:",
            font=ctk.CTkFont(size=16)
        )
        status_label.pack(side="left")
        
        status_combobox = ctk.CTkComboBox(
            status_frame,
            values=["active", "retired", "lost"],
            font=ctk.CTkFont(size=16),
            fg_color=COLORS["black"],
            border_color=COLORS["ash"],
            button_color=COLORS["pink"],
            button_hover_color=COLORS["darker_pink"],
            dropdown_fg_color=COLORS["black"],
            width=200
        )
        status_combobox.pack(side="left", padx=(20, 0))

        # Attributes section
        attributes_frame = ctk.CTkFrame(padding_frame, fg_color="transparent")
        attributes_frame.pack(fill="x", pady=20)
        
        attributes_label = ctk.CTkLabel(
            attributes_frame,
            text="Item Attributes",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        attributes_label.pack(anchor="w")

        # Container for attribute rows
        self.attributes_container = ctk.CTkFrame(attributes_frame, fg_color="transparent")
        self.attributes_container.pack(fill="x", pady=(10, 0))
        
        # Add initial attribute row
        self.add_attribute_row()

        # Add attribute button
        add_attribute_btn = ctk.CTkButton(
            attributes_frame,
            text="+ Add Another Attribute",
            command=self.add_attribute_row,
            fg_color=COLORS["green"],
            hover_color=COLORS["ash"],
            height=40,
            font=ctk.CTkFont(size=14)
        )
        add_attribute_btn.pack(pady=10)

        # Submit button
        submit_button = ctk.CTkButton(
            padding_frame,
            text="Add Item",
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            height=50
        )
        submit_button.pack(fill="x", pady=20)

        # Configure grid
        basic_info.grid_columnconfigure(1, weight=1)

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

    def add_attribute_row(self):
        row_frame = ctk.CTkFrame(self.attributes_container, fg_color=COLORS["secondary_bg"])
        row_frame.pack(fill="x", pady=5)
        
        # Existing attributes dropdown
        attribute_combo = ctk.CTkComboBox(
            row_frame,
            values=["Select Existing", "Create New", "Brand", "Model", "Serial Number"],
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["black"],
            border_color=COLORS["ash"],
            button_color=COLORS["pink"],
            width=150
        )
        attribute_combo.pack(side="left", padx=5)
        
        # Attribute name entry (hidden initially)
        name_entry = ctk.CTkEntry(
            row_frame,
            placeholder_text="Attribute Name",
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["black"],
            border_color=COLORS["ash"],
            width=150
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
        value_entry.pack(side="left", padx=5)
        
        # Remove button
        remove_btn = ctk.CTkButton(
            row_frame,
            text="×",
            width=30,
            font=ctk.CTkFont(size=16),
            fg_color=COLORS["darker_pink"],
            hover_color=COLORS["pink"],
            command=lambda: row_frame.destroy()
        )
        remove_btn.pack(side="left", padx=5)
        
        def on_attribute_select(choice):
            if choice == "Create New":
                attribute_combo.pack_forget()
                name_entry.pack(side="left", padx=5)
            
        attribute_combo.configure(command=on_attribute_select)
        self.attribute_rows.append(row_frame)

    def display(self):
        self.clear_main_frame()
        self.create_header()
        self.create_scrollable_form()

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()