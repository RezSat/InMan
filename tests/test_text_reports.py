"""Legacy text summary helpers still produce usable inventory reports."""
import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.database import Base
from models.models import Division, Employee, EmployeeItem, EmployeeItemAttribute, Item
from utils import summary


class TextSummaryTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.addCleanup(self.engine.dispose)
        with self.Session.begin() as db:
            db.add(Division(division_id=1, name="Operations"))
            db.add(Employee(emp_id="E101", name="Employee One", division_id=1))
            db.add(Item(item_id=1, name="Laptop"))
            db.add(EmployeeItem(
                id=1, emp_id="E101", item_id=1, unique_key="SERIAL-101"
            ))
            db.add(EmployeeItemAttribute(
                emp_item_id=1, name="RAM", value="16GB"
            ))

    def test_employee_summaries(self):
        with self.Session() as db:
            basic = summary.generate_employee_report(db, "E101")
            detailed = summary.generate_detailed_employee_report(db, "E101")
            missing = summary.generate_employee_report(db, "NOT-FOUND")
        self.assertIn("SERIAL-101", basic)
        self.assertIn("RAM: 16GB", detailed)
        self.assertEqual(missing, "Employee not found.")

    def test_item_and_attribute_reports(self):
        with self.Session() as db:
            inventory = summary.generate_item_report(db)
            filtered = summary.generate_attribute_filtered_item_report(
                db, "RAM", "16GB"
            )
        self.assertIn("Laptop", inventory)
        self.assertIn("SERIAL-101", inventory)
        self.assertIn("RAM: 16GB", filtered)


if __name__ == "__main__":
    unittest.main()
