from __future__ import annotations

from PySide6.QtWidgets import QDialog, QVBoxLayout

from stratbox_windows.presentation.qt_desktop.panels.node_overview_panel import NodeOverviewPanel
from stratbox_windows.runtime.bootstrap import AppRuntime


class NodeDialog(QDialog):
    def __init__(self, runtime: AppRuntime, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle('Узел')
        self.resize(560, 420)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.panel = NodeOverviewPanel(runtime, self)
        layout.addWidget(self.panel)
        self.panel.refresh()
