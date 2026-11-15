#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use eframe::egui;
use eframe::wgpu::Backends;
use inman::{logging, ui::InManApp};

const WINDOW_TITLE: &str = "InMan";

fn main() -> eframe::Result {
    logging::init();
    logging::startup("entry", "InMan entry point reached");

    let result = launch();
    match &result {
        Ok(()) => logging::startup("shutdown", "InMan closed normally"),
        Err(error) => {
            logging::error("startup", format!("InMan failed to start: {error}"));
            report_startup_failure(error);
        }
    }
    result
}

fn launch() -> eframe::Result {
    let backends = configured_backends();
    match run(backends) {
        Ok(()) => Ok(()),
        Err(error) => {
            logging::error(
                "graphics",
                format!("graphics backend {backends:?} failed: {error}"),
            );
            // An explicit WGPU_BACKEND is a deliberate support choice; do not
            // silently override it. Only retry if initialization failed before
            // the UI ever rendered (a late event-loop error must not reopen
            // the application).
            if backends == Backends::GL
                || std::env::var_os("WGPU_BACKEND").is_some()
                || inman::ui::has_rendered_frame()
            {
                return Err(error);
            }
            logging::startup("graphics", "retrying with the wgpu GL backend");
            run(Backends::GL)
        }
    }
}

/// Windows defaults to DX12.
///
/// eframe 0.37 uses wgpu and lets it pick Vulkan first. Intel's Vulkan driver
/// (`igvk64.dll`, 31.0.101.2137 on the affected machine) crashes with an access
/// violation while presenting the first frames of this UI. DX12 is the native,
/// supported Windows backend and avoids loading that driver entirely. The
/// standard `WGPU_BACKEND` override remains available for diagnostics.
fn configured_backends() -> Backends {
    let backends = Backends::from_env().unwrap_or_else(|| {
        if cfg!(windows) {
            Backends::DX12
        } else {
            Backends::PRIMARY | Backends::GL
        }
    });
    logging::startup("graphics", format!("configured wgpu backend(s): {backends:?}"));
    backends
}

fn native_options(backends: Backends) -> eframe::NativeOptions {
    let mut wgpu_setup = eframe::egui_wgpu::WgpuSetupCreateNew::without_display_handle();
    wgpu_setup.instance_descriptor.backends = backends;

    let mut options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default()
            .with_inner_size([1200.0, 700.0])
            .with_min_inner_size([800.0, 560.0]),
        ..Default::default()
    };
    options.wgpu_options.wgpu_setup = eframe::egui_wgpu::WgpuSetup::CreateNew(wgpu_setup);
    options
}

fn run(backends: Backends) -> eframe::Result {
    let options = native_options(backends);
    logging::startup(
        "window",
        "creating the native window and initializing eframe/wgpu",
    );
    let result = eframe::run_native(
        WINDOW_TITLE,
        options,
        Box::new(|creation| {
            logging::startup("app", "eframe initialized; constructing InManApp");
            Ok(Box::new(InManApp::new(creation)))
        }),
    );
    match &result {
        Ok(()) => logging::startup("window", "eframe event loop finished"),
        Err(error) => logging::error("window", format!("eframe could not start: {error}")),
    }
    result
}

fn report_startup_failure(error: &eframe::Error) {
    let log_hint = logging::log_file_path()
        .map(|path| format!("\n\nDiagnostic log:\n{}", path.display()))
        .unwrap_or_default();
    let _ = rfd::MessageDialog::new()
        .set_level(rfd::MessageLevel::Error)
        .set_title("InMan could not start")
        .set_description(format!(
            "InMan could not open its application window.\n\n{error}{log_hint}\n\n\
             The diagnostic log records the startup stages that were reached. \
             If the problem continues, update the graphics driver and try again."
        ))
        .show();
}
