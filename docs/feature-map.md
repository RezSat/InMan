# InMan feature and compatibility map

Baseline: `old/v1.3.2` (snapshot of the release before the v1.4 refactor).
Working branch: `refactor/v1.4`.

This document lists behavior to preserve. A refactor is not permission to change the data format, silently rename labels, reorder user flows, or restyle controls.

## Application entry and navigation

- Windows product-key check and persisted user activation; open the same main window after validation.
- Main window: 1200 x 700, dark CustomTkinter theme, left sidebar.
- Sidebar: Dashboard, Login, View Inventory, Package to Share. Preserve existing shortcuts, mouse interactions, and dialogs.
- Manager login: authentication, Manager Tools landing screen, tool navigation, return-to-manager actions.
- Dashboard: employee/item/division totals and per-division item-type summaries.
- UI palette: `config.COLORS` is canonical. Fonts, layout geometry, hover states, strings and widget hierarchy are compatibility constraints.

## View Inventory

Search modes and exported results:

| Mode | Search and filter behavior | Results |
| --- | --- | --- |
| Employees | Name or employee ID, optional division | Employee details and owned items |
| Items | Item name | Matching item types |
| Divisions | Division name | Division counts |
| Unique Key | Assignment's unique asset key | Assigned employee/item/key |
| Employee Items | Item name and optional attribute name/value | Employee ID/name, item name, key and attributes |

Preserve Enter-to-search, the Search button, field filters, preserved search state, export dialog, existing workbook structure and visible columns. Orphaned records must never crash the search.

## Manager Tools

| Section | Actions and screens |
| --- | --- |
| Inventory Management | Add Single Item; Update Item Details; Remove Items (single and bulk); View Item Records |
| Employee Management | Add Employee; Bulk Import Employees; Update Employee Info including ID and attributes; Remove Employee (single and bulk); View Employee Records |
| Division Management | Create Division; Update Division; Remove Division (single and bulk); View Division Structure |
| Asset Assignment | Assign Items to Employee; Transfer Items Between Employees |
| Reports & Analytics | Inventory Report to Excel; Employees to Excel; Items to Excel |

The code also contains an asset assignment log viewer, a timestamped backup function, and menu wiring currently not displayed on the Manager Tools landing screen. Preserve these internal entrypoints.

## Database and side effects

SQLite file: `inventory.db` in the executable working directory. Tables: `divisions`, `employees`, `items`, `employee_items`, `employee_item_attributes`, `users`, `logs`, `item_transfer_history`.

Do not rename columns, change primary/foreign key types, delete data, or require migration for v1.3.2 databases. The user may also use a repaired database with a separate `archived_employee_items` table; that archive must not be touched.

Preserve assignment/transfer history, custom attributes, unique-key formats, counts, exported spreadsheets and login authentication. Removing an employee with assigned items is intentionally blocked since v1.3.1.

## Verification gates

1. Tests run against temporary SQLite databases, never a customer's `inventory.db`.
2. Read endpoints retain response fields and meaningful display ordering.
3. Query-count tests guard against returning to N+1 database access.
4. Static UI contract tests detect accidental changes to visible search choices, toolbar actions, and palette.
5. Windows CI must build `InMan.exe` with the original `CustomTkinter_icon_Windows.ico`.
6. Manual Windows smoke testing still required for dialogs, navigation, first-launch activation, screen appearance, file exports and the packaged EXE. Automated tests are not a substitute for visual desktop validation.
