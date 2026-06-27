from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from stratbox_windows.application.scenarios.models import ScenarioSpec


class BottomScenarioComposer(QFrame):
    run_requested = Signal()
    details_requested = Signal()

    _DETAILS_SLOT_WIDTH = 60

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName('bottomScenarioComposer')

        outer = QHBoxLayout(self)
        outer.setContentsMargins(24, 4, 24, 6)
        outer.setSpacing(0)
        outer.addStretch(1)

        self.launch_group = QWidget(self)
        self.launch_group.setObjectName('bottomScenarioComposerGroup')
        group_layout = QHBoxLayout(self.launch_group)
        group_layout.setContentsMargins(0, 0, 0, 0)
        group_layout.setSpacing(12)

        self.left_reserve = QWidget(self.launch_group)
        self.left_reserve.setObjectName('bottomScenarioComposerReserve')
        self.left_reserve.setFixedWidth(self._DETAILS_SLOT_WIDTH)
        group_layout.addWidget(self.left_reserve)

        self.launch_card = QFrame(self.launch_group)
        self.launch_card.setObjectName('scenarioLaunchCard')
        self.launch_card.setMaximumWidth(720)
        card_layout = QHBoxLayout(self.launch_card)
        card_layout.setContentsMargins(18, 14, 18, 14)
        card_layout.setSpacing(18)

        text_col = QVBoxLayout()
        text_col.setSpacing(3)
        self.title = QLabel('Сценарий не выбран')
        self.title.setObjectName('composerOperationTitle')
        self.title.setWordWrap(True)
        self.summary = QLabel('Выберите сценарий слева или откройте проводник.')
        self.summary.setObjectName('composerPlaceholder')
        self.summary.setWordWrap(True)
        text_col.addWidget(self.title)
        text_col.addWidget(self.summary)
        card_layout.addLayout(text_col, 1)
        card_layout.addStretch(1)

        self.run_button = QPushButton('Запустить')
        self.run_button.setObjectName('primaryRunButton')
        self.run_button.clicked.connect(self.run_requested.emit)
        card_layout.addWidget(self.run_button, 0, Qt.AlignVCenter)

        group_layout.addWidget(self.launch_card, 0, Qt.AlignVCenter)

        self.details_button = QPushButton('☰')
        self.details_button.setObjectName('detailsToggleButton')
        self.details_button.setToolTip('Показать или скрыть детали')
        self.details_button.setFixedSize(48, 48)
        self.details_button.clicked.connect(self.details_requested.emit)
        group_layout.addWidget(self.details_button, 0, Qt.AlignVCenter)

        outer.addWidget(self.launch_group, 0, Qt.AlignHCenter)
        outer.addStretch(1)

    def set_scenario(self, scenario: ScenarioSpec | None, params_summary: str = '') -> None:
        if scenario is None:
            self.title.setText('Сценарий не выбран')
            self.summary.setText('Выберите сценарий слева или откройте проводник.')
            self.run_button.setText('Запустить')
            self.run_button.setEnabled(False)
            return
        self.title.setText(scenario.title)
        steps_count = len(scenario.steps)
        params_hint = params_summary or 'параметры по умолчанию'
        self.summary.setText(f'{steps_count} шаг(ов) · {params_hint}')
        self.run_button.setText(scenario.submit_label)
        self.run_button.setEnabled(True)

    def set_busy(self, busy: bool) -> None:
        self.run_button.setEnabled(not busy)
        self.details_button.setEnabled(not busy)
