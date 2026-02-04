"""Frozen/compiled executable detection.

Detects whether the current process is running from Python source
or a compiled executable (PyInstaller, cx_Freeze, etc.).
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class FrozenState:
    """Result of frozen-executable detection.

    Attributes:
        is_frozen: True if running inside a bundled executable.
        bundler: Name of the bundler ("PyInstaller", "cx_Freeze") or None.
        executable_path: Path to the running executable (sys.executable).
        meipass: PyInstaller's temporary extraction directory, or None.
    """

    is_frozen: bool
    bundler: Optional[str]
    executable_path: str
    meipass: Optional[str]


def detect_frozen() -> FrozenState:
    """Detect whether the process is running from a bundled executable.

    Checks ``sys.frozen`` (set by PyInstaller and cx_Freeze) and
    ``sys._MEIPASS`` (PyInstaller-specific temp directory).

    Returns:
        A FrozenState describing the current execution environment.
    """
    frozen = getattr(sys, "frozen", False)
    meipass = getattr(sys, "_MEIPASS", None)

    if frozen:
        if meipass is not None:
            bundler = "PyInstaller"
        else:
            bundler = "cx_Freeze"
    else:
        bundler = None

    return FrozenState(
        is_frozen=bool(frozen),
        bundler=bundler,
        executable_path=sys.executable,
        meipass=str(meipass) if meipass is not None else None,
    )


def resolve_code_location(caller_file: Optional[str] = None) -> str:
    """Return a meaningful path for where the code lives.

    When frozen (PyInstaller), the individual ``.py`` source files don't
    exist on disk, so we return ``sys.executable`` (the bundled binary).
    When running from source, we resolve *caller_file* to an absolute path.

    Args:
        caller_file: Typically ``__file__`` from the calling module.
            Ignored when running from a frozen executable.

    Returns:
        Absolute path string to the executable or source file.
    """
    state = detect_frozen()
    if state.is_frozen:
        return state.executable_path
    if caller_file is not None:
        return str(Path(caller_file).resolve())
    return state.executable_path
