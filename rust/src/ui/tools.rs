use super::*;
use eframe::egui::{ComboBox, ScrollArea, TextEdit};

impl InManApp {
    pub(super) fn tool_screen(&mut self,ui:&mut Ui) {
        ui.horizontal(|ui|{
            if secondary_control(ui,"← Back to Manager Tools") {
                self.open(Screen::Manager);
            }
            ui.heading(RichText::new(self.tool.name()).size(24.0).color(light()));
        });
        ui.add_space(15.0);
        egui::Frame::group(ui.style()).fill(color(PALETTE.secondary_bg)).show(ui,|ui|{
            ui.set_min_width(610.0);
            match self.tool {
                Tool::AddItem=>self.add_item_ui(ui),
                Tool::UpdateItem=>self.update_item_ui(ui),
                Tool::RemoveItems=>self.remove_items_ui(ui),
                Tool::ViewItems=>self.view_items_ui(ui),
                Tool::AddEmployee=>self.add_employee_ui(ui),
                Tool::BulkEmployees=>self.import_employee_ui(ui),
                Tool::UpdateEmployee=>self.update_employee_ui(ui),
                Tool::RemoveEmployees=>self.remove_employees_ui(ui),
                Tool::ViewEmployees=>self.view_employees_ui(ui),
                Tool::AddDivision=>self.add_division_ui(ui),
                Tool::UpdateDivision=>self.update_division_ui(ui),
                Tool::RemoveDivisions=>self.remove_divisions_ui(ui),
                Tool::ViewDivisions=>self.view_divisions_ui(ui),
                Tool::Assign=>self.assign_ui(ui),
                Tool::Transfer=>self.transfer_ui(ui),
                Tool::ViewAssignmentLog=>self.assignment_log_ui(ui),
                Tool::ReportInventory|Tool::ReportEmployees|Tool::ReportItems=>{}
            }
        });
    }

    fn choose_employee(&mut self,ui:&mut Ui,label:&str) -> bool {
        let previous=self.selected_employee.clone();
        ui.horizontal(|ui|{
            ui.label(label);
            ComboBox::from_id_salt(format!("employee_selector_{label}"))
                .selected_text(if self.selected_employee.is_empty(){
                    "Select employee".to_owned()
                }else{self.selected_employee.clone()})
                .show_ui(ui,|ui|{
                    for employee in &self.employees {
                        ui.selectable_value(&mut self.selected_employee,
                            employee.id.clone(),format!("{} - {}",employee.id,employee.name));
                    }
                });
        });
        previous!=self.selected_employee
    }

    fn choose_item(&mut self,ui:&mut Ui,label:&str) -> bool {
        let previous=self.selected_item;
        ui.horizontal(|ui|{
            ui.label(label);
            let selected=self.items.iter().find(|x|Some(x.id)==self.selected_item)
                .map_or_else(||"Select item".to_owned(),|x|x.name.clone());
            ComboBox::from_id_salt(format!("item_selector_{label}"))
                .selected_text(selected)
                .show_ui(ui,|ui|{
                    for item in &self.items {
                        ui.selectable_value(&mut self.selected_item,
                            Some(item.id),format!("{} - {}",item.id,item.name));
                    }
                });
        });
        previous!=self.selected_item
    }

    fn choose_division(&mut self,ui:&mut Ui,label:&str) -> bool {
        let previous=self.selected_division;
        ui.horizontal(|ui|{
            ui.label(label);
            ComboBox::from_id_salt(format!("division_selector_{label}"))
                .selected_text(self.divisions.iter()
                    .find(|x|Some(x.id)==self.selected_division)
                    .map_or("Select division",|x|x.name.as_str()))
                .show_ui(ui,|ui|{
                    for division in &self.divisions{
                        ui.selectable_value(&mut self.selected_division,
                            Some(division.id),&division.name);
                    }
                });
        });
        previous!=self.selected_division
    }

    fn add_item_ui(&mut self,ui:&mut Ui) {
        ui.label("Item Name");
        ui.add_sized([430.0,38.0],TextEdit::singleline(&mut self.form_name));
        if control(ui,"Add Item") {
            let result=self.db.as_mut().unwrap().add_item(&self.form_name).map(|_|());
            self.notify(result);
        }
    }

    fn update_item_ui(&mut self,ui:&mut Ui) {
        if self.choose_item(ui,"Item") {
            self.form_name=self.items.iter().find(|x|Some(x.id)==self.selected_item)
                .map(|x|x.name.clone()).unwrap_or_default();
        }
        ui.label("Name");
        ui.add_sized([440.0,38.0],TextEdit::singleline(&mut self.form_name));
        if control(ui,"Save Item") {
            if let Some(id)=self.selected_item {
                let result=self.db.as_mut().unwrap().rename_item(id,&self.form_name);
                self.notify(result);
            } else {self.message="Select an item first".into();}
        }
    }

