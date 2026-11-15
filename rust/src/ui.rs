use crate::{db::{Assignment, Database, Division, Employee, InventoryMode, Item}, licensing, reports, VERSION, PALETTE};
use eframe::egui::{self, Color32, RichText, Ui};
use std::{collections::BTreeSet, path::Path};

mod tools;

fn color(rgb: [u8;3]) -> Color32 { Color32::from_rgb(rgb[0],rgb[1],rgb[2]) }
fn pink() -> Color32 { color(PALETTE.pink) }
fn light() -> Color32 { color(PALETTE.white) }

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum Screen { Dashboard, Login, Inventory, Manager, Tool }
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub(super) enum Tool {
    AddItem, UpdateItem, RemoveItems, ViewItems,
    AddEmployee, BulkEmployees, UpdateEmployee, RemoveEmployees, ViewEmployees,
    AddDivision, UpdateDivision, RemoveDivisions, ViewDivisions,
    Assign, Transfer, ReportInventory, ReportEmployees, ReportItems,
    ViewAssignmentLog,
}

impl Tool {
    fn name(self) -> &'static str {
        match self {
            Self::AddItem=>"Add Single Item",
            Self::UpdateItem=>"Update Item Details",
            Self::RemoveItems=>"Remove Items",
            Self::ViewItems=>"View Item Records",
            Self::AddEmployee=>"Add Employee",
            Self::BulkEmployees=>"Bulk Import Employees",
            Self::UpdateEmployee=>"Update Employee Info",
            Self::RemoveEmployees=>"Remove Employee",
            Self::ViewEmployees=>"View Employee Records",
            Self::AddDivision=>"Create Division",
            Self::UpdateDivision=>"Update Division",
            Self::RemoveDivisions=>"Remove Division",
            Self::ViewDivisions=>"View Division Structure",
            Self::Assign=>"Assign Items to Employee",
            Self::Transfer=>"Transfer Items Between Employees",
            Self::ReportInventory=>"Inventory Report to Excel",
            Self::ReportEmployees=>"Employees to Excel",
            Self::ReportItems=>"Items to Excel",
            Self::ViewAssignmentLog=>"View Asset Assignments",
        }
    }
}

fn control(ui: &mut Ui, text: &str) -> bool {
    ui.add_sized(
        [178.0,38.0],
        egui::Button::new(RichText::new(text).color(color(PALETTE.black)).strong())
            .fill(pink())
    ).clicked()
}

fn secondary_control(ui: &mut Ui, text: &str) -> bool {
    ui.add_sized(
        [190.0,34.0],
        egui::Button::new(RichText::new(text).color(light()))
            .fill(color(PALETTE.black))
    ).clicked()
}

pub struct InManApp {
    db: Option<Database>,
    activated: bool,
    key_input: String,
    show_key: bool,
    screen: Screen,
    tool: Tool,
    message: String,
    username: String,
    password: String,
    pub(super) selected_mode: InventoryMode,
    pub(super) query: String,
    pub(super) attr_name: String,
    pub(super) attr_value: String,
    pub(super) division_filter: Option<i64>,
    pub(super) divisions: Vec<Division>,
    pub(super) employees: Vec<Employee>,
    pub(super) items: Vec<Item>,
    pub(super) assignments: Vec<Assignment>,
    pub(super) counts: (i64,i64,i64),
    pub(super) selected_employee: String,
    pub(super) selected_item: Option<i64>,
    pub(super) selected_division: Option<i64>,
    pub(super) selected_assignment: Option<i64>,
    pub(super) destination: String,
    pub(super) form_id: String,
    pub(super) form_name: String,
    pub(super) form_key: String,
    pub(super) form_notes: String,
    pub(super) form_attrs: Vec<(String,String)>,
    pub(super) new_attr_name: String,
    pub(super) new_attr_value: String,
    pub(super) staged: Vec<(String,String,i64)>,
    pub(super) selection: BTreeSet<String>,
}

