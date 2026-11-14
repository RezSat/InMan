"""Selection state shared by the three bulk-removal screens.

This module owns only selection logic. The screens retain their own widgets,
callbacks, labels and layouts.
"""


def selected_ids(rows, key, checked):
    return {key(row) for row in rows} if checked else set()


def toggle_selected(selected, record_id):
    if record_id in selected:
        selected.remove(record_id)
    else:
        selected.add(record_id)


def update_remove_button(button, selected):
    button.configure(state="normal" if selected else "disabled")


def update_select_all_checkbox(checkbox, selected, visible_ids):
    if visible_ids and visible_ids.issubset(selected):
        checkbox.select()
    else:
        checkbox.deselect()
