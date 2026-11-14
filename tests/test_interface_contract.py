"""Static compatibility checks for navigation and branding.

These checks avoid opening a Tk window in CI. Visual regression testing still
requires the Windows executable on a desktop.
"""
import ast
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def source_literals(relative_path):
    tree = ast.parse((ROOT / relative_path).read_text(encoding="utf-8-sig"))
    return {node.value for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)}


class InterfaceContractTests(unittest.TestCase):
    def test_search_modes_are_unchanged(self):
        choices = source_literals("gui/inventory.py")
        self.assertTrue({
            "Select type", "Employees", "Items", "Divisions",
            "Unique Key", "Employee Items"
        }.issubset(choices))

    def test_manager_actions_are_available(self):
        menu = source_literals("gui/manager.py")
        self.assertTrue({
            "Add Single Item", "Update Item Details", "Remove Items", "View Item Records",
            "Add Employee", "Bulk Import Employees", "Update Employee Info",
            "Remove Employee", "View Employee Records", "Create Division",
            "Update Division", "Remove Division", "View Division Structure",
            "Assign Items to Employee", "Transfer Items Between Employees",
            "Inventory Report to Excel", "Employees to Excel", "Items to Excel"
        }.issubset(menu))

    def test_sidebar_routes_remain_present(self):
        buttons = source_literals("gui/sidebar.py")
        self.assertTrue({"Dashboard", "Login", "View Inventory", "Package to Share"}.issubset(buttons))

    def test_palette_remains_stable(self):
        tree = ast.parse((ROOT / "config.py").read_text(encoding="utf-8"))
        assignment = next(node for node in tree.body
                          if isinstance(node, ast.Assign)
                          and any(isinstance(t, ast.Name) and t.id == "COLORS" for t in node.targets))
        actual = ast.literal_eval(assignment.value)
        self.assertEqual(actual, {
            "black": "#2c363f", "pink": "#e75a7c", "darker_pink": "#8F344A",
            "white": "#f2f5ea", "ash": "#d6dbd2", "green": "#4CAF50",
            "secondary_bg": "#1A1A1A"
        })

    def test_release_icon_matches_original(self):
        workflow = (ROOT / ".github/workflows/windows-release.yml").read_text(encoding="utf-8")
        self.assertIn("--icon assets/CustomTkinter_icon_Windows.ico", workflow)


if __name__ == "__main__":
    unittest.main()
