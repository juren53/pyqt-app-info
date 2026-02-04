"""Tests for tools — ToolSpec, ToolResult, ToolRegistry."""

from unittest.mock import MagicMock, patch

from pyqt_app_info.tools import ToolRegistry, ToolResult, ToolSpec


class TestToolSpec:
    """ToolSpec defaults."""

    def test_defaults(self):
        spec = ToolSpec(name="Foo", command="foo")
        assert spec.version_flag == "--version"
        assert spec.fallback_paths == []
        assert spec.version_timeout == 5.0


class TestToolRegistry:
    """ToolRegistry detection logic."""

    def _make_registry(self, *specs: ToolSpec) -> ToolRegistry:
        reg = ToolRegistry()
        for s in specs:
            reg.register(s)
        return reg

    def test_detect_available_via_which(self):
        """Tool found via shutil.which and version retrieved."""
        spec = ToolSpec(name="ExifTool", command="exiftool", version_flag="-ver")
        reg = self._make_registry(spec)

        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = "12.50\n"

        with patch("pyqt_app_info.tools.shutil.which", return_value="/usr/bin/exiftool"), \
             patch("pyqt_app_info.tools.subprocess.run", return_value=mock_proc):
            result = reg.detect("ExifTool")
            assert result.status == "available"
            assert result.path == "/usr/bin/exiftool"
            assert result.version == "12.50"

    def test_detect_not_found(self):
        """Tool not found anywhere."""
        spec = ToolSpec(name="Missing", command="no_such_tool")
        reg = self._make_registry(spec)

        with patch("pyqt_app_info.tools.shutil.which", return_value=None):
            result = reg.detect("Missing")
            assert result.status == "not_found"
            assert result.path is None

    def test_detect_fallback_path(self):
        """Tool found via fallback path when shutil.which fails."""
        spec = ToolSpec(
            name="ExifTool",
            command="exiftool",
            version_flag="-ver",
            fallback_paths=["/opt/exiftool/exiftool"],
        )
        reg = self._make_registry(spec)

        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = "12.40\n"

        with patch("pyqt_app_info.tools.shutil.which", return_value=None), \
             patch("pyqt_app_info.tools.Path.is_file", return_value=True), \
             patch("pyqt_app_info.tools.subprocess.run", return_value=mock_proc):
            result = reg.detect("ExifTool")
            assert result.status == "available"
            assert result.path == "/opt/exiftool/exiftool"

    def test_detect_version_error(self):
        """Tool found but version command returns non-zero."""
        spec = ToolSpec(name="Bad", command="bad")
        reg = self._make_registry(spec)

        mock_proc = MagicMock()
        mock_proc.returncode = 1
        mock_proc.stdout = ""

        with patch("pyqt_app_info.tools.shutil.which", return_value="/usr/bin/bad"), \
             patch("pyqt_app_info.tools.subprocess.run", return_value=mock_proc):
            result = reg.detect("Bad")
            assert result.status == "error"
            assert result.path == "/usr/bin/bad"

    def test_detect_timeout(self):
        """Tool found but version command times out."""
        import subprocess
        spec = ToolSpec(name="Slow", command="slow", version_timeout=0.1)
        reg = self._make_registry(spec)

        with patch("pyqt_app_info.tools.shutil.which", return_value="/usr/bin/slow"), \
             patch("pyqt_app_info.tools.subprocess.run",
                   side_effect=subprocess.TimeoutExpired("slow", 0.1)):
            result = reg.detect("Slow")
            assert result.status == "error"
            assert result.path == "/usr/bin/slow"

    def test_detect_all(self):
        """detect_all returns results for every registered tool."""
        reg = self._make_registry(
            ToolSpec(name="A", command="a"),
            ToolSpec(name="B", command="b"),
        )
        with patch("pyqt_app_info.tools.shutil.which", return_value=None):
            results = reg.detect_all()
            assert len(results) == 2
            assert results[0].name == "A"
            assert results[1].name == "B"

    def test_detect_unknown_raises(self):
        """Detecting an unregistered name raises KeyError."""
        reg = ToolRegistry()
        try:
            reg.detect("nope")
            assert False, "Expected KeyError"
        except KeyError:
            pass

    def test_multiline_version_takes_first_line(self):
        """Only the first line of version output is captured."""
        spec = ToolSpec(name="Multi", command="multi")
        reg = self._make_registry(spec)

        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = "1.2.3\nSome extra info\n"

        with patch("pyqt_app_info.tools.shutil.which", return_value="/usr/bin/multi"), \
             patch("pyqt_app_info.tools.subprocess.run", return_value=mock_proc):
            result = reg.detect("Multi")
            assert result.version == "1.2.3"
