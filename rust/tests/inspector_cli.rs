use anyhow::Result;
use inman::db::Database;
use std::process::Command;
use tempfile::tempdir;

#[test]
fn windows_release_inspector_reads_database_without_changing_it() -> Result<()> {
    let folder=tempdir()?;
    let file=folder.path().join("inventory.db");
    {
        let db=Database::open(&file)?;
        db.db_connection().execute_batch(
            "INSERT INTO divisions(name) VALUES ('Engineering');
             INSERT INTO employees(emp_id,name,division_id,item_count)
             VALUES ('A100','Example',1,0);
             INSERT INTO items(name) VALUES ('Laptop');"
        )?;
    }
    let before=std::fs::read(&file)?;
    let process=Command::new(env!("CARGO_BIN_EXE_inman-inspect"))
        .arg(&file).output()?;
    assert!(process.status.success(),
        "Inspector failed: {}",String::from_utf8_lossy(&process.stderr));
    let stdout=String::from_utf8(process.stdout)?;
    assert!(stdout.contains("SQLite integrity: OK"));
    assert!(stdout.contains("Employees: 1, Item types: 1, Divisions: 1"));
    assert!(stdout.contains("Assigned asset rows: 0; valid joined rows: 0"));
    assert_eq!(std::fs::read(&file)?,before,"Read-only tool modified the database");
    Ok(())
}