impl Default for InManApp {
    fn default() -> Self {
        let activated=licensing::is_activated();
        let db=if activated {Database::open("inventory.db").ok()} else {None};
        let mut state=Self {
            db, activated, key_input:String::new(), show_key:false,
            screen:Screen::Dashboard, tool:Tool::AddItem,
            message:String::new(), username:String::new(),password:String::new(),
            selected_mode:InventoryMode::Employees,query:String::new(),
            attr_name:String::new(),attr_value:String::new(),division_filter:None,
            divisions:vec![],employees:vec![],items:vec![],assignments:vec![],counts:(0,0,0),
            selected_employee:String::new(),selected_item:None,selected_division:None,
            selected_assignment:None,destination:String::new(),form_id:String::new(),
            form_name:String::new(),form_key:String::new(),form_notes:String::new(),
            form_attrs:vec![],new_attr_name:String::new(),new_attr_value:String::new(),
            staged:vec![],selection:BTreeSet::new(),
        };
        if activated && state.db.is_none() {
            state.message="Cannot open inventory.db. Check the working directory.".into();
        }
        state.reload();
        state
    }
}

impl InManApp {
    pub fn new(cc:&eframe::CreationContext<'_>) -> Self {
        let mut visuals=egui::Visuals::dark();
        visuals.panel_fill=color(PALETTE.secondary_bg);
        visuals.window_fill=color(PALETTE.black);
        visuals.widgets.inactive.bg_fill=color(PALETTE.black);
        visuals.widgets.hovered.bg_fill=color(PALETTE.darker_pink);
        visuals.selection.bg_fill=pink();
        cc.egui_ctx.set_visuals(visuals);
        cc.egui_ctx.set_pixels_per_point(1.0);
        Self::default()
    }

    fn reload(&mut self) {
        let Some(db)=self.db.as_ref() else{return};
        let data=(
            db.dashboard_counts(), db.divisions(""),
            db.employees("",None),db.items(""),
        );
        match data {
            (Ok(counts),Ok(divisions),Ok(employees),Ok(items))=>{
                self.counts=counts;
                self.divisions=divisions;
                self.employees=employees;
                self.items=items;
            }
            _=> self.message="Could not load inventory data. Database format may be invalid.".into(),
        }
    }

    fn open(&mut self, screen:Screen) {
        self.screen=screen;
        self.message.clear();
        if matches!(screen,Screen::Dashboard | Screen::Manager | Screen::Tool) {self.reload()}
    }

    fn open_tool(&mut self, tool: Tool) {
        if matches!(tool,Tool::ReportInventory|Tool::ReportEmployees|Tool::ReportItems) {
            self.export_report(tool);
            return
        }
        self.tool=tool;
        self.selected_employee.clear();
        self.selected_item=None;
        self.selected_assignment=None;
        self.selected_division=None;
        self.form_name.clear();
        self.form_id.clear();
        self.form_key.clear();
        self.form_notes.clear();
        self.form_attrs.clear();
        self.new_attr_name.clear();
        self.new_attr_value.clear();
        self.destination.clear();
        self.selection.clear();
        self.staged.clear();
        self.open(Screen::Tool);
    }

    fn notify(&mut self, result:anyhow::Result<()>) {
        match result {
            Ok(value)=>{
                self.message="Changes saved successfully".into();
                self.reload();
            }
            Err(err)=>self.message=err.to_string(),
        }
    }

