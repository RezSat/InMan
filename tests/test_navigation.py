"""Navigation command dispatch without opening a desktop window."""
import unittest
from unittest.mock import Mock

from gui.manager import ManagerTools, AddItems, AddEmployee, AddDivision, RemoveEmployee
from gui.ui import InventoryApp


class NavigationTests(unittest.TestCase):
    def test_manager_commands_keep_their_target_screens(self):
        manager = ManagerTools.__new__(ManagerTools)
        manager._open_tool = Mock()
        for command_name, screen in [
            ("add_item_cmd", AddItems),
            ("add_employee_cmd", AddEmployee),
            ("add_division_cmd", AddDivision),
            ("remove_employee_cmd", RemoveEmployee),
        ]:
            manager._open_tool.reset_mock()
            getattr(manager, command_name)()
            manager._open_tool.assert_called_once_with(screen)

    def test_main_navigation_reuses_the_original_screen_constructor(self):
        app = InventoryApp.__new__(InventoryApp)
        app.main_frame = object()
        app.inventory = ["existing"]
        app.clear_main_frame = Mock()
        screen = Mock()

        app._show_screen(screen)

        app.clear_main_frame.assert_called_once_with()
        screen.assert_called_once_with(app.main_frame, app.inventory)
        screen.return_value.display.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
