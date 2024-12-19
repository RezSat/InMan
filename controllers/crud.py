# controllers/crud.py

from venv import logger
from sqlalchemy.orm import Session, joinedload
from models.models import *
from models.database import session_scope, SessionLocal
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

# Division CRUD Operations
def create_division(name: str):
    try:
        with session_scope() as db:
            division = Division(name=name)
            db.add(division)
            db.commit()
            db.refresh(division)
            db.close()
            return division
    except IntegrityError:
        return False

def get_division(division_id: int):
    db = SessionLocal()
    return db.query(Division).filter(Division.division_id == division_id).first()

def get_all_divisions():
    with session_scope() as db:
        divisions = db.query(Division).all()
        return [
            {
                'division_id': div.division_id,
                'name': div.name,
            } for div in divisions
        ]

def get_division_details_with_counts(division_id: int):
    with session_scope() as db:
        # Get the division
        division = db.query(Division).filter(Division.division_id == division_id).first()
        
        if division:
            # Count employees in the division
            employee_count = db.query(Employee).filter(Employee.division_id == division_id).count()
            
            # Count items owned by employees in the division
            item_count = db.query(Item).join(EmployeeItem).filter(EmployeeItem.emp_id == Employee.emp_id, Employee.division_id == division_id).count()
            
            # Prepare items data
            items_data = db.query(Item.name, func.count(EmployeeItem.id).label('count')) \
                .join(EmployeeItem) \
                .join(Employee) \
                .filter(Employee.division_id == division_id) \
                .group_by(Item.name) \
                .all()
            
            # Format items data
            items_list = [{"name": item.name, "count": item.count} for item in items_data]
            
            # Prepare the details to return
            division_details = {
                "division_id": division.division_id,
                "name": division.name,
                "employee_count": employee_count,
                "item_count": item_count,
                "items": items_list
            }
            
            return division_details
        else:
            return None

def get_all_divisions_with_counts():
    with session_scope() as db:
        # Get all divisions
        divisions = db.query(Division).all()
        
        division_details_list = []
        
        for division in divisions:
            # Count employees in the division
            employee_count = db.query(Employee).filter(Employee.division_id == division.division_id).count()
            
            # Count items owned by employees in the division
            item_count = db.query(Item).join(EmployeeItem).filter(EmployeeItem.emp_id == Employee.emp_id, Employee.division_id == division.division_id).count()
            
            # Prepare items data
            items_data = db.query(Item.name, Item.item_id, func.count(EmployeeItem.id).label('count')) \
                .join(EmployeeItem) \
                .join(Employee) \
                .filter(Employee.division_id == division.division_id) \
                .group_by(Item.name, Item.item_id) \
                .all()
            
            # Format items data
            items_list = [{"name": item.name, "count": item.count} for item in items_data]
            
            # Prepare the details for the division
            division_details = {
                "division_id": division.division_id,
                "name": division.name,
                "employee_count": employee_count,
                "item_count": item_count,
                "items": items_list
            }
            
            division_details_list.append(division_details)
        
        return division_details_list

def delete_division(division_id: int):
    with session_scope() as db:
        division = get_division(division_id)
        if division:
            db.delete(division)
            db.commit()
        return division

# Employee CRUD Operations
def create_employee(emp_id: str, name: str, division_id: int):
    try:
        with session_scope() as db:
            employee = Employee(emp_id=emp_id, name=name, division_id=division_id)
            db.add(employee)
            db.commit()
            db.refresh(employee)
            return employee
    except IntegrityError:
        return False

def get_employee(emp_id: str):
    with session_scope() as db:
        return db.query(Employee).filter(Employee.emp_id == emp_id).first()

def get_all_employees():
    with session_scope() as db:
        employees = db.query(Employee).all()
        return [
            {
                'emp_id': emp.emp_id,
                'name': emp.name,
                'division_id': emp.division_id,
                'division': str(get_division(emp.division_id).name)
            } for emp in employees
        ]

