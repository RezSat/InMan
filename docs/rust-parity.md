# Rust rewrite — compatibility and release contract

Baseline: InMan v1.4 (`main` at branch creation). Development branch: `rust-refactor`. **Do not merge or tag v2.0 until parity gates are passed.**

## Architecture

- `rust/src/db.rs` — direct SQLite access, explicit transactions, parameterized queries, bounded read paths
- `rust/src/licensing.rs` — SHA-256 product-key verification and Windows HKCU `Software\\InMan\ProductKey` compatibility
- `rust/src/reports.rs` — Excel imports/exports using Rust-native libraries
- `rust/src/ui.rs` — Rust-native egui desktop UI, retaining the InMan palette and navigation names
- `rust/src/main.rs` — executable startup
- `rust/tests/` — synthetic SQLite fixtures and behavior tests, never customer databases

The Python source remains unchanged for reference. The Rust app opens the same working-directory `inventory.db`; no migration is permitted to destroy or alter historical records or the optional archive table.

## Screens and flows required before v2.0

| Area | Parity requirements |
| --- | --- |
| Activation | Existing product key accepted, same SHA-256 verification, stored HKCU registry value honored |
| Dashboard | Counts and division breakdown; responsive layout and original colors |
| Manager login | Salted SHA-256 password compatibility; reject bad credentials (Python handler appears inverted) |
| Inventory | Employees, Items, Divisions, Unique Key and Employee Items search; filters, Enter-to-search and Excel results |
| Items | Add, edit, view, delete single/bulk with safe assignment checks |
| Employees | Add, bulk import XLS/XLSX, edit ID/name/division, view records, remove single/bulk |
| Divisions | Create, rename, view structure, remove single/bulk |
| Assignments | Assign with unique key/attributes, edit/remove attributes, transfer precisely selected asset, track logs |
| Reports | Division-wise inventory, employees, items; same sheets/headers/merged cells/totals/styles |
| Sidebar | Dashboard, Login, View Inventory, Package to Share; same back navigation |
| Packaging | Windows EXE retains original IM icon; ZIP includes EXE and DB as appropriate |
| History | Asset transfer history, logs and summary behavior, including unused-but-supported functions |

**Parity is not proven by compiling.** Side-by-side Windows screenshots, keyboard focus/selection, popup behavior, actual user flows and workbook comparisons are mandatory.

## Performance acceptance

On a synthetic fixture and on *copies* of representative customer DBs:

- Employee/item searches must use bounded SQL query counts, not one query per visible record.
- Lists should render visible rows only, or paginate. No widget allocation for all 5,000 records on every frame.
- UI should not run unbounded file IO/SQL inside paint loops.
- Benchmark cold and warm launch, inventory searches, dashboard and exports against v1.4 on the **same machine**. State measurements rather than promising a speedup.

## Release policy

A Rust CI green build can be offered as a test artifact. Publish **v2.0** only after all functions, UI/UX flows, licensing and database compatibility pass the documented matrix. No release is a substitute for testing on the real Windows desktop.