    fn license_screen(&mut self, ui:&mut Ui) {
        ui.vertical_centered(|ui|{
            ui.add_space(75.0);
            ui.horizontal(|ui|{
                ui.heading(RichText::new("In").color(pink()).size(48.0));
                ui.heading(RichText::new("Man").color(light()).size(48.0));
            });
            ui.label("Software by RezSat: http://rezsat.vercel.app");
            ui.add_space(32.0);
            ui.heading("Enter Product Key to Unlock");
            ui.add_space(12.0);
            ui.group(|ui|{
                ui.set_width(410.0);
                ui.label("Product Key");
                let mut editor=egui::TextEdit::singleline(&mut self.key_input)
                    .hint_text("Enter your product key");
                if !self.show_key {editor=editor.password(true)}
                ui.add_sized([350.0,42.0],editor);
                if ui.small_button(if self.show_key {"Hide"}else{"Show"}).clicked(){
                    self.show_key=!self.show_key;
                }
                if control(ui,"Unlock InMan") {
                    if licensing::valid_product_key(&self.key_input) {
                        match licensing::activate(&self.key_input)
                            .and_then(|_|Database::open("inventory.db")) {
                            Ok(db)=>{
                                self.db=Some(db);
                                self.activated=true;
                                self.reload();
                                self.open(Screen::Dashboard);
                            }
                            Err(err)=>self.message=err.to_string(),
                        }
                    } else {self.message="Invalid Product Key".into();}
                }
            });
        });
    }

    fn sidebar(&mut self, ui:&mut Ui) {
        ui.add_space(20.0);
        ui.horizontal(|ui|{
            ui.label(RichText::new("In").size(38.0).strong().color(pink()));
            ui.label(RichText::new("Man").size(38.0).strong().color(light()));
        });
        ui.add_space(22.0);
        if control(ui,"Dashboard") {self.open(Screen::Dashboard)}
        ui.add_space(10.0);
        if control(ui,"Login") {self.open(Screen::Login)}
        ui.add_space(10.0);
        if control(ui,"View Inventory") {
            self.open(Screen::Inventory);
            self.search();
        }
        ui.add_space(10.0);
        if control(ui,"Package to Share") {self.package()}
        ui.add_space(90.0);
        ui.small(format!("v{}",VERSION.trim_start_matches('v')));
    }

    fn dashboard(&mut self,ui:&mut Ui) {
        ui.heading(RichText::new("Dashboard").color(light()).size(26.0));
        ui.hyperlink_to("Office Inventory Management System by RezSat",
                        "http://rezsat.vercel.app");
        ui.add_space(10.0);
        ui.horizontal(|ui|{
            for (title,count) in [
                ("Total Employees",self.counts.0),
                ("Total Items",self.counts.1),
                ("Divisions",self.counts.2)
            ]{
                egui::Frame::group(ui.style()).fill(color(PALETTE.black)).show(ui,|ui|{
                    ui.set_min_width(185.0);
                    ui.label(title);
                    ui.heading(RichText::new(count.to_string()).color(light()).size(22.0));
                });
            }
        });
        ui.add_space(18.0);
        ui.heading("Division Overview");
        egui::ScrollArea::vertical().show(ui,|ui|{
            for division in &self.divisions {
                egui::Frame::group(ui.style()).fill(color(PALETTE.black)).show(ui,|ui|{
                    ui.horizontal(|ui|{
                        ui.heading(&division.name);
                        ui.label(format!("{} Employees | {} Items",
                            division.employee_count,division.item_count));
                    });
                    if let Some(db)=self.db.as_ref() {
                        // Only expand the type breakdown for the opened card.
                        egui::CollapsingHeader::new("Item types").id_salt(division.id)
                            .show(ui,|ui|{
                                if let Ok(items)=db.division_item_types(division.id) {
                                    for (name,count) in items {
                                        ui.label(format!("{name} — {count}"));
                                    }
                                }
                            });
                    }
                });
                ui.add_space(8.0);
            }
        });
    }

