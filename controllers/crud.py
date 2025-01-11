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
    x =  db.query(Division).filter(Division.division_id == division_id).first()
    db.close()
    return x

def get_division_id_from_name(name: str = None):
    """
    Retrieve division ID based on division name
    
    Args:
        name (str, optional): Name of the division. 
                               If None, returns a dictionary of all division names and IDs
    
    Returns:
        int or dict: Division ID if name is provided, 
                     or dictionary of {division_name: division_id} if no name is given
    """
    try:
        with session_scope() as db:
            # If no name is provided, return all divisions as a dictionary
            if name is None:
                divisions = db.query(Division).all()
                return {div.name: div.division_id for div in divisions}
            
            # If name is provided, find the specific division
            division = db.query(Division).filter(Division.name == name).first()
            
            # Return division ID if found, None otherwise
            y = division.division_id if division else None
            db.close()
            return y
    
    except Exception as e:
        logger.error(f"Error retrieving division ID for name {name}: {str(e)}")
        return None
        
def get_all_divisions():
    with session_scope() as db:
        divisions = db.query(Division).all()
        db.close()
        return [
            {
                'division_id': div.division_id,
                'name': div.name,
            } for div in divisions
        ]

def get_all_division_names():
    with session_scope() as db:
        division_names = db.query(Division.name).all()
        db.close()
        return [name[0] for name in division_names]

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

            db.close()
            
            return division_details
        else:
            db.close()
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

        db.close()
        
        return division_details_list

def update_dvision(division_id, name):
    with session_scope() as db:
        division = db.query(Division).filter(Division.division_id == division_id).first()
        if division:
            division.name = name
            db.commit()
            db.close()
            return True
        return False
    
def delete_division(division_id: int):
    with session_scope() as db:
        division = get_division(division_id)
        if division:
            db.delete(division)
            db.commit()
        db.close()
        return division

# Employee CRUD Operations
def create_employee(emp_id: str, name: str, division_id: int):
    try:
        with session_scope() as db:
            employee = Employee(emp_id=emp_id, name=name, division_id=division_id)
            db.add(employee)
            db.commit()
            db.refresh(employee)
            db.close()
            return employee
    except IntegrityError:
        return False

def get_employee(emp_id: str):
    with session_scope() as db:
        y = db.query(Employee).filter(Employee.emp_id == emp_id).first()
        db.close()
        return y

def get_all_employees():
    with session_scope() as db:
        employees = db.query(Employee).all()
        x = [
            {
                'emp_id': emp.emp_id,
                'name': emp.name,
                'division_id': emp.division_id,
                'division': str(get_division(emp.division_id).name)
            } for emp in employees
        ]
        db.close()
        return x

def get_all_employees_ids():
    with session_scope() as db:
        employees = db.query(Employee).all()
        x = [ i.emp_id for i in employees]
        return x
    
