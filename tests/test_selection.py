"""Bulk-selection rules independent of CustomTkinter."""
import unittest

from gui.tools.selection import (
    selected_ids, toggle_selected, update_remove_button,
    update_select_all_checkbox,
)


class FakeCheckbox:
    def __init__(self):
        self.selected = False

    def select(self):
        self.selected = True

    def deselect(self):
        self.selected = False


class FakeButton:
    def __init__(self):
        self.state = "disabled"

    def configure(self, **kwargs):
        self.state = kwargs["state"]


class SelectionTests(unittest.TestCase):
    def test_select_all_uses_only_visible_rows(self):
        data = [{"id": 1}, {"id": 3}]
        self.assertEqual(selected_ids(data, lambda row: row["id"], True), {1, 3})
        self.assertEqual(selected_ids(data, lambda row: row["id"], False), set())

    def test_toggle_selected(self):
        selected = {1}
        toggle_selected(selected, 1)
        self.assertEqual(selected, set())
        toggle_selected(selected, 2)
        self.assertEqual(selected, {2})

    def test_checkbox_and_button_states(self):
        checkbox, button = FakeCheckbox(), FakeButton()
        update_select_all_checkbox(checkbox, {1, 2, 9}, {1, 2})
        update_remove_button(button, {1, 2, 9})
        self.assertTrue(checkbox.selected)
        self.assertEqual(button.state, "normal")
        update_select_all_checkbox(checkbox, {1}, {1, 2})
        update_remove_button(button, set())
        self.assertFalse(checkbox.selected)
        self.assertEqual(button.state, "disabled")
        update_select_all_checkbox(checkbox, set(), set())
        self.assertFalse(checkbox.selected)


if __name__ == "__main__":
    unittest.main()
