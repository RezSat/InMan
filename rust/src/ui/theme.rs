//! InMan's desktop design system. Visual concerns stay out of database code.
use eframe::egui::{self, Color32, Frame, Margin, RichText, Stroke, Ui, Vec2};

pub const BACKGROUND: Color32 = Color32::from_rgb(16, 19, 25);
pub const SIDEBAR: Color32 = Color32::from_rgb(22, 26, 34);
pub const SURFACE: Color32 = Color32::from_rgb(29, 34, 43);
pub const SURFACE_RAISED: Color32 = Color32::from_rgb(37, 43, 54);
pub const BORDER: Color32 = Color32::from_rgb(52, 59, 72);
pub const ACCENT: Color32 = Color32::from_rgb(231, 90, 124);
pub const ACCENT_HOVER: Color32 = Color32::from_rgb(245, 112, 146);
pub const TEXT: Color32 = Color32::from_rgb(242, 245, 234);
pub const MUTED: Color32 = Color32::from_rgb(156, 167, 180);
pub const SUCCESS: Color32 = Color32::from_rgb(92, 196, 146);
pub const DANGER: Color32 = Color32::from_rgb(238, 109, 123);

pub fn install(ctx: &egui::Context) {
    let mut visuals = egui::Visuals::dark();
    visuals.panel_fill = BACKGROUND;
    visuals.window_fill = SURFACE;
    visuals.faint_bg_color = SIDEBAR;
    visuals.extreme_bg_color = SIDEBAR;
    visuals.override_text_color = Some(TEXT);
    visuals.selection.bg_fill = ACCENT.gamma_multiply(0.35);
    visuals.selection.stroke = Stroke::new(1.5, ACCENT);
    visuals.widgets.noninteractive.bg_fill = SURFACE;
    visuals.widgets.noninteractive.bg_stroke = Stroke::new(1.0, BORDER);
    visuals.widgets.inactive.bg_fill = SURFACE_RAISED;
    visuals.widgets.inactive.bg_stroke = Stroke::new(1.0, BORDER);
    visuals.widgets.inactive.fg_stroke = Stroke::new(1.0, TEXT);
    visuals.widgets.hovered.bg_fill = Color32::from_rgb(49, 55, 68);
    visuals.widgets.hovered.bg_stroke = Stroke::new(1.0, ACCENT.gamma_multiply(0.7));
    visuals.widgets.hovered.fg_stroke = Stroke::new(1.0, TEXT);
    visuals.widgets.active.bg_fill = ACCENT.gamma_multiply(0.30);
    visuals.widgets.active.bg_stroke = Stroke::new(1.5, ACCENT);
    visuals.widgets.active.fg_stroke = Stroke::new(1.0, TEXT);
    visuals.window_shadow = egui::Shadow::NONE;
    ctx.set_visuals(visuals);

    // Use the local Windows UI font. We do not ship proprietary font files.
    #[cfg(windows)]
    if let Some(windows) = std::env::var_os("WINDIR") {
        let path = std::path::PathBuf::from(windows).join("Fonts").join("segoeui.ttf");
        if let Ok(bytes) = std::fs::read(path) {
            let mut fonts = egui::FontDefinitions::default();
            fonts.font_data.insert(
                "Segoe UI".to_owned(),
                std::sync::Arc::new(egui::FontData::from_owned(bytes)),
            );
            fonts.families.entry(egui::FontFamily::Proportional)
                .or_default().insert(0, "Segoe UI".to_owned());
            ctx.set_fonts(fonts);
        }
    }

    let mut style = (*ctx.style_of(egui::Theme::Dark)).clone();
    style.text_styles.insert(egui::TextStyle::Body, egui::FontId::proportional(15.0));
    style.text_styles.insert(egui::TextStyle::Button, egui::FontId::proportional(14.5));
    style.text_styles.insert(egui::TextStyle::Small, egui::FontId::proportional(12.5));
    style.text_styles.insert(egui::TextStyle::Heading, egui::FontId::proportional(24.0));
    style.spacing.item_spacing = Vec2::new(10.0, 10.0);
    style.spacing.button_padding = Vec2::new(14.0, 9.0);
    style.spacing.interact_size = Vec2::new(42.0, 36.0);
    style.spacing.window_margin = Margin::same(18);
    ctx.set_style_of(egui::Theme::Dark, style);
}

pub fn card() -> Frame {
    Frame::new()
        .fill(SURFACE)
        .stroke(Stroke::new(1.0, BORDER))
        .corner_radius(egui::CornerRadius::same(12))
        .inner_margin(Margin::same(18))
}

