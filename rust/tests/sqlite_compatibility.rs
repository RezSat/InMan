use anyhow::Result;
use inman::{db::{Database,InventoryMode},licensing,reports};
use rusqlite::params;
use sha2::{Digest,Sha256};
use tempfile::tempdir;
use calamine::{open_workbook_auto,Reader};

fn fixture() -> Result<Database> {
    let db=Database::memory()?;
    db.db_connection().execute_batch(
        "INSERT INTO divisions(division_id,name) VALUES (1,'Operations'),(2,'Finance');
         INSERT INTO employees(emp_id,name,division_id,item_count)
           VALUES ('E01','Alice',1,2),('E02','Bob',1,0),('E03','Cara',2,0);
         INSERT INTO items(item_id,name) VALUES (1,'Laptop'),(2,'Monitor');
         INSERT INTO employee_items(id,emp_id,item_id,unique_key,date_assigned)
           VALUES (1,'E01',1,'LT-001',CURRENT_TIMESTAMP),
                  (2,'E01',1,'LT-002',CURRENT_TIMESTAMP),
                  (3,NULL,2,'ORPHAN',CURRENT_TIMESTAMP);
         INSERT INTO employee_item_attributes(emp_item_id,name,value)
           VALUES (1,'RAM','16GB'),(2,'RAM','32GB');"
    )?;
    Ok(db)
}

#[test]
fn schema_is_unchanged_and_archived_records_are_not_touched() -> Result<()> {
    let temp=tempdir()?;
    let path=temp.path().join("inventory.db");
    let created=Database::open(&path)?;
    created.db_connection().execute_batch(
        "CREATE TABLE archived_employee_items (old_id INTEGER PRIMARY KEY, notes TEXT);
         INSERT INTO archived_employee_items VALUES (42,'old mapping');"
    )?;
    let schema_before=created.schema_version()?;
    drop(created);
    let reopened=Database::open(&path)?;
    assert_eq!(reopened.schema_version()?,schema_before);
    let id:i64=reopened.db_connection().query_row(
        "SELECT old_id FROM archived_employee_items",[],|r|r.get(0)
    )?;
    assert_eq!(id,42);
    reopened.verify_integrity()
}

#[test]
fn searches_ignore_orphans_and_preserve_asset_keys() -> Result<()> {
    let db=fixture()?;
    assert_eq!(InventoryMode::ALL.len(),5);
    assert_eq!(db.employees("Alice",None)?.len(),1);
    assert_eq!(db.items("Lap")?.len(),1);
    assert_eq!(db.divisions("Oper")?[0].item_count,2);
    assert_eq!(db.assignments("",None,None,None)?.len(),2);
    assert_eq!(db.assignments("Laptop",None,Some("RAM"),Some("32"))?[0].unique_key,"LT-002");
    assert_eq!(db.unique_keys("LT-001")?.len(),1);
    assert!(db.unique_keys("ORPHAN")?.is_empty());
    assert_eq!(db.dashboard_counts()?,(3,2,2));
    Ok(())
}

#[test]
fn transfers_one_physical_asset_and_preserves_attributes() -> Result<()> {
    let mut db=fixture()?;
    let new_id=db.transfer(1,"E02","Transferred")?;
    let assets=db.assignments("",None,None,None)?;
    assert!(assets.iter().any(|a|a.unique_key=="LT-002"&&a.employee_id=="E01"));
    let moved=assets.iter().find(|a|a.id==new_id).unwrap();
    assert_eq!(moved.employee_id,"E02");
    assert_eq!(moved.unique_key,"LT-001");
    assert_eq!(moved.attributes[0].value,"16GB");
    assert_eq!(db.transfer_history("",20)?.len(),1);
    assert_eq!(db.employees("E02",None)?[0].item_count,1);
    assert!(db.transfer(new_id,"UNKNOWN","bad").is_err());
    assert_eq!(db.assignments("",None,None,None)?.len(),2);
    db.verify_integrity()
}

