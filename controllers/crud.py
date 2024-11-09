# controllers/crud.py

# crud.py

from sqlalchemy.orm import Session
from models.models import *
from datetime import datetime

# Division CRUD Operations
def create_division(db: Session, name: str):
    division = Division(name=name)
    db.add(division)
    db.commit()
    db.refresh(division)
    return division

def get_division(db: Session, division_id: int):
    return db.query(Division).filter(Division.division_id == division_id).first()

def get_all_divisions(db: Session):
    return db.query(Division).all()

def delete_division(db: Session, division_id: int):
    division = get_division(db, division_id)
    if division:
        db.delete(division)
        db.commit()
    return division

# Employee CRUD Operations
def create_employee(db: Session, emp_id: str, name: str, division_id: int):
    employee = Employee(emp_id=emp_id, name=name, division_id=division_id)
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee

def get_employee(db: Session, emp_id: str):
    return db.query(Employee).filter(Employee.emp_id == emp_id).first()

def get_all_employees(db: Session):
    return db.query(Employee).all()

def delete_employee(db: Session, emp_id: str):
    employee = get_employee(db, emp_id)
    if employee:
        db.delete(employee)
        db.commit()
    return employee

# Item CRUD Operations
def create_item(db: Session, name: str, unique_key: str, is_common: bool):
    item = Item(name=name, unique_key=unique_key, is_common=is_common)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

def get_item(db: Session, item_id: int):
    return db.query(Item).filter(Item.item_id == item_id).first()

def get_all_items(db: Session):
    return db.query(Item).all()

def delete_item(db: Session, item_id: int):
    item = get_item(db, item_id)
    if item:
        db.delete(item)
        db.commit()
    return item


# Log Action
def log_action(db: Session, action_type: str, details: str, user_id: int = None):
    log_entry = Log(action_type=action_type, details=details, user_id=user_id, timestamp=datetime.utcnow())
    db.add(log_entry)
    db.commit()
    return log_entry

# Item Assignment
def assign_item_to_employee(db: Session, emp_id: str, item_id: int, is_unique: bool = False, notes: str = ""):
    employee_item = EmployeeItem(
        emp_id=emp_id,
        item_id=item_id,
        is_unique=is_unique,
        date_assigned=datetime.utcnow(),
        notes=notes
    )
    db.add(employee_item)
    db.commit()

    # Update item count and log assignment
    employee = get_employee(db, emp_id)
    employee.item_count += 1
    db.commit()
    log_action(db, action_type="assign_item", details=f"Assigned item {item_id} to employee {emp_id}")

    return employee_item

# Item Transfer
def transfer_item(db: Session, from_emp_id: str, to_emp_id: str, item_id: int, notes: str = ""):
    # Remove from current employee
    current_assignment = db.query(EmployeeItem).filter(
        EmployeeItem.emp_id == from_emp_id,
        EmployeeItem.item_id == item_id
    ).first()
    
    if current_assignment:
        db.delete(current_assignment)
        db.commit()

        # Update item count for from_emp
        from_employee = get_employee(db, from_emp_id)
        from_employee.item_count -= 1
        db.commit()
    
    # Assign to new employee
    new_assignment = assign_item_to_employee(db, emp_id=to_emp_id, item_id=item_id, notes=notes)

    # Log transfer
    log_action(db, action_type="transfer_item", details=f"Transferred item {item_id} from {from_emp_id} to {to_emp_id}")

    # Update ItemTransferHistory
    transfer_record = ItemTransferHistory(
        item_id=item_id,
        from_emp_id=from_emp_id,
        to_emp_id=to_emp_id,
        transfer_date=datetime.utcnow(),
        notes=notes
    )
    db.add(transfer_record)
    db.commit()

    return new_assignment
