# utils/search.py
from controllers.crud import *
from sqlalchemy.orm import joinedload
from sqlalchemy import or_
from models.models import Log, ItemTransferHistory, Employee, Item
from datetime import datetime, timedelta

def convert_items_to_dict(items):
    return [
        {
            'item_id': item.item_id,
            'name': item.name,
        }
        for item in items
    ]

def convert_employees_to_dict(employees):
    return [
        {
            'emp_id': emp.emp_id,
            'name': emp.name,
            'division_id': emp.division_id,
            'division': str(get_division(emp.division_id).name)  # Assuming get_division returns a Division object
        }
        for emp in employees
    ]

def search_employees(query: str, division_name: str = None):
    with session_scope() as db:
        # Base query to search by name or emp_id
        base_query = db.query(Employee).filter(
            (Employee.name.ilike(f"%{query}%")) |
            (Employee.emp_id.ilike(f"%{query}%"))
        )
        
        # If division name is provided, add division filter
        if division_name:
            base_query = base_query.join(Division).filter(
                Division.name.ilike(f"%{division_name}%")
            )
        
        # Execute the query
        employees = base_query.all()
        
        # Transform employees to list of dictionaries
        employee_list = []
        for emp in employees:
            employee_dict = {
                "emp_id": emp.emp_id,
                "name": emp.name,
                "division": emp.division.name if emp.division else None
            }
            employee_list.append(employee_dict)
        
        return employee_list

def search_items(query: str, status: str = None, is_common: bool = None):
    with session_scope() as db:
        # Base query to search by name
        base_query = db.query(Item).filter(
            Item.name.ilike(f"%{query}%")
        )
                
        # Execute the query
        items = base_query.all()
        
        # Transform items to list of dictionaries
        item_list = []
        for item in items:
            item_dict = {
                "item_id": item.item_id,
                "name": item.name,
            }
            item_list.append(item_dict)
        
        return item_list
    
def search_unique_key(query=""):
    l = []
    with session_scope() as db:
        empitems = (
            db.query(EmployeeItem, Item.name.label('item_name'), Employee.name.label('employee_name'))
            .join(Item, EmployeeItem.item_id == Item.item_id)
            .join(Employee, EmployeeItem.emp_id == Employee.emp_id)
            .filter(EmployeeItem.unique_key.ilike(f"%{query}%"))
            .all()
        )
        for i, item_name, employee_name in empitems:
            q = {
                "emp_id": i.emp_id,
                "unique_key": i.unique_key,
                "item_id": i.item_id,
                "item_name": item_name,
                "employee_name": employee_name
            }
            l.append(q)
    
    return l 
  
# Search Divisions by name
def search_divisions(query: str):
    """
    Search for divisions by name with employee and item counts
    
    Args:
        query (str): Search term to find divisions
    
    Returns:
        List of dictionaries containing division details
    """
    with session_scope() as db:
        # Search for divisions matching the query
        divisions = (
            db.query(Division)
            .filter(Division.name.ilike(f"%{query}%"))
            .all()
        )
        
        division_details_list = []
        
        for division in divisions:
            # Count employees in the division
            employee_count = db.query(Employee).filter(Employee.division_id == division.division_id).count()
            
            # Count items owned by employees in the division
            item_count = db.query(Item).join(EmployeeItem).filter(
                EmployeeItem.emp_id == Employee.emp_id, 
                Employee.division_id == division.division_id
            ).count()
            
            # Prepare the details for the division
            division_details = {
                "division_id": division.division_id,
                "name": division.name,
                "employee_count": employee_count,
                "item_count": item_count
            }
            
            division_details_list.append(division_details)
        
        return division_details_list
    
# Get item by its unique key
def get_item_by_key(db: Session, unique_key: str):
    return db.query(Item).join(EmployeeItem).filter(EmployeeItem.unique_key == unique_key).first()

