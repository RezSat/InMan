use super::*;
use anyhow::{bail, ensure};
use rusqlite::{params, OptionalExtension, Transaction, TransactionBehavior};

fn audit(tx: &Transaction<'_>, action: &str, details: &str) -> Result<()> {
    tx.execute(
        "INSERT INTO logs(action_type,details) VALUES (?1,?2)",
        params![action,details]
    )?;
    Ok(())
}

impl Database {
    /// No account migration: create a manager only if the database has no users.
    pub fn create_first_manager(&mut self, username: &str, password: &str) -> Result<()> {
        ensure!(!username.trim().is_empty(), "Username is required");
        ensure!(password.chars().count() >= 8, "Password must be at least eight characters");
        let tx = self.conn.transaction_with_behavior(TransactionBehavior::Immediate)?;
        let count:i64=tx.query_row("SELECT COUNT(*) FROM users",[],|r|r.get(0))?;
        ensure!(count==0,"Manager account setup is already complete");
        let hash=crate::licensing::hash_password(password)?;
        tx.execute(
            "INSERT INTO users(username,password,role) VALUES (?1,?2,'manager')",
            params![username.trim(),hash]
        )?;
        tx.commit()?;
        Ok(())
    }


    pub fn add_division(&mut self, name: &str) -> Result<i64> {
        ensure!(!name.trim().is_empty(), "Division name cannot be blank");
        self.conn.execute("INSERT INTO divisions(name) VALUES (?1)", [name.trim()])?;
        Ok(self.conn.last_insert_rowid())
    }

    pub fn rename_division(&mut self, id: i64, name: &str) -> Result<()> {
        ensure!(!name.trim().is_empty(), "Division name cannot be blank");
        ensure!(
            self.conn.execute("UPDATE divisions SET name=?1 WHERE division_id=?2",
                              params![name.trim(), id])? == 1,
            "Division not found"
        );
        Ok(())
    }

    pub fn remove_division(&mut self, id: i64) -> Result<()> {
        let tx = self.conn.transaction_with_behavior(TransactionBehavior::Immediate)?;
        let employees: i64 = tx.query_row(
            "SELECT COUNT(*) FROM employees WHERE division_id=?1", [id], |r| r.get(0)
        )?;
        ensure!(employees == 0, "Division still has {employees} employee(s)");
        ensure!(
            tx.execute("DELETE FROM divisions WHERE division_id=?1", [id])? == 1,
            "Division not found"
        );
        tx.commit()?;
        Ok(())
    }

    pub fn add_employee(&mut self, id: &str, name: &str, division_id: i64) -> Result<()> {
        ensure!(!id.trim().is_empty() && !name.trim().is_empty(),
                "Employee ID and name are required");
        self.conn.execute(
            "INSERT INTO employees(emp_id,name,division_id,item_count)
             VALUES (?1,?2,?3,0)",
            params![id.trim(), name.trim(),division_id]
        )?;
        Ok(())
    }

    pub fn import_employees(&mut self, rows: &[(String, String, i64)]) -> Result<usize> {
        let tx = self.conn.transaction_with_behavior(TransactionBehavior::Immediate)?;
        for (id, name, division_id) in rows {
            ensure!(!id.trim().is_empty() && !name.trim().is_empty(),
                    "Employee ID and name are required");
            tx.execute(
                "INSERT INTO employees(emp_id,name,division_id,item_count)
                 VALUES (?1,?2,?3,0)",
                params![id.trim(),name.trim(),division_id]
            )?;
        }
        tx.commit()?;
        Ok(rows.len())
    }

    pub fn update_employee(
        &mut self, id: &str, name: &str, division_id: Option<i64>
    ) -> Result<()> {
        ensure!(!name.trim().is_empty(), "Employee name cannot be blank");
        let count = self.conn.execute(
            "UPDATE employees SET name=?1,division_id=?2 WHERE emp_id=?3",
            params![name.trim(),division_id,id]
        )?;
        ensure!(count == 1, "Employee not found");
        Ok(())
    }