    fn remove_items_ui(&mut self,ui:&mut Ui) {
        ui.label("Select items to remove");
        ScrollArea::vertical().max_height(350.0).show_rows(ui,34.0,self.items.len(),|ui,range|{
            for index in range {
                let item=&self.items[index];
                let key=item.id.to_string();
                let mut selected=self.selection.contains(&key);
                if ui.checkbox(&mut selected,format!("{} — {}",item.id,item.name)).changed(){
                    if selected {self.selection.insert(key);} else {self.selection.remove(&key);}
                }
            }
        });
        if !self.selection.is_empty() &&
           control(ui,&format!("Remove {} Selected",self.selection.len())) {
            let ids=self.selection.iter()
                .filter_map(|s|s.parse::<i64>().ok()).collect();
            self.pending_removal=Some(PendingRemoval::Items(ids));
        }
    }
    fn view_items_ui(&mut self,ui:&mut Ui) {
        ui.label(RichText::new("Item ID                          Name").strong());
        ScrollArea::vertical().max_height(420.0)
            .show_rows(ui,34.0,self.items.len(),|ui,range|{
                for i in range {
                    ui.horizontal(|ui|{
                        ui.label(self.items[i].id.to_string());
                        ui.label(&self.items[i].name);
                    });
                    ui.separator();
                }
            });
    }

    fn add_employee_ui(&mut self,ui:&mut Ui) {
        ui.label("Employee ID");
        ui.add_sized([440.0,38.0],TextEdit::singleline(&mut self.form_id));
        ui.label("Name");
        ui.add_sized([440.0,38.0],TextEdit::singleline(&mut self.form_name));
        self.choose_division(ui,"Division");
        if control(ui,"Add Employee") {
            if let Some(division)=self.selected_division {
                let result=self.db.as_mut().unwrap()
                    .add_employee(&self.form_id,&self.form_name,division);
                self.notify(result);
            } else {self.message="Choose a division".into();}
        }
    }

    fn import_employee_ui(&mut self,ui:&mut Ui) {
        if control(ui,"Import Employees from Excel") {
            if let Some(path)=rfd::FileDialog::new()
                .add_filter("Excel",&["xlsx","xls"]).pick_file() {
                match reports::read_employee_import(&path,&self.divisions) {
                    Ok(rows)=>{self.staged=rows;self.message=format!(
                        "{} employee(s) loaded for review",self.staged.len()
                    );}
                    Err(err)=>self.message=err.to_string(),
                }
            }
        }
        ui.label("Review staged employee records before submitting");
        ScrollArea::vertical().max_height(355.0).show_rows(ui,40.0,self.staged.len(),|ui,range|{
            for index in range {
                let (id,name,division)=&mut self.staged[index];
                ui.horizontal(|ui|{
                    ui.add_sized([95.0,34.0],TextEdit::singleline(id));
                    ui.add_sized([180.0,34.0],TextEdit::singleline(name));
                    ComboBox::from_id_salt(format!("bulk_div_{index}"))
                        .selected_text(self.divisions.iter()
                            .find(|x|x.id==*division).map_or("Division",|x|x.name.as_str()))
                        .show_ui(ui,|ui|{
                            for d in &self.divisions {
                                ui.selectable_value(division,d.id,&d.name);
                            }
                        });
                });
            }
        });
        if control(ui,"Submit") {
            let result=self.db.as_mut().unwrap().import_employees(&self.staged).map(|_|());
            self.notify(result);
            self.staged.clear();
        }
    }

    fn update_employee_ui(&mut self,ui:&mut Ui) {
        if self.choose_employee(ui,"Employee") {
            if let Some(e)=self.employees.iter().find(|e|e.id==self.selected_employee) {
                self.form_id=e.id.clone();
                self.form_name=e.name.clone();
                self.selected_division=e.division_id;
            }
            self.load_selected_assets();
        }
        ui.label("Employee ID");
        ui.add_sized([440.0,38.0],TextEdit::singleline(&mut self.form_id));
        ui.label("Name");
        ui.add_sized([440.0,38.0],TextEdit::singleline(&mut self.form_name));
        self.choose_division(ui,"Division");
        if control(ui,"Update Employee") {
            let original=self.selected_employee.clone();
            let new_id=self.form_id.clone();
            let result=(||->anyhow::Result<()> {
                self.db.as_mut().unwrap().update_employee(
                    &original,&self.form_name,self.selected_division
                )?;
                if new_id!=original {
                    self.db.as_mut().unwrap().change_employee_id(&original,&new_id)?;
                }
                Ok(())
            })();
            self.notify(result);
            self.selected_employee=new_id;
        }
        ui.separator();
        ui.label("Assigned items and attributes");
        self.asset_details(ui,true);
    }

