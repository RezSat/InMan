use anyhow::Result;
use inman::{db::{AssignmentDraft,Database,InventoryMode},licensing,reports};
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
fn attribute_reads_scale_past_sqlite_parameter_limits() -> Result<()> {
    let db=fixture()?;
    db.db_connection().execute_batch(
        "WITH RECURSIVE seq(n) AS (
             SELECT 10 UNION ALL SELECT n+1 FROM seq WHERE n<950
         )
         INSERT INTO employee_items(id,emp_id,item_id,unique_key)
           SELECT n,'E01',1,printf('STRESS-%04d',n) FROM seq;
         INSERT INTO employee_item_attributes(emp_item_id,name,value)
           SELECT id,'Serial',unique_key FROM employee_items WHERE id>=10;"
    )?;
    let matches=db.assignments("",None,None,None)?;
    assert_eq!(matches.len(),943);
    assert!(matches.iter().find(|a|a.unique_key=="STRESS-0950")
        .is_some_and(|a|a.attributes.iter().any(|x|x.value=="STRESS-0950")));
    let filtered=db.unique_keys("STRESS-0945")?;
    assert_eq!(filtered.len(),1);
    assert_eq!(filtered[0].attributes[0].value,"STRESS-0945");
    Ok(())
}

#[test]
fn spreadsheet_import_reads_original_python_column_names() -> Result<()> {
    let mut db=fixture()?;
    let folder=tempdir()?;
    let path=folder.path().join("import.xlsx");
    let mut book=rust_xlsxwriter::Workbook::new();
    let sheet=book.add_worksheet();
    for (column,title) in ["EMP_ID","Name","Division"].iter().enumerate() {
        sheet.write_string(0,column as u16,*title)?;
    }
    for (column,value) in ["E04","New Employee","Operations"].iter().enumerate() {
        sheet.write_string(1,column as u16,*value)?;
    }
    book.save(&path)?;
    let staged=reports::read_employee_import(&path,&db.divisions("")?)?;
    assert_eq!(staged,vec![("E04".into(),"New Employee".into(),1)]);
    assert_eq!(db.import_employees(&staged)?,1);
    assert_eq!(db.employees("E04",None)?[0].division,"Operations");
    Ok(())
}

#[test]
fn package_contains_the_executable_and_database() -> Result<()> {
    use std::{fs,io::Read};
    let folder=tempdir()?;
    let executable=folder.path().join("InMan.exe");
    let database=folder.path().join("inventory.db");
    let output=folder.path().join("InMan.zip");
    fs::write(&executable,b"test executable")?;
    fs::write(&database,b"test SQLite file")?;
    reports::package_app(&output,&executable,&database)?;
    let mut archive=zip::ZipArchive::new(fs::File::open(output)?)?;
    assert_eq!(archive.len(),2);
    let mut contents=Vec::new();
    archive.by_name("inventory.db")?.read_to_end(&mut contents)?;
    assert_eq!(contents,b"test SQLite file");
    Ok(())
}

#[test]
fn ten_staged_assets_commit_together_with_attributes_and_counts() -> Result<()> {
    let mut db=fixture()?;
    let drafts=(0..10).map(|number|AssignmentDraft {
        item_id: if number%2==0 {1}else{2},
        unique_key:format!("BATCH-{number}"),
        notes:"New equipment".into(),
        attributes:vec![
            ("Serial".into(),format!("SER-{number}")),
            ("".into(),"ignored".into()),
        ],
    }).collect::<Vec<_>>();
    let ids=db.assign_many("E02",&drafts)?;
    assert_eq!(ids.len(),10);
    assert_eq!(db.employees("E02",None)?[0].item_count,10);
    let items=db.assignments("",Some("E02"),None,None)?;
    assert_eq!(items.len(),10);
    assert!(items.iter().all(|a|a.attributes.len()==1));
    assert!(items.iter().any(|a|a.unique_key=="BATCH-9"));
    let mut invalid=drafts.clone();
    invalid[9].item_id=999_999;
    assert!(db.assign_many("E02",&invalid).is_err());
    assert_eq!(db.assignments("",Some("E02"),None,None)?.len(),10);
    assert_eq!(db.employees("E02",None)?[0].item_count,10);
    db.verify_integrity()
}

#[test]
fn employee_details_and_id_change_are_one_atomic_operation() -> Result<()> {
    let mut db=fixture()?;
    let before=db.employees("E01",None)?[0].clone();
    assert!(db.update_employee_identity(
        "E01","E02","New name",Some(2)
    ).is_err());
    assert_eq!(db.employees("E01",None)?[0],before);
    db.update_employee_identity("E01","E91","Updated Alice",Some(2))?;
    let updated=&db.employees("E91",None)?[0];
    assert_eq!(updated.name,"Updated Alice");
    assert_eq!(updated.division,"Finance");
    assert_eq!(db.assignments("",Some("E91"),None,None)?.len(),2);
    assert!(db.employees("E01",None)?.is_empty());
    db.verify_integrity()
}

