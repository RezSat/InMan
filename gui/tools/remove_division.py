# gui/tools/remove_division.py

import customtkinter as ctk
import tkinter.messagebox as messagebox
from config import COLORS
from controllers.crud import delete_division, get_all_divisions

class RemoveDivision:
    def __init__(self, main_frame, return_to_manager):
        self.main_frame = main_frame
        self.return_to_manager = return_to_manager

        self.divisions = get_all_divisions()
        self.filtered_divisions = self.divisions.copy()
        self.selected_divisions = set()

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
            text="Remove Divisions",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["white"]
        )
        title.pack(side="left", padx=20)

        # Search and Filter Section
        search_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        search_frame.pack(side="right")
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search divisions...",
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

    def create_divisions_view(self):
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
        self.divisions_scroll = ctk.CTkScrollableFrame(
            container,
            fg_color="transparent",
            scrollbar_button_color=COLORS["pink"],
            scrollbar_button_hover_color=COLORS["darker_pink"]
        )
        self.divisions_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # Create Headers
        headers = ["Select", "Division ID", "Name", "Action"]
        for col, header in enumerate(headers):
            header_frame = ctk.CTkFrame(self.divisions_scroll, fg_color=COLORS["black"])
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

        for i in range(len(headers)):
            self.divisions_scroll.grid_columnconfigure(i, weight=1)
        
        # Add Divisions
        for idx, division in enumerate(self.filtered_divisions, 1):
            self.create_division_row(idx, division)

    def create_division_row(self, row_idx, division):
        # Select Checkbox Cell
        select_frame = ctk.CTkFrame(self.divisions_scroll, fg_color=COLORS["black"])
        select_frame.grid(row=row_idx, column=0, padx=2, pady=2, sticky="nsew")

        checkbox = ctk.CTkCheckBox(
            select_frame,
            text="",
            command=lambda div=division: self.toggle_division_selection(div),
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"],
            checkmark_color=COLORS["white"]
        )
        if division["division_id"] in self.selected_divisions:
            checkbox.select()
        checkbox.pack(padx=10, pady=5)

        # Division ID Cell
        for col, (key, width) in enumerate([
            ("division_id", 100),
            ("name", 200)
        ], 1):  # Start from column 1
            cell_frame = ctk.CTkFrame(self.divisions_scroll, fg_color=COLORS["black"])
            cell_frame.grid(row=row_idx, column=col, padx=2, pady=2, sticky="nsew")

            ctk.CTkLabel(
                cell_frame,
                text=division[key],
                font=ctk.CTkFont(size=12),
                text_color=COLORS["white"]
            ).pack(padx=10, pady=5)

        # Action Button
        action_frame = ctk.CTkFrame(self.divisions_scroll, fg_color=COLORS["black"])
        action_frame.grid(row=row_idx, column=3, padx=2, pady=2, sticky="nsew")  # Changed to column 3

        remove_button = ctk.CTkButton(
            action_frame,
            text="Remove",
            command=lambda div=division: self.confirm_remove_division(division),
            fg_color=COLORS["pink"],
            hover_color=COLORS["darker_pink"]
        )
        remove_button.pack(padx=10, pady=5)

    def perform_search(self):
        search_term = self.search_entry.get().lower()
        self.filtered_divisions = [div for div in self.divisions if search_term in div["name"].lower()]
        self.display()

    def confirm_remove_division(self, division):
        confirm = messagebox.askyesno(
            "Confirm Removal", 
            f"Are you sure you want to remove the Division:\n{division['division_id']} - {division['name']}?"
        )

        if confirm:
            self.remove_division(division)

    def remove_division(self, division):
        # Call the delete function from the controller
        action = delete_division(division['division_id'])
        self.divisions = get_all_divisions()
        self.filtered_divisions = self.divisions.copy()
        self.display()

    def display(self):
        self.clear_main_frame()
        self.create_header()
        self.create_divisions_view()
        self.update_select_all_checkbox()
        self.update_bulk_remove_button()

    def toggle_select_all(self):
        if self.select_all_checkbox.get():
            # Select all filtered divisions
            self.selected_divisions = {div["division_id"] for div in self.filtered_divisions}
        else:
            # Deselect all
            self.selected_divisions.clear()

        self.display()  # Refresh the view to show checkbox states
        self.update_select_all_checkbox()
        self.update_bulk_remove_button()

    def toggle_division_selection(self, division):
        div_id = division["division_id"]
        if div_id in self.selected_divisions:
            self.selected_divisions.remove(div_id)
        else:
            self.selected_divisions.add(div_id)

        self.update_bulk_remove_button()
        self.update_select_all_checkbox()

    def update_bulk_remove_button(self):
        if self.selected_divisions:
            self.bulk_remove_button.configure(state="normal")
        else:
            self.bulk_remove_button.configure(state="disabled")

    def update_select_all_checkbox(self):
        filtered_div_ids = {div["division_id"] for div in self.filtered_divisions}
        selected_filtered = self.selected_divisions.intersection(filtered_div_ids)

        if not filtered_div_ids:
            self.select_all_checkbox.deselect()
        elif selected_filtered == filtered_div_ids:
            self.select_all_checkbox.select()
        else:
            self.select_all_checkbox.deselect()

    def confirm_bulk_remove(self):
        if not self.selected_divisions:
            return

        selected_count = len(self.selected_divisions)
        confirm = messagebox.askyesno(
            "Confirm Bulk Removal",
            f"Are you sure you want to remove {selected_count} selected division(s)?\n\nThis action cannot be undone."
        )

        if confirm:
            self.bulk_remove_divisions()

    def bulk_remove_divisions(self):
        removed_count = 0
        for div_id in list(self.selected_divisions):
            try:
                delete_division(div_id)
                removed_count += 1
            except Exception as e:
                messagebox.showerror("Error", f"Failed to remove division {div_id}: {str(e)}")

        # Clear selections
        self.selected_divisions.clear()

        # Refresh data and display
        self.divisions = get_all_divisions()
        self.filtered_divisions = self.divisions.copy()
        self.update_bulk_remove_button()
        self.display()

        # Show success message
        if removed_count > 0:
            messagebox.showinfo("Success", f"Successfully removed {removed_count} division(s).")

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()