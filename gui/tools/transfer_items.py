# gui/tools/transfer_items.py

from tkinter import messagebox
import customtkinter as ctk
from config import COLORS
import tkinter as tk
from controllers.crud import transfer_item
from utils import search_employees, get_employee_items
from models.database import  SessionLocal

class TransferItemBetweenEmployees:
    def __init__(self, main_frame, return_to_manager):
        self.main_frame = main_frame
        self.return_to_manager = return_to_manager
        self.selected_source_user = None
        self.selected_destination_user = None
        self.source_selected_button = None
        self.destination_selected_button = None

    def create_header(self):
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))

        # Back button
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

        # Title label
        title = ctk.CTkLabel(
            header_frame,
            text="Transfer Items Between Employees",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["white"]
        )
        title.pack(side="left", padx=20)

        # Transfer button
        transfer_button = ctk.CTkButton(
            header_frame,
            text="Transfer Items",
            command=self.transfer_items,
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        transfer_button.pack(side="right", padx=20)

    def create_transfer_layout(self):
        # Main container frame
        main_container = ctk.CTkFrame(
            self.main_frame,
            fg_color=COLORS["secondary_bg"],
            corner_radius=15,
            border_width=2,
            border_color=COLORS["white"]
        )
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Split into two columns
        main_container.grid_columnconfigure((0, 1), weight=1)
        main_container.grid_rowconfigure(1, weight=1)

        # Source Side
        source_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        source_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        source_label = ctk.CTkLabel(
            source_frame, 
            text="Source Employee", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["white"]
        )
        source_label.pack(side="left", padx=(0, 10))

        # Source Search Frame
        source_search_frame = ctk.CTkFrame(main_container, fg_color=COLORS["black"], corner_radius=10)
        source_search_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Search input for source
        self.source_search_input = ctk.CTkEntry(
            source_search_frame,
            placeholder_text="Search by Emp ID or Name",
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["secondary_bg"],
            border_color=COLORS["ash"]
        )
        self.source_search_input.pack(fill="x", padx=10, pady=10)
        

        # Source search results frame
        self.source_results_frame = ctk.CTkScrollableFrame(
            source_search_frame,
            fg_color="transparent",
            scrollbar_button_color=COLORS["pink"],
            scrollbar_button_hover_color=COLORS["darker_pink"]
        )
        self.source_results_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Destination Side (Similar to Source Side)
        destination_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        destination_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        destination_label = ctk.CTkLabel(
            destination_frame, 
            text="Destination Employee", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["white"]
        )
        destination_label.pack(side="left", padx=(0, 10))

        # Destination Search Frame
        destination_search_frame = ctk.CTkFrame(main_container, fg_color=COLORS["black"], corner_radius=10)
        destination_search_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        # Search input for destination
        self.destination_search_input = ctk.CTkEntry(
            destination_search_frame,
            placeholder_text="Search by Emp ID or Name",
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["secondary_bg"],
            border_color=COLORS["ash"]
        )
        self.destination_search_input.pack(fill="x", padx=10, pady=10)

        # Destination search results frame
        self.destination_results_frame = ctk.CTkScrollableFrame(
            destination_search_frame,
            fg_color="transparent",
            scrollbar_button_color=COLORS["pink"],
            scrollbar_button_hover_color=COLORS["darker_pink"]
        )
        self.destination_results_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.bind_search_events()

    def open_item_selection_window(self, user):
        # Ensure the window is modal and prevents interaction with the main window
        item_window = ctk.CTkToplevel(self.main_frame)
        item_window.title(f"Select Items for {user['name']}")
        item_window.geometry("600x500")
        item_window.transient(self.main_frame)  # Set as a child of main window
        item_window.grab_set()  # Make the window modal

        # Prevent the window from being closed immediately
        item_window.protocol("WM_DELETE_WINDOW", lambda: None)

        # Frame for items
        items_frame = ctk.CTkScrollableFrame(
            item_window,
            fg_color=COLORS["secondary_bg"],
            scrollbar_button_color=COLORS["pink"],
            scrollbar_button_hover_color=COLORS["darker_pink"]
        )
        items_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title = ctk.CTkLabel(
            items_frame,
            text=f"Select Items for {user['name']}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["white"]
        )
        title.pack(pady=(0, 20))

        try:
            items = self.get_user_items(user['emp_id'])
        except Exception as e:
            items = []
            error_label = ctk.CTkLabel(
                items_frame,
                text=f"Error fetching items: {str(e)}",
                text_color="red"
            )
            error_label.pack(pady=20)

        selected_items = []

        for item in items:
            var = tk.BooleanVar()
            checkbox = ctk.CTkCheckBox(
                items_frame, 
                text=f"{item['name']} (ID: {item['unique_key']})", 
                variable=var,
                font=ctk.CTkFont(size=14),
                # Replace checkbox_color with other supported color parameters
                fg_color=COLORS["pink"],  # This sets the checked state color
                hover_color=COLORS["darker_pink"]  # This sets the hover color
            )
            checkbox.pack(anchor="w", padx=20, pady=5)
            selected_items.append((item, var))

        # Button frame
        button_frame = ctk.CTkFrame(item_window, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=20)

        def on_ok():
            # Check if both source and destination employees are selected
            if not self.selected_source_user or not self.selected_destination_user:
                messagebox.showerror("Error", "Please select both source and destination employees.")
                return

            # Process selected items
            self.selected_items_to_transfer = []
            for item, var in selected_items:
                if var.get():
                    # Store the item details for transfer
                    self.selected_items_to_transfer.append(item)
            
            item_window.destroy()

            # Check if any items are selected
            if not self.selected_items_to_transfer:
                messagebox.showwarning("No Items Selected", "Please select at least one item to transfer.")
                return

            # Perform transfers
            successful_transfers = 0
            failed_transfers = 0
            failed_items = []

            for item in self.selected_items_to_transfer:
                try:
                    # Use the transfer_item function from CRUD
                    transfer_item(
                        from_emp_id=self.selected_source_user['emp_id'], 
                        to_emp_id=self.selected_destination_user['emp_id'], 
                        item_id=item['id'],
                        unique_key=item['unique_key'],
                        notes=f"Transferred between employees"
                    )
                    successful_transfers += 1

                except Exception as e:
                    messagebox.showerror("Transfer Error", 
                        f"Failed to transfer item '{item['name']}': {str(e)}")
                    failed_transfers += 1
                    failed_items.append(item['name'])

            # Provide transfer summary
            if successful_transfers > 0 and failed_transfers == 0:
                messagebox.showinfo("Success", 
                    f"Successfully transferred {successful_transfers} item(s).")
            elif successful_transfers > 0 and failed_transfers > 0:
                messagebox.showwarning("Partial Success", 
                    f"Transferred {successful_transfers} item(s).\n"
                    f"Failed to transfer {failed_transfers} item(s): {', '.join(failed_items)}")
            elif failed_transfers > 0:
                messagebox.showerror("Transfer Failed", 
                    f"Failed to transfer {failed_transfers} item(s): {', '.join(failed_items)}")

            # Clear selection and refresh view
            self.clear_selection()

        ok_button = ctk.CTkButton(
            button_frame,
            text="OK",
            command=on_ok,
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=100,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        ok_button.pack(side="right", padx=10)

        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=item_window.destroy,
            fg_color=COLORS["black"],
            hover_color=COLORS["darker_pink"],
            width=100,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        cancel_button.pack(side="right", padx=10)

    def get_user_items(self, user_emp_id):
        # Create a database session
        db = SessionLocal()
        
        try:
            # Fetch employee items using the utility function
            employee_items = get_employee_items(db, user_emp_id)
            
            # Convert employee items to a list of item names with additional details
            
            items = [
                {
                    'name': emp_item.item.name,
                    'id': emp_item.item.item_id,
                    'unique_key': emp_item.unique_key

                } 
                for emp_item in employee_items
            ]
            
            return items
        
        except Exception as e:
            print(f"Error retrieving employee items: {e}")
            return []
        
        finally:
            # Always close the database session
            db.close()
            
    def transfer_items(self):
        if self.selected_source_user and self.selected_destination_user:
            self.open_item_selection_window(self.selected_source_user)
        else:
            print("Please select both source and destination employees.")

    def display(self):
        self.clear_main_frame()
        self.create_header()
        self.create_transfer_layout()

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def search_user(self, emp_id_or_name, is_source=True):
        # Clear previous results
        results_frame = self.source_results_frame if is_source else self.destination_results_frame
        for widget in results_frame.winfo_children():
            widget.destroy()

        # Create a database session
        db = SessionLocal()
        
        try:
            # Use search_employees function to find matching employees
            matching_employees = search_employees(db, emp_id_or_name)
            
            # Convert SQLAlchemy objects to dictionary for compatibility
            employees = [
                {
                    "emp_id": emp.emp_id, 
                    "name": emp.name, 
                    "division": emp.division.name if emp.division else "Unassigned"
                } 
                for emp in matching_employees
            ]

            # Display matching employees
            for employee in employees:
                self.create_user_result_row(employee, is_source)
        
        except Exception as e:
            print(f"Error searching employees: {e}")
        
        finally:
            # Always close the database session
            db.close()

    def create_user_result_row(self, user, is_source):
        results_frame = self.source_results_frame if is_source else self.destination_results_frame
        
        row_frame = ctk.CTkFrame(results_frame, fg_color=COLORS["black"])
        row_frame.pack(fill="x", padx=5, pady=5)

        emp_id_label = ctk.CTkLabel(row_frame, text=user["emp_id"], font=ctk.CTkFont(size=14), text_color=COLORS["white"])
        emp_id_label.pack(side="left", padx=5)

        name_label = ctk.CTkLabel(row_frame, text=user["name"], font=ctk.CTkFont(size=14), text_color=COLORS["white"])
        name_label.pack(side="left", padx=5)

        division_label = ctk.CTkLabel(row_frame, text=user["division"], font=ctk.CTkFont(size=14), text_color=COLORS["white"])
        division_label.pack(side="left", padx=5)

        select_button = ctk.CTkButton(
            row_frame,
            text="Select",
            command=lambda: self.select_user(user, is_source, select_button),
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=80,
            height=30,
            font=ctk.CTkFont(size=12)
        )
        select_button.pack(side="right", padx=5)

    def select_user(self, user, is_source, button):
        # Reset previous selection
        if is_source:
            if self.source_selected_button:
                self.source_selected_button.configure(
                    fg_color=COLORS["pink"], 
                    text="Select",
                    state="normal"
                )
            self.selected_source_user = user
            self.source_selected_button = button
        else:
            if self.destination_selected_button:
                self.destination_selected_button.configure(
                    fg_color=COLORS["pink"], 
                    text="Select",
                    state="normal"
                )
            self.selected_destination_user = user
            self.destination_selected_button = button

        # Update selected button
        button.configure(
            fg_color=COLORS["secondary_bg"], 
            text="Selected",
            state="disabled"
        )

        print(f"Selected {'Source' if is_source else 'Destination'} User: {user['name']}")

    def bind_search_events(self):
        self.source_search_input.bind("<Return>", lambda event: self.search_user(self.source_search_input.get(), is_source=True))
        self.destination_search_input.bind("<Return>", lambda event: self.search_user(self.destination_search_input.get(), is_source=False))
