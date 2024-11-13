import customtkinter as ctk
from config import COLORS
import tkinter as tk

class TransferItemBetweenEmployees:
    def __init__(self, main_frame, return_to_manager):
        self.main_frame = main_frame
        self.return_to_manager = return_to_manager
        self.selected_source_user = None
        self.selected_destination_user = None

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
        # Create a new top-level window for item selection
        item_window = ctk.CTkToplevel()
        item_window.title(f"Select Items for {user}")
        item_window.geometry("600x500")

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
            text=f"Select Items for {user}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["white"]
        )
        title.pack(pady=(0, 20))

        # Example items (you'll replace this with actual items)
        items = ["Laptop", "Monitor", "Keyboard", "Mouse", "Headphones"]
        selected_items = []

        for item in items:
            var = tk.BooleanVar()
            checkbox = ctk.CTkCheckBox(
                items_frame, 
                text=item, 
                variable=var,
                font=ctk.CTkFont(size=14),
                checkbox_color=COLORS["pink"],
                hover_color=COLORS["darker_pink"]
            )
            checkbox.pack(anchor="w", padx=20, pady=5)
            selected_items.append((item, var))

        # Button frame
        button_frame = ctk.CTkFrame(item_window, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=20)

        def on_ok():
            # Process selected items
            items_to_transfer = [item for item, var in selected_items if var.get()]
            print(f"Selected items for {user}: {items_to_transfer}")
            item_window.destroy()

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
            fg_color=COLORS["ash"],
            hover_color=COLORS["darker_pink"],
            width=100,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        cancel_button.pack(side="right", padx=10)

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
        # This function would typically query the database for users matching the search criteria
        # For demonstration, we'll use a static list of users
        users = [
            {"emp_id": "EMP001", "name": "Alice Smith", "division": "HR"},
            {"emp_id": "EMP002", "name": "Bob Johnson", "division": "IT"},
            {"emp_id": "EMP003", "name": "Charlie Brown", "division": "Finance"},
        ]
        
        results_frame = self.source_results_frame if is_source else self.destination_results_frame
        for widget in results_frame.winfo_children():
            widget.destroy()  # Clear previous results

        for user in users:
            if emp_id_or_name.lower() in user["emp_id"].lower() or emp_id_or_name.lower() in user["name"].lower():
                self.create_user_result_row(user, is_source)

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
            command=lambda: self.select_user(user, is_source),
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=80,
            height=30,
            font=ctk.CTkFont(size=12)
        )
        select_button.pack(side="right", padx=5)

    def select_user(self, user, is_source):
        if is_source:
            self.selected_source_user = user["name"]
            print(f"Selected Source User: {self.selected_source_user}")
        else:
            self.selected_destination_user = user["name"]
            print(f"Selected Destination User: {self.selected_destination_user}")

    def bind_search_events(self):
        self.source_search_input.bind("<Return>", lambda event: self.search_user(self.source_search_input.get(), is_source=True))
        self.destination_search_input.bind("<Return>", lambda event: self.search_user(self.destination_search_input.get(), is_source=False))
