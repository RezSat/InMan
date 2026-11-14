# gui/utils.py
import json


def load_inventory():
    try:
        with open('inventory.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_inventory(inventory):
    with open('inventory.json', 'w') as file:
        json.dump(inventory, file, indent=4)


def clear_children(frame):
    """Destroy all children without changing the parent frame layout."""
    for widget in frame.winfo_children():
        widget.destroy()
