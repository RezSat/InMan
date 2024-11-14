import customtkinter as ctk
from config import COLORS
import tkinter.messagebox as messagebox

class RemoveItem:
    def __init__(self, main_frame, return_to_manager):
        self.main_frame = main_frame
        self.return_to_manager = return_to_manager
        
        # Sample data (you'll replace this with actual database fetch)
        self.items_data = [
            {
                "item_id": "ITM001", 
                "name": "Dell XPS 15 Laptop", 
                "status": "active",
                "location": "Office A"
            },
            {
                "item_id": "ITM002", 
                "name": "HP Monitor 27\"", 
                "status": "active",
                "location": "Office B"
            },
            {
                "item_id": "ITM003", 
                "name": "Logitech MX Master", 
                "status": "lost",
                "location": "Office C"
            }
        ]
        self.filtered_items = self.items_data.copy()

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
            text="Remove Items",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["white"]
        )
        title.pack(side="left", padx=20)

        # Search and Filter Section
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
        self.items_scroll = ctk.CTkScrollableFrame(
            container,
            fg_color="transparent",
            scrollbar_button_color=COLORS["pink"],
            scrollbar_button_hover_color=COLORS["darker_pink"]
        )
        self.items_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Configure grid weights to make it more responsive
        for i in range(5):  # 5 columns
            self.items_scroll.grid_columnconfigure(i, weight=1)
        
        # Create Headers
        headers = ["Item ID", "Item Name", "Status", "Location", "Action"]
        for col, header in enumerate(headers):
            header_frame = ctk.CTkFrame(self.items_scroll, fg_color=COLORS["black"])
            header_frame.grid(row=0, column=col, padx=2, pady=2, sticky="nsew")
            
            ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=COLORS["white"]
            ).pack(padx=10, pady=8)
        
        # Add Items with proper row indexing
        for idx, item in enumerate(self.filtered_items, 1):
            self.create_item_row(idx, item)

    def remove_item(self, item):
        # Remove item from data source
        self.items_data = [i for i in self.items_data if i["item_id"] != item["item_id"]]
        self.filtered_items = [i for i in self.filtered_items if i["item_id"] != item["item_id"]]
        
        # Clear existing view and recreate
        for widget in self.items_scroll.winfo_children():
            widget.destroy()
        
        # Recreate headers and items
        headers = ["Item ID", "Item Name", "Status", "Location", "Action"]
        for col, header in enumerate(headers):
            header_frame = ctk.CTkFrame(self.items_scroll, fg_color=COLORS["black"])
            header_frame.grid(row=0, column=col, padx=2, pady=2, sticky="nsew")
            
            ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=COLORS["white"]
            ).pack(padx=10, pady=8)
        
        # Recreate items with correct row indexing
        for idx, item in enumerate(self.filtered_items, 1):
            self.create_item_row(idx, item)

    def create_item_row(self, row_idx, item):
        # Item ID Cell
        for col, (key, width) in enumerate([
            ("item_id", 100), 
            ("name", 300), 
            ("status", 100), 
            ("location", 150)
        ]):
            cell_frame = ctk.CTkFrame(self.items_scroll, fg_color=COLORS["black"])
            cell_frame.grid(row=row_idx, column=col, padx=2, pady=2, sticky="nsew")
            
            ctk.CTkLabel(
                cell_frame,
                text=str(item.get(key, "N/A")),
                font=ctk.CTkFont(size=13),
                wraplength=width-20
            ).pack(padx=10, pady=8)
        
        # Action Cell
        action_frame = ctk.CTkFrame(self.items_scroll, fg_color=COLORS["black"])
        action_frame.grid(row=row_idx, column=4, padx=2, pady=2, sticky="nsew")
        
        remove_button = ctk.CTkButton(
            action_frame,
            text="Remove",
            command=lambda i=item: self.confirm_remove_item(i),
            fg_color=COLORS["darker_pink"],
            hover_color=COLORS["pink"],
            width=100
        )
        remove_button.pack(padx=10, pady=8)

    def perform_search(self):
        search_term = self.search_entry.get().lower()
        self.filtered_items = [
            item for item in self.items_data 
            if (search_term in item["item_id"].lower() or 
                search_term in item["name"].lower() or 
                search_term in item.get("status", "").lower() or 
                search_term in item.get("location", "").lower())
        ]
        
        # Clear previous items
        for widget in self.items_scroll.winfo_children():
            widget.destroy()
        
        # Recreate headers
        headers = ["Item ID", "Item Name", "Status", "Location", "Action"]
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

    def confirm_remove_item(self, item):
        # Create confirmation popup
        confirm = messagebox.askyesno(
            "Confirm Removal", 
            f"Are you sure you want to remove the item:\n{item['item_id']} - {item['name']}?"
        )
        
        if confirm:
            self.remove_item(item)

    def remove_item(self, item):
        # Remove item from data source
        self.items_data = [i for i in self.items_data if i["item_id"] != item["item_id"]]
        self.filtered_items = self.items_data.copy()
        
        # Refresh the item view
        for widget in self.items_scroll.winfo_children():
            widget.destroy()
        
        self.create_items_view()

    def display(self):
        self.clear_main_frame()
        self.create_header()
        self.create_items_view()

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()