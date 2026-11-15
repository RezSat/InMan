//! Desktop display preferences. Stored separately from the inventory database.
use std::{fs, path::PathBuf};

pub const MIN_ZOOM: f32 = 1.0;
pub const MAX_ZOOM: f32 = 1.5;
pub const DEFAULT_ZOOM: f32 = 1.12;

fn preference_file() -> PathBuf {
    std::env::var_os("LOCALAPPDATA")
        .filter(|value| !value.is_empty())
        .map(PathBuf::from)
        .unwrap_or_else(std::env::temp_dir)
        .join("InMan")
        .join("ui-scale.txt")
}

fn normalize(value: f32) -> f32 {
    if value.is_finite() {
        (value.clamp(MIN_ZOOM, MAX_ZOOM) * 20.0).round() / 20.0
    } else {
        DEFAULT_ZOOM
    }
}

pub fn load() -> f32 {
    fs::read_to_string(preference_file())
        .ok()
        .and_then(|contents| contents.trim().parse::<f32>().ok())
        .map(normalize)
        .unwrap_or(DEFAULT_ZOOM)
}

pub fn save(value: f32) -> std::io::Result<()> {
    let path = preference_file();
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent)?;
    }
    fs::write(path, format!("{:.2}\n", normalize(value)))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn zoom_range_is_bounded_and_rounded() {
        assert_eq!(normalize(0.3), MIN_ZOOM);
        assert_eq!(normalize(3.0), MAX_ZOOM);
        assert_eq!(normalize(1.127), 1.15);
        assert_eq!(normalize(f32::NAN), DEFAULT_ZOOM);
    }
}