def get_employee_details_with_items_one(emp_id: str):
    """
    Retrieve employee details along with their associated items by employee ID.
    
    Args:
        emp_id (str): The ID of the employee to retrieve.
    
    Returns:
        Dictionary containing employee and item information, or None if not found.
    """
    try:
        with session_scope() as db:
            # Query the specific employee with their items and division in a single query
            employee = (
                db.query(Employee)
                .options(joinedload(Employee.division))  # Load division data
                .filter(Employee.emp_id == emp_id)
                .first()
            )
            
            if not employee:
                return None
            
            # Get items through EmployeeItem relationship
            items_query = (
                db.query(Item)
                .join(EmployeeItem)
                .filter(EmployeeItem.emp_id == emp_id)
                .all()
            )
            
            # Format items data
            items_data = []
            for item in items_query:
                # Get all EmployeeItem records for the current item
                emp_items = (
                    db.query(EmployeeItem)
                    .filter(
                        EmployeeItem.emp_id == emp_id,
                        EmployeeItem.item_id == item.item_id
                    )
                    .all()
                )
                
                # Prepare item data for each EmployeeItem record
                for emp_item in emp_items:
                    item_data = {
                        "item_id": item.item_id,
                        "name": item.name,
                        "unique_key": emp_item.unique_key,
                        "date_assigned": emp_item.date_assigned.strftime('%Y-%m-%d') if emp_item.date_assigned else None,
                        "is_common": item.is_common
                    }
                    items_data.append(item_data)
            
            # Prepare employee data
            emp_data = {
                "emp_id": employee.emp_id,
                "name": employee.name,
                "division": employee.division.name if employee.division else "Unassigned",
                "items": items_data
            }

            return emp_data

    except Exception as e:
        logger.error(f"Error retrieving employee details for ID {emp_id}: {str(e)}")
        return None

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
                    # Get all EmployeeItem records for the current item
                    emp_items = (
                        db.query(EmployeeItem)
                        .filter(
                            EmployeeItem.emp_id == emp.emp_id,
                            EmployeeItem.item_id == item.item_id
                        )
                        .all()
                    )
                    
                    # Prepare item data for each EmployeeItem record
                    for emp_item in emp_items:
                        item_data = {
                            "item_id": item.item_id,
                            "name": item.name,
                            "unique_key": emp_item.unique_key,
                            "date_assigned": emp_item.date_assigned.strftime('%Y-%m-%d') if emp_item.date_assigned else None,
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

  
            db.close()
            
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
        db.close()
        return employee

def add_item_attribute(item_id: int, name: str, value: str):
    with session_scope() as db:
        attribute = EmployeeItemAttribute(emp_item_id=item_id, name=name, value=value)
        db.add(attribute)
        db.commit()
        db.close()
        return attribute

def get_item_attributes(item_id: int):
    with session_scope() as db:
        x = db.query(EmployeeItemAttribute).filter(EmployeeItemAttribute.emp_item_id == item_id).all()
        db.close()
        return x

def update_item_attribute(item_id: int, name: str, new_value: str):
    with session_scope() as db:
        attribute = db.query(EmployeeItemAttribute).filter(
            EmployeeItemAttribute.emp_item_id == item_id,
            EmployeeItemAttribute.name == name
        ).first()

        if attribute:
            attribute.value = new_value
            db.commit()
        db.close()
        return attribute
        
def delete_item_attributes(item_id: int):
    with session_scope() as db:
        db.query(EmployeeItemAttribute).filter(EmployeeItemAttribute.emp_item_id == item_id).delete()
        db.commit()
        db.close()

def delete_item_attribute(item_id: int, name: str):
    with session_scope() as db:
        db.query(EmployeeItemAttribute).filter(
            EmployeeItemAttribute.emp_item_id == item_id,
            EmployeeItemAttribute.name == name
        ).delete()
        db.commit()
        db.close()


# Item CRUD Operations (Updated)
def create_item(name: str):
    with session_scope() as db:
        item = Item(name=name)
        
        db.add(item)
        db.commit()
        db.refresh(item)

        # Add attributes if provided
        #if attributes:
        #    for name, value in attributes.items():
        #        attribute = ItemAttribute(item_id=item.item_id, name=name, value=value)
        #        db.add(attribute)
        
        db.commit()
        x = item.item_id
        db.close()
        return x
    
def update_item_details(item_dict):
    try:
        with session_scope() as db:
            # Extract details from the dictionary
            item_id = item_dict.get('item_id')
            name = item_dict.get('name')
            
            # Retrieve the existing item
            item = db.query(Item).filter(Item.item_id == item_id).first()
            
            if not item:
                logger.warning(f"Item with ID {item_id} not found")
                return None
            
            # Update basic item details
            if name is not None:
                item.name = name
            
            db.commit()
            
            # Refresh and return the updated item
            db.refresh(item)
            
            # Log the action
            log_action(
                action_type="update_item", 
                details=f"Updated item {item_id} details"
            )
            db.close()
            return item
    
    except Exception as e:
        logger.error(f"Error updating item {item_id}: {str(e)}")
        return None
        
def get_item(item_id: int):
    with session_scope() as db:
        # Fetch the item with its attributes in a single query
        item = (
            db.query(Item)
            .options(joinedload(Item.attributes))  # Eagerly load attributes
            .filter(Item.item_id == item_id)
            .first()
        )
                
        return item

def get_all_items():
    db = SessionLocal()
    # Use joinedload to eagerly load the attribute along with the items
    items =  db.query(Item).all()
    db.close()
    return items

def get_all_items_names_dict():
    with session_scope() as db:
        items = db.query(Item).all()
        db.close()
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
            db.close()
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
            x = set(db.query(Item.name).distinct().all())
            db.close()
            return x
    except Exception as e:
        logger.error(f"Error retrieving unique item names: {str(e)}")
        return set()


def delete_item(item_id: int):
    with session_scope() as db:
        item = db.query(Item).options(joinedload(Item.attributes)).filter(Item.item_id == item_id).first()
        if item:
            db.delete(item)
            db.commit()
            db.close()
            return True
    return False

# Log Action
def log_action(action_type: str, details: str, user_id: int = None):
    with session_scope() as db:
        log_entry = Log(action_type=action_type, details=details, user_id=user_id, timestamp=datetime.utcnow())
        db.add(log_entry)
        db.commit()
        db.close()
        return log_entry

def assign_item_to_employee(emp_id: str, item_id: int, unique_key: str, notes: str = ""):
    with session_scope() as db:
        # First, check if the item exists
        item = db.query(Item).filter(Item.item_id == item_id).first()
        
        if not item:
            raise ValueError(f"Item with ID {item_id} not found")
        
        # Create the employee item assignment
        employee_item = EmployeeItem(
            emp_id=emp_id,
            item_id=item_id,
            unique_key=unique_key,
            date_assigned=datetime.utcnow(),
            notes=notes
        )
        db.add(employee_item)
        db.commit()

        # Update item count and log assignment
        employee = get_employee(emp_id)
        employee.item_count += 1
        db.commit()

        # Log the action
        attribute_details = "TODO: ADDING ATTRIBUTE DETAILS HERE"
        
        log_details = f"Assigned item {item_id} to employee {emp_id} with attributes ({attribute_details})"
        log_action(action_type="assign_item", details=log_details)
        
        db.close()
        return employee_item

# Item Transfer
def transfer_item(from_emp_id: str, to_emp_id: str, item_id: int, unique_key: str, notes: str = ""):
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
        new_assignment = assign_item_to_employee(to_emp_id, item_id, unique_key=unique_key, notes=notes)
        
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
        db.close()

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
            db.close()
            return employee
    return None

def update_employee_id(old_emp_id: str, new_emp_id: str):
    try:
        with session_scope() as db:
            # Find the existing employee
            employee = db.query(Employee).filter(Employee.emp_id == old_emp_id).first()
            
            if not employee:
                logger.warning(f"Employee with ID {old_emp_id} not found")
                return None
            
            # Update the employee ID
            employee.emp_id = new_emp_id
            
            # Commit the changes
            db.commit()
            db.refresh(employee)
            
            # Log the action
            log_action(
                action_type="update_employee_id", 
                details=f"Changed employee ID from {old_emp_id} to {new_emp_id}"
            )
            db.close()
            
            return employee
    
    except IntegrityError:
        # Handle potential unique constraint violation
        logger.error(f"Could not update employee ID. The new ID {new_emp_id} might already exist.")
        return None
    
    except Exception as e:
        logger.error(f"Error updating employee ID: {str(e)}")
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
            db.close()
            return True

    return False
