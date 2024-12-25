import customtkinter as ctk
from config import COLORS
from gui.tools import (
    AddItems,
    AddEmployee,
    AddDivision,
    BulkEmployeeImport,
    AssignItemsToEmployees,
    TransferItemBetweenEmployees,
    ViewItemDetails,
    UpdateItemDetails,
    RemoveItem,
    UpdateEmployeeDetail,
    ViewEmployeeRecords,
    RemoveEmployee,
    UpdateDivision,
    RemoveDivision,
    ViewDivisionStructure,
    ViewAssetAssignment
)
from utils.summary import divison_wise_employee_items_to_excel

class ManagerTools():
    def __init__(self, main_frame, inventory):
        self.main_frame = main_frame
        self.inventory = inventory
        
        # Organize tools by category
        self.tool_categories = {
            "Inventory Management": [
                ("Add Single Item", self.add_item_cmd),
                #("Bulk Import Items", self.placeholder_command),
                ("Update Item Details", self.update_item_details_cmd),
                ("Remove Items", self.remove_item_cmd),
                ("View Item History", self.view_item_details_cmd),
            ],
            "Employee Management": [
                ("Add Employee", self.add_employee_cmd),
                ("Bulk Import Employees", self.bulk_employee_import_cmd),
                ("Update Employee Info", self.update_employee_details_cmd),
                ("Remove Employee", self.remove_employee_cmd),
                ("View Employee Records", self.view_employee_records_cmd),
            ],
            "Division Management": [
                ("Create Division", self.add_division_cmd),
                ("Update Division", self.update_division_cmd),
                ("Remove Division", self.remove_division_cmd),
                ("View Division Structure", self.view_division_structure_cmd),
            ],
            "Asset Assignment": [
                ("Assign Items to Employee", self.assign_items_cmd),
                ("Transfer Items Between Employees", self.transfer_items_cmd),
                #("Bulk Asset Transfer", self.placeholder_command),
                #("View Asset Assignments", self.view_asset_assignment_cmd),
            ],
            "Reports & Analytics": [
                ('Inventory Report to Excel', self.divison_wise_employee_items_to_excel),
                ("Employees to Excel", self.placeholder_command),
                ("Items to Excel", self.placeholder_command),
                ("Basic Report with Counts", self.placeholder_command),
                #("", self.placeholder_command),
            ]
        }

    def return_to_manager_function(self):
        self.clear_main_frame()
        self.display()

    def add_item_cmd(self):
        add_items = AddItems(self.main_frame, self.return_to_manager_function)
        add_items.display()

    def add_employee_cmd(self):
        add_employee = AddEmployee(self.main_frame, self.return_to_manager_function)
        add_employee.display()
    
    def add_division_cmd(self):
        add_division = AddDivision(self.main_frame, self.return_to_manager_function)
        add_division.display()

    def bulk_employee_import_cmd(self):
        bulk_employee_import = BulkEmployeeImport(self.main_frame, self.return_to_manager_function)
        bulk_employee_import.display()

    def assign_items_cmd(self):
        assign_items = AssignItemsToEmployees(self.main_frame, self.return_to_manager_function)
        assign_items.display()

    def transfer_items_cmd(self):
        transfer_items = TransferItemBetweenEmployees(self.main_frame, self.return_to_manager_function)
        transfer_items.display()

    def view_item_details_cmd(self):
        view_item_details = ViewItemDetails(self.main_frame, self.return_to_manager_function)
        view_item_details.display()
    
    def update_item_details_cmd(self):
        update_item_details = UpdateItemDetails(self.main_frame, self.return_to_manager_function)
        update_item_details.display()

    def remove_item_cmd(self):
        remove_item = RemoveItem(self.main_frame, self.return_to_manager_function)
        remove_item.display()

    def update_employee_details_cmd(self):
        update_employee_details = UpdateEmployeeDetail(self.main_frame, self.return_to_manager_function)
        update_employee_details.display()

    def view_employee_records_cmd(self):
        view_employee_records = ViewEmployeeRecords(self.main_frame, self.return_to_manager_function)
        view_employee_records.display()

    def remove_employee_cmd(self):
        remove_employee = RemoveEmployee(self.main_frame, self.return_to_manager_function)
        remove_employee.display()

    def update_division_cmd(self):
        update_division = UpdateDivision(self.main_frame, self.return_to_manager_function)
        update_division.display()

    def remove_division_cmd(self):
        remove_division = RemoveDivision(self.main_frame,  self.return_to_manager_function)
        remove_division.display()

    def view_division_structure_cmd(self):
        view_division_structure = ViewDivisionStructure(self.main_frame, self.return_to_manager_function)
        view_division_structure.display()

    def view_asset_assignment_cmd(self):
        view_asset_assignment = ViewAssetAssignment(self.main_frame, self.return_to_manager_function)
        view_asset_assignment.display()

    def divison_wise_employee_items_to_excel(self):
        divison_wise_employee_items_to_excel()

    def placeholder_command(self):
        print("Button clicked!")

    def create_section_header(self, parent, text):
        # Create container for header and separator
        header_container = ctk.CTkFrame(parent, fg_color="transparent")
        
        # Create header label
        header = ctk.CTkLabel(
            header_container,
            text=text,
            font=ctk.CTkFont(size=20, weight="bold", family="Verdana"),
            text_color=COLORS.get("white", "#FFFFFF")
        )
        header.pack(anchor="w", padx=(10, 0), pady=(15, 5))
        
        # Create separator
        separator = ctk.CTkFrame(
            header_container,
            height=2,
            fg_color=COLORS.get("pink", "#FF69B4")
        )
        separator.pack(fill="x", padx=10, pady=(0, 10))
        
        return header_container

    def create_card_button(self, parent, text, command):
        card = ctk.CTkFrame(
            parent,
            corner_radius=10,
            fg_color=COLORS["secondary_bg"],
            border_width=2,
            border_color=COLORS['white']
        )

        def on_enter(e):
            card.configure(fg_color=COLORS.get("hover", "#3E3E3E"))

        def on_leave(e):
            card.configure(fg_color=COLORS.get("secondary_bg", "#1A1A1A"))

        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)

        button = ctk.CTkButton(
            card,
            text=text,
            command=command,
            font=ctk.CTkFont(size=16, weight="bold", family="futura"),
            fg_color="transparent",
            hover_color=COLORS['pink'],
            height=70,  # Slightly reduced height
            width=150,
        )
        button.pack(expand=True, fill="both", padx=8, pady=8)  # Slightly reduced padding

        return card

    def display(self):
        self.clear_main_frame()

        # Create title
        title = ctk.CTkLabel(
            self.main_frame, 
            text="Manager Tools", 
            font=ctk.CTkFont(size=28, weight="bold", family="Verdana"),
        )
        title.pack(pady=(15, 5))

        # Create scrollable container
        container = ctk.CTkScrollableFrame(
            self.main_frame,
            fg_color="transparent",
            scrollbar_button_color=COLORS.get("pink", "#FF69B4"),
            scrollbar_button_hover_color=COLORS.get("hover", "#3E3E3E")
        )
        container.pack(expand=True, fill="both", padx=10, pady=5)

        # Create sections for each category
        for category, tools in self.tool_categories.items():
            # Add section header
            header_container = self.create_section_header(container, category)
            header_container.pack(fill="x")
            
            # Create grid frame for cards in this category
            cards_frame = ctk.CTkFrame(container, fg_color="transparent")
            cards_frame.pack(fill="x", padx=5)
            
            # Configure grid columns
            for i in range(3):
                cards_frame.grid_columnconfigure(i, weight=1)

            # Add tool cards
            for i, (tool_name, command) in enumerate(tools):
                row = i // 3
                col = i % 3
                card = self.create_card_button(cards_frame, tool_name, command)
                card.grid(row=row, column=col, padx=8, pady=8, sticky="ew")

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()