# Search Items by Attribute Key and Value: TODO Modify as per the new EmployeeItemAttributes
def search_items_by_attribute(db: Session, name: str, value: str):
    """
    Search for items with a specific attribute key-value pair.
    """
    return db.query(Item).join(ItemAttribute).filter(
        ItemAttribute.name == name,
        ItemAttribute.value.ilike(f"%{value}%")
    ).all()

# Search Employees by Items with Specific Attributes: TODO same as the above
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



def search_logs(search_term: str = None, 
                start_date: datetime = None, 
                end_date: datetime = None, 
                action_type: str = None):
    db = SessionLocal()
    
    try:
        query = db.query(Log)
        
        # Apply search term filter across multiple fields
        if search_term:
            query = query.filter(
                or_(
                    Log.details.ilike(f"%{search_term}%"),
                    Log.action_type.ilike(f"%{search_term}%")
                )
            )
        
        # Apply date range filter
        if start_date:
            query = query.filter(Log.timestamp >= start_date)
        
        if end_date:
            query = query.filter(Log.timestamp <= end_date)
        
        # Apply action type filter
        if action_type:
            query = query.filter(Log.action_type == action_type)
        
        # Order by most recent first
        query = query.order_by(Log.timestamp.desc())
        
        return query.all()
    
    finally:
        db.close()

def search_item_transfer_history(
    search_term: str = None, 
    start_date: datetime = None, 
    end_date: datetime = None
):
    db = SessionLocal()
    
    try:
        query = db.query(ItemTransferHistory).join(Item).join(
            Employee, ItemTransferHistory.from_emp_id == Employee.emp_id
        ).join(
            Employee, ItemTransferHistory.to_emp_id == Employee.emp_id,
            isouter=True
        )
        
        # Apply search term filter across multiple fields
        if search_term:
            query = query.filter(
                or_(
                    Employee.name.ilike(f"%{search_term}%"),
                    Item.name.ilike(f"%{search_term}%"),
                    ItemTransferHistory.notes.ilike(f"%{search_term}%")
                )
            )
        
        # Apply date range filter
        if start_date:
            query = query.filter(ItemTransferHistory.transfer_date >= start_date)
        
        if end_date:
            query = query.filter(ItemTransferHistory.transfer_date <= end_date)
        
        # Order by most recent first
        query = query.order_by(ItemTransferHistory.transfer_date.desc())
        
        return query.all()
    
    finally:
        db.close()

def get_recent_logs(days: int = 30, limit: int = 100):
    db = SessionLocal()
    
    try:
        # Calculate the date threshold
        threshold_date = datetime.utcnow() - timedelta(days=days)
        
        return (
            db.query(Log)
            .filter(Log.timestamp >= threshold_date)
            .order_by(Log.timestamp.desc())
            .limit(limit)
            .all()
        )
    
    finally:
        db.close()

def get_transfer_history_summary(days: int = 30):
    """
    Get a summary of item transfers in the past specified number of days
    
    Args:
        days (int, optional): Number of days to retrieve transfer history for. Defaults to 30.
    
    Returns:
        Dictionary with transfer summary statistics
    """
    db = SessionLocal()
    
    try:
        # Calculate the date threshold
        threshold_date = datetime.utcnow() - timedelta(days=days)
        
        # Count total transfers
        total_transfers = (
            db.query(ItemTransferHistory)
            .filter(ItemTransferHistory.transfer_date >= threshold_date)
            .count()
        )
        
        # Group transfers by item
        item_transfer_counts = (
            db.query(Item.name, db.func.count(ItemTransferHistory.transfer_id))
            .join(ItemTransferHistory, Item.item_id == ItemTransferHistory.item_id)
            .filter(ItemTransferHistory.transfer_date >= threshold_date)
            .group_by(Item.name)
            .order_by(db.func.count(ItemTransferHistory.transfer_id).desc())
            .limit(10)
            .all()
        )
        
        return {
            "total_transfers": total_transfers,
            "top_transferred_items": item_transfer_counts
        }
    
    finally:
        db.close()