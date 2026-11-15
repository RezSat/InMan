use anyhow::{Context, Result};
use rusqlite::Connection;
use std::{path::Path, time::Duration};

mod queries;
mod writes;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Division {
    pub id: i64,
    pub name: String,
    pub employee_count: i64,
    pub item_count: i64,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Employee {
    pub id: String,
    pub name: String,
    pub division_id: Option<i64>,
    pub division: String,
    pub item_count: i64,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Item {
    pub id: i64,
    pub name: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Attribute {
    pub id: i64,
    pub assignment_id: i64,
    pub name: String,
    pub value: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Assignment {
    pub id: i64,
    pub employee_id: String,
    pub employee_name: String,
    pub item_id: i64,
    pub item_name: String,
    pub unique_key: String,
    pub date_assigned: String,
    pub notes: String,
    pub attributes: Vec<Attribute>,
}

/// One physical asset in an atomic multi-item employee assignment.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct AssignmentDraft {
    pub item_id: i64,
    pub unique_key: String,
    pub notes: String,
    pub attributes: Vec<(String, String)>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Transfer {
    pub id: i64,
    pub item_id: i64,
    pub item_name: String,
    pub from_employee: String,
    pub to_employee: String,
    pub date: String,
    pub notes: String,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct AuditLog {
    pub id: i64,
    pub action: String,
    pub details: String,
    pub timestamp: String,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum InventoryMode {
    Employees,
    Items,
    Divisions,
    UniqueKey,
    EmployeeItems,
}

impl InventoryMode {
    pub const ALL: [Self; 5] = [
        Self::Employees, Self::Items, Self::Divisions, Self::UniqueKey, Self::EmployeeItems
    ];

    pub fn label(self) -> &'static str {
        match self {
            Self::Employees => "Employees",
            Self::Items => "Items",
            Self::Divisions => "Divisions",
            Self::UniqueKey => "Unique Key",
            Self::EmployeeItems => "Employee Items",
        }
    }
}

pub struct Database {
    conn: Connection,
}

impl Database {
    /// Opens the database in the process working directory, as in Python v1.4.
    pub fn open(path: impl AsRef<Path>) -> Result<Self> {
        let conn = Connection::open(path.as_ref())
            .with_context(|| format!("Opening {}", path.as_ref().display()))?;
        conn.busy_timeout(Duration::from_secs(5))?;
        conn.execute_batch("PRAGMA foreign_keys = ON; PRAGMA temp_store = MEMORY;")?;
        let db = Self { conn };
        db.initialize_if_empty()?;
        Ok(db)
    }

    pub fn memory() -> Result<Self> {
        let conn = Connection::open_in_memory()?;
        conn.execute_batch("PRAGMA foreign_keys = ON;")?;
        let db = Self { conn };
        db.initialize_if_empty()?;
        Ok(db)
    }

    fn initialize_if_empty(&self) -> Result<()> {
        let count: i64 = self.conn.query_row(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'",
            [], |row| row.get(0)
        )?;
        if count != 0 {
            // Never rebuild, migrate or touch an existing customer's SQLite data.
            return Ok(());
        }
        self.conn.execute_batch(
            "CREATE TABLE divisions (
                division_id INTEGER PRIMARY KEY, name VARCHAR NOT NULL UNIQUE
            );
            CREATE TABLE employees (
                emp_id VARCHAR PRIMARY KEY, name VARCHAR NOT NULL,
                division_id INTEGER REFERENCES divisions(division_id),
                item_count INTEGER DEFAULT 0,
                date_joined DATETIME DEFAULT (CURRENT_TIMESTAMP)
            );
            CREATE TABLE items (
                item_id INTEGER PRIMARY KEY, name VARCHAR NOT NULL UNIQUE,
                last_assigned DATETIME DEFAULT (CURRENT_TIMESTAMP)
            );
            CREATE TABLE employee_items (
                id INTEGER PRIMARY KEY, emp_id VARCHAR REFERENCES employees(emp_id),
                item_id INTEGER REFERENCES items(item_id), unique_key VARCHAR,
                date_assigned DATETIME, notes TEXT
            );
            CREATE TABLE employee_item_attributes (
                emp_attribute_id INTEGER PRIMARY KEY,
                emp_item_id INTEGER REFERENCES employee_items(id),
                name VARCHAR NOT NULL, value VARCHAR NOT NULL
            );
            CREATE TABLE users (
                user_id INTEGER PRIMARY KEY, username VARCHAR NOT NULL UNIQUE,
                password VARCHAR NOT NULL, role VARCHAR
            );
            CREATE TABLE logs (
                log_id INTEGER PRIMARY KEY, action_type VARCHAR NOT NULL,
                details TEXT, timestamp DATETIME DEFAULT (CURRENT_TIMESTAMP),
                user_id INTEGER REFERENCES users(user_id)
            );
            CREATE TABLE item_transfer_history (
                transfer_id INTEGER PRIMARY KEY,
                item_id INTEGER REFERENCES items(item_id),
                from_emp_id VARCHAR REFERENCES employees(emp_id),
                to_emp_id VARCHAR REFERENCES employees(emp_id),
                transfer_date DATE DEFAULT (CURRENT_TIMESTAMP), notes TEXT
            );"
        )?;
        Ok(())
    }

    pub fn verify_integrity(&self) -> Result<()> {
        let result: String = self.conn.query_row("PRAGMA integrity_check", [], |r| r.get(0))?;
        anyhow::ensure!(result == "ok", "SQLite integrity check failed: {result}");
        Ok(())
    }

    pub fn schema_version(&self) -> Result<i64> {
        Ok(self.conn.query_row("PRAGMA schema_version", [], |r| r.get(0))?)
    }

    pub fn db_connection(&self) -> &Connection { &self.conn }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn legacy_tables_are_created_only_once() -> Result<()> {
        let db = Database::memory()?;
        db.verify_integrity()?;
        let before = db.schema_version()?;
        db.initialize_if_empty()?;
        assert_eq!(before, db.schema_version()?);
        Ok(())
    }

    #[test]
    fn inventory_modes_keep_the_original_names() {
        assert_eq!(InventoryMode::ALL.map(|m| m.label()), [
            "Employees", "Items", "Divisions", "Unique Key", "Employee Items"
        ]);
    }
}
