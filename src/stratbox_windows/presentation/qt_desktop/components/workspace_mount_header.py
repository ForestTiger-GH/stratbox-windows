from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QFontMetrics, QIcon
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout


class WorkspaceMountHeader(QFrame):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName('workspaceMountHeader')
        self.setProperty('available', True)
        self._full_path_text = '(недоступно)'
        self._status_text = ''

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(12)

        self._icon_badge = QFrame(self)
        self._icon_badge.setObjectName('workspaceMountIconBadge')
        icon_layout = QVBoxLayout(self._icon_badge)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setSpacing(0)
        self._icon_label = QLabel(self._icon_badge)
        self._icon_label.setObjectName('workspaceMountIcon')
        self._icon_label.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(self._icon_label)
        layout.addWidget(self._icon_badge, 0, Qt.AlignVCenter)

        text_host = QVBoxLayout()
        text_host.setContentsMargins(0, 0, 0, 0)
        text_host.setSpacing(2)
        self._title_label = QLabel('AppDock', self)
        self._title_label.setObjectName('workspaceMountTitle')
        text_host.addWidget(self._title_label)
        self._path_label = QLabel(self)
        self._path_label.setObjectName('workspaceMountPath')
        self._path_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        text_host.addWidget(self._path_label)
        layout.addLayout(text_host, 1)

        icons_root = Path(__file__).resolve().parents[3] / 'resources' / 'icons' / 'workspace'
        icon_path = icons_root / 'network_drive.svg'
        if icon_path.exists():
            icon = QIcon(str(icon_path))
            self._icon_label.setPixmap(icon.pixmap(24, 24))
        else:
            self._icon_label.setText('⛁')

        self.set_mount(path_text='(недоступно)', available=False, status_text='Источник AppDock пока недоступен.')

    def set_mount(self, *, path_text: str, available: bool, status_text: str = '') -> None:
        self._full_path_text = path_text
        self._status_text = status_text
        self.setProperty('available', bool(available))
        self._title_label.setText('AppDock')
        self._update_path_label()
        tooltip = 'AppDock'
        if path_text:
            tooltip += f'\n{path_text}'
        if status_text:
            tooltip += f'\n{status_text}'
        self.setToolTip(tooltip)
        self._title_label.setToolTip(tooltip)
        self._path_label.setToolTip(tooltip)
        self.style().unpolish(self)
        self.style().polish(self)
        self._icon_badge.style().unpolish(self._icon_badge)
        self._icon_badge.style().polish(self._icon_badge)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._update_path_label()

    def _update_path_label(self) -> None:
        text = self._full_path_text or '(недоступно)'
        metrics = QFontMetrics(self._path_label.font())
        available_width = max(120, self._path_label.width() or self.width() - 120)
        shown = metrics.elidedText(text, Qt.ElideMiddle, available_width)
        self._path_label.setText(shown)
