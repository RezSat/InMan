use crate::{db::{self,Assignment, AssignmentDraft, Database, Division, Employee, InventoryMode, Item}, licensing, logging, reports, VERSION, PALETTE};
use eframe::egui::{self, Color32, RichText, Ui};
use std::{collections::{BTreeMap,BTreeSet}, path::PathBuf, sync::atomic::{AtomicBool, Ordering}};

mod tools;
mod theme;
mod preferences;

/// Set once the UI has produced its first frame. Used to distinguish a startup
/// failure (safe to retry on another graphics backend) from a late event-loop
/// error (which must not silently reopen the application).
static RENDERED_FRAME: AtomicBool = AtomicBool::new(false);

pub fn has_rendered_frame() -> bool {
    RENDERED_FRAME.load(Ordering::SeqCst)
}

fn record_first_frame() {
    if !RENDERED_FRAME.swap(true, Ordering::SeqCst) {
        logging::startup("render", "first UI frame rendered");
    }
}

fn color(rgb: [u8;3]) -> Color32 { Color32::from_rgb(rgb[0],rgb[1],rgb[2]) }
fn pink() -> Color32 { color(PALETTE.pink) }


/// A single item row, kept separate from the persisted inventory until Save.
#[derive(Default)]
pub(super) struct StagedAsset {
    item_id: Option<i64>,
    unique_key: String,
    attributes: Vec<(String,String)>,
}

pub(super) enum PendingRemoval {
    Items(Vec<i64>),
    Employees(Vec<String>),
    Divisions(Vec<i64>),
    Assignment(i64),
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum Screen { Dashboard, Inventory, Manager, Tool, Settings }
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub(super) enum Tool {
    AddItem, UpdateItem, RemoveItems, ViewItems,
    AddEmployee, BulkEmployees, UpdateEmployee, RemoveEmployees, ViewEmployees,
    AddDivision, UpdateDivision, RemoveDivisions, ViewDivisions,
    Assign, Transfer, ReportInventory, ReportEmployees, ReportItems, BackupDatabase,
    #[expect(dead_code, reason = "Legacy asset log viewer remains internal, as in v1.4")]
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
            Self::BackupDatabase=>"Backup Database",
            Self::ViewAssignmentLog=>"View Asset Assignments",
        }
    }
}

fn status_message(ui:&mut Ui,message:&str) {
    if message.is_empty(){return}
    let lower=message.to_ascii_lowercase();
    let successful=["success","saved","created","assigned","transferred","exported",
                    "backup","packaged","imported"].iter()
        .any(|word|lower.contains(word));
    let status_color=if successful{theme::SUCCESS}else{theme::DANGER};
    theme::subtle_card().show(ui,|ui|{
        ui.horizontal(|ui|{
            ui.label(RichText::new(if successful{"COMPLETE"}else{"NOTICE"})
                .size(10.0).strong().color(status_color));
            ui.label(RichText::new(message).size(12.0).color(theme::TEXT));
        });
    });
}

fn control(ui: &mut Ui, text: &str) -> bool {
    theme::primary(ui, text)
}

fn secondary_control(ui: &mut Ui, text: &str) -> bool {
    theme::secondary(ui, text)
}

