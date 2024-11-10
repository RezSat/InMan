# utils/search.py
from controllers.crud import *

# Search Employees by name, emp_id, or division
def search_employees(db: Session, query: str):
    return db.query(Employee).filter(
        (Employee.name.ilike(f"%{query}%")) |
        (Employee.emp_id.ilike(f"%{query}%")) |
        (Employee.division.has(Division.name.ilike(f"%{query}%")))
    ).all()

# Search Items by name or unique_key
def search_items(db: Session, query: str):
    return db.query(Item).filter(
        (Item.name.ilike(f"%{query}%")) |
        (Item.unique_key.ilike(f"%{query}%"))
    ).all()

# Search Divisions by name
def search_divisions(db: Session, query: str):
    return db.query(Division).filter(Division.name.ilike(f"%{query}%")).all()

# Get item by its unique key
def get_item_by_key(db: Session, unique_key: str):
    return db.query(Item).filter(Item.unique_key == unique_key).first()

# Search Items by Attribute Key and Value
def search_items_by_attribute(db: Session, name: str, value: str):
    """
    Search for items with a specific attribute key-value pair.
    """
    return db.query(Item).join(ItemAttribute).filter(
        ItemAttribute.name == name,
        ItemAttribute.value.ilike(f"%{value}%")
    ).all()

# Search Employees by Items with Specific Attributes
def search_employees_by_item_attribute(db: Session, name: str, value: str):
    """
    Search for employees who have been assigned items with a specific attribute.
    """
    return db.query(Employee).join(EmployeeItem).join(Item).join(ItemAttribute).filter(
        ItemAttribute.name == name,
        ItemAttribute.value.ilike(f"%{value}%")
    ).all()

# Search Employees by Item Name
def search_employees_by_item_name(db: Session, item_name: str):
    """
    Search for employees who have a specific item by name.
    """
    return db.query(Employee).join(EmployeeItem).join(Item).filter(
        Item.name.ilike(f"%{item_name}%")
    ).all()