def get_employee_details_with_items():
    """
    Retrieve all employee details along with their associated items
    
    Returns:
        List of dictionaries containing employee and item information
    """
    try:
        with session_scope() as db:
            # Query employees with their items and division in a single query
            employees = (
                db.query(Employee)
                .options(joinedload(Employee.division))  # Load division data
                .all()
            )
            
            # Transform query results into desired format
            employee_details = []
            for emp in employees:
                # Get items through EmployeeItem relationship
                items_query = (
                    db.query(Item)
                    .join(EmployeeItem)
                    .filter(EmployeeItem.emp_id == emp.emp_id)
                    .all()
                )
                
                # Format items data
                items_data = []
                for item in items_query:
                    # Get the EmployeeItem record for additional details
                    emp_item = (
                        db.query(EmployeeItem)
                        .filter(
                            EmployeeItem.emp_id == emp.emp_id,
                            EmployeeItem.item_id == item.item_id
                        )
                        .first()
                    )
                    
                    item_data = {
                        "item_id": item.item_id,
                        "name": item.name,
                        "unique_key": emp_item.unique_key if emp_item else None,
                        "date_assigned": emp_item.date_assigned.strftime('%Y-%m-%d') if emp_item and emp_item.date_assigned else None,
                        "is_common": item.is_common
                    }
                    items_data.append(item_data)
                
                # Prepare employee data
                emp_data = {
                    "emp_id": emp.emp_id,
                    "name": emp.name,
                    "division": emp.division.name if emp.division else "Unassigned",
                    "items": items_data
                }
                employee_details.append(emp_data)
            
            return employee_details
    
    except Exception as e:
        logger.error(f"Error retrieving employee details: {str(e)}")
        raise

def delete_employee(emp_id: str):
    with session_scope() as db:
        employee = get_employee(emp_id)
        if employee:
            db.delete(employee)
            db.commit()
        return employee

def add_item_attribute(item_id: int, name: str, value: str):
    with session_scope() as db:
        attribute = ItemAttribute(item_id=item_id, name=name, value=value)
        db.add(attribute)
        db.commit()
        return attribute

def get_item_attributes(item_id: int):
    with session_scope() as db:
        return db.query(ItemAttribute).filter(ItemAttribute.item_id == item_id).all()


def update_item_attribute(item_id: int, name: str, new_value: str):
    with session_scope() as db:
        attribute = db.query(ItemAttribute).filter(
            ItemAttribute.item_id == item_id,
            ItemAttribute.name == name
        ).first()

        if attribute:
            attribute.value = new_value
            db.commit()
        return attribute
        
def delete_item_attributes(item_id: int):
    with session_scope() as db:
        db.query(ItemAttribute).filter(ItemAttribute.item_id == item_id).delete()
        db.commit()

def delete_item_attribute(item_id: int, name: str):
    with session_scope() as db:
        db.query(ItemAttribute).filter(
            ItemAttribute.item_id == item_id,
            ItemAttribute.name == name
        ).delete()
        db.commit()


# Item CRUD Operations (Updated)
def create_item(name: str, is_common: bool, attributes=None):
    with session_scope() as db:
        item = Item(name=name, is_common=is_common)
        db.add(item)
        db.commit()
        db.refresh(item)

        # Add attributes if provided
        if attributes:
            for name, value in attributes.items():
                attribute = ItemAttribute(item_id=item.item_id, name=name, value=value)
                db.add(attribute)
        
        db.commit()
        return item
    
def update_item_details(item_dict):
    try:
        with session_scope() as db:
            # Extract details from the dictionary
            item_id = item_dict.get('item_id')
            name = item_dict.get('name')
            status = item_dict.get('status')
            is_common = item_dict.get('is_common')
            attributes = item_dict.get('attributes', [])
            
            # Retrieve the existing item
            item = db.query(Item).filter(Item.item_id == item_id).first()
            
            if not item:
                logger.warning(f"Item with ID {item_id} not found")
                return None
            
            # Update basic item details
            if name is not None:
                item.name = name
            
            if is_common is not None:
                item.is_common = bool(is_common)
            
            if status is not None:
                # Validate status
                valid_statuses = ["active", "retired", "lost"]
                if status.lower() not in valid_statuses:
                    raise ValueError(f"Invalid status. Must be one of {valid_statuses}")
                item.status = status.lower()
            
            # Remove existing attributes
            db.query(ItemAttribute).filter(ItemAttribute.item_id == item_id).delete()
            
            # Add attributes if provided
            if attributes:
                for name, value in attributes.items():
                    attribute = ItemAttribute(item_id=item.item_id, name=name, value=value)
                    db.add(attribute)
            
            # Commit changes
            db.commit()
            
            # Refresh and return the updated item
            db.refresh(item)
            
            # Log the action
            log_action(
                action_type="update_item", 
                details=f"Updated item {item_id} details"
            )
            
            return item
    
    except Exception as e:
        logger.error(f"Error updating item {item_id}: {str(e)}")
        return None
        
