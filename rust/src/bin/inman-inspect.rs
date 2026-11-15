//! Read-only health and timing check for an existing InMan SQLite database.
//! Never activates a license, creates tables, or writes to customer data.
use anyhow::{Context,Result,ensure};
use inman::db::Database;
use std::{env,path::PathBuf,time::Instant};

fn main() -> Result<()> {
    let path=env::args_os().nth(1).map(PathBuf::from)
        .context("Usage: inman-inspect <path-to-inventory.db>")?;
    let db=Database::open_read_only(&path)
        .with_context(||format!("Opening {} in read-only mode",path.display()))?;
    let violations=db.foreign_key_violation_count()?;
    ensure!(violations==0,"Database has {violations} foreign-key violation(s)");
    let (employee_count,item_count,division_count)=db.dashboard_counts()?;
    let total_assignments:i64=db.db_connection().query_row(
        "SELECT COUNT(*) FROM employee_items",[],|r|r.get(0)
    )?;
    let archived:i64=db.db_connection().query_row(
        "SELECT COUNT(*) FROM sqlite_master
          WHERE type='table' AND name='archived_employee_items'",[],
        |r|r.get(0)
    )?;
    let archived_count=if archived==1 {
        db.db_connection().query_row(
            "SELECT COUNT(*) FROM archived_employee_items",[],|r|r.get::<_,i64>(0)
        )?
    }else{0};
    let duplicated_keys:i64=db.db_connection().query_row(
        "SELECT COALESCE(SUM(k.count-1),0)
           FROM (SELECT COUNT(*) AS count FROM employee_items
                  WHERE unique_key IS NOT NULL AND unique_key<>''
                  GROUP BY unique_key HAVING COUNT(*)>1) k",
        [],|r|r.get(0)
    )?;

    let start=Instant::now();
    let employee_rows=db.employees("",None)?;
    let employee_elapsed=start.elapsed();
    let start=Instant::now();
    let matched_assets=db.assignments("",None,None,None)?;
    let asset_elapsed=start.elapsed();

    println!("InMan SQLite inspection (read-only)");
    println!("SQLite integrity: OK; foreign key violations: {violations}");
    println!("Employees: {employee_count}, Item types: {item_count}, Divisions: {division_count}");
    println!("Assigned asset rows: {total_assignments}; valid joined rows: {}",matched_assets.len());
    println!("Optional archived rows: {archived_count}; duplicate extra key occurrences: {duplicated_keys}");
    println!("Employees read: {} rows in {:.3} ms",
             employee_rows.len(),employee_elapsed.as_secs_f64()*1000.0);
    println!("Assets read: {} rows in {:.3} ms",
             matched_assets.len(),asset_elapsed.as_secs_f64()*1000.0);
    println!("These figures measure database reads only, not UI/rendering or startup time.");
    Ok(())
}