#[test]
fn duplicate_reference_keys_do_not_cause_the_wrong_asset_to_move() -> Result<()> {
    let mut db=fixture()?;
    db.db_connection().execute_batch(
        "CREATE TABLE archived_employee_items(
             id INTEGER PRIMARY KEY, emp_id VARCHAR,
             unique_key VARCHAR, archive_reason VARCHAR
         );
         INSERT INTO archived_employee_items VALUES(
             991,NULL,'LEGACY-KEY','Historical orphan archived'
         );"
    )?;
    let duplicate_id=db.assign("E01",1,"LT-001",&[(
        "Serial".into(),"SECOND-UNIT".into()
    )],"")?;
    assert_eq!(db.unique_keys("LT-001")?.len(),2);
    let moved_id=db.transfer(duplicate_id,"E02","Move only the second unit")?;
    let old=db.assignments("",Some("E01"),None,None)?;
    assert!(old.iter().any(|a|a.id==1&&a.unique_key=="LT-001"));
    let moved=db.assignments("",Some("E02"),None,None)?;
    assert_eq!(moved[0].id,moved_id);
    assert_eq!(moved[0].attributes[0].value,"SECOND-UNIT");
    let archived: i64=db.db_connection().query_row(
        "SELECT COUNT(*) FROM archived_employee_items WHERE id=991",[],|r|r.get(0)
    )?;
    assert_eq!(archived,1);
    db.verify_integrity()
}

#[test]
fn division_inventory_excel_handles_one_asset_without_a_single_cell_merge() -> Result<()> {
    let mut db=fixture()?;
    db.db_connection().execute_batch(
        "DELETE FROM employee_item_attributes;
         DELETE FROM employee_items;
         UPDATE employees SET item_count=0;"
    )?;
    db.assign("E01",1,"ONLY-ASSET",&[], "")?;
    let temp=tempdir()?;
    let file=temp.path().join("inventory.xlsx");
    reports::export_inventory(&db,&file)?;
    let mut book=open_workbook_auto(&file)?;
    assert_eq!(book.sheet_names()[0],"Sheet");
    let sheet=book.worksheet_range_at(0).unwrap()?;
    assert_eq!(sheet.get((0,0)).unwrap().to_string(),"Division");
    assert_eq!(sheet.get((1,3)).unwrap().to_string(),"Laptop");
    assert_eq!(sheet.get((1,4)).unwrap().to_string(),"ONLY-ASSET");
    Ok(())
}

#[test]
fn backup_is_integrity_checked_and_preserves_optional_archives() -> Result<()> {
    let db=fixture()?;
    db.db_connection().execute_batch(
        "CREATE TABLE archived_employee_items (
             id INTEGER PRIMARY KEY, emp_id TEXT,
             archive_reason TEXT NOT NULL, archived_at_utc TEXT NOT NULL
         );
         INSERT INTO archived_employee_items
           VALUES (101,NULL,'missing employee','2026-08-02T10:00:00Z');"
    )?;
    let temp=tempdir()?;
    let backup=temp.path().join("inventory-copy.db");
    db.backup_to(&backup)?;
    assert!(backup.exists());
    let read_only=Database::open_read_only(&backup)?;
    assert_eq!(read_only.foreign_key_violation_count()?,0);
    assert_eq!(read_only.dashboard_counts()?,(3,2,2));
    let old:i64=read_only.db_connection().query_row(
        "SELECT COUNT(*) FROM archived_employee_items",[],|r|r.get(0)
    )?;
    assert_eq!(old,1);
    assert!(db.backup_to(&backup).is_err(),"Never overwrite an existing backup");
    Ok(())
}

#[test]
fn three_excel_exports_have_the_expected_columns() -> Result<()> {
    let db=fixture()?;
    let dir=tempdir()?;
    for (file,expected) in [
        ("employees.xlsx","Employee ID"),
        ("items.xlsx","Name"),
        ("inventory.xlsx","Division"),
    ] {
        let path=dir.path().join(file);
        match file {
            "employees.xlsx"=>reports::export_employees(&db,&path)?,
            "items.xlsx"=>reports::export_items(&db,&path)?,
            "inventory.xlsx"=>reports::export_inventory(&db,&path)?,
            _=>unreachable!(),
        }
        let mut book=open_workbook_auto(&path)?;
        let sheet=book.worksheet_range_at(0).unwrap()?;
        assert_eq!(sheet.get((0,0)).unwrap().to_string(),expected);
    }
    Ok(())
}
