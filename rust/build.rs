fn main() {
    #[cfg(windows)]
    {
        let mut resources = winres::WindowsResource::new();
        resources.set_icon("../assets/CustomTkinter_icon_Windows.ico");
        resources.set("FileDescription", "InMan Inventory Manager");
        resources.set("ProductName", "InMan");
        resources.set("FileVersion", "2.0.0.0");
        resources.set("ProductVersion", "2.0.0.0");
        resources.compile().expect("failed to embed original IM executable icon");
    }
}
