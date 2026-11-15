use crate::db::{Assignment, Database, Division, Employee};
use anyhow::{anyhow, ensure, Result};
use calamine::{open_workbook_auto, Reader};
use rust_xlsxwriter::{Color, Format, FormatAlign, FormatBorder, Workbook};
use std::{collections::BTreeMap, path::Path};

const HEADER_RGB: u32 = 0xD3D3D3;

fn heading() -> Format {
    Format::new()
        .set_bold()
        .set_font_size(12)
        .set_background_color(Color::RGB(HEADER_RGB))
        .set_align(FormatAlign::Center)
        .set_align(FormatAlign::VerticalCenter)
        .set_border(FormatBorder::Thin)
}

fn cell_style() -> Format {
    Format::new()
        .set_align(FormatAlign::Center)
        .set_align(FormatAlign::VerticalCenter)
        .set_border(FormatBorder::Thin)
}

fn total_style() -> Format {
    Format::new().set_bold().set_underline(rust_xlsxwriter::FormatUnderline::Single)
}

fn grand_style() -> Format {
    Format::new().set_bold().set_font_size(11)
        .set_underline(rust_xlsxwriter::FormatUnderline::Double)
}

fn width_for(value: &str) -> f64 {
    let mut size = value.chars().count() as f64;
    if value.chars().any(|ch| ch.is_uppercase()) { size *= 1.1; }
    if value.chars().any(|ch| !ch.is_alphanumeric()) { size *= 1.1; }
    size + 4.0
}

fn write_headings(
    sheet: &mut rust_xlsxwriter::Worksheet, titles: &[&str]
) -> Result<Vec<f64>> {
    let mut widths = Vec::with_capacity(titles.len());
    for (col, title) in titles.iter().enumerate() {
        sheet.write_string_with_format(0,col as u16,*title,&heading())?;
        widths.push(width_for(title));
    }
    Ok(widths)
}

fn fit_columns(sheet: &mut rust_xlsxwriter::Worksheet, widths: &[f64]) -> Result<()> {
    for (col,width) in widths.iter().enumerate() {
        sheet.set_column_width(col as u16, width.clamp(10.0,60.0))?;
    }
    Ok(())
}

pub fn export_employees(db: &Database, path: impl AsRef<Path>) -> Result<()> {
    let employees = db.employees("",None)?;
    let mut workbook = Workbook::new();
    let sheet = workbook.add_worksheet();
    sheet.set_name("Employees")?;
    let mut widths = write_headings(sheet, &["Employee ID","Name","Division"])?;
    for (index, employee) in employees.iter().enumerate() {
        let row = index as u32 + 1;
        for (col,value) in [employee.id.as_str(),employee.name.as_str(),
                          employee.division.as_str()].into_iter().enumerate() {
            sheet.write_string_with_format(row,col as u16,value,&cell_style())?;
            widths[col] = widths[col].max(width_for(value));
        }
    }
    let total_row = employees.len() as u32 + 2;
    sheet.write_string_with_format(total_row,0,"TOTAL EMPLOYEES COUNT:",&total_style())?;
    sheet.write_number_with_format(total_row,1,employees.len() as f64,&total_style())?;
    fit_columns(sheet,&widths)?;
    workbook.save(path)?;
    Ok(())
}

pub fn export_items(db: &Database, path: impl AsRef<Path>) -> Result<()> {
    let items = db.items("")?;
    let mut workbook = Workbook::new();
    let sheet = workbook.add_worksheet();
    sheet.set_name("Items")?;
    let mut widths = write_headings(sheet,&["Name"])?;
    for (index,item) in items.iter().enumerate() {
        sheet.write_string_with_format(index as u32+1,0,&item.name,&cell_style())?;
        widths[0]=widths[0].max(width_for(&item.name));
    }
    fit_columns(sheet,&widths)?;
    workbook.save(path)?;
    Ok(())
}

