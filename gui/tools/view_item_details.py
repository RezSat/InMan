import customtkinter as ctk
from config import COLORS

class ViewItemDetails:
    def __init__(self, main_frame, return_to_manager):
        self.main_frame = main_frame
        self.return_to_manager = return_to_manager
        
        # Sample data for demonstration
        self.items_data = [
            {
                "item_id": "ITM001",
                "name": "Dell XPS 15 Laptop with Extended Battery Pack and Carrying Case",
                "status": "active",
                "is_common": False,
                "attributes": [
                    {"name": "Serial", "value": "DLL-001"},
                    {"name": "Model", "value": "XPS 15 9520"},
                    {"name": "Serial", "value": "DLL-001"},
                    {"name": "Model", "value": "XPS 15 9520"},
                    {"name": "Serial", "value": "DLL-001"},
                    {"name": "Model", "value": "XPS 15 9520"},
                    {"name": "Serial", "value": "DLL-001"},
                    {"name": "Model", "value": "XPS 15 9520"},

                    {"name": "RAM", "value": "32GB"}
                ]
            },
            {
                "item_id": "ITM002",
                "name": "HP Monitor 27\"",
                "status": "active",
                "is_common": True,
                "attributes": [
                    {"name": "Serial", "value": "HP-MON-002"},
                    {"name": "Resolution", "value": "2K"},
                    {"name": "Serial", "value": "HP-MON-002"},
                    {"name": "Resolution", "value": "2K"},
                    {"name": "Panel", "value": "IPS"}
                ]
            },
            {
                "item_id": "ITM003",
                "name": "Logitech MX Master",
                "status": "lost",
                "is_common": False,
                "attributes": [
                    {"name": "Serial", "value": "LOG-003"},
                    {"name": "Type", "value": "Wireless Mouse"},
                    {"name": "DPI", "value": "4000"}
                ]
            }
        ]

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
            text="Items Inventory",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["white"]
        )
        title.pack(side="left", padx=20)
        
        # Search and filter
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
        
        self.status_filter = ctk.CTkComboBox(
            search_frame,
            values=["All Status", "Active", "Retired", "Lost"],
            width=150,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["black"],
            border_color=COLORS["ash"],
            button_color=COLORS["pink"],
            button_hover_color=COLORS["darker_pink"],
            dropdown_fg_color=COLORS["black"]
        )
        self.status_filter.pack(side="left", padx=5)

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
        
        # Configure grid columns with specific weights and minimum sizes
        self.items_scroll.grid_columnconfigure(0, weight=0, minsize=100)  # Item ID
        self.items_scroll.grid_columnconfigure(1, weight=1, minsize=200)  # Name
        self.items_scroll.grid_columnconfigure(2, weight=0, minsize=100)  # Status
        self.items_scroll.grid_columnconfigure(3, weight=0, minsize=100)  # Type
        self.items_scroll.grid_columnconfigure(4, weight=0, minsize=300)  # Attributes
        
        # Create headers
        headers = ["Item ID", "Name", "Status", "Type", "Attributes"]
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
        for idx, item in enumerate(self.items_data, 1):
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
            wraplength=300  # Allow text to wrap
        ).pack(padx=10, pady=8, fill="x")
        
        # Status Cell
        status_frame = ctk.CTkFrame(self.items_scroll, fg_color=COLORS["black"])
        status_frame.grid(row=row_idx, column=2, padx=2, pady=2, sticky="nsew")
        
        status_tag = ctk.CTkFrame(
            status_frame,
            fg_color={
                "active": "#4CAF50",
                "retired": "#FFA726",
                "lost": "#EF5350"
            }.get(item["status"], COLORS["black"]),
            corner_radius=6
        )
        status_tag.pack(padx=10, pady=8)
        ctk.CTkLabel(
            status_tag,
            text=item["status"].upper(),
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["white"]
        ).pack(padx=8, pady=2)
        
        # Type Cell
        type_frame = ctk.CTkFrame(self.items_scroll, fg_color=COLORS["black"])
        type_frame.grid(row=row_idx, column=3, padx=2, pady=2, sticky="nsew")
        
        type_tag = ctk.CTkFrame(
            type_frame,
            fg_color=COLORS["pink"] if item["is_common"] else COLORS["green"],
            corner_radius=6
        )
        type_tag.pack(padx=10, pady=8)
        ctk.CTkLabel(
            type_tag,
            text="Common" if item["is_common"] else "Individual",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["white"]
        ).pack(padx=8, pady=2)
        
        # Attributes Cell with improved visualization
        attrs_frame = ctk.CTkFrame(self.items_scroll, fg_color=COLORS["black"])
        attrs_frame.grid(row=row_idx, column=4, padx=2, pady=2, sticky="nsew")
        
        attrs_container = ctk.CTkFrame(attrs_frame, fg_color="transparent")
        attrs_container.pack(padx=10, pady=8, fill="x")
        
        # Configure the container to have multiple columns
        max_columns = 3  # Adjust this to control how many attributes per row
        for i, attr in enumerate(item["attributes"]):
            attr_tag = ctk.CTkFrame(
                attrs_container,
                fg_color=COLORS["secondary_bg"],
                corner_radius=6
            )
            # Calculate row and column based on index
            row = i // max_columns
            col = i % max_columns
            
            attr_tag.grid(row=row, column=col, padx=2, pady=2, sticky="w")
            
            ctk.CTkLabel(
                attr_tag,
                text=f"{attr['name']}: {attr['value']}",
                font=ctk.CTkFont(size=12),
                text_color=COLORS["white"]
            ).pack(padx=6, pady=4)
        
        # Configure column weights to distribute space
        for j in range(max_columns):
            attrs_container.grid_columnconfigure(j, weight=1)        
  
        """
        # Add hover effect to all frames in the row
        for frame in [id_frame, name_frame, status_frame, type_frame, attrs_frame]:
            def on_hover_enter(e, f=frame):
                f.configure(fg_color=COLORS["secondary_bg"])
            
            def on_hover_leave(e, f=frame):
                f.configure(fg_color=COLORS["black"])
            
            frame.bind("<Enter>", on_hover_enter)
            frame.bind("<Leave>", on_hover_leave)
        """

    def display(self):
        self.clear_main_frame()
        self.create_header()
        self.create_items_view()

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()