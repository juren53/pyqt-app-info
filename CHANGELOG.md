# Changelog

## v0.1.0 — 2026-02-03

Initial release.

- **Frozen detection** — `detect_frozen()` identifies PyInstaller and cx_Freeze executables via `sys.frozen` / `sys._MEIPASS`
- **Tool registry** — `ToolRegistry` with `ToolSpec` for declaring external CLI tools (e.g. ExifTool), automatic path discovery via `shutil.which()` with fallback paths, and version retrieval
- **App info gathering** — `gather_info()` combines app identity, auto-detected runtime environment, and tool results into a single `AppInfo` object with `.to_dict()` and `.summary_lines` helpers
- **About dialog** — `AboutDialog` for PyQt6 apps, fully parameterized from `AppInfo` — identity/features section plus selectable technical details
- **Zero base dependencies** — core uses only stdlib; PyQt6 is an optional extra (`pip install pyqt-app-info[qt]`)
