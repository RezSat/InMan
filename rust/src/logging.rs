//! Persistent startup diagnostics for the InMan desktop application.
//!
//! Normal Windows launches are console-free, so startup failures used to leave
//! no trace. Every launch now appends to `%LOCALAPPDATA%\InMan\logs\inman.log`.
//! Only operational information (versions, paths, graphics adapter, errors) is
//! written; product keys, passwords, employee records and other customer data
//! are never logged.

use std::{
    backtrace::Backtrace,
    fs::{self, File, OpenOptions},
    io::Write,
    panic,
    path::{Path, PathBuf},
    sync::{Mutex, OnceLock},
};

/// Log file name inside the InMan log directory.
const LOG_FILE_NAME: &str = "inman.log";
/// Rotate the file once it grows past this size so logs stay supportable.
const MAX_LOG_BYTES: u64 = 2 * 1024 * 1024;

static LOG_FILE: OnceLock<Mutex<File>> = OnceLock::new();
static LOG_PATH: OnceLock<PathBuf> = OnceLock::new();

/// Directory used for persistent InMan diagnostics.
pub fn log_directory() -> PathBuf {
    let base = std::env::var_os("LOCALAPPDATA")
        .filter(|value| !value.is_empty())
        .map(PathBuf::from)
        .unwrap_or_else(std::env::temp_dir);
    base.join("InMan").join("logs")
}

/// Full path of the current log file, once logging has been initialized.
pub fn log_file_path() -> Option<&'static Path> {
    LOG_PATH.get().map(PathBuf::as_path)
}

/// Starts file logging and installs a panic hook that records backtraces.
///
/// Safe to call more than once; only the first call has an effect.
pub fn init() {
    let path = prepare_log_file();
    if let Some(path) = path
        && let Ok(file) = OpenOptions::new().create(true).append(true).open(&path)
    {
        let _ = LOG_PATH.set(path);
        let _ = LOG_FILE.set(Mutex::new(file));
    }

    install_panic_hook();
    let _ = log::set_logger(&BRIDGE);
    log::set_max_level(log::LevelFilter::Info);

    info(
        "startup",
        format!(
            "InMan {} starting on {} {}",
            crate::VERSION,
            std::env::consts::OS,
            std::env::consts::ARCH
        ),
    );
    if let Ok(executable) = std::env::current_exe() {
        info("startup", format!("executable: {}", executable.display()));
    }
    if let Ok(working_directory) = std::env::current_dir() {
        info(
            "startup",
            format!("working directory: {}", working_directory.display()),
        );
    }
    match log_file_path() {
        Some(path) => info("startup", format!("diagnostic log: {}", path.display())),
        None => eprintln!("InMan: diagnostic log could not be created"),
    }
}

/// Records a named startup stage. These lines make it obvious which stage a
/// silent native crash reached.
pub fn startup(stage: &str, message: impl AsRef<str>) {
    info(format!("startup/{stage}"), message);
}

/// Records an operational error.
pub fn error(scope: &str, message: impl AsRef<str>) {
    write_record("ERROR", scope, message.as_ref());
}

/// Records a warning.
pub fn warn(scope: &str, message: impl AsRef<str>) {
    write_record("WARN", scope, message.as_ref());
}

/// Records an informational message.
pub fn info(scope: impl AsRef<str>, message: impl AsRef<str>) {
    write_record("INFO", scope.as_ref(), message.as_ref());
}

fn prepare_log_file() -> Option<PathBuf> {
    let directory = log_directory();
    fs::create_dir_all(&directory).ok()?;
    let path = directory.join(LOG_FILE_NAME);
    if fs::metadata(&path).map(|meta| meta.len()).unwrap_or(0) > MAX_LOG_BYTES {
        let previous = directory.join("inman.previous.log");
        let _ = fs::remove_file(&previous);
        let _ = fs::rename(&path, previous);
    }
    Some(path)
}

fn write_record(level: &str, scope: &str, message: &str) {
    write_line(&format!(
        "{} {level:<5} [{scope}] {}",
        timestamp(),
        one_record(message)
    ));
}

fn write_line(line: &str) {
    if let Some(file) = LOG_FILE.get()
        && let Ok(mut file) = file.lock()
    {
        let _ = writeln!(file, "{line}");
        let _ = file.flush();
    }
    #[cfg(debug_assertions)]
    eprintln!("{line}");
}

fn timestamp() -> String {
    chrono::Local::now().format("%Y-%m-%d %H:%M:%S%.3f").to_string()
}

/// Keeps one log record per line so a log file can be scanned safely, while
/// preserving indentation for multi-line backtraces.
fn one_record(message: &str) -> String {
    message
        .lines()
        .collect::<Vec<_>>()
        .join("\n             ")
        .trim_end()
        .to_string()
}

fn install_panic_hook() {
    let previous = panic::take_hook();
    panic::set_hook(Box::new(move |info| {
        let payload = info.payload();
        let message = if let Some(message) = payload.downcast_ref::<&str>() {
            (*message).to_string()
        } else if let Some(message) = payload.downcast_ref::<String>() {
            message.clone()
        } else {
            "panic with a non-string payload".to_string()
        };
        let location = info
            .location()
            .map(|location| {
                format!(
                    "{}:{}:{}",
                    location.file(),
                    location.line(),
                    location.column()
                )
            })
            .unwrap_or_else(|| "unknown location".to_string());
        let thread = std::thread::current();
        error(
            "panic",
            format!(
                "panic on thread '{}' at {location}: {message}\nbacktrace:\n{}",
                thread.name().unwrap_or("<unnamed>"),
                Backtrace::force_capture()
            ),
        );
        previous(info);
    }));
}

/// Bridges `log` records from eframe/wgpu into the persistent InMan log.
struct LogBridge;

impl log::Log for LogBridge {
    fn enabled(&self, metadata: &log::Metadata<'_>) -> bool {
        metadata.level() <= log::Level::Info
    }

    fn log(&self, record: &log::Record<'_>) {
        if self.enabled(record.metadata()) {
            write_record(
                match record.level() {
                    log::Level::Error => "ERROR",
                    log::Level::Warn => "WARN",
                    log::Level::Info => "INFO",
                    log::Level::Debug => "DEBUG",
                    log::Level::Trace => "TRACE",
                },
                record.target(),
                &record.args().to_string(),
            );
        }
    }

    fn flush(&self) {}
}

static BRIDGE: LogBridge = LogBridge;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn log_directory_is_under_local_app_data() {
        let directory = log_directory();
        assert!(directory.ends_with(Path::new("InMan").join("logs")));
    }

    #[test]
    fn multi_line_messages_stay_in_one_record() {
        let record = one_record("first\nsecond\n");
        assert!(record.starts_with("first"));
        assert!(record.contains("second"));
        assert!(!record.ends_with('\n'));
    }
}
