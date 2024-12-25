from controllers.crud import assign_item_to_employee, get_all_employees, get_all_employees_ids, get_employee, get_item
from models.models import Employee, EmployeeItem, Item
from utils.search import search_by_unique_key
from models.database import SessionLocal, session_scope
"""
list_employees = get_all_employees_ids()
for employee in list_employees:
    x = assign_item_to_employee(employee, 2, unique_key="-")"""

query = "-"
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
print(l)