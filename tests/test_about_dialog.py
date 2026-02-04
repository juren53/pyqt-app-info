"""Tests for the AboutDialog — import and instantiation smoke tests.

These tests verify that the dialog can be constructed with an AppInfo
object.  Full GUI interaction tests are skipped when PyQt6 is not
available.
"""

import importlib
import sys

import pytest

from pyqt_app_info.info import AppIdentity, AppInfo, ExecutionInfo
from pyqt_app_info.tools import ToolResult


def _pyqt6_available() -> bool:
    try:
        importlib.import_module("PyQt6.QtWidgets")
        return True
    except ImportError:
        return False


pytestmark = pytest.mark.skipif(
    not _pyqt6_available(), reason="PyQt6 not installed"
)


def _make_app_info() -> AppInfo:
    return AppInfo(
        identity=AppIdentity(
            name="Test App",
            short_name="TA",
            version="1.0.0",
            commit_date="2025-01-01",
            author="Tester",
            description="A test application",
            features=["Feature 1", "Feature 2"],
        ),
        execution=ExecutionInfo(
            python_executable=sys.executable,
            python_version="3.12.0",
            code_location="/fake/path/app.py",
            os_platform="Linux-Test",
            is_frozen=False,
            execution_mode="Python source",
        ),
        tools=[
            ToolResult(name="ExifTool", path="/usr/bin/exiftool",
                       version="12.50", status="available"),
            ToolResult(name="Missing", status="not_found"),
            ToolResult(name="Broken", path="/usr/bin/broken", status="error"),
        ],
    )


class TestAboutDialogImport:
    """Verify the qt subpackage imports work."""

    def test_import_about_dialog(self):
        from pyqt_app_info.qt import AboutDialog
        assert AboutDialog is not None

    def test_construct_dialog(self, qapp):
        """Construct the dialog (requires a QApplication via qapp fixture)."""
        from pyqt_app_info.qt import AboutDialog

        info = _make_app_info()
        dialog = AboutDialog(info)
        assert dialog.windowTitle().startswith("About Test App")

    def test_dialog_with_no_tools(self, qapp):
        """Dialog handles empty tool list."""
        from pyqt_app_info.qt import AboutDialog

        info = AppInfo(
            identity=AppIdentity(name="Minimal"),
            execution=ExecutionInfo(),
            tools=[],
        )
        dialog = AboutDialog(info)
        assert dialog is not None

    def test_dialog_with_no_features(self, qapp):
        """Dialog handles identity with no features."""
        from pyqt_app_info.qt import AboutDialog

        info = AppInfo(
            identity=AppIdentity(name="NoFeat", version="0.1"),
            execution=ExecutionInfo(
                execution_mode="Python source",
                os_platform="Test",
            ),
        )
        dialog = AboutDialog(info)
        assert dialog is not None
