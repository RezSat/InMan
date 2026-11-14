# controllers/crud.py

from venv import logger
from sqlalchemy.orm import Session, joinedload, selectinload
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

def _division_stats(db, divisions):
    """Build dashboard totals with a fixed number of queries.

    Counts refer to employee-owned assignments, not unassigned inventory.
    The response shape is shared by the dashboard and division details view.
    """
    if not divisions:
        return []

    ids = [division.division_id for division in divisions]
    employees_by_division = dict(
        db.query(Employee.division_id, func.count(Employee.emp_id))
        .filter(Employee.division_id.in_(ids))
        .group_by(Employee.division_id)
        .all()
    )
    rows = (
        db.query(
            Employee.division_id,
            Item.name,
            Item.item_id,
            func.count(EmployeeItem.id),
        )
        .join(EmployeeItem, EmployeeItem.emp_id == Employee.emp_id)
        .join(Item, Item.item_id == EmployeeItem.item_id)
        .filter(Employee.division_id.in_(ids))
        .group_by(Employee.division_id, Item.name, Item.item_id)
        .order_by(Item.name, Item.item_id)
        .all()
    )

    items_by_division = {division_id: [] for division_id in ids}
    item_counts = {division_id: 0 for division_id in ids}
    for division_id, item_name, _, count in rows:
        items_by_division[division_id].append({"name": item_name, "count": count})
        item_counts[division_id] += count

    return [
        {
            "division_id": division.division_id,
            "name": division.name,
            "employee_count": employees_by_division.get(division.division_id, 0),
            "item_count": item_counts[division.division_id],
            "items": items_by_division[division.division_id],
        }
        for division in divisions
    ]


def get_division_details_with_counts(division_id: int):
    with session_scope() as db:
        division = db.query(Division).filter(Division.division_id == division_id).first()
        if division is None:
            return None
        return _division_stats(db, [division])[0]


def get_all_divisions_with_counts():
    with session_scope() as db:
        return _division_stats(db, db.query(Division).all())


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
    """Load employee and division labels in one database round trip."""
    with session_scope() as db:
        employees = db.query(Employee).options(joinedload(Employee.division)).all()
        return [
            {
                "emp_id": emp.emp_id,
                "name": emp.name,
                "division_id": emp.division_id,
                "division": str(emp.division.name),
            }
            for emp in employees
        ]

def get_all_employees_ids():
    with session_scope() as db:
        employees = db.query(Employee).all()
        x = [ i.emp_id for i in employees]
        return x
    
def _employee_items_load_options():
    """Load the inventory needed by the employee screens in bounded queries."""
    return (
        joinedload(Employee.division),
        selectinload(Employee.items).joinedload(EmployeeItem.item),
        selectinload(Employee.items).selectinload(EmployeeItem.attributes),
    )


def _employee_with_items_to_dict(employee):
    """Preserve the original item grouping and response fields.

    An employee may have multiple assignments for the same item type.
    Group by item type before returning rows, matching the previous report
    ordering rather than interleaving individual assignments.
    """
    assignments_by_item = {}
    for assignment in sorted(employee.items, key=lambda row: row.id):
        item = assignment.item
        if item is None:
            continue

        record = {
            "item_id": item.item_id,
            "name": item.name,
            "unique_key": assignment.unique_key,
            "date_assigned": (
                assignment.date_assigned.strftime("%Y-%m-%d")
                if assignment.date_assigned else None
            ),
            "attributes": [
                {"name": attribute.name, "value": attribute.value}
                for attribute in sorted(assignment.attributes, key=lambda row: row.emp_attribute_id)
            ],
        }
        assignments_by_item.setdefault(item.item_id, []).append(record)

    return {
        "emp_id": employee.emp_id,
        "name": employee.name,
        "division": employee.division.name if employee.division else "Unassigned",
        "items": [
            record
            for grouped_records in assignments_by_item.values()
            for record in grouped_records
        ],
    }


