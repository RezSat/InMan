# test.py

from models.database import SessionLocal, initialize_database
from controllers.crud import *
from controllers.auth import *
from utils.search import *
from utils.summary import *
from gui.ui import *

def test1():
    # Initialize Database
    initialize_database()

    # Start a session
    db = SessionLocal()

    # Create Division
    division = create_division(db, name="IT Department")
    print(f"Created Division: {division.name}")

    # Create Employee
    employee = create_employee(db, emp_id="E001", name="Alice", division_id=division.division_id)
    print(f"Created Employee: {employee.name}")

    # Create Item
    item = create_item(db, name="Laptop", unique_key="SN12345", is_common=False)
    print(f"Created Item: {item.name}")

    # Log an Action
    log_entry = log_action(db, action_type="create", details="Created an item", user_id=None)
    print(f"Log Entry: {log_entry.details}")

    # Create User
    user = create_user(db, username="manager", password="password123")
    print(f"User Created: {user.username}")

    # Authenticate User
    auth_user = authenticate_user(db, username="manager", password="password123")
    if auth_user:
        print("Authentication successful")
    else:
        print("Authentication failed")

    # Fetch all employees
    employees = get_all_employees(db)
    for emp in employees:
        print(f"Employee: {emp.name}")

    db.close()

def test2():
    db = SessionLocal()

    # Create test division and employees
    division = create_division(db, name="Finance")
    emp1 = create_employee(db, emp_id="E002", name="Bob", division_id=division.division_id)
    emp2 = create_employee(db, emp_id="E003", name="Charlie", division_id=division.division_id)
    
    # Create test items
    item1 = create_item(db, name="Desktop", unique_key="DT56789", is_common=False)
    item2 = create_item(db, name="Office Chair", unique_key="OC12345", is_common=True)

    # Assign item to employee
    assignment = assign_item_to_employee(db, emp_id=emp1.emp_id, item_id=item1.item_id, is_unique=True)
    print(f"Assigned Item: {assignment.item_id} to Employee: {emp1.emp_id}")

    # Transfer item from emp1 to emp2
    transfer = transfer_item(db, from_emp_id=emp1.emp_id, to_emp_id=emp2.emp_id, item_id=item1.item_id)
    print(f"Transferred Item: {item1.item_id} from Employee: {emp1.emp_id} to Employee: {emp2.emp_id}")

    # Search Employees, Items, Divisions
    print("Search Results for 'Bob':", search_employees(db, "Bob"))
    print("Search Results for 'Desktop':", search_items(db, "Desktop"))
    print("Search Results for 'Finance':", search_divisions(db, "Finance"))

    db.close()

def test3():
    db = SessionLocal()

    # Create test division and employees
    division = create_division(db, name="HR Department")
    emp1 = create_employee(db, emp_id="E004", name="Dave", division_id=division.division_id)
    emp2 = create_employee(db, emp_id="E005", name="Eve", division_id=division.division_id)
    
    # Create test items
    item1 = create_item(db, name="Projector", unique_key="PRJ12345", is_common=True)
    item2 = create_item(db, name="Phone", unique_key="PHN67890", is_common=False)

    # Assign item to employee
    assign_item_to_employee(db, emp_id=emp1.emp_id, item_id=item1.item_id, is_unique=True)

    # Get all items assigned to employee
    items = get_employee_items(db, emp_id=emp1.emp_id)
    print(f"Employee {emp1.emp_id} Items:", [item.name for item in items])

    # Get items by division
    division_items = get_items_by_division(db, division_name="HR Department")
    print(f"Items in HR Department:", [item.name for item in division_items])

    # Update Employee Info
    updated_employee = update_employee(db, emp_id="E004", new_name="David")
    print(f"Updated Employee: {updated_employee.name}")

    # Remove item from employee
    remove_item_from_employee(db, emp_id="E004", item_id=item1.item_id)

    # Get Transfer History
    transfer_history = get_item_transfer_history(db)
    print("Transfer History:", transfer_history)

    # Get Item by Key
    item = get_item_by_key(db, unique_key="PHN67890")
    print(f"Item by Key: {item.name if item else 'Not Found'}")

    # Generate Employee Report
    employee_report = generate_employee_report(db, emp_id="E004")
    print("Employee Report:\n", employee_report)

    # Generate System-wide Item Report
    item_report = generate_item_report(db)
    print("System-wide Item Report:\n", item_report)

    db.close()

if __name__ == "__main__":
    app = InventoryApp()
    app.run()

    #test1()
    #test2()
    #test3()
    #main_loop()
