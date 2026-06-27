from __future__ import annotations

from PySide6.QtCore import Qt, Signal

from stratbox_windows.application.events.models import OperationalEvent
from stratbox_windows.presentation.qt_desktop.chat_scene import ChatSceneHost
from stratbox_windows.presentation.qt_desktop.components.background_strip import ActiveBackgroundStrip
from .top_bar import TopBar
from stratbox_windows.presentation.qt_desktop.components.scenario_composer import BottomScenarioComposer
from stratbox_windows.presentation.common.scenario_chat.models import ScenarioChatMessage
from stratbox_windows.presentation.common.scenario_chat.projector import project_case, project_event
from stratbox_windows.presentation.qt_desktop.scenario_chat.widgets import ScenarioChatView
from stratbox_windows.runtime.bootstrap import AppRuntime


class CenterScenarioPanel(ChatSceneHost):
    run_requested = Signal()
    details_requested = Signal()
    artifact_open_requested = Signal(str)
    case_selected = Signal(str)
    background_process_selected = Signal(str)

    def __init__(self, runtime: AppRuntime, parent=None) -> None:
        super().__init__(None, parent)
        self.setObjectName('centerPanel')
        self._runtime = runtime
        self._filter_mode = runtime.context.user_config.chat.filter_mode
        self._chat_context_key: tuple[str, str | None] | None = None
        self.top_bar = TopBar(runtime, self.overlay_top)
        self.overlay_top_layout.addWidget(self.top_bar, 1, Qt.AlignTop)

        self.background_strip = ActiveBackgroundStrip(runtime.background_store)
        self.background_strip.process_selected.connect(self.background_process_selected.emit)
        self.content_layout.addWidget(self.background_strip)
        self.chat = ScenarioChatView()
        self.chat.case_selected.connect(self.case_selected.emit)
        self.chat.artifact_open_requested.connect(self.artifact_open_requested.emit)
        self.content_layout.addWidget(self.chat, 1)
        self.composer = BottomScenarioComposer()
        self.composer.run_requested.connect(self.run_requested.emit)
        self.composer.details_requested.connect(self.details_requested.emit)
        self.content_layout.addWidget(self.composer)
        self.refresh(reset_view=True)

    def current_filter_mode(self) -> str:
        return self._filter_mode

    def set_filter_mode(self, mode: str) -> None:
        self._filter_mode = mode
        self.refresh(reset_view=True)

    def set_scenario(self, scenario, params_summary: str = '') -> None:
        self.composer.set_scenario(scenario, params_summary=params_summary)

    def set_busy(self, busy: bool) -> None:
        self.composer.set_busy(busy)

    def refresh(self, *, reset_view: bool = False) -> None:
        self.background_strip.refresh()
        author_id = self._runtime.context.user_id if self._filter_mode == 'mine' else self._runtime.context.user_config.chat.selected_author_id
        context_key = (self._filter_mode, author_id)
        reset_view = reset_view or self._chat_context_key != context_key
        self._chat_context_key = context_key

        messages: list[ScenarioChatMessage] = [
            project_case(
                case,
                self._runtime.artifact_store,
                current_user_id=self._runtime.context.user_id,
            )
            for case in self._runtime.case_store.visible(mode=self._filter_mode, author_id=author_id)
        ]
        important_events = [
            event for event in self._runtime.event_store.recent(100)
            if event.kind in {'system_notice', 'background_notice', 'assignment_notice'}
            and self._event_visible_for_filter(event)
        ]
        messages.extend(
            project_event(event, current_user_id=self._runtime.context.user_id)
            for event in important_events
        )
        messages.sort(key=lambda item: item.sort_key)
        self.chat.set_messages(tuple(messages), reset_view=reset_view)

    def _event_visible_for_filter(self, event: OperationalEvent) -> bool:
        if self._filter_mode == 'all':
            return True
        if self._filter_mode == 'errors':
            return event.status == 'error'
        if self._filter_mode == 'unread':
            return event.unread
        if self._filter_mode == 'running':
            return event.status == 'running'
        if self._filter_mode == 'mine':
            return event.author_id in {None, self._runtime.context.user_id}
        if self._filter_mode == 'success':
            return event.status in {'success', 'warning'}
        return True