pub struct InManApp {
    db: Option<Database>,
    database_path: PathBuf,
    activated: bool,
    key_input: String,
    show_key: bool,
    screen: Screen,
    tool: Tool,
    message: String,
    ui_scale: f32,
    pub(super) selected_mode: InventoryMode,
    pub(super) query: String,
    pub(super) attr_name: String,
    pub(super) attr_value: String,
    pub(super) division_filter: Option<i64>,
    pub(super) divisions: Vec<Division>,
    pub(super) employees: Vec<Employee>,
    pub(super) items: Vec<Item>,
    pub(super) assignments: Vec<Assignment>,
    // Read-only search result collections; manager selectors remain complete.
    inventory_employees: Vec<Employee>,
    inventory_items: Vec<Item>,
    inventory_divisions: Vec<Division>,
    inventory_assignments: Vec<Assignment>,
    division_item_cache: BTreeMap<i64,Vec<(String,i64)>>,
    pub(super) counts: (i64,i64,i64),
    pub(super) selected_employee: String,
    pub(super) selected_item: Option<i64>,
    pub(super) selected_division: Option<i64>,
    pub(super) selected_assignment: Option<i64>,
    pub(super) destination: String,
    pub(super) form_id: String,
    pub(super) form_name: String,
    pub(super) form_notes: String,
    pub(super) staged_assets: Vec<StagedAsset>,
    pub(super) new_attr_name: String,
    pub(super) new_attr_value: String,
    pub(super) staged: Vec<(String,String,Option<i64>)>,
    pub(super) selection: BTreeSet<String>,
    pub(super) transfer_selection: BTreeSet<i64>,
    pub(super) pending_removal: Option<PendingRemoval>,
}

impl Default for InManApp {
    fn default() -> Self {
        let activated=licensing::is_activated();
        logging::startup("licensing", if activated {
            "stored product key verified"
        } else {
            "no activated product key; showing the activation screen"
        });
        let working_dir=std::env::current_dir().unwrap_or_else(|_|PathBuf::from("."));
        let executable=std::env::current_exe()
            .unwrap_or_else(|_|working_dir.join("InMan.exe"));
        let database_path=db::resolve_inventory_path(&working_dir,&executable);
        logging::startup("database", format!("resolved inventory database: {}",database_path.display()));
        let mut db_error=None;
        let db=if activated {
            match Database::open(&database_path) {
                Ok(db)=>{
                    logging::startup("database", "inventory database opened and ready");
                    Some(db)
                }
                Err(error)=>{
                    logging::error("database", format!(
                        "could not open {}: {error:#}",database_path.display()
                    ));
                    db_error=Some(format!(
                        "Cannot open {}.\n{error:#}",database_path.display()
                    ));
                    None
                }
            }
        }else{None};
        let mut state=Self {
            db, database_path, activated, key_input:String::new(), show_key:false,
            screen:Screen::Dashboard, tool:Tool::AddItem,
            message:String::new(),ui_scale:preferences::load(),
            selected_mode:InventoryMode::Employees,query:String::new(),
            attr_name:String::new(),attr_value:String::new(),division_filter:None,
            divisions:vec![],employees:vec![],items:vec![],assignments:vec![],
            inventory_employees:vec![],inventory_items:vec![],
            inventory_divisions:vec![],inventory_assignments:vec![],
            division_item_cache:BTreeMap::new(),counts:(0,0,0),
            selected_employee:String::new(),selected_item:None,selected_division:None,
            selected_assignment:None,destination:String::new(),form_id:String::new(),
            form_name:String::new(),form_notes:String::new(),
            staged_assets:vec![StagedAsset::default()],new_attr_name:String::new(),new_attr_value:String::new(),
            staged:vec![],selection:BTreeSet::new(),
            transfer_selection:BTreeSet::new(),pending_removal:None,
        };
        if let Some(error)=db_error {
            state.message=error;
        }
        state.reload();
        logging::startup("app", "InManApp constructed");
        state
    }
}

impl InManApp {
    pub fn new(cc:&eframe::CreationContext<'_>) -> Self {
        if let Some(render_state)=cc.wgpu_render_state.as_ref() {
            let info=render_state.adapter.get_info();
            logging::startup("graphics", format!(
                "wgpu adapter: {} (backend {:?}, device type {:?}, driver {}, {})",
                info.name,info.backend,info.device_type,info.driver,info.driver_info
            ));
        }else{
            logging::warn("graphics", "eframe did not provide a wgpu render state");
        }
        theme::install(&cc.egui_ctx);
        let app=Self::default();
        cc.egui_ctx.set_zoom_factor(app.ui_scale);
        app
    }