def get_employee_details_with_items_one(emp_id: str):
    """Return one employee with their assigned assets and custom attributes."""
    try:
        with session_scope() as db:
            employee = (
                db.query(Employee)
                .options(*_employee_items_load_options())
                .filter(Employee.emp_id == emp_id)
                .first()
            )
            if employee is None:
                raise ValueError(f"Employee with ID {emp_id} not found")
            return _employee_with_items_to_dict(employee)
    except Exception as exc:
        logger.error(f"Error retrieving employee details for {emp_id}: {exc}")
        raise


def get_employee_details_with_items(emp_ids=None):
    """Fetch all employees or a requested subset using batched relationships."""
    try:
        with session_scope() as db:
            query = db.query(Employee).options(*_employee_items_load_options())
            if emp_ids is not None:
                if not emp_ids:
                    return []
                query = query.filter(Employee.emp_id.in_(emp_ids))
            return [_employee_with_items_to_dict(employee) for employee in query.all()]
    except Exception as exc:
        logger.error(f"Error retrieving employee details: {exc}")
        raise


def delete_employee(emp_id: str):
    """Delete an employee only after their assigned items have been handled.

    Without this guard, SQLAlchemy may silently NULL the emp_id on existing
    employee_items, leaving historical rows that crash inventory searches.
    """
    with session_scope() as db:
        employee = db.query(Employee).filter(Employee.emp_id == emp_id).first()
        if employee is None:
            return None

        assignment_count = db.query(EmployeeItem).filter(
            EmployeeItem.emp_id == emp_id
        ).count()
        if assignment_count:
            raise ValueError(
                f"Cannot remove employee {emp_id}: {assignment_count} item(s) are "
                "still assigned. Transfer or remove those assignments first."
            )

        db.delete(employee)
        db.flush()
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
        item = db.query(Item).filter(Item.item_id == item_id).first()
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

def save_item_attribute(emp_id, item_id, name, value):
    with session_scope() as db:
        try:
            # Check if the item exists
            item = db.query(EmployeeItem).filter(EmployeeItem.item_id == item_id, EmployeeItem.emp_id == emp_id).first()
            if not item:
                raise ValueError("Item not found")

            # Check if the attribute already exists for the item
            existing_attribute = db.query(EmployeeItemAttribute).filter(
                EmployeeItemAttribute.emp_item_id == item.id,
                EmployeeItemAttribute.name == name
            ).first()
            if existing_attribute:
                # Update the existing attribute
                existing_attribute.value = value
            else:
                # Create a new attribute
                new_attribute = EmployeeItemAttribute(
                    emp_item_id=item.id,
                    name=name,
                    value=value
                )
                db.add(new_attribute)

            db.commit()
            return True
        except Exception as e:
            db.rollback()
            log_action(action_type="error", details=f"Error saving item attribute: {str(e)}")
            return False

def remove_item_attribute(emp_id, item_id, name):
    with session_scope() as db:
        try:
            # Check if the item exists
            item = db.query(EmployeeItem).filter(EmployeeItem.item_id == item_id, EmployeeItem.emp_id == emp_id).first()
            if not item:
                raise ValueError("Item not found")

            # Find the attribute to remove
            attribute = db.query(EmployeeItemAttribute).filter(
                EmployeeItemAttribute.emp_item_id == item.id,
                EmployeeItemAttribute.name == name
            ).first()
            if attribute:
                db.delete(attribute)
                db.commit()
                return True
            else:
                raise ValueError("Attribute not found")
        except Exception as e:
            db.rollback()
            log_action(action_type="error", details=f"Error removing item attribute: {str(e)}")
            return False
              
def assign_item_to_employee(emp_id: str, item_id: int, unique_key: str, attrs: dict, notes: str = ""):
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
        employee = db.query(Employee).filter(Employee.emp_id == emp_id).first()
        employee.item_count += 1
        db.commit()

        # Add attribute details
        for name, value in attrs.items():
            attribute = EmployeeItemAttribute(
                emp_item_id=employee_item.id,
                name=name,
                value=value
            )
            db.add(attribute)
        db.commit()

        # Log the action
        db.close()
        return True
      
