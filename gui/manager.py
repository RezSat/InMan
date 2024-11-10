# gui/manager.py
import customtkinter as ctk
from config import COLORS
from gui.tools.add_items import AddItems

class ManagerTools():
    def __init__(self, main_frame, inventory):
        self.main_frame = main_frame
        self.inventory = inventory
        self.tools = [
            ("Add Items", self.add_item_cmd), ("Add Employees", self.placeholder_command), ("Add Divisions", self.placeholder_command),
            ("Remove Items", self.placeholder_command),("Remove employees", self.placeholder_command),("Remove Divisions", self.placeholder_command),
            ("Edit Items", self.placeholder_command),("Edit Employees", self.placeholder_command),("Edit Divisions", self.placeholder_command),
            ("Tranfer items", self.placeholder_command), ("Tranfer Employees", self.placeholder_command),

        ]

    def return_to_manager_function(self):
        self.clear_main_frame()
        self.display()

    def add_item_cmd(self):
        add_items = AddItems(self.main_frame, self.return_to_manager_function)
        add_items.display()
        
    def placeholder_command(self):
        print("Button clicked!")

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
            height=80,
            width=150,
        )
        button.pack(expand=True, fill="both", padx=10, pady=10)

        return card

    def display(self):
        self.clear_main_frame()

        # Create title
        title = ctk.CTkLabel(
            self.main_frame, 
            text="Manager Tools", 
            font=ctk.CTkFont(size=24, weight="bold", family="Verdana"),
        )
        title.pack(pady=(20, 10))  # Reduced bottom padding

        # Create main container
        container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        container.pack(expand=True, fill="both", padx=20)
        
        # Calculate if scrolling is needed
        tools_count = len(self.tools)
        rows_needed = (tools_count) // 3  # 3 cards per row, rounded up
        # Assume each row takes about 100 pixels (card height + padding)
        estimated_height = rows_needed * 100 
        print(estimated_height)
        print(self.main_frame.winfo_height())
        
        if estimated_height > self.main_frame.winfo_height():
            # Create scrollable layout
            canvas = ctk.CTkCanvas(
                container,
                bg=COLORS['black'],
                highlightthickness=0
            )
            scrollbar = ctk.CTkScrollbar(
                container,
                orientation="vertical",
                command=canvas.yview
            )
            scrollable_frame = ctk.CTkFrame(canvas, fg_color="transparent")
            
            # Configure canvas
            canvas.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            canvas.pack(side="left", fill="both", expand=True)
            
            # Create window for scrollable frame
            canvas.create_window((0, 0), window=scrollable_frame, anchor="n")
            
            # Bind scroll events
            def on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
            canvas.bind_all("<MouseWheel>", on_mousewheel)
            
            # Update scroll region
            def configure_scroll_region(event):
                canvas.configure(scrollregion=canvas.bbox("all"))
            
            scrollable_frame.bind("<Configure>", configure_scroll_region)
            
            content_frame = scrollable_frame
        else:
            # Create non-scrollable layout
            content_frame = ctk.CTkFrame(container, fg_color="transparent")
            content_frame.pack(expand=True, fill="both")
            
            # Center the content vertically
            content_frame.pack_propagate(False)
            
        # Create centered container for cards
        cards_container = ctk.CTkFrame(content_frame, fg_color="transparent")
        cards_container.pack(expand=True)
        
        # Create grid of cards
        for i, (tool_name, command) in enumerate(self.tools):
            row = i // 3
            col = i % 3
            card = self.create_card_button(cards_container, tool_name, command)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Configure grid columns to be equal width
        for i in range(3):
            cards_container.grid_columnconfigure(i, weight=1)

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()