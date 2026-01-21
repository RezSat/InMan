# gui/tools/remove_items.py

import customtkinter as ctk
from config import COLORS
import tkinter.messagebox as messagebox
from controllers import get_all_items, delete_item

class RemoveItem:
    def __init__(self, main_frame, return_to_manager):
        self.main_frame = main_frame
        self.return_to_manager = return_to_manager

        self.items_data = get_all_items()
        self.filtered_items = self.items_data.copy()
        self.selected_items = set()

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
            text="Remove Items",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["white"]
        )
        title.pack(side="left", padx=20)

        # Search and Filter Section
        search_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        search_frame.pack(side="right")
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search items...",
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

        bulk_remove_button = ctk.CTkButton(
            search_frame,
            text="Remove Selected",
            command=self.confirm_bulk_remove,
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=150,
            height=40,
            state="disabled"  # Initially disabled
        )
        bulk_remove_button.pack(side="left", padx=5)
        self.bulk_remove_button = bulk_remove_button

    def create_items_view(self):
        # Main Container
        container = ctk.CTkFrame(
            self.main_frame,
            fg_color=COLORS["secondary_bg"],
            corner_radius=15,
            border_width=2,
            border_color=COLORS["white"]
        )
        container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Scrollable Frame
        self.items_scroll = ctk.CTkScrollableFrame(
            container,
            fg_color="transparent",
            scrollbar_button_color=COLORS["pink"],
            scrollbar_button_hover_color=COLORS["darker_pink"]
        )
        self.items_scroll.pack(fill="both", expand=True, padx=5, pady=5)
                
        # Create Headers
        self.headers = ["Select", "Item ID", "Item Name",  "Action"]
        self.item_params = ["item_id", "name"]

        # Configure grid weights to make it more responsive
        for i in range(len(self.headers)):  # Dynamically based on headers
            self.items_scroll.grid_columnconfigure(i, weight=1)

        for col, header in enumerate(self.headers):
            header_frame = ctk.CTkFrame(self.items_scroll, fg_color=COLORS["black"])
            header_frame.grid(row=0, column=col, padx=2, pady=2, sticky="nsew")

            if header == "Select":
                # Select All Checkbox
                self.select_all_checkbox = ctk.CTkCheckBox(
                    header_frame,
                    text="",
                    command=self.toggle_select_all,
                    fg_color=COLORS["pink"],
                    hover_color=COLORS["darker_pink"],
                    checkmark_color=COLORS["white"]
                )
                self.select_all_checkbox.pack(padx=10, pady=8)
            else:
                ctk.CTkLabel(
                    header_frame,
                    text=header,
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=COLORS["white"]
                ).pack(padx=10, pady=8)
        
        # Add Items with proper row indexing
        for idx, item in enumerate(self.filtered_items, 1):
            self.create_item_row(idx, item)

    def create_item_row(self, row_idx, item):
        # Select Checkbox Cell
        select_frame = ctk.CTkFrame(self.items_scroll, fg_color=COLORS["black"])
        select_frame.grid(row=row_idx, column=0, padx=2, pady=2, sticky="nsew")

        checkbox = ctk.CTkCheckBox(
            select_frame,
            text="",
            command=lambda i=item: self.toggle_item_selection(i),
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            checkmark_color=COLORS["white"]
        )
        if item.item_id in self.selected_items:
            checkbox.select()
        checkbox.pack(padx=10, pady=8)

        # Create item cells dynamically based on params
        for col, param in enumerate(self.item_params, 1):  # Start from column 1
            cell_frame = ctk.CTkFrame(self.items_scroll, fg_color=COLORS["black"])
            cell_frame.grid(row=row_idx, column=col, padx=2, pady=2, sticky="nsew")

            # Accessing the item attributes directly
            ctk.CTkLabel(
                cell_frame,
                text=str(getattr(item, param)),  # Use the retrieved value
                font=ctk.CTkFont(size=13),
                wraplength=100  # Adjust wraplength as needed
            ).pack(padx=10, pady=8)

        # Action Cell
        action_frame = ctk.CTkFrame(self.items_scroll, fg_color=COLORS["black"])
        action_frame.grid(row=row_idx, column=len(self.headers) - 1, padx=2, pady=2, sticky="nsew")  # Column index for Action

        remove_button = ctk.CTkButton(
            action_frame,
            text="Remove",
            command=lambda i=item: self.confirm_remove_item(i),
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            width=100
        )
        remove_button.pack(padx=10, pady=8)

    def perform_search(self):
        search_term = self.search_entry.get().lower()
        self.filtered_items = [
            item for item in self.items_data 
            if (search_term in str(item.item_id) or 
                search_term in item.name.lower() 
                )
        ]
        
        # Clear previous items
        for widget in self.items_scroll.winfo_children():
            widget.destroy()
        
        # Recreate headers
        for col, header in enumerate(self.headers):
            header_frame = ctk.CTkFrame(self.items_scroll, fg_color=COLORS["black"])
            header_frame.grid(row=0, column=col, padx=2, pady=2, sticky="nsew")

            if header == "Select":
                # Select All Checkbox
                self.select_all_checkbox = ctk.CTkCheckBox(
                    header_frame,
                    text="",
                    command=self.toggle_select_all,
                    fg_color=COLORS["pink"],
                    hover_color=COLORS["darker_pink"],
                    checkmark_color=COLORS["white"]
                )
                self.select_all_checkbox.pack(padx=10, pady=8)
            else:
                ctk.CTkLabel(
                    header_frame,
                    text=header,
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=COLORS["white"]
                ).pack(padx=10, pady=8)
        
        # Add filtered items
        for idx, item in enumerate(self.filtered_items, 1):
            self.create_item_row(idx, item)

        # Update UI state after recreating the view
        self.update_select_all_checkbox()
        self.update_bulk_remove_button()

    def confirm_remove_item(self, item):
        # Create confirmation popup
        confirm = messagebox.askyesno(
            "Confirm Removal", 
            f"Are you sure you want to remove the item:\n{item.item_id} - {item.name}?"
        )
        
        if confirm:
            self.remove_item(item)

    def remove_item(self, item):
        # Remove item from data source
        q = delete_item(item.item_id)
        self.items_data = get_all_items()
        self.filtered_items = self.items_data.copy()
                
        self.display()
        

    def display(self):
        self.clear_main_frame()
        self.create_header()
        self.create_items_view()
        self.update_select_all_checkbox()
        self.update_bulk_remove_button()

    def toggle_select_all(self):
        if self.select_all_checkbox.get():
            # Select all filtered items
            self.selected_items = {item.item_id for item in self.filtered_items}
        else:
            # Deselect all
            self.selected_items.clear()

        self.display()  # Refresh the view to show checkbox states
        self.update_select_all_checkbox()
        self.update_bulk_remove_button()

    def toggle_item_selection(self, item):
        item_id = item.item_id
        if item_id in self.selected_items:
            self.selected_items.remove(item_id)
        else:
            self.selected_items.add(item_id)

        self.update_bulk_remove_button()
        self.update_select_all_checkbox()

    def update_bulk_remove_button(self):
        if self.selected_items:
            self.bulk_remove_button.configure(state="normal")
        else:
            self.bulk_remove_button.configure(state="disabled")

    def update_select_all_checkbox(self):
        filtered_item_ids = {item.item_id for item in self.filtered_items}
        selected_filtered = self.selected_items.intersection(filtered_item_ids)

        if not filtered_item_ids:
            self.select_all_checkbox.deselect()
        elif selected_filtered == filtered_item_ids:
            self.select_all_checkbox.select()
        else:
            self.select_all_checkbox.deselect()

    def confirm_bulk_remove(self):
        if not self.selected_items:
            return

        selected_count = len(self.selected_items)
        confirm = messagebox.askyesno(
            "Confirm Bulk Removal",
            f"Are you sure you want to remove {selected_count} selected item(s)?\n\nThis action cannot be undone."
        )

        if confirm:
            self.bulk_remove_items()

    def bulk_remove_items(self):
        removed_count = 0
        for item_id in list(self.selected_items):
            try:
                delete_item(item_id)
                removed_count += 1
            except Exception as e:
                messagebox.showerror("Error", f"Failed to remove item {item_id}: {str(e)}")

        # Clear selections
        self.selected_items.clear()

        # Refresh data and display
        self.items_data = get_all_items()
        self.filtered_items = self.items_data.copy()
        self.update_bulk_remove_button()
        self.display()

        # Show success message
        if removed_count > 0:
            messagebox.showinfo("Success", f"Successfully removed {removed_count} item(s).")

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()