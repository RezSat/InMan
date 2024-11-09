# controllers/crud.py

# crud.py

from sqlalchemy.orm import Session
from models.models import Employee, Division, Item, EmployeeItem, Log
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