#[test]
fn deleting_employee_with_assets_fails_without_data_loss() -> Result<()> {
    let mut db=fixture()?;
    assert!(db.remove_employee("E01").is_err());
    assert!(db.employees("E01",None)?.len()==1);
    db.remove_employee("E03")?;
    assert!(db.employees("E03",None)?.is_empty());
    assert_eq!(db.assignments("",None,None,None)?.len(),2);
    Ok(())
}

#[test]
fn employee_id_changes_keep_assignments_and_transfer_history() -> Result<()> {
    let mut db=fixture()?;
    db.transfer(1,"E02","Moved")?;
    db.change_employee_id("E02","E99")?;
    assert_eq!(db.employees("E99",None)?.len(),1);
    assert_eq!(db.assignments("",Some("E99"),None,None)?.len(),1);
    assert_eq!(db.transfer_history("",10)?[0].to_employee,"E99");
    db.verify_integrity()
}

#[test]
fn assignment_and_bulk_import_are_atomic() -> Result<()> {
    let mut db=fixture()?;
    assert!(db.assign("MISSING",1,"BAD",&[], "").is_err());
    assert_eq!(db.assignments("",None,None,None)?.len(),2);
    let id=db.assign("E02",2,"MON-100",&[("Serial".into(),"S-100".into())],"")?;
    assert_eq!(db.assignments("",Some("E02"),None,None)?[0].attributes[0].value,"S-100");
    db.remove_assignment(id)?;
    assert!(db.assignments("",Some("E02"),None,None)?.is_empty());
    let rows=[
        ("E04".to_string(),"Dan".to_string(),1),
        ("E01".to_string(),"Duplicate".to_string(),1),
    ];
    assert!(db.import_employees(&rows).is_err());
    assert!(db.employees("E04",None)?.is_empty());
    db.verify_integrity()
}

#[test]
fn legacy_database_without_manager_can_create_one_securely() -> Result<()> {
    let mut db=fixture()?;
    assert_eq!(db.manager_count()?, 0);
    assert!(db.create_first_manager("administrator", "short").is_err());
    assert_eq!(db.manager_count()?, 0);
    db.create_first_manager("administrator", "secure-password-123")?;
    assert_eq!(db.manager_count()?, 1);
    assert!(db.authenticate("administrator", "secure-password-123")?);
    assert!(!db.authenticate("administrator", "incorrect")?);
    assert!(db.create_first_manager("another", "another-strong-password").is_err());
    db.verify_integrity()
}

#[test]
fn original_python_salted_manager_password_is_compatible() -> Result<()> {
    let db=fixture()?;
    let salt=[0x44_u8;16];
    let mut hasher=Sha256::new();
    hasher.update(salt);
    hasher.update(b"correct");
    let digest=format!("{}:{}",hex::encode(salt),hex::encode(hasher.finalize()));
    db.db_connection().execute(
        "INSERT INTO users(username,password,role) VALUES (?1,?2,'manager')",
        params!["admin",digest]
    )?;
    assert!(db.authenticate("admin","correct")?);
    assert!(!db.authenticate("admin","wrong")?);
    assert!(!db.authenticate("missing","correct")?);
    assert_eq!(licensing::hashed_product_key("abc"),
               licensing::hashed_product_key("ABC"));
    Ok(())
}

#[test]
fn three_excel_exports_have_the_expected_columns() -> Result<()> {
    let db=fixture()?;
    let dir=tempdir()?;
    for (file,export,expected) in [
        ("employees.xlsx",reports::export_employees as fn(&Database,&std::path::Path)->Result<()>,
         "Employee ID"),
        ("items.xlsx",reports::export_items as fn(&Database,&std::path::Path)->Result<()>,
         "Name"),
        ("inventory.xlsx",reports::export_inventory as fn(&Database,&std::path::Path)->Result<()>,
         "Division"),
    ] {
        let path=dir.path().join(file);
        export(&db,&path)?;
        let mut book=open_workbook_auto(&path)?;
        let sheet=book.worksheet_range_at(0).unwrap()?;
        assert_eq!(sheet.get((0,0)).unwrap().to_string(),expected);
    }
    Ok(())
}