    fn reload(&mut self) {
        self.division_item_cache.clear();
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
            (counts,divisions,employees,items)=>{
                for (stage,error) in [
                    ("dashboard counts",counts.err()),
                    ("divisions",divisions.err()),
                    ("employees",employees.err()),
                    ("items",items.err()),
                ] {
                    if let Some(error)=error {
                        logging::error("database", format!("loading {stage} failed: {error:#}"));
                    }
                }
                self.message="Could not load inventory data. Database format may be invalid.".into();
            }
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
        if tool==Tool::BackupDatabase {
            self.backup_database();
            return;
        }
        self.tool=tool;
        self.selected_employee.clear();
        self.selected_item=None;
        self.selected_assignment=None;
        self.selected_division=None;
        self.form_name.clear();
        self.form_id.clear();
        self.form_notes.clear();
        self.staged_assets=vec![StagedAsset::default()];
        self.new_attr_name.clear();
        self.new_attr_value.clear();
        self.destination.clear();
        self.selection.clear();
        self.transfer_selection.clear();
        self.staged.clear();
        self.pending_removal=None;
        if tool==Tool::Transfer {
            self.form_notes="Transferred between employees".into();
        }
        self.open(Screen::Tool);
    }

    fn notify(&mut self, result:anyhow::Result<()>) {
        match result {
            Ok(())=>{
                self.message="Changes saved successfully".into();
                self.reload();
            }
            Err(err)=>self.message=err.to_string(),
        }
    }

    fn license_screen(&mut self,ui:&mut Ui) {
        ui.vertical_centered(|ui|{
            ui.add_space(62.0);
            ui.label(RichText::new("INMAN DESKTOP").size(11.0)
                .strong().color(theme::ACCENT));
            ui.label(RichText::new("Welcome to InMan").size(34.0)
                .strong().color(theme::TEXT));
            ui.label(RichText::new("Activate your copy to access the inventory workspace.")
                .size(13.0).color(theme::MUTED));
            ui.add_space(27.0);
            theme::card().show(ui,|ui|{
                ui.set_width(400.0);
                ui.label(RichText::new("PRODUCT ACTIVATION").size(11.0)
                    .strong().color(theme::MUTED));
                ui.add_space(8.0);
                ui.label(RichText::new("Product key").strong());
                let mut input=egui::TextEdit::singleline(&mut self.key_input)
                    .hint_text("Enter your product key");
                if !self.show_key {input=input.password(true);}
                ui.add_sized([360.0,42.0],input);
                ui.horizontal(|ui|{
                    ui.checkbox(&mut self.show_key,"Show key");
                });
                ui.add_space(8.0);
                if control(ui,"Activate InMan") {
                    if licensing::valid_product_key(&self.key_input) {
                        match licensing::activate(&self.key_input)
                            .and_then(|_|Database::open(&self.database_path)) {
                            Ok(db)=>{
                                logging::startup("licensing","product key accepted and stored");
                                self.db=Some(db);
                                self.activated=true;
                                self.reload();
                                self.open(Screen::Dashboard);
                            }
                            Err(err)=>{
                                logging::error("licensing",format!("activation failed: {err:#}"));
                                self.message=format!("{err:#}");
                            }
                        }
                    }else{
                        logging::warn("licensing","an invalid product key was entered");
                        self.message="Invalid Product Key".into();
                    }
                }
            });
            ui.add_space(20.0);
            ui.label(RichText::new("INVENTORY MANAGEMENT BY REZSAT")
                .size(10.0).color(theme::MUTED));
        });
    }