def get_item(item_id: int):
    with session_scope() as db:
        item = db.query(Item).filter(Item.item_id == item_id).first()
        if item:
            item.attributes = get_item_attributes(item_id)
        return item

def get_all_items():
    db = SessionLocal()
    # Use joinedload to eagerly load the attribute along with the items
    items =  db.query(Item).options(joinedload(Item.attributes)).all()
    db.close()
    return items

def get_all_items_names_dict():
    with session_scope() as db:
        items = db.query(Item).all()
        return {item.name: item.item_id for item in items}

def get_all_items_with_no_attrs():
    """
    Retrieve a list of all item names from the database
    
    Returns:
        List of item names
    """
    try:
        with session_scope() as db:
            # Query to select only item names
            items = db.query(Item.name).all()
            
            # Extract names from the query result
            item_names = [item.name for item in items]
            
            return item_names
    
    except Exception as e:
        # Log the error
        logger.error(f"Error retrieving item names: {str(e)}")
        return []

# Alternative implementations:

def get_all_items_names_set():
    """
    Retrieve unique item names as a set
    
    Returns:
        Set of unique item names
    """
    try:
        with session_scope() as db:
            return set(db.query(Item.name).distinct().all())
    except Exception as e:
        logger.error(f"Error retrieving unique item names: {str(e)}")
        return set()


def delete_item(item_id: int):
    with session_scope() as db:
        item = db.query(Item).options(joinedload(Item.attributes)).filter(Item.item_id == item_id).first()
        if item:
            # Delete all associated attributes
            for attribute in item.attributes:
                db.delete(attribute)
            db.delete(item)
            db.commit()
            return True
    return False

# Log Action
def log_action(action_type: str, details: str, user_id: int = None):
    with session_scope() as db:
        log_entry = Log(action_type=action_type, details=details, user_id=user_id, timestamp=datetime.utcnow())
        db.add(log_entry)
        db.commit()
        return log_entry

# Item Assignment (Updated to log attributes)
def assign_item_to_employee(emp_id: str, item_id: int, unique_key: str, notes: str = ""):
    with session_scope() as db:
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
        employee = get_employee(emp_id)
        employee.item_count += 1
        db.commit()

        # Log the action along with item attributes
        item = get_item(item_id)
        attribute_details = ", ".join(f"{attr.name}: {attr.value}" for attr in item.attributes)
        log_details = f"Assigned item {item_id} to employee {emp_id} with attributes ({attribute_details})"
        log_action(action_type="assign_item", details=log_details)

        return employee_item

# Item Transfer
def transfer_item(from_emp_id: str, to_emp_id: str, item_id: int, notes: str = ""):
    with session_scope() as db:
        # Remove from current employee
        current_assignment = db.query(EmployeeItem).filter(
            EmployeeItem.emp_id == from_emp_id,
            EmployeeItem.item_id == item_id
        ).first()
        
        if current_assignment:
            db.delete(current_assignment)
            db.commit()

            # Update item count for from_emp
            from_employee = get_employee(from_emp_id)
            from_employee.item_count -= 1
            db.commit()
        
        # Assign to new employee
        new_assignment = assign_item_to_employee(to_emp_id, item_id, unique_key="", notes=notes)

        # Log transfer
        log_action(action_type="transfer_item", details=f"Transferred item {item_id} from {from_emp_id} to {to_emp_id}")

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
def update_employee(emp_id: str, new_name: str = None, new_division_id: int = None):
    with session_scope() as db:
        employee = db.query(Employee).filter(Employee.emp_id == emp_id).first()
        if employee:
            if new_name:
                employee.name = new_name
            if new_division_id:
                employee.division_id = new_division_id
            db.commit()
            db.refresh(employee)
            log_action(action_type="update_employee", details=f"Updated employee {emp_id} details")
            return employee
    return None

# Remove item from an employee's list (does not delete item from DB)
def remove_item_from_employee(emp_id: str, item_id: int):
    with session_scope() as db:
        assignment = db.query(EmployeeItem).filter(
            EmployeeItem.emp_id == emp_id,
            EmployeeItem.item_id == item_id
        ).first()

        if assignment:
            db.delete(assignment)
            db.commit()

            # Update item count for employee
            employee = get_employee(emp_id)
            employee.item_count -= 1
            db.commit()

            log_action(action_type="remove_item", details=f"Removed item {item_id} from employee {emp_id}")

            return True

    return False