    fn login(&mut self,ui:&mut Ui) {
        ui.vertical_centered(|ui|{
            ui.add_space(70.0);
            ui.heading(RichText::new("InMan").size(42.0).color(pink()));
            ui.heading("Login! to be the Inventory Manager");
            ui.add_space(25.0);
            ui.group(|ui|{
                ui.set_width(360.0);
                ui.label("Username");
                ui.add_sized([300.0,40.0],egui::TextEdit::singleline(&mut self.username)
                    .hint_text("Enter your username"));
                ui.label("Password");
                ui.add_sized([300.0,40.0],egui::TextEdit::singleline(&mut self.password)
                    .hint_text("Enter your password").password(true));
                if control(ui,"Login") {
                    match self.db.as_ref().map(|d|d.authenticate(&self.username,&self.password)){
                        Some(Ok(true))=>self.open(Screen::Manager),
                        Some(Ok(false))=>self.message="Invalid username or password".into(),
                        Some(Err(err))=>self.message=err.to_string(),
                        None=>self.message="Database unavailable".into(),
                    }
                }
            });
        });
    }

    fn manager(&mut self,ui:&mut Ui) {
        ui.heading("Manager Tools");
        egui::ScrollArea::vertical().show(ui,|ui|{
            let sections: [(&str,&[Tool]);5]=[
                ("Inventory Management",&[Tool::AddItem,Tool::UpdateItem,Tool::RemoveItems,Tool::ViewItems]),
                ("Employee Management",&[Tool::AddEmployee,Tool::BulkEmployees,Tool::UpdateEmployee,Tool::RemoveEmployees,Tool::ViewEmployees]),
                ("Division Management",&[Tool::AddDivision,Tool::UpdateDivision,Tool::RemoveDivisions,Tool::ViewDivisions]),
                ("Asset Assignment",&[Tool::Assign,Tool::Transfer]),
                ("Reports & Analytics",&[Tool::ReportInventory,Tool::ReportEmployees,Tool::ReportItems]),
            ];
            for (section,tools) in sections {
                ui.add_space(10.0);
                ui.heading(RichText::new(section).size(20.0).color(light()));
                ui.separator();
                for chunk in tools.chunks(3){
                    ui.horizontal(|ui|{
                        for tool in chunk{
                            if ui.add_sized([190.0,70.0],
                                egui::Button::new(RichText::new(tool.name()).color(light()))
                                    .fill(color(PALETTE.black))
                            ).clicked() {
                                self.open_tool(*tool);
                            }
                        }
                    });
                }
            }
        });
    }

    fn search(&mut self) {
        let Some(db)=self.db.as_ref() else{return};
        let outcome=match self.selected_mode {
            InventoryMode::Employees=>db.employees(&self.query,self.division_filter)
                .map(|rows|{self.employees=rows}),
            InventoryMode::Items=>db.items(&self.query)
                .map(|rows|{self.items=rows}),
            InventoryMode::Divisions=>db.divisions(&self.query)
                .map(|rows|{self.divisions=rows}),
            InventoryMode::EmployeeItems=>db.assignments(&self.query,None,
                Some(&self.attr_name),Some(&self.attr_value))
                .map(|rows|{self.assignments=rows}),
            InventoryMode::UniqueKey=>db.unique_keys(&self.query)
                .map(|rows|{self.assignments=rows}),
        };
        if let Err(err)=outcome {self.message=err.to_string();}
    }