    /// Commit the manager's employee-ID, name and division changes together.
    /// Failed ID updates cannot leave a partially edited employee record.
    pub fn update_employee_identity(
        &mut self, old_id: &str, new_id: &str,
        new_name: &str, new_division: Option<i64>
    ) -> Result<()> {
        ensure!(!new_id.trim().is_empty(), "Employee ID is required");
        ensure!(!new_name.trim().is_empty(), "Employee name is required");
        let id=new_id.trim();
        let tx=self.conn.transaction_with_behavior(TransactionBehavior::Immediate)?;
        tx.execute_batch("PRAGMA defer_foreign_keys = ON")?;
        ensure!(tx.query_row(
            "SELECT EXISTS(SELECT 1 FROM employees WHERE emp_id=?1)",
            [old_id],|r|r.get::<_,i64>(0)
        )?!=0,"Original employee was not found");
        if old_id!=id {
            ensure!(tx.query_row(
                "SELECT EXISTS(SELECT 1 FROM employees WHERE emp_id=?1)",
                [id],|r|r.get::<_,i64>(0)
            )?==0,"The new employee ID is already in use");
            tx.execute(
                "UPDATE employee_items SET emp_id=?1 WHERE emp_id=?2",
                params![id,old_id]
            )?;
            tx.execute(
                "UPDATE item_transfer_history SET from_emp_id=?1 WHERE from_emp_id=?2",
                params![id,old_id]
            )?;
            tx.execute(
                "UPDATE item_transfer_history SET to_emp_id=?1 WHERE to_emp_id=?2",
                params![id,old_id]
            )?;
        }
        ensure!(tx.execute(
            "UPDATE employees SET emp_id=?1,name=?2,division_id=?3 WHERE emp_id=?4",
            params![id,new_name.trim(),new_division,old_id]
        )?==1,"Employee was not updated");
        if old_id!=id {
            audit(&tx,"update_employee_id",&format!(
                "Changed employee ID from {old_id} to {id}"
            ))?;
        }
        audit(&tx,"update_employee",&format!("Updated employee {id} details"))?;
        tx.commit()?;
        Ok(())
    }

    pub fn change_employee_id(&mut self, old_id: &str, new_id: &str) -> Result<()> {
        ensure!(!new_id.trim().is_empty(), "New employee ID cannot be blank");
        let tx = self.conn.transaction_with_behavior(TransactionBehavior::Immediate)?;
        tx.execute_batch("PRAGMA defer_foreign_keys = ON")?;
        ensure!(
            tx.query_row(
                "SELECT EXISTS(SELECT 1 FROM employees WHERE emp_id=?1)",
                [old_id], |r| r.get::<_, i64>(0)
            )? != 0, "Employee not found"
        );
        tx.execute(
            "UPDATE employee_items SET emp_id=?1 WHERE emp_id=?2",
            params![new_id,old_id]
        )?;
        tx.execute(
            "UPDATE item_transfer_history SET from_emp_id=?1 WHERE from_emp_id=?2",
            params![new_id,old_id]
        )?;
        tx.execute(
            "UPDATE item_transfer_history SET to_emp_id=?1 WHERE to_emp_id=?2",
            params![new_id,old_id]
        )?;
        tx.execute(
            "UPDATE employees SET emp_id=?1 WHERE emp_id=?2",
            params![new_id,old_id]
        )?;
        audit(&tx,"update_employee_id",&format!(
            "Changed employee ID from {old_id} to {new_id}"
        ))?;
        tx.commit()?;
        Ok(())
    }

    pub fn remove_employee(&mut self, id: &str) -> Result<()> {
        let tx = self.conn.transaction_with_behavior(TransactionBehavior::Immediate)?;
        let count: i64 = tx.query_row(
            "SELECT COUNT(*) FROM employee_items WHERE emp_id=?1", [id], |r| r.get(0)
        )?;
        ensure!(count == 0, "Employee has {count} assigned item(s). Transfer or remove them first.");
        ensure!(
            tx.execute("DELETE FROM employees WHERE emp_id=?1", [id])? == 1,
            "Employee not found"
        );
        tx.commit()?;
        Ok(())
    }

    pub fn add_item(&mut self, name: &str) -> Result<i64> {
        ensure!(!name.trim().is_empty(), "Item name cannot be blank");
        self.conn.execute("INSERT INTO items(name) VALUES (?1)", [name.trim()])?;
        Ok(self.conn.last_insert_rowid())
    }

    pub fn rename_item(&mut self, item_id: i64, name: &str) -> Result<()> {
        ensure!(!name.trim().is_empty(), "Item name cannot be blank");
        ensure!(
            self.conn.execute(
                "UPDATE items SET name=?1 WHERE item_id=?2", params![name.trim(),item_id]
            )? == 1, "Item not found"
        );
        Ok(())
    }

