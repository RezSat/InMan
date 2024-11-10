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
