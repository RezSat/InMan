use super::*;
use rusqlite::{params, params_from_iter};
use std::collections::HashMap;

impl Database {
    pub fn dashboard_counts(&self) -> Result<(i64, i64, i64)> {
        Ok(self.conn.query_row(
            "SELECT (SELECT COUNT(*) FROM employees),
                    (SELECT COUNT(*) FROM items),
                    (SELECT COUNT(*) FROM divisions)",
            [], |r| Ok((r.get(0)?, r.get(1)?, r.get(2)?))
        )?)
    }

    pub fn divisions(&self, search: &str) -> Result<Vec<Division>> {
        let mut statement = self.conn.prepare_cached(
            "WITH ec AS (
                SELECT division_id, COUNT(*) AS count FROM employees GROUP BY division_id
             ), ac AS (
                SELECT e.division_id, COUNT(*) AS count
                  FROM employee_items ei JOIN employees e ON e.emp_id=ei.emp_id
                 GROUP BY e.division_id
             )
             SELECT d.division_id, d.name,
                    COALESCE(ec.count,0), COALESCE(ac.count,0)
               FROM divisions d
               LEFT JOIN ec ON ec.division_id=d.division_id
               LEFT JOIN ac ON ac.division_id=d.division_id
              WHERE d.name LIKE '%' || ?1 || '%'
              ORDER BY d.division_id"
        )?;
        let iter = statement.query_map([search], |r| Ok(Division {
            id: r.get(0)?, name: r.get(1)?,
            employee_count: r.get(2)?, item_count: r.get(3)?,
        }))?;
        Ok(iter.collect::<rusqlite::Result<Vec<_>>>()?)
    }

    pub fn division_item_types(&self, division_id: i64) -> Result<Vec<(String, i64)>> {
        let mut statement = self.conn.prepare_cached(
            "SELECT i.name, COUNT(*) FROM employee_items ei
               JOIN employees e ON e.emp_id=ei.emp_id
               JOIN items i ON i.item_id=ei.item_id
              WHERE e.division_id=?1 GROUP BY i.item_id, i.name ORDER BY i.name"
        )?;
        let rows = statement.query_map([division_id], |r| Ok((r.get(0)?, r.get(1)?)))?;
        Ok(rows.collect::<rusqlite::Result<Vec<_>>>()?)
    }

    pub fn employees(&self, search: &str, division_id: Option<i64>) -> Result<Vec<Employee>> {
        let mut statement = self.conn.prepare_cached(
            "SELECT e.emp_id,e.name,e.division_id,
                    COALESCE(d.name,'Unassigned'),COALESCE(e.item_count,0)
               FROM employees e LEFT JOIN divisions d ON d.division_id=e.division_id
              WHERE (e.name LIKE '%'||?1||'%' OR e.emp_id LIKE '%'||?1||'%')
                AND (?2 IS NULL OR e.division_id=?2)
              ORDER BY e.emp_id"
        )?;
        let rows = statement.query_map(params![search, division_id], |r| Ok(Employee {
            id: r.get(0)?, name: r.get(1)?, division_id: r.get(2)?,
            division: r.get(3)?, item_count: r.get(4)?,
        }))?;
        Ok(rows.collect::<rusqlite::Result<Vec<_>>>()?)
    }

    pub fn items(&self, search: &str) -> Result<Vec<Item>> {
        let mut statement = self.conn.prepare_cached(
            "SELECT item_id,name FROM items WHERE name LIKE '%'||?1||'%' ORDER BY item_id"
        )?;
        let rows = statement.query_map([search], |r| Ok(Item {
            id: r.get(0)?, name: r.get(1)?
        }))?;
        Ok(rows.collect::<rusqlite::Result<Vec<_>>>()?)
    }

    /// A bounded read: assignments and custom attributes require only two SQL queries.
    pub fn assignments(
        &self, item_query: &str, employee_id: Option<&str>,
        attr_name: Option<&str>, attr_value: Option<&str>
    ) -> Result<Vec<Assignment>> {
        let mut statement = self.conn.prepare_cached(
            "SELECT ei.id, e.emp_id, e.name, i.item_id, i.name,
                    COALESCE(ei.unique_key,''),COALESCE(ei.date_assigned,''),
                    COALESCE(ei.notes,'')
               FROM employee_items ei
               JOIN employees e ON e.emp_id=ei.emp_id
               JOIN items i ON i.item_id=ei.item_id
              WHERE i.name LIKE '%'||?1||'%'
                AND (?2 IS NULL OR ei.emp_id=?2)
                AND ((?3 IS NULL AND ?4 IS NULL) OR EXISTS (
                    SELECT 1 FROM employee_item_attributes a
                     WHERE a.emp_item_id=ei.id
                       AND (?3 IS NULL OR a.name=?3)
                       AND (?4 IS NULL OR a.value LIKE '%'||?4||'%')
                ))
              ORDER BY ei.id"
        )?;
        let rows = statement.query_map(
            params![item_query, employee_id, attr_name.filter(|s| !s.is_empty()),
                    attr_value.filter(|s| !s.is_empty())],
            |r| Ok(Assignment {
                id: r.get(0)?, employee_id: r.get(1)?, employee_name: r.get(2)?,
                item_id: r.get(3)?, item_name: r.get(4)?, unique_key: r.get(5)?,
                date_assigned: r.get(6)?, notes: r.get(7)?, attributes: Vec::new()
            })
        )?;
        let mut records = rows.collect::<rusqlite::Result<Vec<_>>>()?;
        drop(statement);
        if records.is_empty() { return Ok(records); }

        // Group related rows in memory instead of querying every asset separately.
        let placeholders = vec!["?"; records.len()].join(",");
        let sql = format!(
            "SELECT emp_attribute_id,emp_item_id,name,value
               FROM employee_item_attributes WHERE emp_item_id IN ({placeholders})
              ORDER BY emp_attribute_id"
        );
        let mut by_id: HashMap<i64, Vec<Attribute>> = HashMap::new();
        let mut attrs = self.conn.prepare(&sql)?;
        let entries = attrs.query_map(
            params_from_iter(records.iter().map(|a| a.id)),
            |r| Ok(Attribute {
                id: r.get(0)?, assignment_id: r.get(1)?,
                name: r.get(2)?, value: r.get(3)?
            })
        )?;
        for entry in entries {
            let attribute = entry?;
            by_id.entry(attribute.assignment_id).or_default().push(attribute);
        }
        for assignment in &mut records {
            assignment.attributes = by_id.remove(&assignment.id).unwrap_or_default();
        }
        Ok(records)
    }

    pub fn unique_keys(&self, query: &str) -> Result<Vec<Assignment>> {
        // Search all item types; match keys once the two-query loader has returned.
        let all = self.assignments("", None, None, None)?;
        let needle = query.to_lowercase();
        Ok(all.into_iter().filter(|a| a.unique_key.to_lowercase().contains(&needle)).collect())
    }

    pub fn logs(&self, query: &str, limit: usize) -> Result<Vec<AuditLog>> {
        let mut stmt = self.conn.prepare_cached(
            "SELECT log_id,action_type,COALESCE(details,''),COALESCE(timestamp,'')
               FROM logs WHERE details LIKE '%'||?1||'%'
                  OR action_type LIKE '%'||?1||'%'
              ORDER BY timestamp DESC, log_id DESC LIMIT ?2"
        )?;
        let rows = stmt.query_map(params![query, limit as i64], |r| Ok(AuditLog {
            id: r.get(0)?, action: r.get(1)?, details: r.get(2)?,
            timestamp: r.get(3)?
        }))?;
        Ok(rows.collect::<rusqlite::Result<Vec<_>>>()?)
    }

    pub fn transfer_history(&self, search: &str, limit: usize) -> Result<Vec<Transfer>> {
        let mut stmt = self.conn.prepare_cached(
            "SELECT h.transfer_id, COALESCE(h.item_id,0),COALESCE(i.name,''),
                    COALESCE(h.from_emp_id,''),COALESCE(h.to_emp_id,''),
                    COALESCE(h.transfer_date,''),COALESCE(h.notes,'')
               FROM item_transfer_history h LEFT JOIN items i ON i.item_id=h.item_id
              WHERE COALESCE(i.name,'') LIKE '%'||?1||'%'
                 OR COALESCE(h.from_emp_id,'') LIKE '%'||?1||'%'
                 OR COALESCE(h.to_emp_id,'') LIKE '%'||?1||'%'
                 OR COALESCE(h.notes,'') LIKE '%'||?1||'%'
              ORDER BY h.transfer_id DESC LIMIT ?2"
        )?;
        let rows = stmt.query_map(params![search,limit as i64], |r| Ok(Transfer {
            id:r.get(0)?,item_id:r.get(1)?,item_name:r.get(2)?,
            from_employee:r.get(3)?,to_employee:r.get(4)?,
            date:r.get(5)?,notes:r.get(6)?
        }))?;
        Ok(rows.collect::<rusqlite::Result<Vec<_>>>()?)
    }

    pub fn authenticate(&self, username: &str, password: &str) -> Result<bool> {
        use rusqlite::OptionalExtension;
        let hash: Option<String> = self.conn.query_row(
            "SELECT password FROM users WHERE username=?1", [username], |r| r.get(0)
        ).optional()?;
        Ok(hash.as_deref().is_some_and(|stored|
            crate::licensing::verify_password(password, stored)
        ))
    }
}
