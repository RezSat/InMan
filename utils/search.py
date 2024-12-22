# utils/search.py
from controllers.crud import *
from sqlalchemy.orm import joinedload
from sqlalchemy import or_
from models.models import Log, ItemTransferHistory, Employee, Item
from datetime import datetime, timedelta

# Search Employees by name, emp_id, or division
def search_employees(db: Session, query: str, limit: int = 100):
    return db.query(Employee).filter(
        (Employee.name.ilike(f"%{query}%")) |
        (Employee.emp_id.ilike(f"%{query}%")) |
        (Employee.division.has(Division.name.ilike(f"%{query}%")))
    ).all()

# Search Items by name or unique_key
def search_items(db: Session, query: str, limit: int = 100):
    return db.query(Item).join(EmployeeItem).filter(
        (Item.name.ilike(f"%{query}%")) |
        (EmployeeItem.unique_key.ilike(f"%{query}%"))
    ).all()

# Search Divisions by name
def search_divisions(db: Session, query: str, limit: int = 100):
    return db.query(Division).filter(Division.name.ilike(f"%{query}%")).limit(limit).all()

# Get item by its unique key
def get_item_by_key(db: Session, unique_key: str):
    return db.query(Item).join(EmployeeItem).filter(EmployeeItem.unique_key == unique_key).first()

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



def search_logs(search_term: str = None, 
                start_date: datetime = None, 
                end_date: datetime = None, 
                action_type: str = None):
    """
    Search logs with flexible filtering options
    
    Args:
        search_term (str, optional): Search term to match against details
        start_date (datetime, optional): Start date for log filtering
        end_date (datetime, optional): End date for log filtering
        action_type (str, optional): Specific action type to filter
    
    Returns:
        List of matching log entries
    """
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
    """
    Search item transfer history with flexible filtering options
    
    Args:
        search_term (str, optional): Search term to match against employee names, item names, or notes
        start_date (datetime, optional): Start date for transfer filtering
        end_date (datetime, optional): End date for transfer filtering
    
    Returns:
        List of matching transfer history entries
    """
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
    """
    Retrieve recent logs from the past specified number of days
    
    Args:
        days (int, optional): Number of days to retrieve logs for. Defaults to 30.
        limit (int, optional): Maximum number of logs to retrieve. Defaults to 100.
    
    Returns:
        List of recent log entries
    """
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