# gui/tools/view_employee_records.py

import customtkinter as ctk
import tkinter.messagebox as messagebox
from config import COLORS
from controllers import get_employee_details_with_items

class ViewEmployeeRecords:
    def __init__(self, main_frame, return_to_manager):
        self.main_frame = main_frame
        self.return_to_manager = return_to_manager
        
        # Placeholder for employee data - you'll replace this with actual database query
        self.employees = get_employee_details_with_items()
        self.filtered_employees = self.employees.copy()

    def create_header(self):
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # Back Button
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
        
        # Title
        title = ctk.CTkLabel(
            header_frame,
            text="Employee Records",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["white"]
        )
        title.pack(side="left", padx=20)

        # Search and Filter Section
        search_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        search_frame.pack(side="right")
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search employees...",
            width=200,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["black"],
            border_color=COLORS["ash"]
        )
        self.search_entry.pack(side="left", padx=5)
        
        search_button = ctk.CTkButton(
            search_frame,
            text="Search",
            command=self.perform_search,
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=100,
            height=40
        )
        search_button.pack(side="left", padx=5)

    def create_employees_view(self):
        # Main Container
        self.container = ctk.CTkFrame(
            self.main_frame,
            fg_color=COLORS["secondary_bg"],
            corner_radius=15,
            border_width=2,
            border_color=COLORS["white"]
        )
        self.container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Split into two main sections
        self.employees_list_frame = ctk.CTkFrame(
            self.container, 
            fg_color="transparent", 
            corner_radius=10
        )
        self.employees_list_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        self.items_details_frame = ctk.CTkFrame(
            self.container, 
            fg_color=COLORS["black"], 
            corner_radius=10
        )
        self.items_details_frame.pack(side ="right", fill="both", expand=True, padx=10, pady=10)

        # Employees List
        employees_title = ctk.CTkLabel(
            self.employees_list_frame, 
            text="Employees",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        employees_title.pack(pady=(0,10))

        # Scrollable Employees List
        self.employees_scroll = ctk.CTkScrollableFrame(
            self.employees_list_frame,
            fg_color="transparent",
            scrollbar_button_color=COLORS["pink"],
            scrollbar_button_hover_color=COLORS["darker_pink"]
        )
        self.employees_scroll.pack(fill="both", expand=True)

        # Populate Employees
        for employee in self.filtered_employees:
            self.create_employee_row(employee)

        # Items Details Section
        items_title = ctk.CTkLabel(
            self.items_details_frame, 
            text="Employee Items",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["white"]
        )
        items_title.pack(pady=(0,10))

        # Scrollable Items List
        self.items_scroll = ctk.CTkScrollableFrame(
            self.items_details_frame,
            fg_color="transparent",
            scrollbar_button_color=COLORS["pink"],
            scrollbar_button_hover_color=COLORS["darker_pink"]
        )
        self.items_scroll.pack(fill="both", expand=True)

    def create_employee_row(self, employee):
        employee_frame = ctk.CTkFrame(
            self.employees_scroll, 
            fg_color=COLORS["black"],
            corner_radius=10
        )
        employee_frame.pack(fill="x", pady=5)

        # Employee Info
        info_frame = ctk.CTkFrame(employee_frame, fg_color="transparent")
        info_frame.pack(padx=10, pady=10, fill="x")

        ctk.CTkLabel(
            info_frame, 
            text=f"{employee['emp_id']} - {employee['name']}",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left")

        ctk.CTkLabel(
            info_frame, 
            text=employee['division'],
            font=ctk.CTkFont(size=12)
        ).pack(side="right")

        # Bind click event to show employee items
        employee_frame.bind("<Button-1>", lambda e, emp=employee: self.show_employee_items(emp))
        info_frame.bind("<Button-1>", lambda e, emp=employee: self.show_employee_items(emp))  # Added this line
        employee_frame.bind("<Enter>", lambda e: employee_frame.configure(fg_color=COLORS["pink"]))
        employee_frame.bind("<Leave>", lambda e: employee_frame.configure(fg_color=COLORS["black"]))
        info_frame.bind("<Enter>", lambda e: employee_frame.configure(fg_color=COLORS["pink"]))
        info_frame.bind("<Leave>", lambda e: employee_frame.configure(fg_color=COLORS["black"]))

    def show_employee_items(self, employee):
        # Clear previous items
        for widget in self.items_scroll.winfo_children():
            widget.destroy()

        # Title with employee name
        ctk.CTkLabel(
            self.items_scroll, 
            text=f"Items for {employee['name']} ({employee['emp_id']})",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["white"]
        ).pack(pady=(0,10))

        # Show items
        for item in employee.get('items', []):
            self.create_item_row(item)

    def create_item_row(self, item):
        item_frame = ctk.CTkFrame(
            self.items_scroll, 
            fg_color=COLORS["secondary_bg"],
            corner_radius=10
        )
        item_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(
            item_frame, 
            text=f"{item['item_id']} - {item['name']}",
            font=ctk.CTkFont(size=14)
        ).pack(padx=10, pady=10)

        # View More Details Button
        view_button = ctk.CTkButton(
            item_frame,
            text="View More Details",
            command=lambda i=item: self.show_item_details(i),
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=120
        )
        view_button.pack(pady=15)

    def show_item_details(self, item):
        # Create a popup window for item details
        self.details_window = ctk.CTkToplevel(self.main_frame)
        self.details_window.title(f"Item Details: {item['item_id']}")
        self.details_window.configure(fg_color=COLORS["secondary_bg"])

        # Make the popup modal and prevent interaction with the main window
        self.details_window.grab_set()

        # Ensure the popup is on top of other windows
        self.details_window.lift()
        self.details_window.focus_force()

        # Prevent the popup from being closed by the window manager's close button
        self.details_window.protocol("WM_DELETE_WINDOW", self.details_window.destroy)

        # Create a frame to contain all widgets
        content_frame = ctk.CTkFrame(self.details_window, fg_color="transparent")
        content_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Title
        title_label = ctk.CTkLabel(
            content_frame,
            text=item['name'],
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["white"]
        )
        title_label.pack(pady=(0, 10))

        # Item ID
        item_id_label = ctk.CTkLabel(
            content_frame,
            text=f"Item ID: {item['item_id']}",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["white"]
        )
        item_id_label.pack(pady=(5, 5))

        # Status
        status_label = ctk.CTkLabel(
            content_frame,
            text=f"Status: {'Active' if item.get('is_common', False) else 'Individual'}",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["white"]
        )
        status_label.pack(pady=(5, 5))

        # Unique Key (if available)
        if item.get('unique_key'):
            unique_key_label = ctk.CTkLabel(
                content_frame,
                text=f"Unique Key: {item['unique_key']}",
                font=ctk.CTkFont(size=14),
                text_color=COLORS["white"],
                wraplength=360  # Allow text wrapping
            )
            unique_key_label.pack(pady=(5, 5))

        # Notes (if available)
        if item.get('notes'):
            # Create a scrollable frame for notes if they are long
            notes_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            notes_frame.pack(pady=(5, 5), fill="x")

            notes_label = ctk.CTkLabel(
                notes_frame,
                text="Notes:",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=COLORS["white"]
            )
            notes_label.pack(anchor="w")

            notes_text = ctk.CTkTextbox(
                notes_frame,
                height=100,  # Fixed height, but will be adjusted dynamically
                width=360,
                font=ctk.CTkFont(size=12),
                fg_color=COLORS["secondary_bg"],
                border_color=COLORS["white"],
                border_width=1,
                text_color=COLORS["white"]
            )
            notes_text.pack(fill="x")
            notes_text.insert("0.0", item['notes'])
            notes_text.configure(state="disabled")  # Make read-only

        # Close Button
        close_button = ctk.CTkButton(
            content_frame,
            text="Close",
            command=self.details_window.destroy,
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=100
        )
        close_button.pack(pady=(20, 10))

        # Update the window to calculate the required size
        self.details_window.update()
        
        # Calculate the minimum required size
        window_width = 400  # Base width
        window_height = content_frame.winfo_reqheight() + 40  # Add some padding

        # Set a maximum height to prevent oversized windows
        window_height = min(window_height, 600)

        # Set the window geometry
        self.details_window.geometry(f"{window_width}x{window_height}")

    def perform_search(self):
        search_term = self.search_entry.get().lower()
        self.filtered_employees = [
            emp for emp in self.employees 
            if (search_term in emp["emp_id"].lower() or 
                search_term in emp["name"].lower() or 
                search_term in emp["division"].lower())
        ]
        
        # Refresh the employee view
        self.display()

    def display(self):
        self.clear_main_frame()
        self.create_header()
        self.create_employees_view()

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()