    fn sidebar(&mut self, ui:&mut Ui) {
        ui.add_space(15.0);
        // Restore the original pink "In" and cream "Man" wordmark.
        ui.horizontal(|ui|{
            ui.spacing_mut().item_spacing.x=0.0;
            ui.label(RichText::new("In").size(30.0).strong().color(theme::ACCENT));
            ui.label(RichText::new("Man").size(30.0).strong().color(theme::TEXT));
        });
        ui.label(RichText::new("INVENTORY MANAGEMENT").size(10.0).color(theme::MUTED));
        ui.add_space(28.0);
        ui.label(RichText::new("WORKSPACE").size(11.0).strong().color(theme::MUTED));
        ui.add_space(8.0);
        if theme::sidebar_item(ui,"Dashboard",self.screen==Screen::Dashboard){
            self.open(Screen::Dashboard)
        }
        if theme::sidebar_item(ui,"View Inventory",self.screen==Screen::Inventory){
            self.open(Screen::Inventory);
            self.search();
        }
        ui.add_space(18.0);
        ui.label(RichText::new("OPERATIONS").size(11.0).strong().color(theme::MUTED));
        ui.add_space(8.0);
        if theme::sidebar_item(ui,"Manager Tools",
            matches!(self.screen,Screen::Manager|Screen::Tool)) {
            self.open(Screen::Manager)
        }
        if theme::sidebar_item(ui,"Package to Share",false){self.package()}
        ui.add_space(16.0);
        if theme::sidebar_item(ui,"Settings",self.screen==Screen::Settings){
            self.open(Screen::Settings)
        }
        ui.add_space(18.0);
        ui.separator();
        ui.label(RichText::new(format!("InMan {}",VERSION)).size(12.0).color(theme::MUTED));
    }

    fn settings(&mut self,ui:&mut Ui) {
        theme::heading(ui,"PREFERENCES","Settings",
            "Adjust readability without changing your inventory data.");
        let available=ui.available_width();
        theme::card().show(ui,|ui|{
            ui.set_min_width((available-40.0).max(240.0));
            theme::section(ui,"Display size","Changes apply to the entire interface.");
            ui.add_space(7.0);
            let mut percentage=(self.ui_scale*100.0).round();
            let mut changed=false;
            ui.horizontal_wrapped(|ui|{
                ui.label(RichText::new("Minimum 100%").color(theme::MUTED));
                let width=(ui.available_width()-180.0).clamp(130.0,430.0);
                changed|=ui.add_sized([width,35.0],
                    egui::Slider::new(&mut percentage,100.0..=150.0)
                        .step_by(5.0).suffix("%")
                ).changed();
                ui.label(RichText::new("Maximum 150%").color(theme::MUTED));
            });
            ui.horizontal_wrapped(|ui|{
                if ui.add_enabled(percentage>100.0,egui::Button::new("A−  Smaller")).clicked(){
                    percentage=(percentage-5.0).max(100.0);
                    changed=true;
                }
                if ui.add_enabled(percentage<150.0,egui::Button::new("A+  Larger")).clicked(){
                    percentage=(percentage+5.0).min(150.0);
                    changed=true;
                }
                if ui.button("Restore default (110%)").clicked(){
                    percentage=110.0;
                    changed=true;
                }
            });
            if changed {
                self.ui_scale=(percentage/100.0)
                    .clamp(preferences::MIN_ZOOM,preferences::MAX_ZOOM);
                ui.ctx().set_zoom_factor(self.ui_scale);
                if let Err(error)=preferences::save(self.ui_scale) {
                    self.message=format!("Could not save display size: {error}");
                } else {
                    self.message=format!("Display size set to {}%",percentage.round() as i32);
                }
            }
            ui.add_space(12.0);
            ui.label(RichText::new("Font: Segoe UI on Windows, with a built-in fallback.")
                .color(theme::MUTED));
            ui.label(RichText::new("The display setting is saved on this computer. Database contents are unaffected.")
                .color(theme::MUTED));
        });
    }

