from controllers.crud import *

# Get all items assigned to an employee
def get_employee_items(db: Session, emp_id: str):
    return db.query(Item).join(EmployeeItem).filter(EmployeeItem.emp_id == emp_id).all()

# Get all items assigned to employees in a specific division
def get_items_by_division(db: Session, division_name: str):
    division = db.query(Division).filter(Division.name == division_name).first()
    if division:
        return db.query(Item).join(EmployeeItem).join(Employee).filter(Employee.division_id == division.division_id).all()
    return []

# Get all item transfers history
def get_item_transfer_history(db: Session):
    return db.query(ItemTransferHistory).all()

# Generate a report of all items assigned to an employee
def generate_employee_report(db: Session, emp_id: str):
    employee = get_employee(db, emp_id)
    if not employee:
        return "Employee not found."
    
    items = get_employee_items(db, emp_id)
    report = f"Report for Employee: {employee.name} ({emp_id})\n\n"
    
    if not items:
        report += "No items assigned.\n"
    else:
        for item in items:
            report += f"Item Name: {item.name}, Unique Key: {item.unique_key}\n"
    
    return report

# Generate a report of all items in the system
def generate_item_report(db: Session):
    items = get_all_items(db)
    report = "System-wide Item Report\n\n"
    
    if not items:
        report += "No items in the system.\n"
    else:
        for item in items:
            report += f"Item Name: {item.name}, Unique Key: {item.unique_key}, Is Common: {'Yes' if item.is_common else 'No'}\n"
    
    return report
