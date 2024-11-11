import customtkinter as ctk
from config import COLORS
from gui.tools import AddItems, AddEmployee, AddDivision, BulkEmployeeImport, AssignItemsToEmployees, TransferItemBetweenEmployees

class ManagerTools():
    def __init__(self, main_frame, inventory):
        self.main_frame = main_frame
        self.inventory = inventory
        
        # Organize tools by category
        self.tool_categories = {
            "Inventory Management": [
                ("Add Single Item", self.add_item_cmd),
                ("Bulk Import Items", self.placeholder_command),
                ("Update Item Details", self.placeholder_command),
                ("Remove Items", self.placeholder_command),
                ("View Item History", self.placeholder_command),
            ],
            "Employee Management": [
                ("Add Employee", self.add_employee_cmd),
                ("Bulk Import Employees", self.bulk_employee_import_cmd),
                ("Update Employee Info", self.placeholder_command),
                ("Remove Employee", self.placeholder_command),
                ("View Employee Records", self.placeholder_command),
            ],
            "Division Management": [
                ("Create Division", self.add_division_cmd),
                ("Update Division", self.placeholder_command),
                ("Remove Division", self.placeholder_command),
                ("View Division Structure", self.placeholder_command),
            ],
            "Asset Assignment": [
                ("Assign Items to Employee", self.assign_items_cmd),
                ("Transfer Items Between Employees", self.transfer_items_cmd),
                ("Bulk Asset Transfer", self.placeholder_command),
                ("View Asset Assignments", self.placeholder_command),
            ],
            "Reports & Analytics": [
                ("Inventory Report", self.placeholder_command),
                ("Asset Utilization", self.placeholder_command),
                ("Employee Assignment Summary", self.placeholder_command),
                ("Division Statistics", self.placeholder_command),
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