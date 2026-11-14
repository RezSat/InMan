# InMan desktop release checklist

Use the same Windows account and test database for the last released binary and the candidate 1.4 binary. Test against **copies**, not production databases.

## Setup

- [ ] Create two test directories, each with its own `InMan.exe` and copied `inventory.db`.
- [ ] Confirm the original IM icon appears in Explorer and the Properties dialog.
- [ ] Launch both builds without changing the working directory unexpectedly.
- [ ] Confirm product-key activation and manager authentication.
- [ ] Capture Dashboard, View Inventory, Manager Tools, dialogs and report output from both versions for side-by-side comparison.
- [ ] Confirm the color palette, labels, dimensions, fonts, hover states and scroll behavior match.

## Sidebar and dashboard

- [ ] Dashboard loads employee counts, item-type count, division count and each division's item assignments.
- [ ] Login and Manager Tools open and return to the correct screen.
- [ ] View Inventory opens and its search mode selector works.
- [ ] Package to Share produces a usable ZIP beside the selected save location.
- [ ] Empty lists and a missing-but-new database launch without a crash.

## Inventory searches

- [ ] Employees: empty query, partial name, employee ID, division filter, export.
- [ ] Items: empty query, partial item name, no matches, export.
- [ ] Divisions: empty query, partial name, employee/item totals, export.
- [ ] Unique Key: exact and partial asset ID, no matches, export.
- [ ] Employee Items: item name, attribute name, attribute value, combinations, blank query, export.
- [ ] Search from Return and Search button.
- [ ] Search keeps the chosen mode, current text, and filters when results load.
- [ ] Previously orphaned employee-item rows do not crash the search; valid rows still display.

## Manager tools

- [ ] Add a new item type, update its details, view it, then remove it.
- [ ] Add an employee, update name/division/ID, and open employee records.
- [ ] Import employees from a spreadsheet; confirm the same import validation and table layout.
- [ ] Add, update and view divisions, including existing employees and counts.
- [ ] Assign two item instances with custom attributes to one employee.
- [ ] Transfer an item between employees and inspect attributes, counts and transfer logs.
- [ ] Update and remove an item attribute; compare expected values.
- [ ] Single- and multi-select removal screens maintain their checkbox, selection and confirmation behavior.
- [ ] Attempt to remove an employee with assigned items; expect a clear rejection without data loss.
- [ ] Remove a test employee with no assignments, after confirmation.
- [ ] Export division-wise inventory, employee list and item types; compare sheet names, headers, values, merged cells, styles and totals.

## Database invariants

- [ ] No schema migration is required when opening a v1.3.2 SQLite database.
- [ ] Primary keys and assignment-to-employee/item relationships remain valid.
- [ ] `employee_item_attributes` remain tied to the correct physical item.
- [ ] `item_transfer_history` and `logs` preserve existing rows.
- [ ] Foreign key and integrity checks pass: `PRAGMA foreign_key_check;`, `PRAGMA integrity_check;`.
- [ ] Close InMan, reopen it and confirm all changes persist.
- [ ] Test the sample with an optional archive table; it must remain untouched.

## Performance observations

Record warm and cold load times for both builds on the **same machine** using identical data:

| Operation | v1.3.2 | v1.4 | Notes |
| --- | --- | --- | --- |
| Dashboard open | | | |
| View Inventory empty search | | | |
| Employees search, all | | | |
| Employee Items, all valid | | | |
| Manager employee records | | | |
| Division-wise inventory Excel export | | | |

Do not claim a speedup without measured numbers. SQL query-count tests provide a guardrail, but they do not measure UI rendering latency or Windows startup time.

## Ship/no-ship

Release only when automated tests, Windows executable packaging and the manual feature comparison pass. Do not overwrite a verified older release: retain `old/v1.3.2` and its release assets. Signing/reputation warnings require separate Authenticode validation.
