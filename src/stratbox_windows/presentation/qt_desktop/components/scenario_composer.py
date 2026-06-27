from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from stratbox_windows.application.scenarios.models import ScenarioSpec


class BottomScenarioComposer(QFrame):
    run_requested = Signal()
    details_requested = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName('bottomScenarioComposer')

        self._scenario_available = False
        self._busy = False

        outer = QHBoxLayout(self)
        outer.setContentsMargins(24, 4, 24, 10)
        outer.setSpacing(0)
        outer.addStretch(1)

        self.launch_card = QFrame(self)
        self.launch_card.setObjectName('scenarioLaunchCard')
        self.launch_card.setMaximumWidth(760)
        self.launch_card.setMinimumWidth(560)
        card_layout = QGridLayout(self.launch_card)
        card_layout.setContentsMargins(22, 18, 18, 16)
        card_layout.setHorizontalSpacing(16)
        card_layout.setVerticalSpacing(8)
        card_layout.setColumnStretch(0, 1)
        card_layout.setColumnStretch(1, 0)

        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(6)

        self.title = QLabel('Сценарий не выбран')
        self.title.setObjectName('composerOperationTitle')
        self.title.setWordWrap(True)
        text_col.addWidget(self.title)

        self.summary = QLabel('Выберите сценарий слева или откройте проводник.')
        self.summary.setObjectName('composerScenarioSummary')
        self.summary.setWordWrap(True)
        text_col.addWidget(self.summary)

        self.meta = QLabel('После выбора сценария здесь появится краткая сводка запуска.')
        self.meta.setObjectName('composerScenarioMeta')
        self.meta.setWordWrap(True)
        text_col.addWidget(self.meta)

        card_layout.addLayout(text_col, 0, 0, 2, 1)

        self.actions_host = QHBoxLayout()
        self.actions_host.setContentsMargins(0, 0, 0, 0)
        self.actions_host.setSpacing(10)
        self.actions_host.addStretch(1)

        self.details_button = QPushButton('☰')
        self.details_button.setObjectName('detailsToggleButton')
        self.details_button.setToolTip('Показать или скрыть детали')
        self.details_button.setCursor(Qt.PointingHandCursor)
        self.details_button.setFixedSize(46, 46)
        self.details_button.clicked.connect(self.details_requested.emit)
        self.actions_host.addWidget(self.details_button)

        self.run_button = QPushButton('→')
        self.run_button.setObjectName('primaryRunButton')
        self.run_button.setToolTip('Запустить сценарий')
        self.run_button.setCursor(Qt.PointingHandCursor)
        self.run_button.setFixedSize(46, 46)
        self.run_button.clicked.connect(self.run_requested.emit)
        self.actions_host.addWidget(self.run_button)

        card_layout.addLayout(self.actions_host, 1, 1, 1, 1, Qt.AlignRight | Qt.AlignBottom)

        outer.addWidget(self.launch_card, 0, Qt.AlignHCenter)
        outer.addStretch(1)

    @staticmethod
    def _compact_params_text(params_summary: str) -> str:
        if not params_summary:
            return 'Параметры по умолчанию'
        normalized = params_summary.strip()
        if not normalized:
            return 'Параметры по умолчанию'
        if normalized == 'параметры по умолчанию':
            return 'Параметры по умолчанию'
        parts = [part.strip() for part in normalized.split(',') if part.strip()]
        if not parts:
            return 'Параметры по умолчанию'
        visible = parts[:2]
        suffix = ' · …' if len(parts) > 2 else ''
        compact = ' · '.join(visible) + suffix
        if len(compact) > 110:
            compact = compact[:109].rstrip() + '…'
        return compact

    def set_scenario(self, scenario: ScenarioSpec | None, params_summary: str = '') -> None:
        if scenario is None:
            self.title.setText('Сценарий не выбран')
            self.summary.setText('Выберите сценарий слева или откройте проводник.')
            self.meta.setText('После выбора сценария здесь появится краткая сводка запуска.')
            self.run_button.setToolTip('Запустить сценарий')
            self._scenario_available = False
            self._apply_enabled_state()
            return

        steps_count = len(scenario.steps)
        steps_label = f'{steps_count} шаг' if steps_count == 1 else f'{steps_count} шаг(ов)'
        summary_text = (scenario.description or 'Сценарий готов к запуску.').strip()
        if len(summary_text) > 150:
            summary_text = summary_text[:149].rstrip() + '…'
        self.title.setText(scenario.title)
        self.summary.setText(summary_text)
        self.meta.setText(f'{steps_label} · {self._compact_params_text(params_summary)}')
        self.run_button.setToolTip(scenario.submit_label or 'Запустить сценарий')
        self._scenario_available = True
        self._apply_enabled_state()

    def set_busy(self, busy: bool) -> None:
        self._busy = busy
        self._apply_enabled_state()

    def _apply_enabled_state(self) -> None:
        enabled = self._scenario_available and not self._busy
        self.run_button.setEnabled(enabled)
        self.details_button.setEnabled(enabled)
