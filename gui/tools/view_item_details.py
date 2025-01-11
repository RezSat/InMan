import customtkinter as ctk
from config import COLORS
from controllers import get_all_items

class ViewItemDetails:
    def __init__(self, main_frame, return_to_manager):
        self.main_frame = main_frame
        self.return_to_manager = return_to_manager
        raw_items = get_all_items()
        self.items_data = self.convert_items_to_dicts(raw_items)
        self.filtered_items = self.items_data.copy()

    def convert_items_to_dicts(self,items):

        items_data = []
        for item in items:
            item_dict = {
                "item_id": item.item_id,
                "name": item.name,
            }
                        
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

        self.search_entry.bind('<Return>', self.filter_items)

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
        # Create headers
        headers = ["Item ID", "Name"]
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
            text=item['item_id'],
            font=ctk.CTkFont(size=13),
        ).pack(padx=10, pady=8)
        
        # Name Cell
        name_frame = ctk.CTkFrame(self.items_scroll, fg_color=COLORS["black"])
        name_frame.grid(row=row_idx, column=1, padx=2, pady=2, sticky="nsew")
        ctk.CTkLabel(
            name_frame,
            text=item['name'],
            font=ctk.CTkFont(size=13),
            wraplength=300  # Allow text to wrap
        ).pack(padx=10, pady=8, fill="x")
        
        
    def filter_items(self, event=None):
        search_term = self.search_entry.get().lower()
        filtered_items = []

        for item in self.items_data:
            matches_search = (search_term in item['name'].lower() or
                          search_term in str(item['item_id']).lower())
        

            if matches_search:
                filtered_items.append(item)

        self.update_items_view(filtered_items)

    def update_items_view(self, items):
        for widget in self.items_scroll.winfo_children():
            widget.destroy()

        # Create headers
        headers = ["Item ID", "Name"]
        for col, header in enumerate(headers):
            header_frame = ctk.CTkFrame(self.items_scroll, fg_color=COLORS["black"])
            header_frame.grid(row=0, column=col, padx=2, pady=2, sticky="nsew")
            
            ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=COLORS["white"]
            ).pack(padx=10, pady=8)

        for idx,item in enumerate(items, 1):
            self.create_item_row(idx, item)

    def display(self):
        self.clear_main_frame()
        self.create_header()
        self.create_items_view()

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()