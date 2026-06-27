from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFontMetrics
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QToolButton, QWidget


class WorkspacePathBar(QWidget):
    up_requested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName('workspacePathBar')
        self._display_text = 'Рабочая область'
        self._tooltip_text = ''
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self._up_button = QToolButton(self)
        self._up_button.setObjectName('workspacePathUpButton')
        self._up_button.setText('↑')
        self._up_button.clicked.connect(self.up_requested.emit)
        layout.addWidget(self._up_button, 0, Qt.AlignVCenter)

        self._label = QLabel(self)
        self._label.setObjectName('workspacePathLabel')
        self._label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(self._label, 1, Qt.AlignVCenter)

        self.set_path(parts=tuple(), can_go_up=False, tooltip_text='')

    def set_path(self, *, parts: tuple[str, ...], can_go_up: bool, tooltip_text: str) -> None:
        self._display_text = ' > '.join(parts) if parts else 'Рабочая область'
        self._tooltip_text = tooltip_text or self._display_text
        self._up_button.setEnabled(can_go_up)
        self._up_button.setVisible(True)
        self._update_label_text()
        self.setToolTip(self._tooltip_text)
        self._label.setToolTip(self._tooltip_text)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._update_label_text()

    def _update_label_text(self) -> None:
        metrics = QFontMetrics(self._label.font())
        width = max(120, self._label.width() or self.width() - 44)
        shown = metrics.elidedText(self._display_text, Qt.ElideMiddle, width)
        self._label.setText(shown)