pub fn export_inventory(db: &Database, path: impl AsRef<Path>) -> Result<()> {
    let employees = db.employees("",None)?;
    let assignments = db.assignments("",None,None,None)?;
    let mut assets_by_employee: BTreeMap<String,Vec<&Assignment>>=BTreeMap::new();
    for assignment in &assignments {
        assets_by_employee.entry(assignment.employee_id.clone())
            .or_default().push(assignment);
    }
    let mut divisions: Vec<(String,Vec<&Employee>)> = Vec::new();
    for employee in &employees {
        if let Some((_,group))=divisions.iter_mut().find(|(name,_)|name==&employee.division) {
            group.push(employee);
        } else {
            divisions.push((employee.division.clone(),vec![employee]));
        }
    }

    let mut workbook = Workbook::new();
    let sheet = workbook.add_worksheet();
    // openpyxl's default workbook sheet name is "Sheet".
    sheet.set_name("Sheet")?;
    let mut widths=write_headings(sheet,&[
        "Division","Employee Name","Employee ID","Item Name",
        "Unique Key | Reference ID","Attributes"
    ])?;
    let mut row=1_u32;
    let mut total_items=0_usize;
    for (division, members) in &divisions {
        let division_start=row;
        let mut division_items=0_usize;
        widths[0]=widths[0].max(width_for(division));
        for employee in members {
            let assets=assets_by_employee.get(&employee.id);
            let start=row;
            widths[1]=widths[1].max(width_for(&employee.name));
            widths[2]=widths[2].max(width_for(&employee.id));
            if let Some(assets)=assets {
                division_items+=assets.len();
                for (index,asset) in assets.iter().enumerate() {
                    let attr_text=asset.attributes.iter().map(|attr|format!(
                        "{}: {}",attr.name,attr.value
                    )).collect::<Vec<_>>().join(", ");
                    let cols=[
                        if index==0 {division.as_str()} else {""},
                        if index==0 {employee.name.as_str()} else {""},
                        if index==0 {employee.id.as_str()} else {""},
                        asset.item_name.as_str(),
                        asset.unique_key.as_str(),
                        attr_text.as_str()
                    ];
                    for (col,value) in cols.iter().enumerate() {
                        sheet.write_string_with_format(row,col as u16,*value,&cell_style())?;
                        widths[col]=widths[col].max(width_for(value));
                    }
                    row+=1;
                }
                if assets.len()>1 {
                    sheet.merge_range(start,1,row-1,1,&employee.name,&cell_style())?;
                    sheet.merge_range(start,2,row-1,2,&employee.id,&cell_style())?;
                }
            }
        }
        // A one-cell range is not a valid merge in rust_xlsxwriter.
        // The first row already contains the division name.
        if row>division_start+1 {
            sheet.merge_range(division_start,0,row-1,0,division,&cell_style())?;
        }
        widths[0]=widths[0].max(width_for("Total Employees:"));
        widths[2]=widths[2].max(width_for("Total Items:"));
        row+=1;
        sheet.write_string_with_format(row,0,"Total Employees:",&total_style())?;
        sheet.write_number_with_format(row,1,members.len() as f64,&total_style())?;
        sheet.write_string_with_format(row,2,"Total Items:",&total_style())?;
        sheet.write_number_with_format(row,3,division_items as f64,&total_style())?;
        total_items+=division_items;
        row+=2;
    }
    if divisions.len()>1 {
        for (title,count) in [
            ("TOTAL DIVISIONS:",divisions.len()),
            ("TOTAL EMPLOYEES COUNT:",employees.len()),
            ("TOTAL ITEMS COUNT:",total_items)
        ] {
            widths[0]=widths[0].max(width_for(title));
            sheet.write_string_with_format(row,0,title,&grand_style())?;
            sheet.write_number_with_format(row,1,count as f64,&grand_style())?;
            row+=1;
        }
    }
    fit_columns(sheet,&widths)?;
    workbook.save(path)?;
    Ok(())
}

pub fn export_search(
    path: impl AsRef<Path>, headers: &[&str], rows: &[Vec<String>]
) -> Result<()> {
    let mut workbook=Workbook::new();
    let sheet=workbook.add_worksheet();
    let mut widths=write_headings(sheet,headers)?;
    for (i,values) in rows.iter().enumerate() {
        for (j,value) in values.iter().enumerate().take(headers.len()) {
            sheet.write_string_with_format(i as u32+1,j as u16,value,&cell_style())?;
            widths[j]=widths[j].max(width_for(value));
        }
    }
    fit_columns(sheet,&widths)?;
    workbook.save(path)?;
    Ok(())
}

/// Reads the same EMP_ID / Name / Division columns as the Python bulk import.
/// No database writes happen until the operator approves the staged rows.
pub fn read_employee_import(
    path: impl AsRef<Path>, divisions: &[Division]
) -> Result<Vec<(String,String,i64)>> {
    let mut book = open_workbook_auto(path.as_ref())?;
    let range=book.worksheet_range_at(0)
        .ok_or_else(||anyhow!("The spreadsheet contains no worksheets"))??;
    let mut rows=range.rows();
    let headings=rows.next().ok_or_else(||anyhow!("Missing header row"))?;
    let headers: Vec<String>=headings.iter().map(|v|v.to_string()).collect();
    let col=|name:&str| headers.iter().position(|h|h==name)
        .ok_or_else(||anyhow!("Missing {name} column"));
    let id_col=col("EMP_ID")?;
    let name_col=col("Name")?;
    let div_col=col("Division")?;
    let mut records=Vec::new();
    for (index,row) in rows.enumerate() {
        let text=|col:usize|row.get(col).map(|v|v.to_string()).unwrap_or_default();
        let id=text(id_col);
        let name=text(name_col);
        if id.trim().is_empty() && name.trim().is_empty() { continue; }
        ensure!(!id.trim().is_empty() && !name.trim().is_empty(),
                "Row {}: employee ID/name missing",index+2);
        let division=text(div_col);
        let division_id=divisions.iter().find(|d|d.name==division).map(|d|d.id)
            .ok_or_else(||anyhow!("Row {}: unknown division '{}'",index+2,division))?;
        records.push((id,name,division_id));
    }
    Ok(records)
}

pub fn package_app(output: impl AsRef<Path>, executable: impl AsRef<Path>, database: impl AsRef<Path>) -> Result<()> {
    use std::{fs::File, io::{Read,Write}};
    use zip::{write::SimpleFileOptions, CompressionMethod, ZipWriter};
    let mut archive=ZipWriter::new(File::create(output)?);
    for path in [executable.as_ref(),database.as_ref()] {
        let filename=path.file_name().and_then(|s|s.to_str())
            .ok_or_else(||anyhow!("Invalid package filename"))?;
        archive.start_file(
            filename,SimpleFileOptions::default()
                .compression_method(CompressionMethod::Deflated)
        )?;
        let mut input=File::open(path)?;
        let mut buffer=[0_u8;32*1024];
        loop {
            let read=input.read(&mut buffer)?;
            if read==0 {break}
            archive.write_all(&buffer[..read])?;
        }
    }
    archive.finish()?;
    Ok(())
}