    pub fn remove_item(&mut self, item_id: i64) -> Result<()> {
        let tx = self.conn.transaction_with_behavior(TransactionBehavior::Immediate)?;
        let count: i64 = tx.query_row(
            "SELECT COUNT(*) FROM employee_items WHERE item_id=?1",
            [item_id], |r| r.get(0)
        )?;
        ensure!(count == 0, "Item type has {count} assigned asset(s)");
        ensure!(tx.execute("DELETE FROM items WHERE item_id=?1", [item_id])? == 1,
                "Item not found");
        tx.commit()?;
        Ok(())
    }

    pub fn assign(
        &mut self, employee_id: &str, item_id: i64, unique_key: &str,
        attributes: &[(String,String)], notes: &str
    ) -> Result<i64> {
        let draft=AssignmentDraft {
            item_id, unique_key: unique_key.to_owned(),
            notes: notes.to_owned(), attributes: attributes.to_owned(),
        };
        Ok(self.assign_many(employee_id,&[draft])?[0])
    }

    /// All of a manager's staged assets are saved or none of them are.
    /// Assignment IDs, not unique_key, distinguish physical assets.
    pub fn assign_many(
        &mut self, employee_id: &str, drafts: &[AssignmentDraft]
    ) -> Result<Vec<i64>> {
        ensure!(!drafts.is_empty() && drafts.len() <= 10,
                "Select between one and ten physical assets");
        let tx = self.conn.transaction_with_behavior(TransactionBehavior::Immediate)?;
        ensure!(
            tx.query_row("SELECT EXISTS(SELECT 1 FROM employees WHERE emp_id=?1)",
                         [employee_id],|r|r.get::<_,i64>(0))?!=0,
            "Employee not found"
        );
        let mut created=Vec::with_capacity(drafts.len());
        for (index,draft) in drafts.iter().enumerate() {
            ensure!(!draft.unique_key.trim().is_empty(),
                    "Asset {} needs a unique/reference key",index+1);
            ensure!(
                tx.query_row("SELECT EXISTS(SELECT 1 FROM items WHERE item_id=?1)",
                             [draft.item_id],|r|r.get::<_,i64>(0))?!=0,
                "Asset {} uses an unknown item type",index+1
            );
            tx.execute(
                "INSERT INTO employee_items
                   (emp_id,item_id,unique_key,date_assigned,notes)
                 VALUES (?1,?2,?3,CURRENT_TIMESTAMP,?4)",
                params![employee_id,draft.item_id,draft.unique_key.trim(),draft.notes]
            )?;
            let assignment_id=tx.last_insert_rowid();
            for (name,value) in &draft.attributes {
                if name.trim().is_empty() || value.trim().is_empty() {continue;}
                tx.execute(
                    "INSERT INTO employee_item_attributes(emp_item_id,name,value)
                     VALUES (?1,?2,?3)",
                    params![assignment_id,name.trim(),value.trim()]
                )?;
            }
            created.push(assignment_id);
        }
        tx.execute(
            "UPDATE employees
                SET item_count=COALESCE(item_count,0)+?1 WHERE emp_id=?2",
            params![created.len() as i64,employee_id]
        )?;
        tx.commit()?;
        Ok(created)
    }

    pub fn upsert_attribute(&mut self, assignment_id: i64, name: &str, value: &str) -> Result<()> {
        ensure!(!name.trim().is_empty(), "Attribute name is required");
        let tx = self.conn.transaction_with_behavior(TransactionBehavior::Immediate)?;
        ensure!(
            tx.query_row(
                "SELECT EXISTS(SELECT 1 FROM employee_items WHERE id=?1)",
                [assignment_id], |r| r.get::<_,i64>(0)
            )? != 0, "Assigned item not found"
        );
        let existing: Option<i64> = tx.query_row(
            "SELECT emp_attribute_id FROM employee_item_attributes
              WHERE emp_item_id=?1 AND name=?2 LIMIT 1",
            params![assignment_id,name], |r| r.get(0)
        ).optional()?;
        if let Some(id) = existing {
            tx.execute(
                "UPDATE employee_item_attributes SET value=?1 WHERE emp_attribute_id=?2",
                params![value,id]
            )?;
        } else {
            tx.execute(
                "INSERT INTO employee_item_attributes(emp_item_id,name,value)
                 VALUES (?1,?2,?3)", params![assignment_id,name,value]
            )?;
        }
        tx.commit()?;
        Ok(())
    }

