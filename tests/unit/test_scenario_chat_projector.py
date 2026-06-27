from __future__ import annotations

from datetime import datetime, timedelta

from stratbox_windows.application.cases.models import ScenarioRunCase
from stratbox_windows.application.events.models import OperationalEvent
from stratbox_windows.presentation.common.scenario_chat.projector import project_case, project_event


class _EmptyArtifactStore:
    def by_case(self, case_id: str):
        return ()


def test_project_case_uses_author_for_outgoing_side_and_created_at_sort_key() -> None:
    created_at = datetime(2026, 1, 1, 10, 0)
    case = ScenarioRunCase(
        case_id='case-1',
        scenario_id='scenario',
        scenario_title='Обновить данные',
        params={'scope': 'all'},
        status='success',
        created_at=created_at,
        author_id='user-1',
        author_label='Дима',
        started_at=created_at + timedelta(minutes=1),
        finished_at=created_at + timedelta(minutes=3),
        message='Готово',
    )

    message = project_case(case, _EmptyArtifactStore(), current_user_id='user-1')

    assert message.placement == 'outgoing'
    assert message.avatar_text == 'Д'
    assert message.avatar_palette_key == 'user:user-1'
    assert message.sort_key == created_at.isoformat()


def test_project_event_keeps_system_message_incoming_even_with_current_user_author() -> None:
    event = OperationalEvent.create(
        event_id='evt-1',
        kind='system_notice',
        status='info',
        title='Готово',
        body='Рабочая поверхность готова',
        actor_kind='system',
        author_id='user-1',
        author_label='Дима',
    )

    message = project_event(event, current_user_id='user-1')

    assert message.placement == 'incoming'
    assert message.avatar_text == 'SB'
    assert message.avatar_palette_key == 'system'


def test_project_event_puts_foreign_user_message_on_incoming_side() -> None:
    event = OperationalEvent.create(
        event_id='evt-2',
        kind='assignment_notice',
        status='info',
        title='Поручение обновлено',
        body='Нужно проверить выгрузку',
        actor_kind='user',
        author_id='user-2',
        author_label='Анна',
    )

    message = project_event(event, current_user_id='user-1')

    assert message.placement == 'incoming'
    assert message.avatar_text == 'А'
    assert message.avatar_palette_key == 'user:user-2'
