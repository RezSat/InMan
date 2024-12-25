import customtkinter as ctk
from tkinter import ttk, filedialog
import pandas as pd
from config import COLORS
from controllers import (get_all_employees, get_all_items, get_all_divisions, 
                       get_division_details_with_counts, get_employee_details_with_items)
from controllers.crud import get_all_division_names, get_division
from models.database import SessionLocal
from utils.search import search_divisions, search_employees, search_items, search_unique_key

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
        search_types = ["Select type","Employees", "Items", "Divisions", "Unique Key"]
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
        division_filter = ctk.CTkLabel(
        self.filters_frame,
        text="",
        font=ctk.CTkFont(size=14),
        text_color=COLORS["ash"]
            )
        division_filter.pack(side="left", padx=5)

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
        elif search_type == "Unique Key":
            results = search_unique_key(query)
            self.display_unique_key_results(results)
        else:
            # Perform all searches
            
            emp_results = [{
                                'emp_id': emp.emp_id,
                                'name': emp.name,
                                'division_id': emp.division_id,
                                'division': str(get_division(emp.division_id).name)  # Assuming get_division returns a Division object
                            }
                            for emp in search_employees(SessionLocal(), query)
                            ]
            item_results = [
                            {
                                'item_id': item.item_id,
                                'name': item.name,
                                #'unique_key': item.EmployeeItem.unique_key  # Assuming there is a unique_key field
                            }
                            for item in search_items(SessionLocal(), query)
                        ]
            div_results = [
                            {
                                'division_id': division.division_id,
                                'name': division.name,
                            }
                            for division in search_divisions(SessionLocal(), query)
                        ]
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
        """
        Display search results in separate, independent containers
        
        Args:
            emp_results (list): List of employee search results
            item_results (list): List of item search results
            div_results (list): List of division search results
        """
        # Clear existing results frame
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        # Create a scrollable main container
        main_container = ctk.CTkScrollableFrame(
            self.results_frame, 
            fg_color="transparent",
            scrollbar_button_color=COLORS["pink"],
            scrollbar_button_hover_color=COLORS["darker_pink"]
        )
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Employees Results Container
        if emp_results:
            # Employees Container
            employees_container = ctk.CTkFrame(
                main_container, 
                fg_color=COLORS["secondary_bg"],
                corner_radius=10
            )
            employees_container.pack(fill="x", pady=10)

            # Employees Header
            emp_header = ctk.CTkFrame(employees_container, fg_color=COLORS["black"])
            emp_header.pack(fill="x", padx=2, pady=2)
            ctk.CTkLabel(
                emp_header,
                text="Employees Search Results",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=COLORS["white"]
            ).pack(padx=10, pady=8)

            # Employees Results Grid
            emp_results_grid = ctk.CTkFrame(employees_container, fg_color="transparent")
            emp_results_grid.pack(fill="x", padx=5, pady=5)

            # Configure grid columns
            emp_results_grid.grid_columnconfigure(0, weight=0, minsize=100)  # ID
            emp_results_grid.grid_columnconfigure(1, weight=1, minsize=200)  # Name
            emp_results_grid.grid_columnconfigure(2, weight=0, minsize=150)  # Division

            # Headers
            headers = ["Employee ID", "Name", "Division"]
            for col, header in enumerate(headers):
                header_frame = ctk.CTkFrame(emp_results_grid, fg_color=COLORS["black"])
                header_frame.grid(row=0, column=col, padx=2, pady=2, sticky="nsew")
                ctk.CTkLabel(
                    header_frame,
                    text=header,
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=COLORS["white"]
                ).pack(padx=10, pady=8)

            # Add employee rows
            for idx, employee in enumerate(emp_results, 1):
                # ID Cell
                id_frame = ctk.CTkFrame(emp_results_grid, fg_color=COLORS["black"])
                id_frame.grid(row=idx, column=0, padx=2, pady=2, sticky="nsew")
                ctk.CTkLabel(
                    id_frame,
                    text=str(employee['emp_id']),
                    font=ctk.CTkFont(size=13)
                ).pack(padx=10, pady=8)
                
                # Name Cell
                name_frame = ctk.CTkFrame(emp_results_grid, fg_color=COLORS["black"])
                name_frame.grid(row=idx, column=1, padx=2, pady=2, sticky="nsew")
                ctk.CTkLabel(
                    name_frame,
                    text=employee['name'],
                    font=ctk.CTkFont(size=13)
                ).pack(padx=10, pady=8)
                
                # Division Cell
                div_frame = ctk.CTkFrame(emp_results_grid, fg_color=COLORS["black"])
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

        # Items Results Container
        if item_results:
            # Items Container
            items_container = ctk.CTkFrame(
                main_container, 
                fg_color=COLORS["secondary_bg"],
                corner_radius=10
            )
            items_container.pack(fill="x", pady=10)

            # Items Header
            items_header = ctk.CTkFrame(items_container, fg_color=COLORS["black"])
            items_header.pack(fill="x", padx=2, pady=2)
            ctk.CTkLabel(
                items_header,
                text="Items Search Results",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=COLORS["white"]
            ).pack(padx=10, pady=8)

            # Items Results Grid
            items_results_grid = ctk.CTkFrame(items_container, fg_color="transparent")
            items_results_grid.pack(fill="x", padx=5, pady=5)

            # Configure grid columns
            items_results_grid.grid_columnconfigure(0, weight=1, minsize=200)  # Name
            items_results_grid.grid_columnconfigure(1, weight=0, minsize=100)  # Status
            items_results_grid.grid_columnconfigure(2, weight=0, minsize=300)  # Attributes

            # Headers
            headers = ["Item Name", "Status", "Attributes"]
            for col, header in enumerate(headers):
                header_frame = ctk.CTkFrame(items_results_grid, fg_color=COLORS["black"])
                header_frame.grid(row=0, column=col, padx=2, pady=2, sticky="nsew")
                ctk.CTkLabel(
                    header_frame,
                    text=header,
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=COLORS["white"]
                ).pack(padx=10, pady=8)

            # Add item rows
            for idx, item in enumerate(item_results, 1):
                # Name Cell
                name_frame = ctk.CTkFrame(items_results_grid, fg_color=COLORS["black"])
                name_frame.grid(row=idx, column=0, padx=2, pady=2, sticky="nsew")
                ctk.CTkLabel(
                    name_frame,
                    text=item['name'],
                    font=ctk.CTkFont(size=13),
                    wraplength=300
                ).pack(padx=10, pady=8)
                
                # Status Cell
                status_frame = ctk.CTkFrame(items_results_grid, fg_color=COLORS["black"])
                status_frame.grid(row=idx, column=1, padx=2, pady=2, sticky="nsew")
                
                status_tag = ctk.CTkFrame(
                    status_frame,
                    fg_color={
                        "active": "#4CAF50",
                        "retired": "#FFA726",
                        "lost": "#EF5350"
                    }.get(item.get('status', '').lower(), COLORS["black"]),
                    corner_radius=6
                )
                status_tag.pack(padx=10, pady=8)
                ctk.CTkLabel(
                    status_tag,
                    text=item.get('status', 'N/A').upper(),
                    font=ctk.CTkFont(size=12 , weight="bold"),
                    text_color=COLORS["white"]
                ).pack(padx=8, pady=2)
                
                # Attributes Cell
                attrs_frame = ctk.CTkFrame(items_results_grid, fg_color=COLORS["black"])
                attrs_frame.grid(row=idx, column=2, padx=2, pady=2, sticky="nsew")
                
                attrs_container = ctk.CTkFrame(attrs_frame, fg_color="transparent")
                attrs_container.pack(padx=10, pady=8, fill="x")
                
                if 'attributes' in item:
                    for attr in item['attributes']:
                        attr_tag = ctk.CTkFrame(
                            attrs_container,
                            fg_color=COLORS["secondary_bg"],
                            corner_radius=6
                        )
                        attr_tag.pack(side="left", padx=2, pady=2)
                        ctk.CTkLabel(
                            attr_tag,
                            text=f"{attr['name']}: {attr['value']}",
                            font=ctk.CTkFont(size=12),
                            text_color=COLORS["white"]
                        ).pack(padx=6, pady=4)

        # Divisions Results Container
        if div_results:
            # Divisions Container
            divisions_container = ctk.CTkFrame(
                main_container, 
                fg_color=COLORS["secondary_bg"],
                corner_radius=10
            )
            divisions_container.pack(fill="x", pady=10)

            # Divisions Header
            div_header = ctk.CTkFrame(divisions_container, fg_color=COLORS["black"])
            div_header.pack(fill="x", padx=2, pady=2)
            ctk.CTkLabel(
                div_header,
                text="Divisions Search Results",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=COLORS["white"]
            ).pack(padx=10, pady=8)

            # Divisions Results Grid
            div_results_grid = ctk.CTkFrame(divisions_container, fg_color="transparent")
            div_results_grid.pack(fill="x", padx=5, pady=5)

            # Configure grid columns
            div_results_grid.grid_columnconfigure(0, weight=1, minsize=200)  # Name
            div_results_grid.grid_columnconfigure(1, weight=0, minsize=150)  # Employee Count

            # Headers
            headers = ["Division Name", "Employee Count"]
            for col, header in enumerate(headers):
                header_frame = ctk.CTkFrame(div_results_grid, fg_color=COLORS["black"])
                header_frame.grid(row=0, column=col, padx=2, pady=2, sticky="nsew")
                ctk.CTkLabel(
                    header_frame,
                    text=header,
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=COLORS["white"]
                ).pack(padx=10, pady=8)

            # Add division rows
            for idx, division in enumerate(div_results, 1):
                # Name Cell
                name_frame = ctk.CTkFrame(div_results_grid, fg_color=COLORS["black"])
                name_frame.grid(row=idx, column=0, padx=2, pady=2, sticky="nsew")
                ctk.CTkLabel(
                    name_frame,
                    text=division['name'],
                    font=ctk.CTkFont(size=13)
                ).pack(padx=10, pady=8)
                
                # Employee Count Cell
                count_frame = ctk.CTkFrame(div_results_grid, fg_color=COLORS["black"])
                count_frame.grid(row=idx, column=1, padx=2, pady=2, sticky="nsew")
                
                count_tag = ctk.CTkFrame(
                    count_frame,
                    fg_color=COLORS["green"],
                    corner_radius=6
                )
                count_tag.pack(padx=10, pady=8)
                ctk.CTkLabel(
                    count_tag,
                    text=str(division['employee_count']),
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=COLORS["white"]
                ).pack(padx=8, pady=2)

        # Optional: Add a message if no results were found
        if not emp_results and not item_results and not div_results:
            no_results_frame = ctk.CTkFrame(main_container, fg_color=COLORS["black"])
            no_results_frame.pack(fill="x", padx=2, pady=(10, 2))
            ctk.CTkLabel(
                no_results_frame,
                text="No results found.",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=COLORS["white"]
            ).pack(padx=10, pady=8)

    def display_unique_key_results(self, results):
        # Configure grid columns
        self.results_frame.grid_columnconfigure(0, weight=0, minsize=100)  # Employee ID
        self.results_frame.grid_columnconfigure(1, weight=1, minsize=200)  # Employee Name
        self.results_frame.grid_columnconfigure(2, weight=1, minsize=200)  # Item Name
        self.results_frame.grid_columnconfigure(3, weight=1, minsize=200)  # Unique Key

        # Create headers
        headers = ["Employee ID", "Employee Name", "Item Name", "Unique Key"]
        for col, header in enumerate(headers):
            header_frame = ctk.CTkFrame(self.results_frame, fg_color=COLORS["black"])
            header_frame.grid(row=0, column=col, padx=2, pady=2, sticky="nsew")
            
            ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=COLORS["white"]
            ).pack(padx=10, pady=8)

        # Add rows
        for idx, result in enumerate(results, 1):
            # Employee ID Cell
            emp_id_frame = ctk.CTkFrame(self.results_frame, fg_color=COLORS["black"])
            emp_id_frame.grid(row=idx, column=0, padx=2, pady=2, sticky="nsew")
            ctk.CTkLabel(
                emp_id_frame,
                text=result['emp_id'],
                font=ctk.CTkFont(size=13)
            ).pack(padx=10, pady=8)
            
            # Employee Name Cell
            emp_name_frame = ctk.CTkFrame(self.results_frame, fg_color=COLORS["black"])
            emp_name_frame.grid(row=idx, column=1, padx=2, pady=2, sticky="nsew")
            ctk.CTkLabel(
                emp_name_frame,
                text=result['employee_name'],
                font=ctk.CTkFont(size=13)
            ).pack(padx=10, pady=8)
            
            # Item Name Cell
            item_name_frame = ctk.CTkFrame(self.results_frame, fg_color=COLORS["black"])
            item_name_frame.grid(row=idx, column=2, padx=2, pady=2, sticky="nsew")
            ctk.CTkLabel(
                item_name_frame,
                text=result['item_name'],
                font=ctk.CTkFont(size=13)
            ).pack(padx=10, pady=8)
            
            # Unique Key Cell
            unique_key_frame = ctk.CTkFrame(self.results_frame, fg_color=COLORS["black"])
            unique_key_frame.grid(row=idx, column=3, padx=2, pady=2, sticky="nsew")
            
            unique_key_tag = ctk.CTkFrame(
                unique_key_frame,
                fg_color=COLORS["pink"],
                corner_radius=6
            )
            unique_key_tag.pack(padx=10, pady=8)
            ctk.CTkLabel(
                unique_key_tag,
                text=result['unique_key'],
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS["white"]
            ).pack(padx=8, pady=2)

        # Optional: No results message
        if not results:
            no_results_frame = ctk.CTkFrame(self.results_frame, fg_color=COLORS["black"])
            no_results_frame.grid(row=1, column=0, columnspan=4, padx=2, pady=(10, 2), sticky="nsew")
            ctk.CTkLabel(
                no_results_frame,
                text="No results found.",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=COLORS["white"]
            ).pack(padx=10, pady=8)