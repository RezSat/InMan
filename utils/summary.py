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
