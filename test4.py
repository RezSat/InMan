from controllers.crud import assign_item_to_employee, get_all_employees_ids


list_employees = get_all_employees_ids()
for employee in list_employees:
    x = assign_item_to_employee(employee, 2, unique_key="-")
