import customtkinter as ctk
from tkinter import ttk, filedialog
import pandas as pd
from config import COLORS
from controllers import (get_all_employees, get_all_items, get_all_divisions, 
                       get_division_details_with_counts, get_employee_details_with_items)
from controllers.crud import get_all_division_names
from models.database import SessionLocal
from utils.search import search_divisions, search_employees, search_items

class InventoryDisplay:
    def __init__(self, main_frame, inv):
        self.main_frame = main_frame
        self.current_view = None
        self.search_results = []
        
    def create_header(self):
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # Title
        title = ctk.CTkLabel(
            header_frame,
            text="Inventory Search",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["white"]
        )
        title.pack(side="left", padx=20)
        
        # Export button
        export_btn = ctk.CTkButton(
            header_frame,
            text="Export Results",
            command=self.export_to_excel,
            fg_color=COLORS["green"],
            hover_color=COLORS["ash"],
            width=120,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        export_btn.pack(side="right", padx=10)

    def create_search_panel(self):
        search_panel = ctk.CTkFrame(self.main_frame, fg_color=COLORS["secondary_bg"])
        search_panel.pack(fill="x", padx=20, pady=10)
        
        # Create two rows for search controls
        top_row = ctk.CTkFrame(search_panel, fg_color="transparent")
        top_row.pack(fill="x", padx=10, pady=(10, 5))
        
        bottom_row = ctk.CTkFrame(search_panel, fg_color="transparent")
        bottom_row.pack(fill="x", padx=10, pady=(5, 10))
        
        # Configure grid columns for top row
        top_row.grid_columnconfigure(1, weight=1)  # Search entry will expand
        
        # Search type selector with improved styling
        search_types = ["All", "Employees", "Items", "Divisions"]
        self.search_type = ctk.CTkComboBox(
            top_row,
            values=search_types,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["black"],
            border_color=COLORS["ash"],
            button_color=COLORS["pink"],
            button_hover_color=COLORS["darker_pink"],
            command=self.on_search_type_change
        )
        self.search_type.grid(row=0, column=0, padx=(0, 10), sticky="w")
        
        # Search entry with improved styling and expansion
        self.search_entry = ctk.CTkEntry(
            top_row,
            placeholder_text="Search...",
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["black"],
            border_color=COLORS["ash"]
        )
        self.search_entry.grid(row=0, column=1, padx=10, sticky="ew")
        self.search_entry.bind('<Return>', self.perform_search)
        
        # Search button with improved styling
        search_btn = ctk.CTkButton(
            top_row,
            text="Search",
            command=self.perform_search,
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=100,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        search_btn.grid(row=0, column=2, padx=(10, 0), sticky="e")
        
        # Advanced filters frame in bottom row
        self.filters_frame = ctk.CTkFrame(bottom_row, fg_color="transparent")
        self.filters_frame.pack(fill="x", expand=True)
        
        # Configure bottom row for filter expansion
        self.filters_frame.grid_columnconfigure(0, weight=1)

    def create_advanced_filters(self, search_type):
        # Clear existing filters
        for widget in self.filters_frame.winfo_children():
            widget.destroy()
            
        if search_type == "Employees":
            # Division filter
            divisions = ["All Divisions"] + get_all_division_names()
            self.division_filter = ctk.CTkComboBox(
                self.filters_frame,
                values=divisions,
                width=150,
                height=35,
                font=ctk.CTkFont(size=14),
                fg_color=COLORS["black"],
                border_color=COLORS["ash"],
                button_color=COLORS["pink"],
                button_hover_color=COLORS["darker_pink"]
            )
            self.division_filter.pack(side="left", padx=5)
            
        elif search_type == "Items":
            filters_container = ctk.CTkFrame(self.filters_frame, fg_color="transparent")
            filters_container.pack(fill="x", expand=True)
            
            # Status filter
            self.status_filter = ctk.CTkComboBox(
                filters_container,
                values=["All Status", "Active", "Retired", "Lost"],
                width=150,
                height=35,
                font=ctk.CTkFont(size=14),
                fg_color=COLORS["black"],
                border_color=COLORS["ash"],
                button_color=COLORS["pink"],
                button_hover_color=COLORS["darker_pink"]
            )
            self.status_filter.pack(side="left", padx=5)
            
            # Type filter
            self.type_filter = ctk.CTkComboBox(
                filters_container,
                values=["All Types", "Common", "Individual"],
                width=150,
                height=35,
                font=ctk.CTkFont(size=14),
                fg_color=COLORS["black"],
                border_color=COLORS["ash"],
                button_color=COLORS["pink"],
                button_hover_color=COLORS["darker_pink"]
            )
            self.type_filter.pack(side="left", padx=5)
            
            # Attribute filters container
            attr_container = ctk.CTkFrame(filters_container, fg_color="transparent")
            attr_container.pack(side="left", padx=5)
            
            self.attr_name = ctk.CTkEntry(
                attr_container,
                placeholder_text="Attribute Name",
                width=150,
                height=35,
                font=ctk.CTkFont(size=14),
                fg_color=COLORS["black"],
                border_color=COLORS["ash"]
            )
            self.attr_name.pack(side="left", padx=2)
            
            self.attr_value = ctk.CTkEntry(
                attr_container,
                placeholder_text="Attribute Value",
                width=150,
                height=35,
                font=ctk.CTkFont(size=14),
                fg_color=COLORS["black"],
                border_color=COLORS["ash"]
            )
            self.attr_value.pack(side="left", padx=2)

    def create_results_view(self):
        # Main container with border and rounded corners
        container = ctk.CTkFrame(
            self.main_frame,
            fg_color=COLORS["secondary_bg"],
            corner_radius=15,
            border_width=2,
            border_color=COLORS["white"]
        )
        container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Scrollable frame for results
        self.results_frame = ctk.CTkScrollableFrame(
            container,
            fg_color="transparent",
            scrollbar_button_color=COLORS["pink"],
            scrollbar_button_hover_color=COLORS["darker_pink"]
        )
        self.results_frame.pack(fill="both", expand=True, padx=5, pady=5)

    def create_advanced_filters(self, search_type):
        # Clear existing filters
        for widget in self.filters_frame.winfo_children():
            widget.destroy()
            
        if search_type == "Employees":
            # Division filter
            divisions = ["All Divisions"] + get_all_division_names()
            self.division_filter = ctk.CTkComboBox(
                self.filters_frame,
                values=divisions,
                width=150
            )
            self.division_filter.pack(side="left", padx=5)
            
        elif search_type == "Items":
            # Status filter
            self.status_filter = ctk.CTkComboBox(
                self.filters_frame,
                values=["All Status", "Active", "Retired", "Lost"],
                width=150
            )
            self.status_filter.pack(side="left", padx=5)
            
            # Type filter
            self.type_filter = ctk.CTkComboBox(
                self.filters_frame,
                values=["All Types", "Common", "Individual"],
                width=150
            )
            self.type_filter.pack(side="left", padx=5)
            
            # Attribute search
            self.attr_name = ctk.CTkEntry(
                self.filters_frame,
                placeholder_text="Attribute Name",
                width=150
            )
            self.attr_value = ctk.CTkEntry(
                self.filters_frame,
                placeholder_text="Attribute Value",
                width=150
            )
            self.attr_name.pack(side="left", padx=5)
            self.attr_value.pack(side="left", padx=5)

    def perform_search(self, event=None):
        search_type = self.search_type.get()
        query = self.search_entry.get()
        
        # Clear existing results in the results frame
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        if search_type == "Employees":
            results = get_all_employees()
            self.display_employee_results(results)
        elif search_type == "Items":
            results = search_items(SessionLocal(), query)
            self.display_item_results(results)
        elif search_type == "Divisions":
            results = search_divisions(SessionLocal(), query)
            self.display_division_results(results)
        else:
            # Perform all searches
            emp_results = search_employees(SessionLocal(), query)
            item_results = search_items(SessionLocal(), query)
            div_results = search_divisions(SessionLocal(), query)
            self.display_combined_results(emp_results, item_results, div_results)

    def export_to_excel(self):
        if not self.search_results:
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
        
        if file_path:
            df = pd.DataFrame(self.search_results)
            
            # Create Excel writer with styling
            with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Search Results', index=False)
                
                # Get workbook and worksheet objects
                workbook = writer.book
                worksheet = writer.sheets['Search Results']
                
                # Define formats
                header_format = workbook.add_format({
                    'bold': True,
                    'font_size': 12,
                    'bg_color': '#2c363f',
                    'font_color': '#ffffff'
                })
                
                # Apply formats
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                    worksheet.set_column(col_num, col_num, 15)

    def display(self):
        self.clear_main_frame()
        self.create_header()
        self.create_search_panel()
        self.create_results_view()

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def on_search_type_change(self, selected_type):
        """Handle changes in the search type selection."""
        self.create_advanced_filters(selected_type)

    def create_headers_for_current_view(self):
        """Create headers for the current view based on the search type."""
        search_type = self.search_type.get()
        # Clear existing headers if any
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        if search_type == "Employees":
            headers = ["Name", "ID", "Division"]
        elif search_type == "Items":
            headers = ["Item Name", "Status", "Attributes"]
        elif search_type == "Divisions":
            headers = ["Division Name", "Employee Count"]
        else:
            headers = ["Search Results"]
        
        for header in headers:
            label = ctk.CTkLabel(self.results_frame, text=header)
            label.pack(side="top", padx=5, pady=5)

    def display_employee_results(self, results):
        # Configure grid columns
        self.results_frame.grid_columnconfigure(0, weight=0, minsize=100)  # ID
        self.results_frame.grid_columnconfigure(1, weight=1, minsize=200)  # Name
        self.results_frame.grid_columnconfigure(2, weight=0, minsize=150)  # Division

        # Create headers
        headers = ["Employee ID", "Name", "Division"]
        for col, header in enumerate(headers):
            header_frame = ctk.CTkFrame(self.results_frame, fg_color=COLORS["black"])
            header_frame.grid(row=0, column=col, padx=2, pady=2, sticky="nsew")
            
            ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=COLORS["white"]
            ).pack(padx=10, pady=8)

        # Add employee rows
        for idx, employee in enumerate(results, 1):
            # ID Cell
            id_frame = ctk.CTkFrame(self.results_frame, fg_color=COLORS["black"])
            id_frame.grid(row=idx, column=0, padx=2, pady=2, sticky="nsew")
            ctk.CTkLabel(
                id_frame,
                text=employee['emp_id'],
                font=ctk.CTkFont(size=13)
            ).pack(padx=10, pady=8)
            
            # Name Cell
            name_frame = ctk.CTkFrame(self.results_frame, fg_color=COLORS["black"])
            name_frame.grid(row=idx, column=1, padx=2, pady=2, sticky="nsew")
            ctk.CTkLabel(
                name_frame,
                text=employee['name'],
                font=ctk.CTkFont(size=13)
            ).pack(padx=10, pady=8)
            
            # Division Cell
            div_frame = ctk.CTkFrame(self.results_frame, fg_color=COLORS["black"])
            div_frame.grid(row=idx, column=2, padx=2, pady=2, sticky="nsew")
            
            div_tag = ctk.CTkFrame(
                div_frame,
                fg_color=COLORS["pink"],
                corner_radius=6
            )
            div_tag.pack(padx=10, pady=8)
            ctk.CTkLabel(
                div_tag,
                text=employee['division'],
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS["white"]
            ).pack(padx=8, pady=2)

    def display_item_results(self, results):
        # Configure grid columns
        self.results_frame.grid_columnconfigure(0, weight=1, minsize=200)  # Name
        self.results_frame.grid_columnconfigure(1, weight=0, minsize=100)  # Status
        self.results_frame.grid_columnconfigure(2, weight=0, minsize=300)  # Attributes

        # Create headers
        headers = ["Item Name", "Status", "Attributes"]
        for col, header in enumerate(headers):
            header_frame = ctk.CTkFrame(self.results_frame, fg_color=COLORS["black"])
            header_frame.grid(row=0, column=col, padx=2, pady=2, sticky="nsew")
            
            ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=COLORS["white"]
            ).pack(padx=10, pady=8)

        # Add item rows
        for idx, item in enumerate(results, 1):
            # Name Cell
            name_frame = ctk.CTkFrame(self.results_frame, fg_color=COLORS["black"])
            name_frame.grid(row=idx, column=0, padx=2, pady=2, sticky="nsew")
            ctk.CTkLabel(
                name_frame,
                text=item.name,
                font=ctk.CTkFont(size=13),
                wraplength=300
            ).pack(padx=10, pady=8)
            
            # Status Cell
            status_frame = ctk.CTkFrame(self.results_frame, fg_color=COLORS["black"])
            status_frame.grid(row=idx, column=1, padx=2, pady=2, sticky="nsew")
            
            status_tag = ctk.CTkFrame(
                status_frame,
                fg_color={
                    "active": "#4CAF50",
                    "retired": "#FFA726",
                    "lost": "#EF5350"
                }.get(item.status.lower(), COLORS["black"]),
                corner_radius=6
            )
            status_tag.pack(padx=10, pady=8)
            ctk.CTkLabel(
                status_tag,
                text=item.status.upper(),
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS["white"]
            ).pack(padx=8, pady=2)
            
            # Attributes Cell
            attrs_frame = ctk.CTkFrame(self.results_frame, fg_color=COLORS["black"])
            attrs_frame.grid(row=idx, column=2, padx=2, pady=2, sticky="nsew")
            
            attrs_container = ctk.CTkFrame(attrs_frame, fg_color="transparent")
            attrs_container.pack(padx=10, pady=8, fill="x")
            
            if hasattr(item, 'attributes'):
                for i, attr in enumerate(item.attributes):
                    attr_tag = ctk.CTkFrame(
                        attrs_container,
                        fg_color=COLORS["secondary_bg"],
                        corner_radius=6
                    )
                    attr_tag.pack(side="left", padx=2, pady=2)
                    ctk.CTkLabel(
                        attr_tag,
                        text=f"{attr.name}: {attr.value}",
                        font=ctk.CTkFont(size=12),
                        text_color=COLORS["white"]
                    ).pack(padx=6, pady=4)


    def display_division_results(self, results):
        # Configure grid columns
        self.results_frame.grid_columnconfigure(0, weight=1, minsize=200)  # Name
        self.results_frame.grid_columnconfigure(1, weight=0, minsize=150)  # Employee Count

        # Create headers
        headers = ["Division Name", "Employee Count"]
        for col, header in enumerate(headers):
            header_frame = ctk.CTkFrame(self.results_frame, fg_color=COLORS["black"])
            header_frame.grid(row=0, column=col, padx=2, pady=2, sticky="nsew")
            
            ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=COLORS["white"]
            ).pack(padx=10, pady=8)

        # Add division rows
        for idx, division in enumerate(results, 1):
            # Name Cell
            name_frame = ctk.CTkFrame(self.results_frame, fg_color=COLORS["black"])
            name_frame.grid(row=idx, column=0, padx=2, pady=2, sticky="nsew")
            ctk.CTkLabel(
                name_frame,
                text=division.name,
                font=ctk.CTkFont(size=13)
            ).pack(padx=10, pady=8)
            
            # Employee Count Cell
            count_frame = ctk.CTkFrame(self.results_frame, fg_color=COLORS["black"])
            count_frame.grid(row=idx, column=1, padx=2, pady=2, sticky="nsew")
            
            count_tag = ctk.CTkFrame(
                count_frame,
                fg_color=COLORS["green"],
                corner_radius=6
            )
            count_tag.pack(padx=10, pady=8)
            ctk.CTkLabel(
                count_tag,
                text=str(division.employee_count),
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS["white"]
            ).pack(padx=8, pady=2)

    def display_combined_results(self, emp_results, item_results, div_results):
        current_row = 0

        if emp_results:
            # Employee section header
            header_frame = ctk.CTkFrame(self.results_frame, fg_color=COLORS["black"])
            header_frame.grid(row=current_row, column=0, columnspan=3, padx=2, pady=(10, 2), sticky="nsew")
            ctk.CTkLabel(
                header_frame,
                text="Employees",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=COLORS["white"]
            ).pack(padx=10, pady=8)
            current_row += 1
            
            self.display_employee_results(emp_results)
            current_row += len(emp_results) + 1

        if item_results:
            # Item section header
            header_frame = ctk.CTkFrame(self.results_frame, fg_color=COLORS["black"])
            header_frame.grid(row=current_row, column=0, columnspan=3, padx=2, pady=(10, 2), sticky="nsew")
            ctk.CTkLabel(
                header_frame,
                text="Items",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=COLORS["white"]
            ).pack(padx=10, pady=8)
            current_row += 1
            
            self.display_item_results(item_results)
            current_row += len(item_results) + 1

        if div_results:
            # Division section header
            header_frame = ctk.CTkFrame(self.results_frame, fg_color=COLORS["black"])
            header_frame.grid(row=current_row, column=0, columnspan=2, padx=2, pady=(10, 2), sticky="nsew")
            ctk.CTkLabel(
                header_frame,
                text="Divisions",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=COLORS["white"]
            ).pack(padx=10, pady=8)
            current_row += 1
            
            self.display_division_results(div_results)
