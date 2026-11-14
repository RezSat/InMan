from gui.utils import clear_children
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
from utils.summary import divison_wise_employee_items_to_excel, employee_id_name_to_excel, items_to_excel

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
                ("View Item Records", self.view_item_details_cmd),
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
                ("Employees to Excel", self.employee_id_name_to_excel),
                ("Items to Excel", self.items_to_excel),
                #("", self.placeholder_command),
            ]
        }

    def return_to_manager_function(self):
        self.clear_main_frame()
        self.display()

    def _open_tool(self, screen):
        screen(self.main_frame, self.return_to_manager_function).display()

    def add_item_cmd(self):
        self._open_tool(AddItems)

    def add_employee_cmd(self):
        self._open_tool(AddEmployee)

    def add_division_cmd(self):
        self._open_tool(AddDivision)

    def bulk_employee_import_cmd(self):
        self._open_tool(BulkEmployeeImport)

    def assign_items_cmd(self):
        self._open_tool(AssignItemsToEmployees)

    def transfer_items_cmd(self):
        self._open_tool(TransferItemBetweenEmployees)

    def view_item_details_cmd(self):
        self._open_tool(ViewItemDetails)

    def update_item_details_cmd(self):
        self._open_tool(UpdateItemDetails)

    def remove_item_cmd(self):
        self._open_tool(RemoveItem)

    def update_employee_details_cmd(self):
        self._open_tool(UpdateEmployeeDetail)

    def view_employee_records_cmd(self):
        self._open_tool(ViewEmployeeRecords)

    def remove_employee_cmd(self):
        self._open_tool(RemoveEmployee)

    def update_division_cmd(self):
        self._open_tool(UpdateDivision)

    def remove_division_cmd(self):
        self._open_tool(RemoveDivision)

    def view_division_structure_cmd(self):
        self._open_tool(ViewDivisionStructure)

    def view_asset_assignment_cmd(self):
        self._open_tool(ViewAssetAssignment)

    def divison_wise_employee_items_to_excel(self):
        divison_wise_employee_items_to_excel()

    def employee_id_name_to_excel(self):
        employee_id_name_to_excel()

    def items_to_excel(self):
        items_to_excel()

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
        clear_children(self.main_frame)