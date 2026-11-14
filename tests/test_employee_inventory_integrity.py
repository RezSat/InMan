"""Regression tests for orphaned inventory and employee removal.

Uses an isolated in-memory SQLite database; never opens inventory.db.
"""
import unittest
from datetime import date
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.database import Base
from models.models import Division, Employee, EmployeeItem, EmployeeItemAttribute, Item, ItemTransferHistory
from controllers import crud
from utils import search
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

    def test_assign_item_persists_attributes_and_count_together(self):
        self.assertTrue(crud.assign_item_to_employee(
            "E002", 1, "NEW-ASSET", {"Serial": "123", "RAM": "8GB"}
        ))
        with self.Session() as db:
            assignment = db.query(EmployeeItem).filter(
                EmployeeItem.unique_key == "NEW-ASSET"
            ).one()
            attributes = db.query(EmployeeItemAttribute).filter(
                EmployeeItemAttribute.emp_item_id == assignment.id
            ).all()
            self.assertEqual({a.name: a.value for a in attributes},
                             {"Serial": "123", "RAM": "8GB"})
            self.assertEqual(db.get(Employee, "E002").item_count, 1)

    def test_failed_assignment_has_no_partial_rows(self):
        with self.assertRaisesRegex(ValueError, "Employee .* not found"):
            crud.assign_item_to_employee("BAD-ID", 1, "GHOST", {"Serial": "x"})
        with self.assertRaisesRegex(ValueError, "Item .* not found"):
            crud.assign_item_to_employee("E002", 999, "BAD-ITEM", {})
        with self.Session() as db:
            self.assertEqual(db.query(EmployeeItem).count(), 2)
            self.assertEqual(db.get(Employee, "E002").item_count, 0)

    def test_transfer_history_search_and_summary(self):
        with self.Session.begin() as db:
            db.add(ItemTransferHistory(
                item_id=1, from_emp_id="E001", to_emp_id="E002",
                transfer_date=date.today(), notes="Moved"
            ))
        by_source = search.search_item_transfer_history("Current")
        by_destination = search.search_item_transfer_history("No Items")
        self.assertEqual(len(by_source), 1)
        self.assertEqual(len(by_destination), 1)
        self.assertEqual(by_source[0].item.name, "Monitor")
        self.assertEqual(search.get_transfer_history_summary(days=30)["total_transfers"], 1)

    def test_employee_id_changes_preserve_asset_and_transfer_references(self):
        with self.Session.begin() as db:
            db.add(ItemTransferHistory(
                item_id=1, from_emp_id="E001", to_emp_id="E002",
                transfer_date=date.today(),
            ))
        employee = crud.update_employee_id("E001", "E100")
        self.assertIsNotNone(employee)
        with self.Session() as db:
            self.assertIsNone(db.get(Employee, "E001"))
            self.assertEqual(db.get(Employee, "E100").name, "Current Employee")
            self.assertEqual(db.get(EmployeeItem, 1).emp_id, "E100")
            transfer = db.query(ItemTransferHistory).one()
            self.assertEqual((transfer.from_emp_id, transfer.to_emp_id),
                             ("E100", "E002"))
        self.assertEqual(
            crud.get_employee_details_with_items_one("E100")["items"][0]["unique_key"],
            "CURRENT",
        )

    def test_duplicate_employee_id_rolls_back_all_references(self):
        self.assertIsNone(crud.update_employee_id("E001", "E002"))
        with self.Session() as db:
            self.assertIsNotNone(db.get(Employee, "E001"))
            self.assertEqual(db.get(EmployeeItem, 1).emp_id, "E001")

    def test_transfer_moves_exact_asset_and_keeps_attributes(self):
        with self.Session.begin() as db:
            db.add(EmployeeItem(
                id=3, emp_id="E001", item_id=1, unique_key="ANOTHER-LAPTOP"
            ))
            db.add(EmployeeItemAttribute(
                emp_item_id=1, name="Serial", value="S-101"
            ))
            db.get(Employee, "E001").item_count = 2

        self.assertTrue(crud.transfer_item(
            "E001", "E002", 1, "CURRENT", notes="Moved"
        ))
        with self.Session() as db:
            source_keys = {
                record.unique_key for record in db.query(EmployeeItem).filter(
                    EmployeeItem.emp_id == "E001"
                ).all()
            }
            self.assertEqual(source_keys, {"ANOTHER-LAPTOP"})
            target = db.query(EmployeeItem).filter(
                EmployeeItem.emp_id == "E002"
            ).one()
            self.assertEqual(target.unique_key, "CURRENT")
            attrs = db.query(EmployeeItemAttribute).filter(
                EmployeeItemAttribute.emp_item_id == target.id
            ).all()
            self.assertEqual([(a.name, a.value) for a in attrs],
                             [("Serial", "S-101")])
            self.assertEqual(db.get(Employee, "E001").item_count, 1)
            self.assertEqual(db.get(Employee, "E002").item_count, 1)

    def test_transfer_failure_does_not_move_other_instance(self):
        self.assertFalse(crud.transfer_item("E001", "E002", 1, "NO-SUCH-KEY"))
        self.assertFalse(crud.transfer_item("E001", "MISSING", 1, "CURRENT"))
        with self.Session() as db:
            assignment = db.get(EmployeeItem, 1)
            self.assertEqual(assignment.emp_id, "E001")
            self.assertEqual(db.get(Employee, "E001").item_count, 1)
            self.assertEqual(db.get(Employee, "E002").item_count, 0)

    def test_missing_employee_is_noop(self):
        self.assertIsNone(crud.delete_employee("NOT-FOUND"))


if __name__ == "__main__":
    unittest.main()
