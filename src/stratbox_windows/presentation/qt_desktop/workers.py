from __future__ import annotations

from typing import Any

from PySide6.QtCore import QObject, Signal, Slot

from stratbox_windows.application.artifacts.models import ArtifactRecord
from stratbox_windows.application.artifacts.store import ArtifactStore
from stratbox_windows.application.cases.models import ScenarioRunCase
from stratbox_windows.application.events.models import OperationalEvent
from stratbox_windows.application.events.store import OperationalEventStore
from stratbox_windows.application.logs.models import LogRecord
from stratbox_windows.application.logs.store import LogStore
from stratbox_windows.application.operations.catalog.models import OperationRegistry
from stratbox_windows.application.scenarios.models import ScenarioSpec
from stratbox_windows.application.scenarios.runner import run_scenario
from stratbox_windows.runtime.context import AppContext


class ScenarioWorker(QObject):
    case_updated = Signal(object)
    event_appended = Signal(object)
    artifacts_created = Signal(object)
    log_created = Signal(object)
    finished = Signal(object)

    def __init__(
        self,
        *,
        scenario: ScenarioSpec,
        operation_registry: OperationRegistry,
        context: AppContext,
        params: dict[str, Any],
        case: ScenarioRunCase,
    ) -> None:
        super().__init__()
        self._scenario = scenario
        self._operation_registry = operation_registry
        self._context = context
        self._params = dict(params)
        self._case = case

    @Slot()
    def run(self) -> None:
        try:
            final_case = run_scenario(
                scenario=self._scenario,
                operation_registry=self._operation_registry,
                context=self._context,
                params=self._params,
                case=self._case,
                on_case_updated=self.case_updated.emit,
                on_event=self.event_appended.emit,
                on_artifacts=self.artifacts_created.emit,
                on_log=self.log_created.emit,
            )
        except Exception as exc:  # pragma: no cover - defensive boundary
            self._context.logger.exception('Unhandled scenario worker failure: %s', self._scenario.id)
            self._case.status = 'failed'
            self._case.message = f'Unhandled scenario failure: {exc}'
            final_case = self._case
        self.finished.emit(final_case)
