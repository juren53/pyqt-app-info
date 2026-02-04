"""pyqt-app-info — reusable app-info gathering and About dialog for PyQt apps.

Core API (stdlib only, no PyQt6 needed)::

    from pyqt_app_info import AppIdentity, gather_info
    info = gather_info(AppIdentity(name="My App", version="1.0"))

Qt dialog (requires ``pip install pyqt-app-info[qt]``)::

    from pyqt_app_info.qt import AboutDialog
    AboutDialog(info, parent=window).exec()
"""

from .info import AppIdentity, AppInfo, ExecutionInfo, gather_info
from .tools import ToolRegistry, ToolResult, ToolSpec

__all__ = [
    "AppIdentity",
    "AppInfo",
    "ExecutionInfo",
    "gather_info",
    "ToolRegistry",
    "ToolResult",
    "ToolSpec",
]

__version__ = "0.1.0"
