pub mod db;
pub mod licensing;
pub mod logging;
pub mod reports;
pub mod ui;

pub const VERSION: &str = "2.0.0-rc.4";
pub const PALETTE: Palette = Palette {
    black: [0x2c, 0x36, 0x3f],
    pink: [0xe7, 0x5a, 0x7c],
    darker_pink: [0x8f, 0x34, 0x4a],
    white: [0xf2, 0xf5, 0xea],
    ash: [0xd6, 0xdb, 0xd2],
    green: [0x4c, 0xaf, 0x50],
    secondary_bg: [0x1a, 0x1a, 0x1a],
};

pub struct Palette {
    pub black: [u8; 3],
    pub pink: [u8; 3],
    pub darker_pink: [u8; 3],
    pub white: [u8; 3],
    pub ash: [u8; 3],
    pub green: [u8; 3],
    pub secondary_bg: [u8; 3],
}
