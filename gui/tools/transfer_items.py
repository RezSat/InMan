import customtkinter as ctk
from config import COLORS

class TransferItemBetweenEmployees:
    def __init__(self, main_frame, return_to_manager):
        self.main_frame = main_frame
        self.return_to_manager = return_to_manager
        self.selected_item = None  # To store the selected item
        self.selected_emp1 = None  # To store the selected employee 1
        self.selected_emp2 = None  # To store the selected employee 2

    def create_header(self):
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.hf = header_frame
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
            text="Transfer Items Between Employees",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["white"]
        )
        title.pack(side="left", padx=20)

    def create_transfer_interface(self):
        outer_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=COLORS["secondary_bg"],
            corner_radius=15,
            border_width=2,
            border_color=COLORS["white"]
        )
        outer_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Search for Employee 1
        self.emp1_search_entry = ctk.CTkEntry(
            outer_frame,
            height=35,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["black"],
            border_color=COLORS["ash"],
            border_width=2,
            placeholder_text="Search Employee (Name or EMP ID)"
        )
        self.emp1_search_entry.pack(padx=10, pady=(10, 5), fill='x')

        emp1_search_button = ctk.CTkButton(
            outer_frame,
            text="Search Employee 1",
            command=self.search_employee_1,
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=200,
            height=35,
            font=ctk.CTkFont(size=14)
        )
        emp1_search_button.pack(padx=10, pady=(0, 10))

        self.emp1_result_box = ctk.CTkScrollableFrame(outer_frame, fg_color="transparent")
        self.emp1_result_box.pack(fill="both", expand=True, padx=10, pady=5)

        # Search for Employee 2
        self.emp2_search_entry = ctk.CTkEntry(
            outer_frame,
            height=35,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["black"],
            border_color=COLORS["ash"],
            border_width=2,
            placeholder_text="Search Employee to Transfer To (Name or EMP ID)"
        )
        self.emp2_search_entry.pack(padx=10, pady=(10, 5), fill='x')

        emp2_search_button = ctk.CTkButton(
            outer_frame,
            text="Search Employee 2",
            command=self.search_employee_2,
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=200,
            height=35,
            font=ctk.CTkFont(size=14)
        )
        emp2_search_button.pack(padx=10, pady=(0, 10))

        self.emp2_result_box = ctk.CTkScrollableFrame(outer_frame, fg_color="transparent")
        self.emp2_result_box.pack (fill="both", expand=True, padx=10, pady=5)

        # Transfer Button
        transfer_button = ctk.CTkButton(
            self.hf,
            text="Transfer Item",
            command=self.transfer_item,
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=200,
            height=35,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        transfer_button.pack(side="right", padx=20)

    def search_employee_1(self):
        emp_id_or_name = self.emp1_search_entry.get()
        # Logic to search for employee by ID or Name
        # For demonstration, let's assume we found an employee
        employee_details = {"emp_id": "EMP001", "name": "John Doe", "items": [("Laptop", "SN12345"), ("Phone", "SN67890")]}
        self.selected_emp1 = employee_details['emp_id']
        self.display_employee_results(employee_details, self.emp1_result_box)

    def search_employee_2(self):
        emp_id_or_name = self.emp2_search_entry.get()
        # Logic to search for employee by ID or Name
        # For demonstration, let's assume we found an employee
        employee_details = {"emp_id": "EMP002", "name": "Jane Smith"}
        self.selected_emp2 = employee_details['emp_id']
        self.display_employee_results(employee_details, self.emp2_result_box, is_emp2=True)

    def display_employee_results(self, employee_details, result_box, is_emp2=False):
        # Clear previous results
        for widget in result_box.winfo_children():
            widget.destroy()
        
        # Display employee details
        emp_label = ctk.CTkLabel(result_box, text=f"{employee_details['emp_id']} - {employee_details['name']}", font=ctk.CTkFont(size=14), text_color=COLORS["white"])
        emp_label.pack(pady=5)

        if is_emp2:
            print(f"Selected Employee 2: {self.selected_emp2}")  # Debugging print
        else:
            # Display items if available
            if "items" in employee_details:
                items = [f"{item_name} (SN: {serial_number})" for item_name, serial_number in employee_details["items"]]
                self.item_dropdown = ctk.CTkComboBox(
                    result_box,
                    height=35,
                    font=ctk.CTkFont(size=14),
                    fg_color=COLORS["black"],
                    border_color=COLORS["ash"],
                    button_color=COLORS["pink"],
                    button_hover_color=COLORS["darker_pink"],
                    dropdown_fg_color=COLORS["black"],
                    values=items,
                    state="readonly",
                    command=self.select_item
                )
                self.item_dropdown.pack(pady=5)

    def select_item(self, selected_item):
        self.selected_item = selected_item
        print(f"Selected Item: {selected_item}")  # For debugging

    def transfer_item(self):
        emp1 = self.selected_emp1
        emp2 = self.selected_emp2
        
        if emp1 and emp2 and self.selected_item:
            print(f"Transferred {self.selected_item} from {emp1} to {emp2}")
            
            # Reset selection
            self.selected_item = None
            self.item_dropdown.set("")  # Reset dropdown
        else:
            print("Please ensure both employees and an item are selected before transferring.")
            print(f"emp1: {emp1}, emp2: {emp2}, selected_item: {self.selected_item}")  # Debugging print

    def display(self):
        self.clear_main_frame()
        self.create_header()
        self.create_transfer_interface()

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