# Item Transfer
def transfer_item(from_emp_id: str, to_emp_id: str, item_id: int, unique_key: str, notes: str = "") -> bool:
    with session_scope() as db:
        try:
            # Clean up orphaned EmployeeItemAttributes (emp_item_id = NULL)
            db.query(EmployeeItemAttribute).filter(
                EmployeeItemAttribute.emp_item_id.is_(None)
            ).delete()

            # Find the current EmployeeItem assignment
            current_assignment = db.query(EmployeeItem).filter(
                EmployeeItem.emp_id == from_emp_id,
                EmployeeItem.item_id == item_id
            ).first()

            if not current_assignment:
                # If no assignment is found, return False
                log_action(action_type="error", details=f"No assignment found for item {item_id} and employee {from_emp_id}")
                return False

            # Get the associated EmployeeItemAttributes
            attributes = db.query(EmployeeItemAttribute).filter(
                EmployeeItemAttribute.emp_item_id == current_assignment.id
            ).all()

            # Remove the current assignment
            db.delete(current_assignment)

            # Update item count for the from_employee
            from_employee = db.query(Employee).filter(Employee.emp_id == from_emp_id).first()
            if from_employee:
                from_employee.item_count -= 1

            # Create a new assignment for the to_employee
            new_assignment = EmployeeItem(
                emp_id=to_emp_id,
                item_id=item_id,
                unique_key=unique_key,
                notes=notes,
                date_assigned=datetime.utcnow()
            )
            db.add(new_assignment)
            db.flush()  # Flush to get the new_assignment.id

            # Transfer the attributes to the new assignment
            for attribute in attributes:
                new_attribute = EmployeeItemAttribute(
                    emp_item_id=new_assignment.id,
                    name=attribute.name,
                    value=attribute.value
                )
                db.add(new_attribute)

            # Update item count for the to_employee
            to_employee = db.query(Employee).filter(Employee.emp_id == to_emp_id).first()
            if to_employee:
                to_employee.item_count += 1

            # Log the transfer
            log_action(action_type="transfer_item", details=f"Transferred item {item_id} from {from_emp_id} to {to_emp_id}")

            # Add a record to ItemTransferHistory
            transfer_record = ItemTransferHistory(
                item_id=item_id,
                from_emp_id=from_emp_id,
                to_emp_id=to_emp_id,
                transfer_date=datetime.utcnow(),
                notes=notes
            )
            db.add(transfer_record)

            db.query(EmployeeItemAttribute).filter(
                EmployeeItemAttribute.emp_item_id.is_(None)
            ).delete()
            
            # Commit the transaction
            db.commit()
            return True

        except Exception as e:
            # Handle any exceptions that occur during the transaction
            db.rollback()
            log_action(action_type="error", details=f"Error transferring item {item_id} from {from_emp_id} to {to_emp_id}: {str(e)}")
            return False
        
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
    
def remove_item_from_employee(emp_id: str, item_id: int) -> bool:
    with session_scope() as db:
        try:
            # Find the EmployeeItem assignment
            assignment = db.query(EmployeeItem).filter(
                EmployeeItem.emp_id == emp_id,
                EmployeeItem.item_id == item_id
            ).first()

            if assignment:
                # Delete all associated EmployeeItemAttributes
                db.query(EmployeeItemAttribute).filter(
                    EmployeeItemAttribute.emp_item_id == assignment.id
                ).delete()

                # Remove the EmployeeItem assignment
                db.delete(assignment)

                # Update item count for the employee
                employee = db.query(Employee).filter(Employee.emp_id == emp_id).first()
                if employee:
                    employee.item_count -= 1

                # Log the action
                log_action(action_type="remove_item", details=f"Removed item {item_id} from employee {emp_id}")

                # Commit the transaction
                db.commit()
                return True
            else:
                # If no assignment was found, return False
                return False

        except Exception as e:
            # Handle any exceptions that occur during the transaction
            db.rollback()
            log_action(action_type="error", details=f"Error removing item {item_id} from employee {emp_id}: {str(e)}")
            return False