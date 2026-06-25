from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QMenu, QPushButton, QWidget

from stratbox_windows.runtime.bootstrap import AppRuntime


class TopBar(QWidget):
    diagnostics_requested = Signal()
    settings_requested = Signal()
    refresh_requested = Signal()
    exit_requested = Signal()
    node_requested = Signal()
    filter_changed = Signal(str)

    _FILTERS = (
        ('all', 'Все'),
        ('mine', 'Мои'),
        ('running', 'В работе'),
        ('success', 'Успешные'),
        ('errors', 'Ошибки'),
        ('unread', 'Непрочитанные'),
    )

    def __init__(self, runtime: AppRuntime, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName('topBar')
        self._runtime = runtime
        self._filter_buttons: dict[str, QPushButton] = {}
        self._filter_mode = runtime.context.user_config.chat.filter_mode
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 12, 20, 12)
        layout.setSpacing(10)
        self.filters_host = QWidget(self)
        self.filters_host.setObjectName('topBarFiltersHost')
        filters_layout = QHBoxLayout(self.filters_host)
        filters_layout.setContentsMargins(0, 0, 0, 0)
        filters_layout.setSpacing(8)
        for mode, title in self._FILTERS:
            button = QPushButton(title, self.filters_host)
            button.setCheckable(True)
            button.setObjectName('scenarioFilterPill')
            button.clicked.connect(lambda checked=False, value=mode: self.set_filter_mode(value, emit=True))
            self._filter_buttons[mode] = button
            filters_layout.addWidget(button)
        filters_layout.addStretch(1)
        layout.addWidget(self.filters_host, 1)
        self.user_button = QPushButton('', self)
        self.user_button.setObjectName('topBarAvatarButton')
        self.user_button.setToolTip('Меню пользователя')
        self.user_button.clicked.connect(self._show_menu)
        layout.addWidget(self.user_button)
        self.set_filter_mode(self._filter_mode)
        self.refresh_context()

    def _avatar_text(self) -> str:
        account = (self._runtime.context.account_name or '').strip()
        if account:
            return account[:1].upper()
        user_id = (self._runtime.context.user_id or '').strip()
        if user_id:
            return user_id[:1].upper()
        return 'U'

    def refresh_context(self) -> None:
        self.user_button.setText(self._avatar_text())
        account = self._runtime.context.account_name or 'Пользователь'
        self.user_button.setToolTip(f'{account} · меню пользователя')

    def set_filter_mode(self, mode: str, *, emit: bool = False) -> None:
        if mode not in self._filter_buttons:
            mode = 'all'
        self._filter_mode = mode
        for key, button in self._filter_buttons.items():
            active = key == mode
            button.setChecked(active)
            button.setProperty('active', active)
            button.style().unpolish(button)
            button.style().polish(button)
        if emit:
            self.filter_changed.emit(mode)

    def _show_menu(self) -> None:
        menu = QMenu(self)
        node = menu.addAction('Узел')
        settings = menu.addAction('Настройки')
        refresh = menu.addAction('Обновить состояние')
        diagnostics = menu.addAction('Диагностика')
        menu.addSeparator()
        exit_action = menu.addAction('Выход')
        selected = menu.exec(self.user_button.mapToGlobal(self.user_button.rect().bottomRight()))
        if selected == node:
            self.node_requested.emit()
        elif selected == settings:
            self.settings_requested.emit()
        elif selected == refresh:
            self.refresh_requested.emit()
        elif selected == diagnostics:
            self.diagnostics_requested.emit()
        elif selected == exit_action:
            self.exit_requested.emit()
