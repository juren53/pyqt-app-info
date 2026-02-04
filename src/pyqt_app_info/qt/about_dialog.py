"""Reusable About dialog for PyQt6 applications.

Takes a fully populated ``AppInfo`` from ``gather_info()`` and renders
it in a two-section dialog: identity/features at the top, technical
details (selectable) at the bottom.
"""

from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..info import AppInfo


class AboutDialog(QDialog):
    """A parameterized About dialog driven by ``AppInfo``.

    Args:
        app_info: The ``AppInfo`` object returned by ``gather_info()``.
        parent: Optional parent widget.
    """

    def __init__(
        self,
        app_info: AppInfo,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._app_info = app_info
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        ident = self._app_info.identity
        exe = self._app_info.execution
        tools = self._app_info.tools

        # Window title
        title = f"About {ident.name}"
        if ident.short_name:
            title += f" [ {ident.short_name} ]"
        self.setWindowTitle(title)
        self.resize(600, 500)

        layout = QVBoxLayout(self)

        # --- Section 1: Identity ---
        heading = ident.name
        if ident.short_name:
            heading += f" [ {ident.short_name} ]"

        parts = [f"<h3>{_esc(heading)}</h3>"]
        if ident.version:
            parts.append(f"<p><b>Version:</b> {_esc(ident.version)}</p>")
        if ident.commit_date:
            parts.append(f"<p><b>Commit Date:</b> {_esc(ident.commit_date)}</p>")
        if ident.description:
            parts.append(f"<br><p>{_esc(ident.description)}</p>")
        if ident.features:
            parts.append("<br><p><b>Features:</b></p><ul>")
            for feat in ident.features:
                parts.append(f"<li>{_esc(feat)}</li>")
            parts.append("</ul>")

        identity_label = QLabel("".join(parts))
        identity_label.setTextFormat(Qt.TextFormat.RichText)
        identity_label.setWordWrap(True)
        layout.addWidget(identity_label)

        # Separator spacing
        layout.addSpacing(10)

        # --- Section 2: Technical info ---
        tech_parts = [
            f'<p style="font-size: 9pt; color: #666;">',
            f"<b>Execution Mode:</b> {_esc(exe.execution_mode)}<br><br>",
            f"<b>Code Location:</b><br>{_esc(exe.code_location)}<br><br>",
            f"<b>Python Executable:</b><br>{_esc(exe.python_executable)}<br><br>",
        ]

        # Tools
        for tool in tools:
            if tool.status == "available":
                tech_parts.append(
                    f"<b>{_esc(tool.name)}:</b> v{_esc(tool.version or '')}<br>"
                    f"{_esc(tool.path or '')}<br><br>"
                )
            elif tool.path:
                tech_parts.append(
                    f"<b>{_esc(tool.name)}:</b> Found but version unavailable<br>"
                    f"{_esc(tool.path)}<br><br>"
                )
            else:
                tech_parts.append(
                    f"<b>{_esc(tool.name)}:</b> Not found in PATH<br><br>"
                )

        tech_parts.append(f"<b>OS:</b> {_esc(exe.os_platform)}")
        tech_parts.append("</p>")

        tech_label = QLabel("".join(tech_parts))
        tech_label.setTextFormat(Qt.TextFormat.RichText)
        tech_label.setWordWrap(True)
        tech_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        layout.addWidget(tech_label)

        # --- OK button ---
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        ok_btn.setDefault(True)
        ok_btn.setMinimumWidth(80)
        button_layout.addWidget(ok_btn)
        layout.addLayout(button_layout)


def _esc(text: str) -> str:
    """Minimal HTML escaping for display strings."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
