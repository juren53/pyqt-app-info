"""Core data model for application information.

Defines the dataclasses that describe an application's identity and
runtime environment, plus the ``gather_info()`` entry-point that
auto-detects everything in one call.
"""

from __future__ import annotations

import platform
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ._compat import detect_frozen, resolve_code_location
from .tools import ToolRegistry, ToolResult


@dataclass
class AppIdentity:
    """Static identity information supplied by the host application.

    Attributes:
        name: Full display name (e.g. "HSTL Photo Metadata Framework").
        short_name: Abbreviation shown in titles (e.g. "HPM").
        version: Semantic version string.
        commit_date: Human-readable build / commit date.
        author: Author or organization name.
        description: One-line description of the application.
        features: Optional bullet-point feature list.
    """

    name: str
    short_name: str = ""
    version: str = ""
    commit_date: str = ""
    author: str = ""
    description: str = ""
    features: List[str] = field(default_factory=list)


@dataclass
class ExecutionInfo:
    """Automatically detected runtime environment details.

    Attributes:
        python_executable: Path to the Python interpreter.
        python_version: ``sys.version`` string.
        code_location: Resolved path to the executable or source file.
        os_platform: ``platform.platform()`` result.
        is_frozen: Whether running inside a bundled executable.
        execution_mode: Human-readable label ("Compiled executable" or
            "Python source").
        bundler: Bundler name if frozen, else None.
    """

    python_executable: str = ""
    python_version: str = ""
    code_location: str = ""
    os_platform: str = ""
    is_frozen: bool = False
    execution_mode: str = ""
    bundler: Optional[str] = None


@dataclass
class AppInfo:
    """Complete application information — identity + environment + tools.

    Returned by ``gather_info()``.
    """

    identity: AppIdentity
    execution: ExecutionInfo
    tools: List[ToolResult] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a plain dict (useful for logging / JSON)."""
        return {
            "identity": {
                "name": self.identity.name,
                "short_name": self.identity.short_name,
                "version": self.identity.version,
                "commit_date": self.identity.commit_date,
                "author": self.identity.author,
                "description": self.identity.description,
                "features": list(self.identity.features),
            },
            "execution": {
                "python_executable": self.execution.python_executable,
                "python_version": self.execution.python_version,
                "code_location": self.execution.code_location,
                "os_platform": self.execution.os_platform,
                "is_frozen": self.execution.is_frozen,
                "execution_mode": self.execution.execution_mode,
                "bundler": self.execution.bundler,
            },
            "tools": [
                {
                    "name": t.name,
                    "path": t.path,
                    "version": t.version,
                    "status": t.status,
                }
                for t in self.tools
            ],
        }

    @property
    def summary_lines(self) -> List[str]:
        """Human-readable summary lines (handy for CLI output)."""
        ident = self.identity
        exe = self.execution
        lines: List[str] = []

        title = ident.name
        if ident.short_name:
            title += f" [ {ident.short_name} ]"
        lines.append(title)

        if ident.version:
            lines.append(f"  Version:      {ident.version}")
        if ident.commit_date:
            lines.append(f"  Commit Date:  {ident.commit_date}")
        if ident.description:
            lines.append(f"  {ident.description}")

        lines.append("")
        lines.append(f"  Execution:    {exe.execution_mode}")
        lines.append(f"  Code:         {exe.code_location}")
        lines.append(f"  Python:       {exe.python_executable}")
        lines.append(f"  Python Ver:   {exe.python_version}")
        lines.append(f"  OS:           {exe.os_platform}")

        for tool in self.tools:
            if tool.status == "available":
                lines.append(f"  {tool.name}:  v{tool.version}  ({tool.path})")
            elif tool.path:
                lines.append(f"  {tool.name}:  found but version unavailable  ({tool.path})")
            else:
                lines.append(f"  {tool.name}:  not found")

        return lines


def gather_info(
    identity: AppIdentity,
    *,
    registry: Optional[ToolRegistry] = None,
    caller_file: Optional[str] = None,
) -> AppInfo:
    """Detect the runtime environment and return a complete ``AppInfo``.

    Args:
        identity: Static app identity supplied by the caller.
        registry: Optional tool registry; if provided, every registered
            tool is detected and included in the result.
        caller_file: Typically ``__file__`` from the calling module.
            Used to resolve the code location when not frozen.

    Returns:
        An ``AppInfo`` combining *identity*, auto-detected execution
        details, and tool results.
    """
    frozen_state = detect_frozen()

    execution = ExecutionInfo(
        python_executable=sys.executable,
        python_version=sys.version.split()[0],
        code_location=resolve_code_location(caller_file),
        os_platform=platform.platform(),
        is_frozen=frozen_state.is_frozen,
        execution_mode=(
            "Compiled executable" if frozen_state.is_frozen else "Python source"
        ),
        bundler=frozen_state.bundler,
    )

    tools: List[ToolResult] = []
    if registry is not None:
        tools = registry.detect_all()

    return AppInfo(identity=identity, execution=execution, tools=tools)