    fn dashboard(&mut self,ui:&mut Ui) {
        theme::heading(ui,"OVERVIEW","Dashboard","A clear view of the current inventory.");
        let stats=[
            ("EMPLOYEES",self.counts.0,"People in the inventory"),
            ("ITEM TYPES",self.counts.1,"Distinct catalogue items"),
            ("DIVISIONS",self.counts.2,"Registered departments")
        ];
        let columns=if ui.available_width()>800.0{3}
            else if ui.available_width()>440.0{2}else{1};
        for row in stats.chunks(columns) {
            ui.columns(columns,|cells|{
                for (cell,(title,value,caption)) in cells.iter_mut().zip(row.iter()){
                    let width=(cell.available_width()-6.0).max(100.0);
                    theme::card().show(cell,|ui|{
                        ui.vertical(|ui|{
                            ui.set_width((width-36.0).max(100.0));
                            ui.set_min_height(112.0);
                            ui.label(RichText::new(*title).size(12.0)
                                .strong().color(theme::MUTED));
                            ui.add_space(5.0);
                            ui.label(RichText::new(value.to_string()).size(34.0)
                                .strong().color(theme::TEXT));
                            ui.label(RichText::new(*caption).size(13.0)
                                .color(theme::MUTED));
                        });
                    });
                }
            });
            ui.add_space(8.0);
        }
        ui.add_space(17.0);
        theme::section(ui,"Quick actions","Go straight to a task.");
        ui.horizontal_wrapped(|ui|{
            if secondary_control(ui,"Browse inventory"){
                self.open(Screen::Inventory);
                self.search();
            }
            if secondary_control(ui,"Manager Tools"){self.open(Screen::Manager);}
        });
        ui.add_space(23.0);
        theme::section(ui,"Division overview","Departments and assigned assets");
        egui::ScrollArea::vertical().auto_shrink([false,false])
            .max_height(ui.available_height().max(220.0))
            .show(ui,|ui|{
                for division in &self.divisions {
                    let width=ui.available_width();
                    theme::card().show(ui,|ui|{
                        ui.set_min_width((width-37.0).max(200.0));
                        ui.horizontal_wrapped(|ui|{
                            ui.vertical(|ui|{
                                ui.label(RichText::new(&division.name)
                                    .size(15.0).strong().color(theme::TEXT));
                                ui.label(RichText::new(format!(
                                    "{} employees",division.employee_count))
                                    .size(13.0).color(theme::MUTED));
                            });
                            ui.with_layout(egui::Layout::right_to_left(egui::Align::Center),|ui|{
                                ui.label(RichText::new(format!(
                                    "{} ASSETS",division.item_count))
                                    .size(12.0).strong().color(theme::ACCENT));
                            });
                        });
                        if let Some(db)=self.db.as_ref(){
                            egui::CollapsingHeader::new("Assigned item types")
                                .id_salt(division.id).show(ui,|ui|{
                                let items=self.division_item_cache.entry(division.id)
                                    .or_insert_with(||db.division_item_types(division.id)
                                        .unwrap_or_default());
                                if items.is_empty(){ui.label("No items assigned");}
                                for (name,count) in items.iter(){
                                    ui.horizontal(|ui|{
                                        ui.label(name);
                                        ui.label(RichText::new(format!("× {count}"))
                                            .color(theme::MUTED));
                                    });
                                }
                            });
                        }
                    });
                    ui.add_space(8.0);
                }
            });
    }

    fn manager(&mut self,ui:&mut Ui) {
        theme::heading(ui, "MANAGEMENT", "Manager tools",
            "Choose an operation. All inventory records and actions are preserved.");
        egui::ScrollArea::vertical().auto_shrink([false,false]).show(ui,|ui|{
            let sections: [(&str,&str,&[Tool]);5]=[
                ("Inventory management","Manage the item catalogue",&[
                    Tool::AddItem,Tool::UpdateItem,Tool::RemoveItems,Tool::ViewItems
                ]),
                ("Employee management","People and ownership records",&[
                    Tool::AddEmployee,Tool::BulkEmployees,Tool::UpdateEmployee,
                    Tool::RemoveEmployees,Tool::ViewEmployees
                ]),
                ("Division management","Department structure",&[
                    Tool::AddDivision,Tool::UpdateDivision,Tool::RemoveDivisions,Tool::ViewDivisions
                ]),
                ("Asset assignment","Issue, track and transfer equipment",&[
                    Tool::Assign,Tool::Transfer
                ]),
                ("Reports & analytics","Export and safeguard your data",&[
                    Tool::ReportInventory,Tool::ReportEmployees,
                    Tool::ReportItems,Tool::BackupDatabase
                ]),
            ];
            for (name,description,tools) in sections {
                theme::section(ui,name,description);
                ui.horizontal_wrapped(|ui|{
                    ui.spacing_mut().item_spacing=egui::vec2(10.0,10.0);
                    for tool in tools {
                        if ui.add_sized([205.0,74.0],
                            egui::Button::new(RichText::new(tool.name())
                                .size(13.0).strong().color(theme::TEXT))
                                .fill(theme::SURFACE)
                                .stroke(egui::Stroke::new(1.0,theme::BORDER))
                                .corner_radius(egui::CornerRadius::same(10))
                        ).clicked() {
                            self.open_tool(*tool);
                        }
                    }
                });
                ui.add_space(22.0);
            }
        });
    }

