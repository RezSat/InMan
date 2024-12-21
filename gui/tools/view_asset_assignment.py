# gui/tools/view_asset_assignment.py

import customtkinter as ctk
from config import COLORS
from tkinter import ttk
from models.database import SessionLocal
from utils.search import search_logs

class ViewAssetAssignment:
    def __init__(self, main_frame, return_to_manager):
        self.main_frame = main_frame
        self.return_to_manager = return_to_manager

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
            text="View Asset Assignment",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["white"]
        )
        title.pack(side="left", padx=20)

        # Export button
        export_button = ctk.CTkButton(
            header_frame,
            text="Export Logs",
            command=self.export_logs,
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        export_button.pack(side="right", padx=20)

    def create_logs_layout(self):
        # Main container frame
        main_container = ctk.CTkFrame(
            self.main_frame,
            fg_color=COLORS["secondary_bg"],
            corner_radius=15,
            border_width=2,
            border_color=COLORS["white"]
        )
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Search Frame
        search_frame = ctk.CTkFrame(main_container, fg_color=COLORS["black"], corner_radius=10)
        search_frame.pack(fill="x", padx=10, pady=10)

        # Search input
        self.search_input = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search logs by Employee, Item, or Action",
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["secondary_bg"],
            border_color=COLORS["ash"]
        )
        self.search_input.pack(fill="x", padx=10, pady=10)

        # Logs Treeview
        self.logs_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        self.logs_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Create Treeview
        self.logs_tree = ttk.Treeview(
            self.logs_frame, 
            columns=("Timestamp", "Action Type", "Employee", "Item", "Details"), 
            show='headings'
        )
        
        # Configure column headings
        self.logs_tree.heading("Timestamp", text="Timestamp")
        self.logs_tree.heading("Action Type", text="Action Type")
        self.logs_tree.heading("Employee", text="Employee")
        self.logs_tree.heading("Item", text="Item")
        self.logs_tree.heading("Details", text="Details")

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.logs_frame, orient="vertical", command=self.logs_tree.yview)
        self.logs_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.logs_tree.pack(fill="both", expand=True)

        # Bind search event
        self.bind_search_events()

    def bind_search_events(self):
        self.search_input.bind("<Return>", self.search_logs)

    def search_logs(self, event=None):
        # Clear previous results
        for item in self.logs_tree.get_children():
            self.logs_tree.delete(item)

        search_term = self.search_input.get()
        
        # Create a database session
        db = SessionLocal()
        
        try:
            # Use search_logs function to find matching logs
            matching_logs = search_logs(db, search_term)
            
            # Insert logs into treeview
            for log in matching_logs:
                self.logs_tree.insert("", "end", values=(
                    log.timestamp, 
                    log.action_type, 
                    log.employee_name, 
                    log.item_name, 
                    log.details
                ))
        
        except Exception as e:
            print(f"Error searching logs: {e}")
        
        finally:
            # Always close the database session
            db.close()

    def export_logs(self):
        # Placeholder for export functionality
        print("Exporting logs...")

    def display(self):
        self.clear_main_frame()
        self.create_header()
        self.create_logs_layout()

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()