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
            height=35
        )
        export_btn.pack(side="right", padx=10)

    def create_search_panel(self):
        # Search panel container
        search_panel = ctk.CTkFrame(self.main_frame, fg_color=COLORS["secondary_bg"])
        search_panel.pack(fill="x", padx=20, pady=10)
        
        # Search type selector
        search_types = ["All", "Employees", "Items", "Divisions"]
        self.search_type = ctk.CTkComboBox(
            search_panel,
            values=search_types,
            width=150,
            command=self.on_search_type_change
        )
        self.search_type.pack(side="left", padx=10, pady=10)
        
        # Search entry
        self.search_entry = ctk.CTkEntry(
            search_panel,
            placeholder_text="Search...",
            width=300,
            height=35
        )
        self.search_entry.pack(side="left", padx=10, pady=10)
        self.search_entry.bind('<Return>', self.perform_search)
        
        # Advanced filters frame
        self.filters_frame = ctk.CTkFrame(search_panel, fg_color="transparent")
        self.filters_frame.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        
        # Search button
        search_btn = ctk.CTkButton(
            search_panel,
            text="Search",
            command=self.perform_search,
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=100,
            height=35
        )
        search_btn.pack(side="right", padx=10, pady=10)

    def create_results_view(self):
        # Results container
        self.results_frame = ctk.CTkScrollableFrame(
            self.main_frame,
            fg_color=COLORS["secondary_bg"],
            scrollbar_button_color=COLORS["pink"],
            scrollbar_button_hover_color=COLORS["darker_pink"]
        )
        self.results_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Configure grid columns
        self.results_frame.grid_columnconfigure(0, weight=1)
        
        # Header row will be added dynamically based on search type
        self.create_headers_for_current_view()

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
            results = search_employees(SessionLocal(), query)
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
            headers = ["Name", "Position", "Division"]
        elif search_type == "Items":
            headers = ["Item Name", "Status", "Type"]
        elif search_type == "Divisions":
            headers = ["Division Name", "Employee Count"]
        else:
            headers = ["Search Results"]
        
        for header in headers:
            label = ctk.CTkLabel(self.results_frame, text=header)
            label.pack(side="top", padx=5, pady=5)

    def display_employee_results(self, results):
        """Display employee search results."""
        header = ctk.CTkLabel(self.results_frame, text="Employees", font=ctk.CTkFont(size=16, weight="bold"))
        header.pack(side="top", padx=5, pady=(5, 0))

        # Create a frame for the table
        table_frame = ctk.CTkFrame(self.results_frame)
        table_frame.pack(fill="both", expand=True)

        # Create headers for the table
        name_header = ctk.CTkLabel(table_frame, text="Name", font=ctk.CTkFont(weight="bold"))
        name_header.grid(row=0, column=0, padx=5, pady=5)

        position_header = ctk.CTkLabel(table_frame, text="Position", font=ctk.CTkFont(weight="bold"))
        position_header.grid(row=0, column=1, padx=5, pady=5)

        # Populate the table with employee results
        for index, employee in enumerate(results):
            name_label = ctk.CTkLabel(table_frame, text=employee.name)
            name_label.grid(row=index + 1, column=0, padx=5, pady=2)

            position_label = ctk.CTkLabel(table_frame, text=employee.position)
            position_label.grid(row=index + 1, column=1, padx=5, pady=2)

    def display_item_results(self, results):
        """Display item search results."""
        header = ctk.CTkLabel(self.results_frame, text="Items", font=ctk.CTkFont(size=16, weight="bold"))
        header.pack(side="top", padx=5, pady=(5, 0))

        # Create a frame for the table
        table_frame = ctk.CTkFrame(self.results_frame)
        table_frame.pack(fill="both", expand=True)

        # Create headers for the table
        name_header = ctk.CTkLabel(table_frame, text="Item Name", font=ctk.CTkFont(weight="bold"))
        name_header.grid(row=0, column=0, padx=5, pady=5)

        status_header = ctk.CTkLabel(table_frame, text="Status", font=ctk.CTkFont(weight="bold"))
        status_header.grid(row=0, column=1, padx=5, pady=5)

        # Populate the table with item results
        for index, item in enumerate(results):
            name_label = ctk.CTkLabel(table_frame, text=item.name)
            name_label.grid(row=index + 1, column=0, padx=5, pady=2)

            status_label = ctk.CTkLabel(table_frame, text=item.status)
            status_label.grid(row=index + 1, column=1, padx=5, pady=2)

    def display_division_results(self, results):
        """Display division search results."""
        header = ctk.CTkLabel(self.results_frame, text="Divisions", font=ctk.CTkFont(size=16, weight="bold"))
        header.pack(side="top", padx=5, pady=(5, 0))

        # Create a frame for the table
        table_frame = ctk.CTkFrame(self.results_frame)
        table_frame.pack(fill="both", expand=True)

        # Create headers for the table
        name_header = ctk.CTkLabel(table_frame, text="Division Name", font=ctk.CTkFont(weight="bold"))
        name_header.grid(row=0, column=0, padx=5, pady=5)

        employee_count_header = ctk.CTkLabel(table_frame, text="Employee Count", font=ctk.CTkFont(weight="bold"))
        employee_count_header.grid(row=0, column=1, padx=5, pady=5)

        # Populate the table with division results
        for index, division in enumerate(results):
            name_label = ctk.CTkLabel(table_frame, text=division.name)
            name_label.grid(row=index + 1, column=0, padx=5, pady=2)

            employee_count_label = ctk.CTkLabel(table_frame, text=division.employee_count)
            employee_count_label.grid(row=index + 1, column=1, padx=5, pady=2)

    def display_combined_results(self, emp_results, item_results, div_results):
        """Display combined search results."""
        for emp in emp_results:
            label = ctk.CTkLabel(self.results_frame, text=f"Employee: {emp.name}")
            label.pack(side="top", padx=5, pady=5)
        for item in item_results:
            label = ctk.CTkLabel(self.results_frame, text=f"Item: {item.name}")
            label.pack(side="top", padx=5, pady=5)
        for div in div_results:
            label = ctk.CTkLabel(self.results_frame, text=f"Division: {div.name}")
            label.pack(side="top", padx=5, pady=5)
