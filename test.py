# test.py

from models.database import SessionLocal, initialize_database, session_scope
from controllers.crud import *
from controllers.auth import *
from utils.search import *
from utils.summary import *
from gui.ui import *
from models.models import *

def test1():
    # Initialize Database
    #initialize_database()

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
    #initialize_database()
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
    #initialize_database()
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


def test4():
    initialize_database()
    # updated test case after the new database model.
    db = SessionLocal()

    # Create a test division
    division = create_division(db, name="Engineering")
    print(f"Created Division: {division.name}")

    # Create test employees
    emp1 = create_employee(db, emp_id="E006", name="Frank", division_id=division.division_id)
    emp2 = create_employee(db, emp_id="E007", name="Grace", division_id=division.division_id)
    print(f"Created Employee: {emp1.name}, ID: {emp1.emp_id}")
    print(f"Created Employee: {emp2.name}, ID: {emp2.emp_id}")

    # Create test items with attributes
    item1 = create_item(db, name="Laptop", unique_key="LT12345", is_common=False)
    item2 = create_item(db, name="Router", unique_key="RT54321", is_common=True)
    print(f"Created Item: {item1.name}, Unique Key: {item1.unique_key}")
    print(f"Created Item: {item2.name}, Unique Key: {item2.unique_key}")

    # Add attributes to items
    add_item_attribute(db, item_id=item1.item_id, name="brand", value="Dell")
    add_item_attribute(db, item_id=item1.item_id, name="model", value="Latitude 5400")
    add_item_attribute(db, item_id=item2.item_id, name="brand", value="Cisco")
    add_item_attribute(db, item_id=item2.item_id, name="model", value="RV340")

    # Assign items to employees
    assign_item_to_employee(db, emp_id=emp1.emp_id, item_id=item1.item_id, is_unique=True)
    assign_item_to_employee(db, emp_id=emp2.emp_id, item_id=item2.item_id, is_unique=False)
    print(f"Assigned Item {item1.name} to Employee {emp1.name}")
    print(f"Assigned Item {item2.name} to Employee {emp2.name}")

    # Test searching items by attribute
    laptops = search_items_by_attribute(db, name="brand", value="Dell")
    print(f"Items with brand 'Dell':", [item.name for item in laptops])

    # Test searching employees by item attribute
    employees_with_dell = search_employees_by_item_attribute(db, name="brand", value="Dell")
    print(f"Employees with Dell items:", [emp.name for emp in employees_with_dell])

    # Test searching employees by item name
    employees_with_laptops = search_employees_by_item_name(db, item_name="Laptop")
    print(f"Employees with Laptops:", [emp.name for emp in employees_with_laptops])

    # Generate detailed employee report
    detailed_report = generate_detailed_employee_report(db, emp_id=emp1.emp_id)
    print("Detailed Employee Report:\n", detailed_report)

    # Generate attribute-filtered item report
    attribute_report = generate_attribute_filtered_item_report(db, name="brand", value="Cisco")
    print("Attribute-Filtered Item Report:\n", attribute_report)

    db.close()


def login_user_creation_test():
    db = SessionLocal()
    create_user(db, username="manager", password="password123")
    db.close()

def get_all_items_():
    db = SessionLocal()
        # Use joinedload to eagerly load the attribute along with the items
    items = db.query(Item).options(joinedload(Item.attributes)).all()
    db.close()
    return items


items = get_all_items_()

def convert_items_to_dicts(items):
    items_data = []
    for item in items:
        item_dict = {
            "item_id": item.item_id,
            "name": item.name,
            "status": item.status,
            "is_common": item.is_common,
            "attributes": []
        }
        
        # Add attributes
        for attr in item.attributes:
            item_dict["attributes"].append({
                "name": attr.name,
                "value": attr.value
            })
        
        items_data.append(item_dict)
    
    return items_data


# Call the functions together within the same session context
def testsomething():
    with session_scope() as db:
        divisions = get_all_divisions()  # This will still be in the session context
        for div in divisions:
            print(div.name)  # Accessing attributes while in the session context



print(get_employee_details_with_items())

"""import pandas as pd

# Create a DataFrame with the test data
data = {
    'EMP_ID': [101, 102, 103, 104, 105, 106],
    'Name': ['Alice Smith', 'Bob Johnson', 'Charlie Lee', 'David Brown', 'Eva White', 'Frank Black'],
    'Division': ['IT', 'HR', '', 'Sales', '', 'Finance']  # Missing division for Eva White
}

df = pd.DataFrame(data)

# Save the DataFrame to an Excel file
file_name = 'employee_import_test.xlsx'
df.to_excel(file_name, index=False)

print(f"Excel file '{file_name}' created successfully.")
"""
#if __name__ == "__main__":
    #app = InventoryApp()
    #app.run()
    # get_all_items()

    #test1()
    #test2()
    #test3()
    #test4()
    #main_loop()
