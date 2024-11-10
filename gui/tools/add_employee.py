# gui/tools/add_employee.py
import customtkinter as ctk
from collections import defaultdict

from controllers.crud import create_employee
from config import COLORS

class AddEmployee:
    def __init__(self, main_frame, return_to_manager):
        self.main_frame = main_frame
        self.return_to_manager = return_to_manager
        self.row_frames = []
        self.current_rows = 0
        self.min_rows = 5  # Minimum number of rows to show
        
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
            text="Add Employees",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["white"]
        )
        title.pack(side="left", padx=20)

    def create_spreadsheet(self):
        # Main container frame
        outer_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=COLORS["secondary_bg"],
            corner_radius=15,
            border_width=2,
            border_color=COLORS["white"]
        )
        outer_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create headers container
        headers_frame = ctk.CTkFrame(outer_frame, fg_color=COLORS["black"], height=50)
        headers_frame.pack(fill="x", padx=5, pady=5)
        headers_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Create column headers
        headers = ["EMP ID", "NAME", "DIVISION"]
        for i, header in enumerate(headers):
            header_label = ctk.CTkLabel(
                headers_frame,
                text=header,
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=COLORS["white"]
            )
            header_label.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
        
        # Create scrollable frame for rows
        self.scrollable_frame = ctk.CTkScrollableFrame(
            outer_frame,
            fg_color="transparent",
            scrollbar_button_color=COLORS["pink"],
            scrollbar_button_hover_color=COLORS["darker_pink"]
        )
        self.scrollable_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Configure grid columns for the scrollable frame
        self.scrollable_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Add initial rows
        for _ in range(self.min_rows):
            self.add_row()
            
        # Create buttons frame at the bottom
        buttons_frame = ctk.CTkFrame(outer_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=5, pady=10)
        
        # Add Row button
        add_row_btn = ctk.CTkButton(
            buttons_frame,
            text="+ Add Row",
            command=self.add_row,
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=120,
            height=35,
            font=ctk.CTkFont(size=14)
        )
        add_row_btn.pack(side="left", padx=5)
        
        # Submit button
        submit_btn = ctk.CTkButton(
            buttons_frame,
            text="Submit",
            command=self.submit_employees,
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=120,
            height=35,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        submit_btn.pack(side="right", padx=5)

    def add_row(self):
        self.current_rows += 1
        row_number = self.current_rows
        
        # Employee ID Entry
        emp_id = ctk.CTkEntry(
            self.scrollable_frame,
            height=35,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["black"],
            border_color=COLORS["ash"],
            border_width=2,
            placeholder_text=f"EMP{row_number:03d}"
        )
        emp_id.grid(row=row_number-1, column=0, padx=5, pady=5, sticky="ew")
        
        # Name Entry
        name = ctk.CTkEntry(
            self.scrollable_frame,
            height=35,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["black"],
            border_color=COLORS["ash"],
            border_width=2,
            placeholder_text="Enter Name"
        )
        name.grid(row=row_number-1, column=1, padx=5, pady=5, sticky="ew")
        
        # Division Dropdown
        division = ctk.CTkComboBox(
            self.scrollable_frame,
            height=35,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["black"],
            border_color=COLORS["ash"],
            button_color=COLORS["pink"],
            button_hover_color=COLORS["darker_pink"],
            dropdown_fg_color=COLORS["black"],
            values=["IT", "HR", "Finance", "Operations", "Marketing", "Sales"],
            state="readonly"
        )
        division.grid(row=row_number-1, column=2, padx=5, pady=5, sticky="ew")
        
        # Store the row's widgets for later access
        self.row_frames.append((emp_id, name, division))

    def submit_employees(self):
        employees_data = []
        for emp_id, name, division in self.row_frames:
            if emp_id.get() and name.get() and division.get():  # Only collect filled rows
                employees_data.append({
                    "emp_id": emp_id.get(),
                    "name": name.get(),
                    "division": division.get()
                })
        
        print("Collected Employee Data:", employees_data)
        # Here you would typically save this data to your database
        # For now, we'll just print it
        
    def display(self):
        self.clear_main_frame()
        self.create_header()
        self.create_spreadsheet()

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()