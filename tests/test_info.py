"""Tests for info — AppIdentity, ExecutionInfo, AppInfo, gather_info()."""

import sys
from unittest.mock import patch

from pyqt_app_info.info import AppIdentity, AppInfo, ExecutionInfo, gather_info
from pyqt_app_info.tools import ToolRegistry, ToolResult, ToolSpec


class TestAppIdentity:
    """AppIdentity defaults."""

    def test_minimal(self):
        ident = AppIdentity(name="TestApp")
        assert ident.name == "TestApp"
        assert ident.short_name == ""
        assert ident.features == []

    def test_full(self):
        ident = AppIdentity(
            name="My App",
            short_name="MA",
            version="1.0",
            commit_date="2025-01-01",
            author="Dev",
            description="A test app",
            features=["feat1", "feat2"],
        )
        assert ident.short_name == "MA"
        assert len(ident.features) == 2


class TestGatherInfo:
    """Tests for gather_info()."""

    def test_basic_gather(self):
        """gather_info produces valid AppInfo with no registry."""
        ident = AppIdentity(name="Test", version="0.1")
        info = gather_info(ident, caller_file=__file__)

        assert info.identity.name == "Test"
        assert info.execution.python_executable == sys.executable
        assert info.execution.is_frozen is False
        assert info.execution.execution_mode == "Python source"
        assert info.tools == []

    def test_gather_with_registry(self):
        """gather_info includes tool detection results."""
        ident = AppIdentity(name="Test")
        reg = ToolRegistry()
        reg.register(ToolSpec(name="FakeTool", command="no_such_binary_xyz"))

        info = gather_info(ident, registry=reg)
        assert len(info.tools) == 1
        assert info.tools[0].name == "FakeTool"
        assert info.tools[0].status == "not_found"

    def test_gather_frozen(self):
        """gather_info detects frozen mode."""
        ident = AppIdentity(name="Frozen")
        with patch.object(sys, "frozen", True, create=True), \
             patch.object(sys, "_MEIPASS", "/tmp/mei", create=True):
            info = gather_info(ident)
            assert info.execution.is_frozen is True
            assert info.execution.execution_mode == "Compiled executable"
            assert info.execution.bundler == "PyInstaller"


class TestAppInfo:
    """Tests for AppInfo helpers."""

    def _make_info(self) -> AppInfo:
        return AppInfo(
            identity=AppIdentity(
                name="Demo App",
                short_name="DA",
                version="2.0",
                commit_date="2025-06-01",
                description="A demo",
                features=["Feature A"],
            ),
            execution=ExecutionInfo(
                python_executable="/usr/bin/python3",
                python_version="3.12.0",
                code_location="/home/user/app.py",
                os_platform="Linux-6.1",
                is_frozen=False,
                execution_mode="Python source",
            ),
            tools=[
                ToolResult(name="ExifTool", path="/usr/bin/exiftool",
                           version="12.50", status="available"),
                ToolResult(name="Missing", status="not_found"),
            ],
        )

    def test_to_dict(self):
        d = self._make_info().to_dict()
        assert d["identity"]["name"] == "Demo App"
        assert d["execution"]["is_frozen"] is False
        assert len(d["tools"]) == 2
        assert d["tools"][0]["status"] == "available"

    def test_summary_lines(self):
        lines = self._make_info().summary_lines
        assert any("Demo App" in l for l in lines)
        assert any("Python source" in l for l in lines)
        assert any("ExifTool" in l and "12.50" in l for l in lines)
        assert any("Missing" in l and "not found" in l for l in lines)

    def test_summary_lines_tool_error(self):
        """Tool with path but no version shows 'found but version unavailable'."""
        info = AppInfo(
            identity=AppIdentity(name="X"),
            execution=ExecutionInfo(),
            tools=[ToolResult(name="Broken", path="/usr/bin/broken", status="error")],
        )
        lines = info.summary_lines
        assert any("Broken" in l and "unavailable" in l for l in lines)
