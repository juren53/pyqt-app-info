# pyqt-app-info

Reusable system/application info gathering and About dialog for PyQt apps.

Detects whether the app is running from Python source or a compiled
(PyInstaller / cx_Freeze) executable, discovers external CLI tools, and
provides a ready-made About dialog.

## Installation

### From PyPI

**Core only** (stdlib, zero dependencies):

```bash
pip install pyqt-app-info
```

**With Qt dialog** (adds PyQt6):

```bash
pip install pyqt-app-info[qt]
```

### From Local Repository

```bash
python -m pip install C:\Users\jimur\Projects\pyqt-app-info
```

### From GitHub

```bash
pip install git+https://github.com/juren53/pyqt-app-info
```

## Quick Start

```python
from pyqt_app_info import AppIdentity, ToolSpec, ToolRegistry, gather_info

identity = AppIdentity(
    name="My Application",
    short_name="MyApp",
    version="1.0.0",
    commit_date="2025-06-01",
    description="Does useful things.",
    features=["Feature A", "Feature B"],
)

registry = ToolRegistry()
registry.register(ToolSpec(name="ExifTool", command="exiftool", version_flag="-ver"))

info = gather_info(identity, registry=registry, caller_file=__file__)

# CLI summary
for line in info.summary_lines:
    print(line)

# Serializable dict (for logging, JSON, etc.)
print(info.to_dict())
```

### About Dialog (requires PyQt6)

```python
from pyqt_app_info.qt import AboutDialog

AboutDialog(info, parent=self).exec()
```

## API

### Core (no dependencies)

| Class / Function | Description |
|---|---|
| `AppIdentity` | Static app identity (name, version, features, ...) |
| `ExecutionInfo` | Auto-detected runtime environment |
| `AppInfo` | Combined identity + execution + tools |
| `gather_info(identity, *, registry, caller_file)` | Detect everything in one call |
| `ToolSpec` | Specification for an external CLI tool |
| `ToolResult` | Detection result for one tool |
| `ToolRegistry` | Register and detect multiple tools |

### Qt (requires `pyqt-app-info[qt]`)

| Class | Description |
|---|---|
| `AboutDialog(app_info, parent)` | Parameterized About dialog |

## Frozen Detection

The core novelty: `gather_info()` automatically detects whether the
process is running from source or a bundled executable.

| Scenario | `execution_mode` | `is_frozen` | `bundler` |
|---|---|---|---|
| Normal `python app.py` | `"Python source"` | `False` | `None` |
| PyInstaller one-file | `"Compiled executable"` | `True` | `"PyInstaller"` |
| cx_Freeze | `"Compiled executable"` | `True` | `"cx_Freeze"` |

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history, or view the
[latest release](https://github.com/juren53/pyqt-app-info/releases/latest) on GitHub.

## License

MIT
