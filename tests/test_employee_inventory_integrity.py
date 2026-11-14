"""Regression tests for orphaned inventory and employee removal.

Uses an isolated in-memory SQLite database; never opens inventory.db.
"""
import unittest
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.database import Base
from models.models import Division, Employee, EmployeeItem, Item
from controllers import crud
from utils import search
import models.database as database


class EmployeeInventoryIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)
        self.patch_session_scope = patch.object(database, "Session", self.Session)
        self.patch_search_session = patch.object(search, "SessionLocal", self.Session)
        self.patch_session_scope.start()
        self.patch_search_session.start()
        self.addCleanup(self.patch_session_scope.stop)
        self.addCleanup(self.patch_search_session.stop)
        self.addCleanup(self.engine.dispose)
        with self.Session.begin() as db:
            db.add(Division(division_id=1, name="Operations"))
            db.add(Employee(emp_id="E001", name="Current Employee", division_id=1, item_count=1))
            db.add(Employee(emp_id="E002", name="No Items", division_id=1, item_count=0))
            db.add(Item(item_id=1, name="Monitor"))
            db.add(EmployeeItem(id=1, emp_id="E001", item_id=1, unique_key="CURRENT"))
            db.add(EmployeeItem(id=2, emp_id=None, item_id=1, unique_key="ORPHAN"))

    def test_employee_items_search_ignores_orphaned_assignments(self):
        result = search.search_employee_items("")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["emp_id"], "E001")
        self.assertEqual(result[0]["unique_key"], "CURRENT")

    def test_deleting_employee_with_items_is_blocked_without_changes(self):
        with self.assertRaisesRegex(ValueError, "1 item\\(s\\) are still assigned"):
            crud.delete_employee("E001")
        with self.Session() as db:
            self.assertIsNotNone(db.get(Employee, "E001"))
            self.assertEqual(db.get(EmployeeItem, 1).emp_id, "E001")
            self.assertIsNone(db.get(EmployeeItem, 2).emp_id)

    def test_employee_without_items_can_be_deleted(self):
        crud.delete_employee("E002")
        with self.Session() as db:
            self.assertIsNone(db.get(Employee, "E002"))
            self.assertEqual(db.query(EmployeeItem).count(), 2)

    def test_missing_employee_is_noop(self):
        self.assertIsNone(crud.delete_employee("NOT-FOUND"))


if __name__ == "__main__":
    unittest.main()
