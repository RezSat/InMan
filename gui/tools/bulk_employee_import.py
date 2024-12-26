# gui/tools/bulk_employee_import.py

import customtkinter as ctk
import pandas as pd
from tkinter import filedialog, messagebox
from config import COLORS
from controllers.crud import create_employee, get_all_divisions

class BulkEmployeeImport:
    def __init__(self, main_frame, return_to_manager):
        self.main_frame = main_frame
        self.return_to_manager = return_to_manager
        self.row_frames = []
        self.default_division = "Not Assigned"  # Default value for division
        self.current_rows = 0
        self.division_dict = {div['name']: div['division_id'] for div in get_all_divisions()}
        self.divisions = [div['name'] for div in get_all_divisions()]

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
            text="Bulk Employee Import",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["white"]
        )
        title.pack(side="left", padx=20)

    def create_import_section(self):
        # Main container frame
        outer_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=COLORS["secondary_bg"],
            corner_radius=15,
            border_width=2,
            border_color=COLORS["white"]
        )
        outer_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create Import Button
        import_button = ctk.CTkButton(
            outer_frame,
            text="Import Employees from Excel",
            command=self.import_employees,
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=200,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        import_button.pack(pady=20)

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

        # Add a Submit button
        submit_button = ctk.CTkButton(
            outer_frame,
            text="Submit",
            command=self.submit_employees,
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=200,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        submit_button.pack(pady=10)

    def import_employees(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
        if not file_path:
            return  # User cancelled the file dialog

        try:
            # Read the Excel file
            df = pd.read_excel(file_path)

            # Clear previous rows
            self.row_frames.clear()
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()

            # Populate the rows with data
            for index, row in df.iterrows():
                emp_id = row.get("EMP_ID", "")
                name = row.get("Name", "")
                division = row.get("Division", self.default_division)

                #if not division or division == self.default_division:
                #    messagebox.showerror("Error", f"Division is not specified for employee '{name}' (ID: {emp_id}). PLEASE SELECT AN DIVISION FROM THE DROPDOWN, IT WIL BE LABALLED AS 'NaN'.")
                #if division not in self.divisions:
                #    messagebox.showerror("Error", f"Division: {division} is not found in the database. Please select an available division from the dropdown for the employee : {emp_id} - {name}" )
                self.add_row(emp_id, name, division)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load spreadsheet: {str(e)}")

    def add_row(self, emp_id="", name="", division=""):
        # Employee ID Entry
        emp_id_entry = ctk.CTkEntry(
            self.scrollable_frame,
            height=35,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["black"],
            border_color=COLORS["ash"],
            border_width=2,
            placeholder_text=""
        )
        emp_id_entry.grid(row=self.current_rows, column=0, padx=5, pady=5, sticky="ew")
        emp_id_entry.insert( 0, emp_id)  # Set the value instead of placeholder
        
        # Name Entry
        name_entry = ctk.CTkEntry(
            self.scrollable_frame,
            height=35,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["black"],
            border_color=COLORS["ash"],
            border_width=2,
            placeholder_text=""
        )
        name_entry.grid(row=self.current_rows, column=1, padx=5, pady=5, sticky="ew")
        name_entry.insert(0, name)  # Set the value instead of placeholder
        
        # Division Dropdown
        division_entry = ctk.CTkComboBox(
            self.scrollable_frame,
            height=35,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["black"],
            border_color=COLORS["ash"],
            button_color=COLORS["pink"],
            button_hover_color=COLORS["darker_pink"],
            dropdown_fg_color=COLORS["black"],
            values=self.divisions,
            state="readonly"
        )
        division_entry.grid(row=self.current_rows, column=2, padx=5, pady=5, sticky="ew")
        division_entry.set(division)  # Set the division if provided
        
        # Store the row's widgets for later access
        self.row_frames.append((emp_id_entry, name_entry, division_entry))
        self.current_rows += 1  # Increment the row count

    def submit_employees(self):
        x = []
        for emp_id_entry, name_entry, division_entry in self.row_frames:
            emp_id = emp_id_entry.get()
            name = name_entry.get()
            division = division_entry.get()
            if emp_id and name:
                c = create_employee(emp_id, name, self.division_dict[division])
                x.append(c)
        
        if False not in x:
            messagebox.showinfo("Employee Create", "Employees created successfully.")
        else:
            messagebox.showerror("Employee Create", "There were some errors!")
        

    def display(self):
        self.clear_main_frame()
        self.create_header()
        self.create_import_section()

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()