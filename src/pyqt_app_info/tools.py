"""Generic external-tool detection registry.

Provides a registry for declaring external CLI tools (e.g. ExifTool,
ImageMagick) and detecting their availability, path, and version at
runtime.  Uses only the stdlib (``shutil.which``, ``subprocess``).
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class ToolSpec:
    """Specification for an external CLI tool to detect.

    Attributes:
        name: Human-readable display name (e.g. "ExifTool").
        command: Executable name passed to ``shutil.which()`` (e.g. "exiftool").
        version_flag: CLI flag that prints the version (e.g. "-ver", "--version").
        fallback_paths: Extra directories to probe when ``shutil.which()``
            returns nothing.  Each entry is a path to the *executable itself*,
            not just the directory.
        version_timeout: Seconds to wait for the version command.
    """

    name: str
    command: str
    version_flag: str = "--version"
    fallback_paths: List[str] = field(default_factory=list)
    version_timeout: float = 5.0


@dataclass
class ToolResult:
    """Detection result for a single tool.

    Attributes:
        name: Display name (copied from ToolSpec).
        path: Absolute path to the executable, or None if not found.
        version: Version string reported by the tool, or None.
        status: One of ``"available"``, ``"not_found"``, ``"error"``.
    """

    name: str
    path: Optional[str] = None
    version: Optional[str] = None
    status: str = "not_found"  # "available" | "not_found" | "error"


class ToolRegistry:
    """Registry of external tools to detect.

    Usage::

        registry = ToolRegistry()
        registry.register(ToolSpec(
            name="ExifTool",
            command="exiftool",
            version_flag="-ver",
            fallback_paths=["/usr/local/bin/exiftool"],
        ))
        results = registry.detect_all()
    """

    def __init__(self) -> None:
        self._specs: Dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec) -> None:
        """Register a tool specification."""
        self._specs[spec.name] = spec

    def detect(self, name: str) -> ToolResult:
        """Detect a single registered tool by name.

        Args:
            name: The ``ToolSpec.name`` that was registered.

        Returns:
            A ToolResult with detection outcome.

        Raises:
            KeyError: If *name* was never registered.
        """
        spec = self._specs[name]
        return self._detect_one(spec)

    def detect_all(self) -> List[ToolResult]:
        """Detect every registered tool.

        Returns:
            List of ToolResult in registration order.
        """
        return [self._detect_one(spec) for spec in self._specs.values()]

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _detect_one(spec: ToolSpec) -> ToolResult:
        """Run detection for a single ToolSpec."""
        path = shutil.which(spec.command)

        # Fallback paths
        if path is None:
            for candidate in spec.fallback_paths:
                if Path(candidate).is_file():
                    path = candidate
                    break

        if path is None:
            return ToolResult(name=spec.name, status="not_found")

        # Try to get version
        try:
            proc = subprocess.run(
                [path, spec.version_flag],
                capture_output=True,
                text=True,
                timeout=spec.version_timeout,
            )
            if proc.returncode == 0:
                version = proc.stdout.strip().split("\n")[0]
                return ToolResult(
                    name=spec.name,
                    path=path,
                    version=version,
                    status="available",
                )
            return ToolResult(name=spec.name, path=path, status="error")
        except (subprocess.TimeoutExpired, OSError):
            return ToolResult(name=spec.name, path=path, status="error")
