from __future__ import annotations

from stratbox_windows.application.artifacts.store import ArtifactStore
from stratbox_windows.application.cases.models import ScenarioRunCase
from stratbox_windows.application.events.models import OperationalEvent
from .models import ScenarioArtifactLine, ScenarioChatMessage, ScenarioStepLine


_STATUS_LABELS = {
    'prepared': 'Подготовлено',
    'queued': 'В очереди',
    'running': 'Выполняется',
    'success': 'Завершено',
    'warning': 'С замечаниями',
    'failed': 'Ошибка',
    'cancelled': 'Отменено',
    'info': 'Инфо',
    'error': 'Ошибка',
}


def _initial(value: str | None, fallback: str) -> str:
    text = (value or '').strip()
    if not text:
        text = fallback
    for char in text:
        if char.isalnum():
            return char.upper()
    return fallback[:1].upper()


def _case_avatar_palette_key(case: ScenarioRunCase) -> str:
    author_key = case.author_id or case.author_label or case.case_id
    return f'user:{author_key}'


def _event_avatar_text(event: OperationalEvent) -> str:
    if event.actor_kind in {'system', 'background'}:
        return 'SB'
    if event.actor_kind == 'ai':
        return 'AI'
    return _initial(event.author_label or event.author_id, 'U')


def _event_avatar_palette_key(event: OperationalEvent) -> str:
    if event.actor_kind == 'background':
        process_id = event.meta.get('process_id') if event.meta else None
        return f'background:{process_id or event.event_id}'
    if event.actor_kind == 'system':
        return 'system'
    if event.actor_kind == 'ai':
        return 'ai'
    author_key = event.author_id or event.author_label or event.event_id
    return f'user:{author_key}'


def _event_placement(event: OperationalEvent, *, current_user_id: str | None) -> str:
    if event.actor_kind in {'system', 'background', 'ai'}:
        return 'incoming'
    if current_user_id and event.author_id == current_user_id:
        return 'outgoing'
    return 'incoming'


def project_case(
    case: ScenarioRunCase,
    artifacts: ArtifactStore,
    *,
    current_user_id: str | None = None,
) -> ScenarioChatMessage:
    case_artifacts = artifacts.by_case(case.case_id)
    placement = 'outgoing' if current_user_id and case.author_id == current_user_id else 'incoming'
    return ScenarioChatMessage(
        message_id=case.case_id,
        message_kind='case',
        tone=case.status,
        title=case.scenario_title,
        summary=case.message or ('Сценарий выполняется.' if case.status == 'running' else 'Сценарий подготовлен.'),
        status_label=_STATUS_LABELS.get(case.status, case.status),
        status=case.status,
        author_label=case.author_label or 'Пользователь',
        timestamp_label=case.timestamp_label,
        sort_key=case.created_at.isoformat(),
        actor_kind='user',
        actor_id=case.author_id or '',
        placement=placement,
        avatar_text=_initial(case.author_label or case.author_id, 'U'),
        avatar_palette_key=_case_avatar_palette_key(case),
        message_family='case',
        unread=case.unread,
        stage_label=case.current_stage or None,
        params_summary=case.short_params_text(),
        steps=tuple(ScenarioStepLine(step.title, step.status, step.message) for step in case.steps),
        artifacts=tuple(ScenarioArtifactLine(item.name, item.path) for item in case_artifacts),
        source_case_id=case.case_id,
    )


def project_event(
    event: OperationalEvent,
    *,
    current_user_id: str | None = None,
) -> ScenarioChatMessage:
    default_author = 'Фоновый процесс' if event.actor_kind == 'background' else 'Система'
    return ScenarioChatMessage(
        message_id=event.event_id,
        message_kind='notice',
        tone=event.status,
        title=event.title,
        summary=event.body,
        status_label=_STATUS_LABELS.get(event.status, event.status),
        status=event.status,
        author_label=event.author_label or default_author,
        timestamp_label=event.timestamp_label,
        sort_key=event.created_at.isoformat(),
        actor_kind=event.actor_kind,
        actor_id=event.author_id or '',
        placement=_event_placement(event, current_user_id=current_user_id),
        avatar_text=_event_avatar_text(event),
        avatar_palette_key=_event_avatar_palette_key(event),
        message_family='notice',
        unread=event.unread,
        source_event_id=event.event_id,
        source_case_id=event.case_id,
    )