    fn remove_employees_ui(&mut self,ui:&mut Ui) {
        ui.label("Select employees to remove");
        ScrollArea::vertical().max_height(355.0).show_rows(ui,36.0,self.employees.len(),|ui,range|{
            for i in range {
                let employee=&self.employees[i];
                let mut selected=self.selection.contains(&employee.id);
                if ui.checkbox(&mut selected,format!(
                    "{} — {} ({})",employee.id,employee.name,employee.division
                )).changed(){
                    if selected {self.selection.insert(employee.id.clone());}
                    else {self.selection.remove(&employee.id);}
                }
            }
        });
        if !self.selection.is_empty() &&
           control(ui,&format!("Remove {} Selected",self.selection.len())) {
            self.pending_removal=Some(PendingRemoval::Employees(
                self.selection.iter().cloned().collect()
            ));
        }
    }
    fn view_employees_ui(&mut self,ui:&mut Ui) {
        if self.choose_employee(ui,"Employee") {self.load_selected_assets();}
        self.asset_details(ui,false);
    }

    fn add_division_ui(&mut self,ui:&mut Ui) {
        ui.label("Division Name");
        ui.add_sized([440.0,38.0],TextEdit::singleline(&mut self.form_name));
        if control(ui,"Create Division") {
            let result=self.db.as_mut().unwrap().add_division(&self.form_name).map(|_|());
            self.notify(result);
        }
    }

    fn update_division_ui(&mut self,ui:&mut Ui) {
        if self.choose_division(ui,"Division") {
            self.form_name=self.divisions.iter().find(|d|Some(d.id)==self.selected_division)
                .map(|d|d.name.clone()).unwrap_or_default();
        }
        ui.label("Division Name");
        ui.add_sized([440.0,38.0],TextEdit::singleline(&mut self.form_name));
        if control(ui,"Update Division") {
            if let Some(id)=self.selected_division{
                let result=self.db.as_mut().unwrap().rename_division(id,&self.form_name);
                self.notify(result);
            }
        }
    }

    fn remove_divisions_ui(&mut self,ui:&mut Ui) {
        ScrollArea::vertical().max_height(355.0).show_rows(ui,36.0,self.divisions.len(),|ui,range|{
            for i in range {
                let division=&self.divisions[i];
                let key=division.id.to_string();
                let mut selected=self.selection.contains(&key);
                if ui.checkbox(&mut selected,format!(
                    "{} — {} ({} Employees)",division.id,division.name,division.employee_count
                )).changed(){
                    if selected {self.selection.insert(key);}else{self.selection.remove(&key);}
                }
            }
        });
        if !self.selection.is_empty() &&
           control(ui,&format!("Remove {} Selected",self.selection.len())) {
            let ids=self.selection.iter().filter_map(|s|s.parse::<i64>().ok()).collect();
            self.pending_removal=Some(PendingRemoval::Divisions(ids));
        }
    }
    fn view_divisions_ui(&mut self,ui:&mut Ui) {
        self.choose_division(ui,"Division");
        if let Some(id)=self.selected_division{
            if let Some(division)=self.divisions.iter().find(|d|d.id==id) {
                ui.heading(&division.name);
                ui.label(format!("{} Employees | {} Items",
                    division.employee_count,division.item_count));
            }
            if let Some(db)=self.db.as_ref(){
                if let Ok(items)=db.division_item_types(id) {
                    for (name,count) in items {ui.label(format!("{name}: {count}"));}
                }
                if let Ok(employees)=db.employees("",Some(id)) {
                    for employee in employees {
                        ui.label(format!("{} — {}",employee.id,employee.name));
                    }
                }
            }
        }
    }

