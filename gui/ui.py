import customtkinter as ctk
from controllers.crud import *
from utils.search import *
from models.database import SessionLocal
from tkinter import messagebox

# Initialize Database Session
db = SessionLocal()

# Initialize the customtkinter window
app = ctk.CTk()
app.title("InMan")
app.geometry("900x600")
app.configure(bg="#f0f0f0")

# Sidebar Frame
sidebar_frame = ctk.CTkFrame(app, width=200, height=600, corner_radius=0, fg_color="#2c3e50")
sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")

# Sidebar Buttons
def show_employee_management():
    print("Show Employee Management Section")
    # This is where you would call a function to show the Employee Management UI

def show_item_management():
    print("Show Item Management Section")
    # This is where you would call a function to show the Item Management UI

sidebar_buttons = [
    ("Employee Management", show_employee_management),
    ("Item Management", show_item_management),
    ("Search", lambda: search_function()),  # Implement search functionality
]

for text, func in sidebar_buttons:
    button = ctk.CTkButton(sidebar_frame, text=text, width=180, command=func)
    button.grid(pady=10)

# Main Content Area
main_content_frame = ctk.CTkFrame(app, fg_color="#ecf0f1")
main_content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

# Function to create the Employee Management section UI
def show_employee_management_ui():
    # Clear previous widgets
    for widget in main_content_frame.winfo_children():
        widget.destroy()

    employee_label = ctk.CTkLabel(main_content_frame, text="Employee Management", font=("Arial", 18))
    employee_label.grid(row=0, column=0, pady=10)

    # Add Employee Section
    add_employee_button = ctk.CTkButton(main_content_frame, text="Add Employee", command=add_employee)
    add_employee_button.grid(row=1, column=0, pady=5)

    # List Employees Section
    employees = get_all_employees(db)
    employees_label = ctk.CTkLabel(main_content_frame, text="All Employees", font=("Arial", 16))
    employees_label.grid(row=2, column=0, pady=10)

    for i, employee in enumerate(employees):
        emp_button = ctk.CTkButton(main_content_frame, text=employee.name, command=lambda e=employee: show_employee_details(e))
        emp_button.grid(row=3+i, column=0, pady=5)

# Function to add employee
def add_employee():
    emp_id = emp_id_entry.get()
    name = name_entry.get()
    division_id = division_id_entry.get()
    create_employee(db, emp_id, name, division_id)
    messagebox.showinfo("Success", f"Employee {name} added successfully!")

# Function to show employee details
def show_employee_details(employee):
    messagebox.showinfo("Employee Details", f"Employee ID: {employee.emp_id}\nName: {employee.name}\nDivision: {employee.division.name}")

# Function to create the Item Management section UI
def show_item_management_ui():
    # Clear previous widgets
    for widget in main_content_frame.winfo_children():
        widget.destroy()

    item_label = ctk.CTkLabel(main_content_frame, text="Item Management", font=("Arial", 18))
    item_label.grid(row=0, column=0, pady=10)

    # Add Item Section
    add_item_button = ctk.CTkButton(main_content_frame, text="Add Item", command=add_item)
    add_item_button.grid(row=1, column=0, pady=5)

    # List Items Section
    items = get_all_items(db)
    items_label = ctk.CTkLabel(main_content_frame, text="All Items", font=("Arial", 16))
    items_label.grid(row=2, column=0, pady=10)

    for i, item in enumerate(items):
        item_button = ctk.CTkButton(main_content_frame, text=item.name, command=lambda i=item: show_item_details(i))
        item_button.grid(row=3+i, column=0, pady=5)

# Function to add item
def add_item():
    name = item_name_entry.get()
    unique_key = item_unique_key_entry.get()
    is_common = is_common_item_var.get()
    create_item(db, name, unique_key, is_common)
    messagebox.showinfo("Success", f"Item {name} added successfully!")

# Function to show item details
def show_item_details(item):
    messagebox.showinfo("Item Details", f"Item Name: {item.name}\nUnique Key: {item.unique_key}\nCommon: {item.is_common}")

# Main UI Loop
def main_loop():
    app.mainloop()

# Search Entry and Search Function
def search_function():
    # Clear previous widgets
    for widget in main_content_frame.winfo_children():
        widget.destroy()

    search_label = ctk.CTkLabel(main_content_frame, text="Search", font=("Arial", 18))
    search_label.grid(row=0, column=0, pady=10)

    search_entry = ctk.CTkEntry(main_content_frame, width=200)
    search_entry.grid(row=1, column=0, pady=5)

    def perform_search():
        query = search_entry.get()
        employees = search_employees(db, query)
        items = search_items(db, query)
        divisions = search_divisions(db, query)

        # Display search results
        results_label = ctk.CTkLabel(main_content_frame, text="Search Results", font=("Arial", 16))
        results_label.grid(row=3, column=0, pady=10)

        for i, employee in enumerate(employees):
            result_button = ctk.CTkButton(main_content_frame, text=f"Employee: {employee.name}", command=lambda e=employee: show_employee_details(e))
            result_button.grid(row=4+i, column=0, pady=5)

        for i, item in enumerate(items):
            result_button = ctk.CTkButton(main_content_frame, text=f"Item: {item.name}", command=lambda i=item: show_item_details(i))
            result_button.grid(row=4+len(employees)+i, column=0, pady=5)

        for i, division in enumerate(divisions):
            result_button = ctk.CTkButton(main_content_frame, text=f"Division: {division.name}")
            result_button.grid(row=4+len(employees)+len(items)+i, column=0, pady=5)

    search_button = ctk.CTkButton(main_content_frame, text="Search", command=perform_search)
    search_button.grid(row=2, column=0, pady=5)


