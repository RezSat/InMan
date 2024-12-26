from controllers.crud import assign_item_to_employee, get_all_employees, get_all_employees_ids, get_employee, get_item
from models.models import Employee, EmployeeItem, Item
from utils.search import search_items
from models.database import SessionLocal, session_scope
"""
list_employees = get_all_employees_ids()
for employee in list_employees:
    x = assign_item_to_employee(employee, 2, unique_key="-")"""

results = search_items("")
for idx, item in enumerate(results, 1):
    print(idx, item)
    if item['attributes']:
        for i, attr in enumerate(item['attributes']):
            print(attr)