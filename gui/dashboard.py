# 
import customtkinter as ctk
from config import COLORS
from controllers import (
    get_all_employees,
    get_all_items,
    get_all_divisions,
    get_division_details_with_counts
)
from controllers.crud import get_all_divisions_with_counts

class Dashboard:
    def __init__(self, main_frame, inventory):
        self.main_frame = main_frame
        self.inventory = inventory
        
    def create_header(self):
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # Title with welcome message
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side="left")
        
        ctk.CTkLabel(
            title_frame,
            text="Dashboard",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["white"]
        ).pack(side="top", anchor="w")
        
        ctk.CTkLabel(
            title_frame,
            text="Office Inventory Management System by RezSat:",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["ash"]
        ).pack(side="top", anchor="w")

    def create_stat_card(self, parent, title, value, icon_text="📊", secondary_text=None):
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS["secondary_bg"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["ash"]
        )
        
        # Icon
        icon_label = ctk.CTkLabel(
            card,
            text=icon_text,
            font=ctk.CTkFont(size=24),
            text_color=COLORS["pink"]
        )
        icon_label.pack(side="left", padx=15, pady=15)
        
        # Text container
        text_container = ctk.CTkFrame(card, fg_color="transparent")
        text_container.pack(side="left", fill="both", expand=True, padx=(0, 15), pady=15)
        
        # Title
        ctk.CTkLabel(
            text_container,
            text=title,
            font=ctk.CTkFont(size=12),
            text_color=COLORS["ash"]
        ).pack(anchor="w")
        
        # Value
        ctk.CTkLabel(
            text_container,
            text=str(value),
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["white"]
        ).pack(anchor="w")
        
        # Secondary text if provided
        if secondary_text:
            ctk.CTkLabel(
                text_container,
                text=secondary_text,
                font=ctk.CTkFont(size=12),
                text_color=COLORS["green"]
            ).pack(anchor="w")
            
        return card

    def create_division_card(self, parent, division_data):
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS["secondary_bg"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["ash"]
        )
        
        # Header
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 5))
        
        ctk.CTkLabel(
            header,
            text=division_data['name'],
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["white"]
        ).pack(side="left", padx=(0, 10))
        
        emp_tag = ctk.CTkFrame(
            header,
            fg_color=COLORS["pink"],
            corner_radius=5
        )
        emp_tag.pack(side="right")
        
        ctk.CTkLabel(
            emp_tag,
            text=f"{division_data['employee_count']} Employees",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["white"]
        ).pack(padx=8, pady=2)
        
        # Stats
        stats = ctk.CTkFrame(card, fg_color="transparent")
        stats.pack(fill="x", padx=15, pady=(5, 10))
        
        # Total Items Count
        total_items_frame = ctk.CTkFrame(stats, fg_color="transparent")
        total_items_frame.pack(fill="x", padx=(0, 15), pady=(0, 10))
        
        ctk.CTkLabel(
            total_items_frame,
            text="Total Items",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["ash"]
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            total_items_frame,
            text=str(division_data['item_count']),
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["white"]
        ).pack(anchor="w")
        
        # Item Types Grid
        item_types_frame = ctk.CTkFrame(card, fg_color="transparent")
        item_types_frame.pack(fill="both", padx=15, pady=(5, 15))
        
        # Configure grid for item types
        item_types_frame.grid_columnconfigure(0, weight=1)  # Item Name Column
        item_types_frame.grid_columnconfigure(1, weight=1)  # Item Count Column
        
        # Header for Item Types
        ctk.CTkLabel(item_types_frame, text="Item Name", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["ash"]).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ctk.CTkLabel(item_types_frame, text="Count", font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["ash"]).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # Create grid for item types and counts
        for index, item in enumerate(division_data['items']):
            ctk.CTkLabel(item_types_frame, text=item['name'], font=ctk.CTkFont(size=14), text_color=COLORS["ash"]).grid(row=index + 1, column=0, sticky="w", padx=5, pady=2)
            ctk.CTkLabel(item_types_frame, text=str(item['count']), font=ctk.CTkFont(size=14), text_color=COLORS["white"]).grid(row=index + 1, column=1, sticky="w", padx=5, pady=2)
        return card
    
    def create_overview_section(self):
        # Container for overview cards
        overview_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        overview_frame.pack(fill="x", padx=20, pady=10)
        
        # Configure grid for responsive layout
        overview_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Fetch data
        total_employees = len(get_all_employees())
        total_items = len(get_all_items())
        all_divisions = get_all_divisions()
        total_divisions = len(all_divisions)
        active_items = sum(1 for item in get_all_items() if item.status.lower() == 'active')
        
        # Create stat cards
        self.create_stat_card(
            overview_frame,
            "Total Employees",
            total_employees,
            "👥"
        ).grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        self.create_stat_card(
            overview_frame,
            "Total Items",
            total_items,
            "📦",
        ).grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        self.create_stat_card(
            overview_frame,
            "Divisions",
            total_divisions,
            "🏢"
        ).grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
        

    def create_divisions_section(self):
        # Section title
        section_header = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        section_header.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            section_header,
            text="Division Overview",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["white"]
        ).pack(side="left")
        
        # Container for division cards
        divisions_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        divisions_frame.pack(fill="x", padx=20, pady=10)
        
        # Configure grid for responsive layout
        divisions_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Get division details
        divisions = get_all_divisions_with_counts()
        
        # Create division cards in a 2-column grid
        for i, division in enumerate(divisions):
            self.create_division_card(
                divisions_frame,
                division
            ).grid(row=i//2, column=i%2, padx=5, pady=5, sticky="nsew")
    
    def display(self):
        # Clear existing content
        self.clear_main_frame()

        # Create a scrollable frame
        scrollable_frame = ctk.CTkScrollableFrame(
            self.main_frame, 
            fg_color="transparent",
            scrollbar_button_color=COLORS["pink"],
            scrollbar_button_hover_color=COLORS["darker_pink"]
        )
        scrollable_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # Temporarily change main_frame to scrollable_frame for creating content
        original_main_frame = self.main_frame
        self.main_frame = scrollable_frame

        # Create dashboard sections
        self.create_header()
        self.create_overview_section()
        self.create_divisions_section()

        # Restore original main_frame
        self.main_frame = original_main_frame

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()