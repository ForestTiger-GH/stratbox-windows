from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFrame, QPushButton, QVBoxLayout


class ShellMode:
    WORKSPACE = 'workspace'
    ATOMIC_SCENARIOS = 'atomic_scenarios'
    SCENARIO_BLOCKS = 'scenario_blocks'
    BACKGROUND = 'background'
    PEOPLE = 'people'
    ASSIGNMENTS = 'assignments'


class ModeRail(QFrame):
    mode_changed = Signal(str)

    _ITEMS = (
        (ShellMode.WORKSPACE, 'workspace.svg', 'workspace_active.svg', 'Проводник', 'W'),
        (ShellMode.ATOMIC_SCENARIOS, 'scenarios.svg', 'scenarios_active.svg', 'Сценарии', 'S'),
        (ShellMode.SCENARIO_BLOCKS, 'cascades.svg', 'cascades_active.svg', 'Каскады сценариев', 'C'),
        (ShellMode.BACKGROUND, 'background.svg', 'background_active.svg', 'Фоновые процессы', 'B'),
        (ShellMode.PEOPLE, 'people.svg', 'people_active.svg', 'Участники', 'P'),
        (ShellMode.ASSIGNMENTS, 'assignments.svg', 'assignments_active.svg', 'Поручения', 'T'),
    )

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName('modeRail')
        self.setFixedWidth(96)
        self._buttons: dict[str, QPushButton] = {}
        self._icons: dict[str, tuple[QIcon | None, QIcon | None]] = {}
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 10)
        layout.setSpacing(0)
        icons_root = Path(__file__).resolve().parents[3] / 'resources' / 'icons' / 'modes'
        for mode, icon_name, active_icon_name, tooltip, fallback in self._ITEMS:
            button = QPushButton(self)
            button.setObjectName('modeRailButton')
            button.setCheckable(True)
            button.setToolTip(tooltip)
            button.setFixedSize(96, 96)
            button.setIconSize(QSize(64, 64))
            icon_path = icons_root / icon_name
            active_icon_path = icons_root / active_icon_name
            normal_icon = QIcon(str(icon_path)) if icon_path.exists() else None
            active_icon = QIcon(str(active_icon_path)) if active_icon_path.exists() else normal_icon
            self._icons[mode] = (normal_icon, active_icon)
            if normal_icon is not None:
                button.setIcon(normal_icon)
                button.setText('')
            else:
                button.setText(fallback)
            button.clicked.connect(lambda checked=False, value=mode: self.set_mode(value, emit=True))
            self._buttons[mode] = button
            layout.addWidget(button)
        layout.addStretch(1)

    def set_mode(self, mode: str, *, emit: bool = False) -> None:
        for key, button in self._buttons.items():
            active = key == mode
            button.setChecked(active)
            button.setProperty('active', active)
            normal_icon, active_icon = self._icons.get(key, (None, None))
            if normal_icon is not None:
                button.setIcon(active_icon if active else normal_icon)
                button.setText('')
            button.style().unpolish(button)
            button.style().polish(button)
        if emit:
            self.mode_changed.emit(mode)