pub fn subtle_card() -> Frame {
    Frame::new()
        .fill(SIDEBAR)
        .stroke(Stroke::new(1.0, BORDER))
        .corner_radius(egui::CornerRadius::same(10))
        .inner_margin(Margin::same(14))
}

pub fn heading(ui: &mut Ui, kicker: &str, title: &str, description: &str) {
    ui.label(RichText::new(kicker.to_uppercase()).size(11.0).strong().color(ACCENT));
    ui.label(RichText::new(title).size(29.0).strong().color(TEXT));
    if !description.is_empty() {
        ui.label(RichText::new(description).size(14.0).color(MUTED));
    }
    ui.add_space(15.0);
}

pub fn section(ui: &mut Ui, title: &str, supporting: &str) {
    ui.label(RichText::new(title).size(19.0).strong().color(TEXT));
    if !supporting.is_empty() {
        ui.label(RichText::new(supporting).size(13.0).color(MUTED));
    }
    ui.add_space(9.0);
}

pub fn primary(ui: &mut Ui, label: &str) -> bool {
    ui.add(egui::Button::new(RichText::new(label).strong().color(BACKGROUND))
        .fill(ACCENT)
        .stroke(Stroke::NONE)
        .corner_radius(egui::CornerRadius::same(8))
        .min_size(Vec2::new(118.0, 36.0)))
        .clicked()
}

pub fn secondary(ui: &mut Ui, label: &str) -> bool {
    ui.add(egui::Button::new(RichText::new(label).color(TEXT))
        .fill(SURFACE_RAISED)
        .stroke(Stroke::new(1.0, BORDER))
        .corner_radius(egui::CornerRadius::same(8))
        .min_size(Vec2::new(112.0, 36.0)))
        .clicked()
}

pub fn sidebar_item(ui: &mut Ui, text: &str, active: bool) -> bool {
    let fill = if active { ACCENT.gamma_multiply(0.18) } else { Color32::TRANSPARENT };
    let foreground = if active { ACCENT_HOVER } else { MUTED };
    let available = ui.available_width();
    ui.add_sized(
        [available, 43.0],
        egui::Button::new(RichText::new(text).color(foreground).size(14.0).strong())
            .fill(fill)
            .stroke(if active { Stroke::new(1.0, ACCENT.gamma_multiply(0.4)) } else { Stroke::NONE })
            .corner_radius(egui::CornerRadius::same(8)),
    ).clicked()
}

/// Widths follow the window size and never shrink below a readable minimum.
pub fn column_widths(available: f32, proportions: &[f32], minimum: f32) -> Vec<f32> {
    let width=available.max(minimum).max(0.0);
    let gaps=proportions.len().saturating_sub(1) as f32 * 9.0;
    let content=(width-24.0-gaps).max(proportions.len() as f32*65.0);
    let sum=proportions.iter().sum::<f32>().max(0.001);
    proportions.iter().map(|weight|content*weight/sum).collect()
}

pub fn table_header_sized(ui:&mut Ui, columns:&[(&str,f32)]) {
    Frame::new().fill(SURFACE_RAISED)
        .corner_radius(egui::CornerRadius::same(6))
        .inner_margin(Margin::symmetric(12,9))
        .show(ui,|ui|{
            ui.horizontal(|ui|{
                ui.spacing_mut().item_spacing.x=9.0;
                for (name,width) in columns {
                    ui.add_sized([*width,22.0],egui::Label::new(
                        RichText::new(*name).size(12.0).strong().color(MUTED)
                    ).truncate());
                }
            });
        });
}

pub fn table_row(ui:&mut Ui, columns:&[(&str,f32)]) {
    Frame::new().inner_margin(Margin::symmetric(12,4)).show(ui,|ui|{
        ui.horizontal(|ui|{
            ui.spacing_mut().item_spacing.x=9.0;
            for (value,width) in columns {
                ui.add_sized([*width,24.0],egui::Label::new(
                    RichText::new(*value).size(14.0).color(TEXT)
                ).truncate()).on_hover_text(*value);
            }
        });
    });
}

#[cfg(test)]
mod layout_tests {
    use super::*;
    #[test]
    fn table_columns_fill_space_and_respect_minimum() {
        let widths=column_widths(1200.0,&[0.2,0.4,0.4],580.0);
        assert_eq!(widths.len(),3);
        assert!(widths[1]>widths[0]);
        assert!((widths.iter().sum::<f32>()+24.0+18.0-1200.0).abs()<0.01);
        let narrow=column_widths(200.0,&[1.0,1.0],480.0);
        assert!(narrow.iter().sum::<f32>()>400.0);
    }
}
