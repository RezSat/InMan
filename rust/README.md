# InMan 2.0 — Rust development build

Native Windows desktop rewrite of InMan using Rust, egui, and SQLite.

**Current version: 2.0.0-rc.1.** This is an unsigned release candidate, not a production replacement for Python v1.4. The initial Rust rewrite was merged into `main`; follow-on parity work is in [`rust-v2-completion`](https://github.com/RezSat/InMan/tree/rust-v2-completion). The last stable binary remains the Python v1.4 release. The old code is preserved at [`old/v1.4`](https://github.com/RezSat/InMan/tree/old/v1.4).

## Current implementation

- Original product-key SHA-256 verification and Windows `HKCU\Software\InMan` registry compatibility.
- Existing Python salted-SHA-256 manager passwords; first-run manager setup for databases without users.
- Native egui dashboard, sidebar, inventory search, manager tools, forms, and confirmation dialogs.
- All five inventory search modes: Employees, Items, Divisions, Unique Key, Employee Items.
- Item types, divisions, employees, up to 10 staged physical assignments with independent attributes, single/bulk removals, multi-select transfers, and audit history.
- Spreadsheet employee import; division-wise inventory, employee, and item-type Excel exports; results export.
- Consistent, integrity-checked SQLite backups and ZIP packaging; original pink/cream Windows IM executable icon.
- SQLite queries with bounded joins/attribute batches and transactions that roll back on failure. Large scrollable result lists use row virtualization.

## Run on Windows

1. Back up `inventory.db` and keep a copy completely outside the test folder.
2. Put the Rust `InMan.exe` in a separate folder alongside **a copy** of `inventory.db`.
3. Start `InMan.exe` from that folder. It uses the process working directory to resolve `inventory.db`, just like the existing Python version.
4. Existing product-key registry activation should be recognized. For databases with no manager accounts, the login screen now asks for an initial username and password (at least eight characters).

Do not point this beta at your only copy of a live inventory database. The executable is **not digitally signed**, so Microsoft Defender SmartScreen can flag it as an unfamiliar download.

## Build from source

Install Rust stable (Rust 1.95 or newer) and the Visual Studio C++ build tools on Windows.

```powershell
git clone --branch rust-v2-completion https://github.com/RezSat/InMan.git
cd InMan\rust
cargo fmt --all
cargo test --all-targets
cargo clippy --all-targets -- -D warnings
cargo run --release
```

To make a portable Windows executable:

```powershell
cargo build --release --bins
```

The GUI binary is in `rust/target/release/inman.exe`. The read-only inspection utility is `rust/target/release/inman-inspect.exe` and can be run as `inman-inspect.exe "C:\\path\\to\\inventory.db"`. It prints counts, integrity status, and SQL timings without exposing employee names. The GUI icon comes from `assets/CustomTkinter_icon_Windows.ico`.

## Code layout

| Module | Responsibility |
| --- | --- |
| `src/db.rs` | Legacy SQLite connection, models, and schema initialization |
| `src/db/queries.rs` | Search, dashboard, inventory, audit and manager account queries |
| `src/db/writes.rs` | Transactional employee, item, division and assignment writes |
| `src/licensing.rs` | Product-key compatibility and manager password hashing |
| `src/reports.rs` | Excel import/export and ZIP packaging |
| `src/ui.rs` | Native desktop shell, sidebar, search and navigation |
| `src/ui/tools.rs` | Manager screens and operations |
| `tests/sqlite_compatibility.rs` | Synthetic fixtures and integrity/compatibility tests |

CI uses `.github/workflows/rust-ci.yml` to run Windows and Linux tests, Clippy, and an optimized Windows build. An RC prerelease is published only after both Windows and Linux CI jobs succeed.

## Compatibility and performance status

This Rust implementation deliberately preserves database table names, key/attribute references and the licensed activation path. The old Python source is still the authoritative interface baseline.

**Not yet signed off for v2.0 final:**

- Native egui controls are not a pixel-perfect clone of CustomTkinter. Visual appearance, hover behavior, popups, keyboard focus and every tool flow still need a side-by-side Windows test.
- The Rust assignment form now stages up to ten assets in one transaction, and the transfer form supports multiple selected assignment IDs. Modal dialogs and focus behavior still require visual comparison.
- The original formatted XLSX reports need workbook-by-workbook visual comparison on representative data, beyond structural tests.
- End-to-end desktop and real-machine startup/search/render/export benchmarks have not been performed. The headless `inman-inspect` utility measures SQLite queries only.
- Code signing is not configured for the Windows release.

See [`docs/rust-parity.md`](../docs/rust-parity.md) for the full parity matrix. **Do not merge the Rust branch into production `main` or tag `v2.0` final until those remaining checks pass.**

## Performance verification

Benchmark both executables using separate copies of the same SQLite database on the same Windows computer. Record cold launch, dashboard load, all-employee search, Employee Items search, scrolling with thousands of items and Excel exports. Compare correctness and output counts before comparing durations. The database layer is optimized for bounded query counts, but a Rust rewrite alone is not proof of a specific speedup.