    fn inventory(&mut self,ui:&mut Ui) {
        ui.horizontal(|ui|{
            ui.heading("Inventory Search");
            if ui.button("Export Results").clicked() {self.export_search();}
        });
        ui.add_space(10.0);
        ui.horizontal(|ui|{
            let previous=self.selected_mode;
            egui::ComboBox::from_id_salt("search_type")
                .selected_text(self.selected_mode.label())
                .show_ui(ui,|ui|{
                    for mode in InventoryMode::ALL {
                        ui.selectable_value(&mut self.selected_mode,mode,mode.label());
                    }
                });
            let response=ui.add_sized([360.0,36.0],
                egui::TextEdit::singleline(&mut self.query).hint_text("Search..."));
            let entered=response.lost_focus() && ui.input(|i|i.key_pressed(egui::Key::Enter));
            if control(ui,"Search") || entered {self.search();}
            if previous!=self.selected_mode {self.query.clear();self.search();}
        });
        if self.selected_mode==InventoryMode::Employees {
            ui.horizontal(|ui|{
                egui::ComboBox::from_id_salt("division_filter")
                    .selected_text(self.divisions.iter()
                        .find(|d|Some(d.id)==self.division_filter)
                        .map_or("All Divisions",|d|d.name.as_str()))
                    .show_ui(ui,|ui|{
                        ui.selectable_value(&mut self.division_filter,None,"All Divisions");
                        for division in &self.divisions{
                            ui.selectable_value(&mut self.division_filter,
                                Some(division.id),&division.name);
                        }
                    });
            });
        } else if self.selected_mode==InventoryMode::EmployeeItems {
            ui.horizontal(|ui|{
                ui.label("Attribute Name:");
                ui.text_edit_singleline(&mut self.attr_name);
                ui.label("Attribute Value:");
                ui.text_edit_singleline(&mut self.attr_value);
            });
        }
        ui.add_space(12.0);
        egui::Frame::group(ui.style()).fill(color(PALETTE.black)).show(ui,|ui|{
            ui.set_min_height(380.0);
            match self.selected_mode {
                InventoryMode::Employees=>self.draw_employees(ui),
                InventoryMode::Items=>self.draw_items(ui),
                InventoryMode::Divisions=>self.draw_divisions(ui),
                InventoryMode::EmployeeItems|InventoryMode::UniqueKey=>self.draw_assignments(ui),
            }
        });
    }

    fn draw_employees(&self,ui:&mut Ui) {
        ui.label(RichText::new("Employee ID         Name                         Division").strong());
        egui::ScrollArea::vertical().auto_shrink([false,false])
            .show_rows(ui,34.0,self.employees.len(),|ui,range|{
                for index in range {
                    let record=&self.employees[index];
                    ui.horizontal(|ui|{
                        ui.label(&record.id);
                        ui.separator();
                        ui.label(&record.name);
                        ui.separator();
                        ui.label(&record.division);
                    });
                    ui.separator();
                }
            });
    }

    fn draw_items(&self,ui:&mut Ui) {
        ui.label(RichText::new("Name").strong());
        egui::ScrollArea::vertical().auto_shrink([false,false])
            .show_rows(ui,33.0,self.items.len(),|ui,range|{
                for i in range {ui.label(&self.items[i].name);ui.separator();}
            });
    }

    fn draw_divisions(&self,ui:&mut Ui) {
        ui.label(RichText::new("Division                        Employees       Items").strong());
        egui::ScrollArea::vertical().auto_shrink([false,false])
            .show_rows(ui,35.0,self.divisions.len(),|ui,range|{
                for i in range {
                    let d=&self.divisions[i];
                    ui.horizontal(|ui|{
                        ui.label(&d.name);
                        ui.label(format!("{} Employees",d.employee_count));
                        ui.label(format!("{} Items",d.item_count));
                    });
                    ui.separator();
                }
            });
    }

    fn draw_assignments(&self,ui:&mut Ui) {
        ui.label(RichText::new("Employee ID          Employee          Item          Unique Key          Attributes").strong());
        egui::ScrollArea::vertical().auto_shrink([false,false])
            .show_rows(ui,40.0,self.assignments.len(),|ui,range|{
                for i in range {
                    let a=&self.assignments[i];
                    ui.horizontal(|ui|{
                        ui.label(&a.employee_id);
                        ui.separator();
                        ui.label(&a.employee_name);
                        ui.separator();
                        ui.label(&a.item_name);
                        ui.separator();
                        ui.label(&a.unique_key);
                        ui.separator();
                        ui.label(a.attributes.iter()
                            .map(|x|format!("{}: {}",x.name,x.value))
                            .collect::<Vec<_>>().join(", "));
                    });
                    ui.separator();
                }
            });
    }

