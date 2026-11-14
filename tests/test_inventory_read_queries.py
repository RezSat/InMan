"""Employee read-path contracts and SQL query budget."""
import unittest
from unittest.mock import patch

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from controllers import crud
from utils import search
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
        self.search_patch = patch.object(search, "SessionLocal", self.Session)
        self.search_patch.start()
        self.addCleanup(self.search_patch.stop)
        self.addCleanup(self.engine.dispose)
        with self.Session.begin() as db:
            db.add(Division(division_id=1, name="Operations"))
            db.add(Division(division_id=2, name="Empty Division"))
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
                EmployeeItem(id=5, emp_id=None, item_id=1, unique_key="OLD-ORPHAN"),
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

    def test_employee_search_keeps_order_and_item_payload(self):
        matches, queries = self.sql_count(
            lambda: search.search_employees("Employee", items_need=True)
        )
        self.assertEqual([row["emp_id"] for row in matches],
                         ["E001", "E002", "E003", "E004"])
        self.assertEqual(matches[0]["items"][0]["unique_key"], "LP-01")
        self.assertLessEqual(queries, 5, f"Employee search issued {queries} queries")
        self.assertEqual(
            [row["emp_id"] for row in search.search_employees("E002")],
            ["E002"],
        )

    def test_employee_items_search_ignores_orphans_in_bounded_queries(self):
        matches, queries = self.sql_count(lambda: search.search_employee_items("Laptop"))
        self.assertEqual([row["unique_key"] for row in matches],
                         ["LP-01", "LP-02"])
        self.assertEqual(matches[0]["emp_name"], "Employee 1")
        self.assertEqual(matches[0]["attributes"], "RAM: 16GB")
        self.assertLessEqual(queries, 3, f"Employee items search issued {queries} queries")

    def test_dashboard_headline_counts_use_bounded_queries(self):
        totals, queries = self.sql_count(crud.get_dashboard_counts)
        self.assertEqual(totals, {"employees": 4, "items": 2, "divisions": 2})
        self.assertLessEqual(queries, 3)

    def test_division_search_keeps_field_contract(self):
        matches, queries = self.sql_count(lambda: search.search_divisions("Oper"))
        self.assertEqual(matches, [{
            "division_id": 1,
            "name": "Operations",
            "employee_count": 4,
            "item_count": 4,
        }])
        self.assertLessEqual(queries, 3)
        self.assertEqual(search.search_divisions("does-not-exist"), [])

    def test_dashboard_counts_match_assignments(self):
        divisions, queries = self.sql_count(crud.get_all_divisions_with_counts)
        self.assertEqual(len(divisions), 2)
        self.assertEqual(divisions[0], {
            "division_id": 1,
            "name": "Operations",
            "employee_count": 4,
            "item_count": 4,
            "items": [
                {"name": "Laptop", "count": 2},
                {"name": "Monitor", "count": 2},
            ],
        })
        self.assertEqual(divisions[1], {
            "division_id": 2,
            "name": "Empty Division",
            "employee_count": 0,
            "item_count": 0,
            "items": [],
        })
        self.assertLessEqual(queries, 3, f"Dashboard issued {queries} queries")

    def test_single_division_keeps_response_contract(self):
        division, queries = self.sql_count(
            lambda: crud.get_division_details_with_counts(1)
        )
        self.assertEqual(division["item_count"], 4)
        self.assertEqual(division["employee_count"], 4)
        self.assertLessEqual(queries, 3)
        self.assertIsNone(crud.get_division_details_with_counts(999))

    def test_single_employee_items_keep_fields_and_grouping(self):
        employee = crud.get_employee_details_with_items_one("E001")
        self.assertEqual(set(employee), {"emp_id", "name", "division", "items"})
        self.assertEqual([item["unique_key"] for item in employee["items"]],
                         ["LP-01", "LP-02", "MN-01"])
        self.assertEqual([a["value"] for a in employee["items"][1]["attributes"]], ["32GB"])
        self.assertEqual(employee["division"], "Operations")

    def test_item_lookup_uses_existing_schema(self):
        item = crud.get_item(1)
        self.assertEqual(item.name, "Laptop")
        self.assertIsNone(crud.get_item(999))

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
