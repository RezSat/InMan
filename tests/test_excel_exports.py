"""Excel report checks using generated fixtures, not employee databases."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from openpyxl import load_workbook

from utils import summary


class ExcelExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

    def save_path(self, name):
        return str(Path(self.temp.name) / name)

    def test_employee_report_columns_and_totals(self):
        path = self.save_path("employees.xlsx")
        employees = [
            {"emp_id": "E101", "name": "Employee One", "division": "Operations"},
            {"emp_id": "E102", "name": "Employee Two", "division": "Operations"},
        ]
        with patch.object(summary.filedialog, "asksaveasfilename", return_value=path), \
             patch.object(summary, "get_all_employees", return_value=employees), \
             patch.object(summary.messagebox, "showinfo"), \
             patch.object(summary.messagebox, "showerror") as error:
            summary.employee_id_name_to_excel()
            error.assert_not_called()

        book = load_workbook(path)
        sheet = book["Employees"]
        self.assertEqual([sheet.cell(1, col).value for col in range(1, 4)],
                         ["Employee ID", "Name", "Division"])
        self.assertEqual([sheet.cell(2, col).value for col in range(1, 4)],
                         ["E101", "Employee One", "Operations"])
        self.assertEqual(sheet.cell(5, 2).value, 2)
        self.assertTrue(sheet.cell(1, 1).font.bold)
        self.assertEqual(sheet.cell(1, 1).alignment.horizontal, "center")
        self.assertEqual(sheet.cell(1, 1).border.left.style, "thin")

    def test_item_types_report(self):
        path = self.save_path("items.xlsx")
        class ItemRecord:
            def __init__(self, item_id, name):
                self.item_id = item_id
                self.name = name

        with patch.object(summary.filedialog, "asksaveasfilename", return_value=path), \
             patch.object(summary, "get_all_items", return_value=[
                 ItemRecord(1, "Laptop"), ItemRecord(2, "Monitor")
             ]), \
             patch.object(summary.messagebox, "showinfo"), \
             patch.object(summary.messagebox, "showerror") as error:
            summary.items_to_excel()
            error.assert_not_called()

        sheet = load_workbook(path)["Items"]
        self.assertEqual([sheet.cell(row, 1).value for row in range(1, 4)],
                         ["Name", "Laptop", "Monitor"])
        self.assertTrue(sheet.cell(1, 1).font.bold)

    def test_division_inventory_keeps_headers_and_asset_rows(self):
        path = self.save_path("inventory.xlsx")
        fixture = [{
            "emp_id": "E101", "name": "Employee One", "division": "Operations",
            "items": [{
                "item_id": 1, "name": "Laptop", "unique_key": "ASSET-1",
                "date_assigned": "2026-11-15",
                "attributes": [{"name": "RAM", "value": "16GB"}],
            }],
        }]
        with patch.object(summary.filedialog, "asksaveasfilename", return_value=path), \
             patch.object(summary, "get_employee_details_with_items", return_value=fixture), \
             patch.object(summary.messagebox, "showinfo"), \
             patch.object(summary.messagebox, "showerror") as error:
            summary.divison_wise_employee_items_to_excel()
            error.assert_not_called()

        sheet = load_workbook(path).active
        self.assertEqual([sheet.cell(1, col).value for col in range(1, 7)], [
            "Division", "Employee Name", "Employee ID", "Item Name",
            "Unique Key | Reference ID", "Attributes",
        ])
        self.assertEqual([sheet.cell(2, col).value for col in range(1, 7)], [
            "Operations", "Employee One", "E101", "Laptop", "ASSET-1",
            "RAM: 16GB",
        ])
        self.assertTrue(sheet.cell(1, 1).fill.start_color.rgb.endswith("D3D3D3"))


if __name__ == "__main__":
    unittest.main()
