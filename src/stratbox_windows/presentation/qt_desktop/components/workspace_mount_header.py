from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QFontMetrics, QIcon
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QWidget


class WorkspaceMountHeader(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName('workspaceMountHeader')
        self.setProperty('available', True)
        self._full_line_text = 'AppDock (недоступно)'
        self._status_text = ''

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self._icon_label = QLabel(self)
        self._icon_label.setObjectName('workspaceMountIcon')
        self._icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._icon_label, 0, Qt.AlignVCenter)

        self._line_label = QLabel(self)
        self._line_label.setObjectName('workspaceMountLine')
        self._line_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(self._line_label, 1, Qt.AlignVCenter)

        icons_root = Path(__file__).resolve().parents[3] / 'resources' / 'icons' / 'workspace'
        icon_path = icons_root / 'network_drive.svg'
        if icon_path.exists():
            icon = QIcon(str(icon_path))
            self._icon_label.setPixmap(icon.pixmap(16, 16))
        else:
            self._icon_label.setText('⛁')

        self.set_mount(path_text='(недоступно)', available=False, status_text='Источник AppDock пока недоступен.')

    def set_mount(self, *, path_text: str, available: bool, status_text: str = '') -> None:
        self._status_text = status_text
        self.setProperty('available', bool(available))
        self._full_line_text = f'AppDock {path_text or "(недоступно)"}'
        self._update_line_label()
        tooltip = self._full_line_text
        if status_text:
            tooltip += f'\n{status_text}'
        self.setToolTip(tooltip)
        self._line_label.setToolTip(tooltip)
        self.style().unpolish(self)
        self.style().polish(self)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._update_line_label()

    def _update_line_label(self) -> None:
        metrics = QFontMetrics(self._line_label.font())
        width = max(140, self._line_label.width() or self.width() - 28)
        shown = metrics.elidedText(self._full_line_text, Qt.ElideMiddle, width)
        self._line_label.setText(shown)
