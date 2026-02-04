"""Tests for _compat — frozen-executable detection."""

import sys
from pathlib import Path
from unittest.mock import patch

from pyqt_app_info._compat import FrozenState, detect_frozen, resolve_code_location


class TestDetectFrozen:
    """Tests for detect_frozen()."""

    def test_not_frozen(self):
        """Normal Python source execution — no sys.frozen."""
        state = detect_frozen()
        assert state.is_frozen is False
        assert state.bundler is None
        assert state.executable_path == sys.executable
        assert state.meipass is None

    def test_pyinstaller_frozen(self):
        """Simulate PyInstaller: sys.frozen=True, sys._MEIPASS set."""
        with patch.object(sys, "frozen", True, create=True), \
             patch.object(sys, "_MEIPASS", "/tmp/fake_meipass", create=True):
            state = detect_frozen()
            assert state.is_frozen is True
            assert state.bundler == "PyInstaller"
            assert state.meipass == "/tmp/fake_meipass"

    def test_cxfreeze_frozen(self):
        """Simulate cx_Freeze: sys.frozen=True, no _MEIPASS."""
        with patch.object(sys, "frozen", True, create=True):
            # Ensure _MEIPASS is absent
            if hasattr(sys, "_MEIPASS"):
                with patch.object(sys, "_MEIPASS", None, create=True):
                    pass  # shouldn't happen in normal test env
            state = detect_frozen()
            # When no _MEIPASS is set on sys, it should detect cx_Freeze
            # (but only if frozen is True)
            if not hasattr(sys, "_MEIPASS"):
                assert state.bundler == "cx_Freeze"

    def test_frozen_state_is_immutable(self):
        """FrozenState is a frozen dataclass."""
        state = detect_frozen()
        try:
            state.is_frozen = True  # type: ignore[misc]
            assert False, "Should have raised"
        except AttributeError:
            pass


class TestResolveCodeLocation:
    """Tests for resolve_code_location()."""

    def test_from_source_with_caller_file(self):
        """Returns resolved caller_file when not frozen."""
        result = resolve_code_location(__file__)
        assert result == str(Path(__file__).resolve())

    def test_from_source_no_caller_file(self):
        """Falls back to sys.executable when caller_file is None."""
        result = resolve_code_location(None)
        assert result == sys.executable

    def test_frozen_ignores_caller_file(self):
        """When frozen, always returns sys.executable."""
        with patch.object(sys, "frozen", True, create=True), \
             patch.object(sys, "_MEIPASS", "/tmp/mei", create=True):
            result = resolve_code_location("/some/source/file.py")
            assert result == sys.executable