    pub fn remove_attribute(&mut self, assignment_id: i64, name: &str) -> Result<()> {
        ensure!(self.conn.execute(
            "DELETE FROM employee_item_attributes WHERE emp_item_id=?1 AND name=?2",
            params![assignment_id,name]
        )? > 0, "Attribute not found");
        Ok(())
    }

    pub fn remove_assignment(&mut self, assignment_id: i64) -> Result<()> {
        let tx = self.conn.transaction_with_behavior(TransactionBehavior::Immediate)?;
        let employee: String = tx.query_row(
            "SELECT emp_id FROM employee_items WHERE id=?1",
            [assignment_id], |r| r.get(0)
        )?;
        tx.execute(
            "DELETE FROM employee_item_attributes WHERE emp_item_id=?1", [assignment_id]
        )?;
        tx.execute("DELETE FROM employee_items WHERE id=?1", [assignment_id])?;
        tx.execute(
            "UPDATE employees SET item_count=MAX(0,COALESCE(item_count,0)-1)
              WHERE emp_id=?1", [employee.as_str()]
        )?;
        audit(&tx,"remove_item",&format!(
            "Removed asset assignment {assignment_id} from employee {employee}"
        ))?;
        tx.commit()?;
        Ok(())
    }

    pub fn transfer(
        &mut self, assignment_id: i64, new_employee_id: &str, notes: &str
    ) -> Result<i64> {
        let tx = self.conn.transaction_with_behavior(TransactionBehavior::Immediate)?;
        let (old_employee,item_id,key): (String,i64,String) = tx.query_row(
            "SELECT emp_id,item_id,COALESCE(unique_key,'')
               FROM employee_items WHERE id=?1",
            [assignment_id], |r| Ok((r.get(0)?,r.get(1)?,r.get(2)?))
        )?;
        if old_employee == new_employee_id {
            bail!("Source and destination employees are the same");
        }
        ensure!(
            tx.query_row("SELECT EXISTS(SELECT 1 FROM employees WHERE emp_id=?1)",
                         [new_employee_id],|r| r.get::<_,i64>(0))? != 0,
            "Destination employee not found"
        );
        let attrs: Vec<(String,String)> = {
            let mut stmt = tx.prepare(
                "SELECT name,value FROM employee_item_attributes WHERE emp_item_id=?1"
            )?;
            let rows = stmt.query_map([assignment_id], |r| Ok((r.get(0)?,r.get(1)?)))?;
            rows.collect::<rusqlite::Result<Vec<_>>>()?
        };
        tx.execute("DELETE FROM employee_item_attributes WHERE emp_item_id=?1",
                   [assignment_id])?;
        tx.execute("DELETE FROM employee_items WHERE id=?1", [assignment_id])?;
        tx.execute(
            "INSERT INTO employee_items
                (emp_id,item_id,unique_key,date_assigned,notes)
             VALUES (?1,?2,?3,CURRENT_TIMESTAMP,?4)",
            params![new_employee_id,item_id,key,notes]
        )?;
        let new_id = tx.last_insert_rowid();
        for (name,value) in attrs {
            tx.execute(
                "INSERT INTO employee_item_attributes(emp_item_id,name,value)
                 VALUES (?1,?2,?3)",params![new_id,name,value]
            )?;
        }
        tx.execute(
            "UPDATE employees SET item_count=MAX(0,COALESCE(item_count,0)-1)
              WHERE emp_id=?1", [old_employee.as_str()]
        )?;
        tx.execute(
            "UPDATE employees SET item_count=COALESCE(item_count,0)+1 WHERE emp_id=?1",
            [new_employee_id]
        )?;
        tx.execute(
            "INSERT INTO item_transfer_history
               (item_id,from_emp_id,to_emp_id,transfer_date,notes)
             VALUES (?1,?2,?3,date('now'),?4)",
            params![item_id,old_employee,new_employee_id,notes]
        )?;
        audit(&tx,"transfer_item",&format!(
            "Transferred item {item_id} from {old_employee} to {new_employee_id}"
        ))?;
        tx.commit()?;
        Ok(new_id)
    }
}
