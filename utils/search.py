# utils/search.py
from controllers.crud import *

# Search Employees by name, emp_id, or division
def search_employees(db: Session, query: str):
    return db.query(Employee).filter(
        (Employee.name.ilike(f"%{query}%")) |
        (Employee.emp_id.ilike(f"%{query}%")) |
        (Employee.division.has(name.ilike(f"%{query}%")))
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