    fn export_report(&mut self,tool:Tool) {
        let Some(path)=rfd::FileDialog::new().add_filter("Excel",&["xlsx"])
            .set_file_name("inventory.xlsx").save_file() else{return};
        let Some(db)=self.db.as_ref() else{return};
        let result=match tool {
            Tool::ReportInventory=>reports::export_inventory(db,&path),
            Tool::ReportEmployees=>reports::export_employees(db,&path),
            Tool::ReportItems=>reports::export_items(db,&path),
            _=>return,
        };
        self.message=match result {Ok(())=>format!("Report saved: {}",path.display()),
                                   Err(err)=>err.to_string()};
    }

    fn export_search(&mut self) {
        let Some(path)=rfd::FileDialog::new().add_filter("Excel",&["xlsx"])
            .set_file_name("search_results.xlsx").save_file() else{return};
        let (headers,rows): (Vec<&str>,Vec<Vec<String>>)=match self.selected_mode {
            InventoryMode::Employees=>(
                vec!["Employee ID","Name","Division"],
                self.employees.iter().map(|e|vec![e.id.clone(),e.name.clone(),e.division.clone()]).collect()
            ),
            InventoryMode::Items=>(vec!["Name"],
                self.items.iter().map(|i|vec![i.name.clone()]).collect()),
            InventoryMode::Divisions=>(vec!["Division","Employees","Items"],
                self.divisions.iter().map(|d|vec![
                    d.name.clone(),d.employee_count.to_string(),d.item_count.to_string()
                ]).collect()),
            InventoryMode::UniqueKey=>(vec!["Employee ID","Employee Name","Item Name","Unique Key"],
                self.assignments.iter().map(|a|vec![
                    a.employee_id.clone(),a.employee_name.clone(),
                    a.item_name.clone(),a.unique_key.clone()
                ]).collect()),
            InventoryMode::EmployeeItems=>(vec!["Employee ID","Employee Name","Item Name","Unique Key","Attributes"],
                self.assignments.iter().map(|a|vec![
                    a.employee_id.clone(),a.employee_name.clone(),a.item_name.clone(),a.unique_key.clone(),
                    a.attributes.iter().map(|attr|format!("{}: {}",attr.name,attr.value))
                        .collect::<Vec<_>>().join(", ")
                ]).collect()),
        };
        self.message=match reports::export_search(path,&headers,&rows) {
            Ok(())=>"Results exported".into(),Err(err)=>err.to_string()
        };
    }

    fn package(&mut self) {
        let Some(output)=rfd::FileDialog::new()
            .add_filter("ZIP archive",&["zip"]).set_file_name("InMan.zip").save_file() else{return};
        let executable=std::env::current_exe();
        self.message=match executable.and_then(|exe|{
            reports::package_app(&output,&exe,Path::new("inventory.db"))
                .map_err(std::io::Error::other)
        }){
            Ok(())=>format!("Application packaged: {}",output.display()),
            Err(err)=>err.to_string()
        };
    }
}

impl eframe::App for InManApp {
    fn ui(&mut self, ui:&mut Ui, _frame:&mut eframe::Frame) {
        if !self.activated {
            self.license_screen(ui);
            if !self.message.is_empty(){
                ui.colored_label(pink(),&self.message);
            }
            return;
        }
        egui::SidePanel::left("inman_sidebar").exact_width(205.0)
            .resizable(false).show(ui.ctx(),|panel|{
                self.sidebar(panel);
            });
        egui::CentralPanel::default().show(ui.ctx(),|main|{
            main.add_space(12.0);
            match self.screen {
                Screen::Dashboard=>self.dashboard(main),
                Screen::Login=>self.login(main),
                Screen::Inventory=>self.inventory(main),
                Screen::Manager=>self.manager(main),
                Screen::Tool=>self.tool_screen(main),
            }
            if !self.message.is_empty() {
                main.separator();
                main.label(RichText::new(&self.message).color(pink()));
            }
        });
    }
}
