"""Employee read-path contracts and SQL query budget."""
import unittest
from unittest.mock import patch

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from controllers import crud
import models.database as database
from models.database import Base
from models.models import Division, Employee, Item, EmployeeItem, EmployeeItemAttribute


class EmployeeReadTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)
        self.session_patch = patch.object(database, "Session", self.Session)
        self.session_patch.start()
        self.addCleanup(self.session_patch.stop)
        self.addCleanup(self.engine.dispose)
        with self.Session.begin() as db:
            db.add(Division(division_id=1, name="Operations"))
            db.add(Item(item_id=1, name="Laptop"))
            db.add(Item(item_id=2, name="Monitor"))
            for number in range(1, 5):
                db.add(Employee(
                    emp_id=f"E{number:03}", name=f"Employee {number}",
                    division_id=1, item_count=0,
                ))
            db.flush()
            db.add_all([
                EmployeeItem(id=1, emp_id="E001", item_id=1, unique_key="LP-01"),
                EmployeeItem(id=2, emp_id="E001", item_id=2, unique_key="MN-01"),
                EmployeeItem(id=3, emp_id="E001", item_id=1, unique_key="LP-02"),
                EmployeeItem(id=4, emp_id="E002", item_id=2, unique_key="MN-02"),
            ])
            db.flush()
            db.add_all([
                EmployeeItemAttribute(emp_item_id=1, name="RAM", value="16GB"),
                EmployeeItemAttribute(emp_item_id=3, name="RAM", value="32GB"),
            ])

    def sql_count(self, read):
        count = 0

        def on_query(conn, cursor, statement, parameters, context, executemany):
            nonlocal count
            if statement.lstrip().upper().startswith("SELECT"):
                count += 1

        event.listen(self.engine, "before_cursor_execute", on_query)
        try:
            result = read()
        finally:
            event.remove(self.engine, "before_cursor_execute", on_query)
        return result, count

    def test_single_employee_items_keep_fields_and_grouping(self):
        employee = crud.get_employee_details_with_items_one("E001")
        self.assertEqual(set(employee), {"emp_id", "name", "division", "items"})
        self.assertEqual([item["unique_key"] for item in employee["items"]],
                         ["LP-01", "LP-02", "MN-01"])
        self.assertEqual([a["value"] for a in employee["items"][1]["attributes"]], ["32GB"])
        self.assertEqual(employee["division"], "Operations")

    def test_missing_employee_still_raises(self):
        with self.assertRaisesRegex(ValueError, "not found"):
            crud.get_employee_details_with_items_one("missing")

    def test_full_inventory_has_bounded_queries(self):
        employees, queries = self.sql_count(crud.get_employee_details_with_items)
        self.assertEqual(len(employees), 4)
        self.assertEqual([len(row["items"]) for row in employees], [3, 1, 0, 0])
        self.assertLessEqual(queries, 4, f"Full employee inventory issued {queries} queries")

    def test_single_employee_has_bounded_queries(self):
        _, queries = self.sql_count(lambda: crud.get_employee_details_with_items_one("E001"))
        self.assertLessEqual(queries, 4)


if __name__ == "__main__":
    unittest.main()