    fn assign_ui(&mut self,ui:&mut Ui) {
        self.choose_employee(ui,"Employee");
        self.choose_item(ui,"Item");
        ui.label("Unique Key / Reference ID");
        ui.add_sized([430.0,36.0],TextEdit::singleline(&mut self.form_key));
        ui.label("Notes");
        ui.add_sized([430.0,36.0],TextEdit::singleline(&mut self.form_notes));
        ui.separator();
        ui.label("Custom Attributes");
        for (index,(name,value)) in self.form_attrs.iter_mut().enumerate() {
            ui.horizontal(|ui|{
                ui.label(format!("{}",index+1));
                ui.add_sized([155.0,30.0],TextEdit::singleline(name));
                ui.add_sized([155.0,30.0],TextEdit::singleline(value));
            });
        }
        ui.horizontal(|ui|{
            if secondary_control(ui,"Add Attribute") {
                self.form_attrs.push((String::new(),String::new()));
            }
            if secondary_control(ui,"Remove Last") {self.form_attrs.pop();}
        });
        if control(ui,"Assign Items to Employee") {
            if let Some(item_id)=self.selected_item {
                let result=self.db.as_mut().unwrap()
                    .assign(&self.selected_employee,item_id,&self.form_key,
                            &self.form_attrs,&self.form_notes)
                    .map(|_|());
                self.notify(result);
            }else{self.message="Choose an item type".into();}
        }
    }

    fn load_selected_assets(&mut self) {
        let Some(db)=self.db.as_ref() else{return};
        match db.assignments("",Some(&self.selected_employee),None,None) {
            Ok(records)=>self.assignments=records,
            Err(err)=>self.message=err.to_string(),
        }
    }

    fn asset_details(&mut self,ui:&mut Ui,editable:bool) {
        ScrollArea::vertical().max_height(280.0).show(ui,|ui|{
            for asset in &self.assignments {
                let selected=self.selected_assignment==Some(asset.id);
                if ui.selectable_label(selected,format!(
                    "{} — {} | {}",asset.item_name,asset.unique_key,
                    asset.attributes.iter().map(|attr|format!("{}: {}",attr.name,attr.value))
                        .collect::<Vec<_>>().join(", ")
                )).clicked() {self.selected_assignment=Some(asset.id);}
            }
        });
        if editable {
            if self.selected_assignment.is_some() {
                ui.horizontal(|ui|{
                    ui.label("Attribute Name");
                    ui.text_edit_singleline(&mut self.new_attr_name);
                    ui.label("Value");
                    ui.text_edit_singleline(&mut self.new_attr_value);
                });
                if secondary_control(ui,"Save Attribute") {
                    let result=self.db.as_mut().unwrap().upsert_attribute(
                        self.selected_assignment.unwrap(),&self.new_attr_name,&self.new_attr_value
                    );
                    self.notify(result);
                    self.load_selected_assets();
                }
                if secondary_control(ui,"Remove Attribute") {
                    let result=self.db.as_mut().unwrap().remove_attribute(
                        self.selected_assignment.unwrap(),&self.new_attr_name
                    );
                    self.notify(result);
                    self.load_selected_assets();
                }
                if secondary_control(ui,"Remove Assigned Item") {
                    self.pending_removal=Some(PendingRemoval::Assignment(
                        self.selected_assignment.unwrap()
                    ));
                }
            }
        }
    }

    fn transfer_ui(&mut self,ui:&mut Ui) {
        if self.choose_employee(ui,"From Employee") {self.load_selected_assets();}
        ui.label("Select a physical asset to transfer");
        self.asset_details(ui,false);
        ui.horizontal(|ui|{
            ui.label("To Employee");
            ComboBox::from_id_salt("to_employee")
                .selected_text(if self.destination.is_empty(){
                    "Select employee".to_owned()
                }else{self.destination.clone()})
                .show_ui(ui,|ui|{
                    for employee in &self.employees {
                        ui.selectable_value(&mut self.destination,
                            employee.id.clone(),format!("{} - {}",employee.id,employee.name));
                    }
                });
        });
        ui.label("Notes");
        ui.add_sized([440.0,36.0],TextEdit::singleline(&mut self.form_notes));
        if control(ui,"Transfer Items") {
            if let Some(id)=self.selected_assignment {
                let result=self.db.as_mut().unwrap()
                    .transfer(id,&self.destination,&self.form_notes).map(|_|());
                self.notify(result);
                self.selected_assignment=None;
                self.load_selected_assets();
            } else {self.message="Select an asset to transfer".into();}
        }
    }

    fn assignment_log_ui(&mut self,ui:&mut Ui) {
        if let Some(db)=self.db.as_ref() {
            if let Ok(logs)=db.logs("",200) {
                ScrollArea::vertical().show_rows(ui,38.0,logs.len(),|ui,range|{
                    for i in range {
                        let log=&logs[i];
                        ui.label(format!("{} | {} | {}",
                            log.timestamp,log.action,log.details));
                        ui.separator();
                    }
                });
            }
        }
    }
}