    fn search(&mut self) {
        let Some(db)=self.db.as_ref() else{return};
        let outcome=match self.selected_mode {
            InventoryMode::Employees=>db.employees(&self.query,self.division_filter)
                .map(|rows|{self.inventory_employees=rows}),
            InventoryMode::Items=>db.items(&self.query)
                .map(|rows|{self.inventory_items=rows}),
            InventoryMode::Divisions=>db.divisions(&self.query)
                .map(|rows|{self.inventory_divisions=rows}),
            InventoryMode::EmployeeItems=>db.assignments(&self.query,None,
                Some(&self.attr_name),Some(&self.attr_value))
                .map(|rows|{self.inventory_assignments=rows}),
            InventoryMode::UniqueKey=>db.unique_keys(&self.query)
                .map(|rows|{self.inventory_assignments=rows}),
        };
        if let Err(err)=outcome {
            logging::error("database", format!("inventory search failed: {err:#}"));
            self.message=err.to_string();
        }
    }

    fn inventory(&mut self,ui:&mut Ui) {
        theme::heading(ui,"ASSET DIRECTORY","Inventory",
            "Search employees, item types, divisions and assigned assets.");
        ui.horizontal(|ui|{
            ui.label(RichText::new(self.selected_mode.label()).color(theme::MUTED).size(12.0));
            ui.with_layout(egui::Layout::right_to_left(egui::Align::Center),|ui|{
                if secondary_control(ui,"Export Results"){self.export_search();}
            });
        });
        ui.add_space(12.0);
        theme::card().show(ui,|ui|{
        ui.label(RichText::new("SEARCH & FILTER").size(11.0).strong().color(theme::MUTED));
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
            let old_division=self.division_filter;
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
            if old_division!=self.division_filter {self.search();}
        } else if self.selected_mode==InventoryMode::EmployeeItems {
            ui.horizontal(|ui|{
                ui.label("Attribute Name:");
                ui.text_edit_singleline(&mut self.attr_name);
                ui.label("Attribute Value:");
                ui.text_edit_singleline(&mut self.attr_value);
            });
        }
        });
        ui.add_space(20.0);
        let result_count=match self.selected_mode {
            InventoryMode::Employees=>self.inventory_employees.len(),
            InventoryMode::Items=>self.inventory_items.len(),
            InventoryMode::Divisions=>self.inventory_divisions.len(),
            _=>self.inventory_assignments.len(),
        };
        theme::section(ui,"Search results",&format!("{result_count} records"));
        theme::card().show(ui,|ui|{
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
        theme::table_header_sized(ui,&[
            ("EMPLOYEE ID",135.0),("EMPLOYEE NAME",225.0),("DIVISION",210.0)
        ]);
        egui::ScrollArea::vertical().auto_shrink([false,false])
            .show_rows(ui,36.0,self.inventory_employees.len(),|ui,range|{
                for index in range {
                    let record=&self.inventory_employees[index];
                    theme::table_row(ui,&[
                        (&record.id,135.0),(&record.name,225.0),(&record.division,210.0)
                    ]);
                    ui.separator();
                }
            });
    }

    fn draw_items(&self,ui:&mut Ui) {
        theme::table_header_sized(ui,&[("ITEM TYPE",560.0)]);
        egui::ScrollArea::vertical().auto_shrink([false,false])
            .show_rows(ui,35.0,self.inventory_items.len(),|ui,range|{
                for index in range {
                    theme::table_row(ui,&[(&self.inventory_items[index].name,560.0)]);
                    ui.separator();
                }
            });
    }

    fn draw_divisions(&self,ui:&mut Ui) {
        theme::table_header_sized(ui,&[
            ("DIVISION",300.0),("EMPLOYEES",130.0),("ASSETS",130.0)
        ]);
        egui::ScrollArea::vertical().auto_shrink([false,false])
            .show_rows(ui,36.0,self.inventory_divisions.len(),|ui,range|{
                for index in range {
                    let division=&self.inventory_divisions[index];
                    let employees=division.employee_count.to_string();
                    let items=division.item_count.to_string();
                    theme::table_row(ui,&[
                        (&division.name,300.0),(&employees,130.0),(&items,130.0)
                    ]);
                    ui.separator();
                }
            });
    }

    fn draw_assignments(&self,ui:&mut Ui) {
        theme::table_header_sized(ui,&[
            ("EMPLOYEE ID",105.0),("EMPLOYEE",155.0),("ASSET",155.0),
            ("REFERENCE KEY",160.0),("ATTRIBUTES",250.0)
        ]);
        egui::ScrollArea::horizontal().show(ui,|ui|{
            egui::ScrollArea::vertical().auto_shrink([false,false])
                .show_rows(ui,40.0,self.inventory_assignments.len(),|ui,range|{
                    for index in range {
                        let asset=&self.inventory_assignments[index];
                        let attributes=asset.attributes.iter()
                            .map(|item|format!("{}: {}",item.name,item.value))
                            .collect::<Vec<_>>().join(", ");
                        theme::table_row(ui,&[
                            (&asset.employee_id,105.0),(&asset.employee_name,155.0),
                            (&asset.item_name,155.0),(&asset.unique_key,160.0),
                            (&attributes,250.0)
                        ]);
                        ui.separator();
                    }
                });
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
                self.inventory_employees.iter().map(|e|vec![e.id.clone(),e.name.clone(),e.division.clone()]).collect()
            ),
            InventoryMode::Items=>(vec!["Name"],
                self.inventory_items.iter().map(|i|vec![i.name.clone()]).collect()),
            InventoryMode::Divisions=>(vec!["Division","Employees","Items"],
                self.inventory_divisions.iter().map(|d|vec![
                    d.name.clone(),d.employee_count.to_string(),d.item_count.to_string()
                ]).collect()),
            InventoryMode::UniqueKey=>(vec!["Employee ID","Employee Name","Item Name","Unique Key"],
                self.inventory_assignments.iter().map(|a|vec![
                    a.employee_id.clone(),a.employee_name.clone(),
                    a.item_name.clone(),a.unique_key.clone()
                ]).collect()),
            InventoryMode::EmployeeItems=>(vec!["Employee ID","Employee Name","Item Name","Unique Key","Attributes"],
                self.inventory_assignments.iter().map(|a|vec![
                    a.employee_id.clone(),a.employee_name.clone(),a.item_name.clone(),a.unique_key.clone(),
                    a.attributes.iter().map(|attr|format!("{}: {}",attr.name,attr.value))
                        .collect::<Vec<_>>().join(", ")
                ]).collect()),
        };
        self.message=match reports::export_search(path,&headers,&rows) {
            Ok(())=>"Results exported".into(),Err(err)=>err.to_string()
        };
    }

    fn execute_removal(&mut self, removal: PendingRemoval) {
        let Some(db)=self.db.as_mut() else{return};
        let mut errors=Vec::new();
        match removal {
            PendingRemoval::Items(ids)=>{
                for id in ids {
                    if let Err(err)=db.remove_item(id) {errors.push(format!("{id}: {err}"))}
                }
            }
            PendingRemoval::Employees(ids)=>{
                for id in ids {
                    if let Err(err)=db.remove_employee(&id) {errors.push(format!("{id}: {err}"))}
                }
            }
            PendingRemoval::Divisions(ids)=>{
                for id in ids {
                    if let Err(err)=db.remove_division(id) {errors.push(format!("{id}: {err}"))}
                }
            }
            PendingRemoval::Assignment(id)=>{
                if let Err(err)=db.remove_assignment(id) {errors.push(format!("{id}: {err}"))}
                self.selected_assignment=None;
            }
        }
        if errors.is_empty() {
            self.message="Selected records removed".into();
        }else{
            self.message=errors.join("; ");
        }
        self.selection.clear();
        self.reload();
        if !self.selected_employee.is_empty() {self.load_selected_assets();}
    }

    fn backup_database(&mut self) {
        let Some(path)=rfd::FileDialog::new()
            .add_filter("SQLite database",&["db"])
            .set_file_name("inventory-backup.db").save_file() else{return};
        let Some(db)=self.db.as_ref() else{return};
        self.message=match db.backup_to(&path) {
            Ok(())=>format!("Verified database backup created: {}",path.display()),
            Err(err)=>err.to_string(),
        };
    }

    fn package(&mut self) {
        let Some(output)=rfd::FileDialog::new()
            .add_filter("ZIP archive",&["zip"]).set_file_name("InMan.zip").save_file() else{return};
        let result=(||->anyhow::Result<()> {
            let executable=std::env::current_exe()?;
            let temp=tempfile::tempdir()?;
            let snapshot=temp.path().join("inventory.db");
            let db=self.db.as_ref().ok_or_else(||anyhow::anyhow!(
                "Database is not loaded"
            ))?;
            // Package a consistent snapshot instead of blindly copying a live SQLite file.
            db.backup_to(&snapshot)?;
            reports::package_app(&output,&executable,&snapshot)?;
            Ok(())
        })();
        self.message=match result {
            Ok(())=>format!("Application packaged: {}",output.display()),
            Err(err)=>err.to_string(),
        };
    }

}

impl eframe::App for InManApp {
    fn ui(&mut self, ui:&mut Ui, _frame:&mut eframe::Frame) {
        if !self.activated {
            self.license_screen(ui);
            status_message(ui,&self.message);
            record_first_frame();
            return;
        }
        egui::Panel::left("inman_sidebar").exact_size(205.0)
            .resizable(false).show(ui,|panel|{
                self.sidebar(panel);
            });
        egui::CentralPanel::default().show(ui,|main|{
            main.add_space(12.0);
            match self.screen {
                Screen::Dashboard=>self.dashboard(main),
                Screen::Inventory=>self.inventory(main),
                Screen::Manager=>self.manager(main),
                Screen::Tool=>self.tool_screen(main),
                Screen::Settings=>self.settings(main),
            }
            if !self.message.is_empty() {
                main.add_space(16.0);
                status_message(main,&self.message);
            }
        });

        if let Some(removal)=self.pending_removal.as_ref() {
            let (count,description)=match removal {
                PendingRemoval::Items(records)=>(records.len(),"item type(s)"),
                PendingRemoval::Employees(records)=>(records.len(),"employee(s)"),
                PendingRemoval::Divisions(records)=>(records.len(),"division(s)"),
                PendingRemoval::Assignment(_)=>(1,"asset assignment"),
            };
            let mut choice=None;
            egui::Window::new("Confirm Removal")
                .collapsible(false).resizable(false)
                .show(ui.ctx(),|dialog|{
                    dialog.label(format!(
                        "Remove {count} {description}? This action cannot be undone."
                    ));
                    dialog.horizontal(|dialog|{
                        if dialog.button("Cancel").clicked(){choice=Some(false);}
                        if dialog.add(
                            egui::Button::new("Remove").fill(pink())
                        ).clicked(){choice=Some(true);}
                    });
                });
            if let Some(confirmed)=choice {
                let selected=self.pending_removal.take();
                if confirmed && let Some(removal)=selected {
                    self.execute_removal(removal);
                }
            }
        }
        record_first_frame();
    }
}

impl Drop for InManApp {
    fn drop(&mut self) {
        logging::startup("shutdown", "application state dropped");
    }
}
