# controllers/crud.py

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

# --- New CRUD functions for Item Attributes ---

def add_item_attribute(db: Session, item_id: int, name: str, value: str):
    """
    Add an attribute to an item.
    """
    attribute = ItemAttribute(item_id=item_id, name=name, value=value)
    db.add(attribute)
    db.commit()
    return attribute

def get_item_attributes(db: Session, item_id: int):
    """
    Retrieve all attributes of an item.
    """
    return db.query(ItemAttribute).filter(ItemAttribute.item_id == item_id).all()

def update_item_attribute(db: Session, item_id: int, name: str, new_value: str):
    """
    Update an attribute of an item.
    """
    attribute = db.query(ItemAttribute).filter(
        ItemAttribute.item_id == item_id,
        ItemAttribute.name == name
    ).first()

    if attribute:
        attribute.value = new_value
        db.commit()
    return attribute

def delete_item_attributes(db: Session, item_id: int):
    """
    Delete all attributes for a given item.
    """
    db.query(ItemAttribute).filter(ItemAttribute.item_id == item_id).delete()
    db.commit()

def delete_item_attribute(db: Session, item_id: int, name: str):
    """
    Delete a specific attribute of an item.
    """
    db.query(ItemAttribute).filter(
        ItemAttribute.item_id == item_id,
        ItemAttribute.name == name
    ).delete()
    db.commit()

# Item CRUD Operations (Updated)
def create_item(db: Session, name: str, is_common: bool, attributes=None):
    """
    Create a new item, optionally with attributes.
    `attributes` is a dictionary with key-value pairs for item properties.
    """
    item = Item(name=name, is_common=is_common)
    db.add(item)
    db.commit()
    db.refresh(item)

    # Add attributes if provided
    if attributes:
        for name, value in attributes.items():
            add_item_attribute(db, item_id=item.item_id, name=name, value=value)

    return item

def get_item(db: Session, item_id: int):
    item = db.query(Item).filter(Item.item_id == item_id).first()
    if item:
        # Retrieve attributes for this item
        item.attributes = get_item_attributes(db, item_id)
    return item

def get_all_items(db: Session):
    return db.query(Item).all()

def delete_item(db: Session, item_id: int):
    # Delete attributes first
    delete_item_attributes(db, item_id)

    # Delete item
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

# Item Assignment (Updated to log attributes)
def assign_item_to_employee(db: Session, emp_id: str, item_id: int, unique_key: str, notes: str = ""):
    """
    Assign an item to an employee and include attributes in the log.
    """
    employee_item = EmployeeItem(
        emp_id=emp_id,
        item_id=item_id,
        unique_key=unique_key,
        date_assigned=datetime.utcnow(),
        notes=notes
    )
    db.add(employee_item)
    db.commit()

    # Update item count and log assignment with item attributes
    employee = get_employee(db, emp_id)
    employee.item_count += 1
    db.commit()

    # Log the action along with item attributes
    item = get_item(db, item_id)
    attribute_details = ", ".join(f"{attr.name}: {attr.value}" for attr in item.attributes)
    log_details = f"Assigned item {item_id} to employee {emp_id} with attributes ({attribute_details})"
    log_action(db, action_type="assign_item", details=log_details)

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

# Update Employee Info
def update_employee(db: Session, emp_id: str, new_name: str = None, new_division_id: int = None):
    employee = db.query(Employee).filter(Employee.emp_id == emp_id).first()
    if employee:
        if new_name:
            employee.name = new_name
        if new_division_id:
            employee.division_id = new_division_id
        db.commit()
        db.refresh(employee)
        log_action(db, action_type="update_employee", details=f"Updated employee {emp_id} details")
        return employee
    return None

# Remove item from an employee’s list (does not delete item from DB)
def remove_item_from_employee(db: Session, emp_id: str, item_id: int):
    assignment = db.query(EmployeeItem).filter(
        EmployeeItem.emp_id == emp_id,
        EmployeeItem.item_id == item_id
    ).first()

    if assignment:
        db.delete(assignment)
        db.commit()

        # Update item count for employee
        employee = get_employee(db, emp_id)
        employee.item_count -= 1
        db.commit()

        log_action(db, action_type="remove_item", details=f"Removed item {item_id} from employee {emp_id}")
        return True
    return False
