from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QVariantAnimation
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from stratbox_windows.runtime.bootstrap import AppRuntime
from .center_panel import CenterScenarioPanel
from .left_panel import LeftPanel
from .mode_rail import ModeRail
from .right_drawer import RightInspectorDrawer


class ShellBodyWidget(QWidget):
    def __init__(self, runtime: AppRuntime, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName('shellRoot')
        self.runtime = runtime
        self.drawer_width = runtime.context.user_config.shell.right_inspector_width
        self._drawer_progress = 0.0

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.left_shell = QWidget(self)
        self.left_shell.setObjectName('leftShell')
        left_shell_layout = QVBoxLayout(self.left_shell)
        left_shell_layout.setContentsMargins(0, 0, 0, 0)
        left_shell_layout.setSpacing(0)

        self.left_brand_header = QWidget(self.left_shell)
        self.left_brand_header.setObjectName('leftShellHeader')
        left_brand_layout = QVBoxLayout(self.left_brand_header)
        left_brand_layout.setContentsMargins(18, 16, 16, 16)
        left_brand_layout.setSpacing(0)
        self.left_brand_title = QLabel('Strategy Box', self.left_brand_header)
        self.left_brand_title.setObjectName('leftShellBrandTitle')
        left_brand_layout.addWidget(self.left_brand_title)
        left_shell_layout.addWidget(self.left_brand_header)

        self.left_body = QWidget(self.left_shell)
        self.left_body.setObjectName('leftShellBody')
        left_body_layout = QHBoxLayout(self.left_body)
        left_body_layout.setContentsMargins(0, 0, 0, 0)
        left_body_layout.setSpacing(0)
        self.mode_rail = ModeRail(self.left_body)
        self.left_panel = LeftPanel(runtime, self.left_body)
        self.left_panel.setFixedWidth(runtime.context.user_config.shell.left_panel_width)
        left_body_layout.addWidget(self.mode_rail)
        left_body_layout.addWidget(self.left_panel)
        left_shell_layout.addWidget(self.left_body, 1)
        root.addWidget(self.left_shell)

        self.central_host = QWidget(self)
        self.central_host.setObjectName('centralHost')
        central_layout = QVBoxLayout(self.central_host)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)
        self.center_panel = CenterScenarioPanel(runtime, self.central_host)
        self.top_bar = self.center_panel.top_bar
        central_layout.addWidget(self.center_panel, 1)
        root.addWidget(self.central_host, 1)

        self.right_drawer = RightInspectorDrawer(runtime, self)
        root.addWidget(self.right_drawer)

        self._animation = QVariantAnimation(self)
        self._animation.setDuration(220)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)
        self._animation.valueChanged.connect(lambda value: self.set_drawer_progress(float(value)))
        self._animation.finished.connect(self._finalize_drawer_visibility)
        self.right_drawer.close_requested.connect(lambda: self.set_right_drawer_open(False))
        self._connect_state_persistence()
        self._apply_drawer_state(self._drawer_progress)

    def _connect_state_persistence(self) -> None:
        self.mode_rail.mode_changed.connect(lambda mode: self.runtime.preferences.save(selected_mode=mode))
        self.top_bar.filter_changed.connect(lambda mode: self.runtime.preferences.save(filter_mode=mode))
        self.right_drawer.tab_changed.connect(lambda tab: self.runtime.preferences.save(right_inspector_tab=tab))

    def set_drawer_progress(self, value: float) -> None:
        self._drawer_progress = max(0.0, min(1.0, value))
        self._apply_drawer_state(self._drawer_progress)

    def _apply_drawer_state(self, progress: float) -> None:
        target_width = int(round(self.drawer_width * progress))
        if target_width <= 0:
            self.right_drawer.setFixedWidth(0)
            if not self._animation.state():
                self.right_drawer.setVisible(False)
            return
        self.right_drawer.setVisible(True)
        self.right_drawer.setFixedWidth(target_width)

    def _finalize_drawer_visibility(self) -> None:
        if self._drawer_progress <= 0.0:
            self.right_drawer.setVisible(False)
            self.right_drawer.setFixedWidth(0)

    def is_right_drawer_open(self) -> bool:
        return self._drawer_progress >= 0.5

    def toggle_right_drawer(self) -> None:
        self.set_right_drawer_open(not self.is_right_drawer_open())

    def set_right_drawer_open(self, open_: bool) -> None:
        target = 1.0 if open_ else 0.0
        if open_:
            self.right_drawer.setVisible(True)
        self._animation.stop()
        self._animation.setStartValue(self._drawer_progress)
        self._animation.setEndValue(target)
        self._animation.start()
        self.runtime.preferences.save(right_inspector_open=open_)

    def open_right_drawer(self, tab: str | None = None) -> None:
        if tab:
            self.right_drawer.set_active_tab(tab, emit=True)
        self.set_right_drawer_open(True)
